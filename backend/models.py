from flask_sqlalchemy import SQLAlchemy
from flask_security.models import fsqla_v3 as fsqla
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from utils import get_ist_now

db = SQLAlchemy()

# Configure Flask-Security models
fsqla.FsModels.set_db_info(db)

# Define models using Flask-Security mixins
class Role(db.Model, fsqla.FsRoleMixin):
    pass

class User(db.Model, fsqla.FsUserMixin):
    # Additional fields beyond the Flask-Security standard ones
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True)
    
    # Add relationship to reservations
    reservations = db.relationship('Reservation', backref='user', lazy=True)

class Parking_lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False, default=5.0)  # Price per hour
    created_at = db.Column(db.DateTime, default=get_ist_now)
    updated_at = db.Column(db.DateTime, default=get_ist_now, onupdate=get_ist_now)
    
    # Relationship to parking spots
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.String(20), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_ist_now)
    
    # Relationship to reservations
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True)
    
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=get_ist_now)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    
    # Cost and duration tracking
    reserved_duration_hours = db.Column(db.Float, nullable=True)  # Originally reserved duration
    actual_duration_hours = db.Column(db.Float, nullable=True)    # Actual parking duration
    estimated_cost = db.Column(db.Float, nullable=True)           # Initial estimated cost
    final_cost = db.Column(db.Float, nullable=True)               # Final calculated cost
    hourly_rate = db.Column(db.Float, nullable=True)              # Rate at time of reservation
    
    # Timestamps for better tracking
    occupied_at = db.Column(db.DateTime, nullable=True)           # When user actually arrived
    released_at = db.Column(db.DateTime, nullable=True)           # When user left
    
    # Vehicle details
    vehicle_number = db.Column(db.String(20), nullable=True)      # Vehicle registration number

    
    