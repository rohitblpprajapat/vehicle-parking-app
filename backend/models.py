from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fs_uniquifier = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy=True))
    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)
    


class Parking_lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.String(20), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    
    parking_lot = db.relationship('Parking_lot', backref=db.backref('spots', lazy=True))
    
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref=db.backref('reservations', lazy=True))
    parking_spot = db.relationship('ParkingSpot', backref=db.backref('reservations', lazy=True))
    