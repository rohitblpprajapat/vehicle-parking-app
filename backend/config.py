import os
import secrets

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or str(secrets.SystemRandom().getrandbits(128))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Security settings
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = False  # Disable email confirmation
    SECURITY_SEND_REGISTER_EMAIL = False  # Don't send registration emails
    SECURITY_RECOVERABLE = False   # Disable password reset (requires email)
    SECURITY_CHANGEABLE = True    # Enable password change
    SECURITY_TRACKABLE = True     # Track user login stats
    
    # Enable token authentication
    SECURITY_TOKEN_AUTHENTICATION_KEY = 'Authentication-Token'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    SECURITY_TOKEN_MAX_AGE = 86400  # 24 hours
    
    # Disable all email features
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = False
    
    # JSON API support
    SECURITY_JSON = True
    SECURITY_URL_PREFIX = '/api/auth'
    
    # Post-authentication views
    SECURITY_POST_LOGIN_VIEW = '/dashboard'
    SECURITY_POST_LOGOUT_VIEW = '/'
    SECURITY_POST_REGISTER_VIEW = '/dashboard'
    
    # Username support
    SECURITY_USERNAME_ENABLE = True
    SECURITY_USERNAME_REQUIRED = False  # Email is still primary
    
    # Email settings (for development)
    SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": False}
    
    # Password settings
    SECURITY_PASSWORD_HASH = 'argon2'
    SECURITY_PASSWORD_LENGTH_MIN = 6
    
    # CSRF settings for API
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for API endpoints
    
    # CORS settings for Flask-Security
    SECURITY_CORS_ORIGINS = ["http://127.0.0.1:5173", "http://localhost:5173"]
    SECURITY_CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "Authentication-Token"]
    
    # Session settings
    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"
    
    # JWT for token-based auth
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_urlsafe(32)

class ProductionConfig(Config):
    DEBUG = False
    # Override for production - use strong secrets
    SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": True}

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    DEBUG = True
    WTF_CSRF_ENABLED = False