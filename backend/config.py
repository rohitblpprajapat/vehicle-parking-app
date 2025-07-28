import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ram-bharose'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'ram-bharose'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_Secret_key') or "ye bhi ram bharose"
    SECURITY_JSON = True
    SECURITY_POST_LOGIN_VIEW = '/'

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    DEBUG = True