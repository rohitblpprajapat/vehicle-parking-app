from flask import Flask
from flask_cors import CORS
from models import db
from config import DevelopmentConfig
from sec import datastore
from flask_security import Security
from initial_data import create_initial_data
from flask_migrate import Migrate
from api_routes import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    migrate = Migrate(app, db)
    
    # Configure CORS with more permissive settings for development
    CORS(app, 
         resources={
             r"/api/v1/*": {
                 "origins": "*",
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Authentication-Token"]
             }
         }, 
         supports_credentials=True)
    
    with app.app_context():
        # Initialize database
        db.init_app(app)
        
        # Initialize Flask-Security
        security = Security(app, datastore)
        
        # Create database tables
        db.drop_all()  # Drop existing tables to handle schema changes
        db.create_all()
        
        # Create initial data
        create_initial_data()
        
        # Register API blueprint
        app.register_blueprint(api)
    
    return app

app = create_app()

@app.route('/')
def index():
    return {'message': 'Vehicle Parking API', 'status': 'running'}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)