import redis
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request
import hashlib

# Setup logging
logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, app=None):
        self.redis_client = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Redis cache with Flask app"""
        try:
            redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.key_prefix = app.config.get('CACHE_KEY_PREFIX', 'vehicle_parking:')
            
            # Test connection
            self.redis_client.ping()
            
            # Register with Flask extensions
            if not hasattr(app, 'extensions'):
                app.extensions = {}
            app.extensions['redis_cache'] = self
            
            app.logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            app.logger.error(f"Failed to initialize Redis cache: {e}")
            # Set to None so we can fall back gracefully
            self.redis_client = None
    
    def is_available(self):
        """Check if Redis is available"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def get(self, key):
        """Get value from cache"""
        if not self.is_available():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    def set(self, key, value, timeout=300):
        """Set value in cache with timeout (default 5 minutes)"""
        if not self.is_available():
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, timeout, serialized_value)
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    def _get_cache_key(self, key):
        """Generate cache key with prefix"""
        return f"{self.key_prefix}{key}"
    
    def exists(self, key):
        """Check if a key exists in cache"""
        try:
            cache_key = self._get_cache_key(key)
            return self.redis_client.exists(cache_key) > 0
        except Exception as e:
            current_app.logger.error(f"Cache exists error: {e}")
            return False
    
    def invalidate_pattern(self, pattern):
        """Delete all keys matching a pattern"""
        try:
            pattern_key = self._get_cache_key(pattern)
            keys = self.redis_client.keys(pattern_key)
            if keys:
                self.redis_client.delete(*keys)
                current_app.logger.info(f"Invalidated {len(keys)} keys matching pattern: {pattern}")
        except Exception as e:
            current_app.logger.error(f"Pattern invalidation error: {e}")
    
    def delete(self, key):
        """Delete a key from cache"""
        try:
            full_key = self._get_cache_key(key)
            return self.redis_client.delete(full_key)
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern):
        """Delete all keys matching pattern"""
        if not self.is_available():
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting pattern from cache: {str(e)}")
            return False
    
    def flush_all(self):
        """Clear all cache"""
        if not self.is_available():
            return False
        
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Error flushing cache: {str(e)}")
            return False

    def acquire_lock(self, lock_name, acquire_timeout=10, lock_timeout=10):
        """
        Acquire a distributed lock
        Args:
            lock_name: Unique name for the lock
            acquire_timeout: How long to wait to acquire the lock (seconds)
            lock_timeout: How long the lock remains valid (seconds)
        Returns:
             identifier (str) if acquired, False otherwise
        """
        if not self.is_available():
            return False
            
        identifier = str(datetime.now().timestamp())
        lock_key = f"lock:{lock_name}"
        end_time = datetime.now() + timedelta(seconds=acquire_timeout)
        
        while datetime.now() < end_time:
            if self.redis_client.setnx(lock_key, identifier):
                self.redis_client.expire(lock_key, lock_timeout)
                return identifier
            
            # Check if lock is expired but not deleted (deadlock prevention)
            if self.redis_client.ttl(lock_key) == -1:
                self.redis_client.expire(lock_key, lock_timeout)
                
            import time
            time.sleep(0.1)
            
        return False

    def release_lock(self, lock_name, identifier):
        """Release a distributed lock"""
        if not self.is_available():
            return False
            
        lock_key = f"lock:{lock_name}"
        try:
            # Use optimistic locking/watch to ensure we only release OUR lock
            pipe = self.redis_client.pipeline(True)
            while True:
                try:
                    pipe.watch(lock_key)
                    lock_value = pipe.get(lock_key)
                    
                    if lock_value == identifier:
                        pipe.multi()
                        pipe.delete(lock_key)
                        pipe.execute()
                        return True
                        
                    pipe.unwatch()
                    break
                    
                except redis.WatchError:
                    continue
                    
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
            
        return False

# Global cache instance
cache = RedisCache()

def generate_cache_key(prefix, *args, **kwargs):
    """Generate a unique cache key"""
    # Include user context for user-specific caching
    user_id = getattr(request, 'user_id', 'anonymous') if request else 'anonymous'
    
    # Create a hash of arguments for consistent key generation
    key_data = f"{prefix}:{user_id}:{':'.join(map(str, args))}"
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        key_data += f":{':'.join(f'{k}={v}' for k, v in sorted_kwargs)}"
    
    # Hash the key if it's too long
    if len(key_data) > 200:
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    return key_data

def cached(timeout=300, key_prefix=None):
    """
    Decorator for caching function results
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Custom key prefix (default: function name)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                from flask import has_app_context, current_app
                
                # Only use caching if we're in a Flask app context
                if not has_app_context():
                    return func(*args, **kwargs)
                
                # Get the redis cache instance from current app
                cache_instance = current_app.extensions.get('redis_cache')
                if not cache_instance:
                    return func(*args, **kwargs)
                
                # Generate cache key
                func_name = key_prefix or func.__name__
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{func_name}:{hash(args_str)}"
                
                # Try to get from cache
                cached_result = cache_instance.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache_instance.set(cache_key, result, timeout)
                return result
                
            except Exception as e:
                if has_app_context():
                    current_app.logger.error(f"Caching error in {func.__name__}: {e}")
                # Fall back to executing function without caching
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern):
    """Helper function to invalidate cache by pattern"""
    return cache.delete_pattern(pattern)

def invalidate_parking_cache():
    """Invalidate all parking-related cache"""
    patterns = [
        "parking_lots:*",
        "available_spots:*",
        "parking_analytics:*",
        "lot_details:*"
    ]
    
    for pattern in patterns:
        cache.delete_pattern(pattern)
    
    logger.info("Invalidated parking-related cache")

def invalidate_user_cache(user_id):
    """Invalidate user-specific cache"""
    patterns = [
        f"user_data:{user_id}:*",
        f"user_reservations:{user_id}:*",
        f"user_analytics:{user_id}:*"
    ]
    
    for pattern in patterns:
        cache.delete_pattern(pattern)
    
    logger.info(f"Invalidated cache for user: {user_id}")

# Cache configuration constants
class CacheConfig:
    # Cache timeouts (in seconds)
    PARKING_LOTS_TIMEOUT = 300        # 5 minutes
    AVAILABLE_SPOTS_TIMEOUT = 60      # 1 minute (frequent updates)
    USER_DATA_TIMEOUT = 600           # 10 minutes
    ANALYTICS_TIMEOUT = 1800          # 30 minutes
    RESERVATIONS_TIMEOUT = 120        # 2 minutes
    ADMIN_ANALYTICS_TIMEOUT = 900     # 15 minutes
    
    # Cache key prefixes
    PARKING_LOTS_KEY = "parking_lots"
    AVAILABLE_SPOTS_KEY = "available_spots"
    USER_DATA_KEY = "user_data"
    USER_RESERVATIONS_KEY = "user_reservations"
    USER_ANALYTICS_KEY = "user_analytics"
    ADMIN_ANALYTICS_KEY = "admin_analytics"
    LOT_DETAILS_KEY = "lot_details"

# Global cache instances
redis_cache = RedisCache()
cache = redis_cache
