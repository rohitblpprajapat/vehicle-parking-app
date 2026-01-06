from flask import Flask, request
from flask_cors import CORS
from models import db
from config import DevelopmentConfig
from sec import datastore
from flask_security import Security
from initial_data import create_initial_data
from flask_migrate import Migrate
# from api_routes import api
from redis_cache import cache, redis_cache

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    @app.before_request
    def log_request_info():
        print(f"DEBUG Headers: {request.headers}")
        print(f"DEBUG Cookies: {request.cookies}")
    
    # Initialize extensions
    migrate = Migrate(app, db)
    cache.init_app(app)
    redis_cache.init_app(app)
    
    # Configure CORS with more permissive settings for development
    # Configure CORS with credentials support
    # Configure CORS - Simplification for Development
    # We are using supports_credentials=True, so we must specific origins.
    # We will use the top-level CORS constructor to apply it globally to /api/v1/*
    CORS(app, 
         resources={r"/api/v1/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "Authentication-Token"],
         expose_headers=["Content-Range", "X-Total-Count"])
    
    with app.app_context():
        # Initialize database
        db.init_app(app)
        
        # Initialize Flask-Security
        security = Security(app, datastore)
        
        # Create database tables
        # db.drop_all()  # Commented out to prevent data loss on restart
        db.create_all()
        
        # Create initial data (idempotent, safe to run)
        create_initial_data()
        
        # Register modular blueprints
        from routes import auth_bp, parking_bp, reservation_bp, admin_bp, analytics_bp
        
        # Auth Routes (/api/v1/auth/*)
        app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        
        # Parking Lot Routes (/api/v1 - needed because some are root-like)
        app.register_blueprint(parking_bp, url_prefix='/api/v1')
        
        # Reservation Routes (/api/v1/reservations/*)
        app.register_blueprint(reservation_bp, url_prefix='/api/v1/reservations')
        
        # Admin Routes (/api/v1/admin/*)
        app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
        
        # Analytics Routes (/api/v1 - mixed admin and user routes)
        app.register_blueprint(analytics_bp, url_prefix='/api/v1')

    
    return app

app = create_app()

@app.route('/')
def index():
    return {'message': 'Vehicle Parking API', 'status': 'running'}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)