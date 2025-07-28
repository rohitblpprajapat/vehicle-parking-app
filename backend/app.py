from flask import Flask
from models import db
from config import DevelopmentConfig

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    with app.app_context():
        db.init_app(app)
        db.create_all()  # Create database tables if they don't exist
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)