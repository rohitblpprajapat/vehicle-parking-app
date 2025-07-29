from flask import Blueprint, request, jsonify, current_app
from flask_security import login_user, logout_user, auth_required, current_user, hash_password
from flask_security.utils import verify_password
from models import db, User, Role
from sec import datastore
import secrets

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

# Add a global OPTIONS handler for CORS preflight requests
@api.before_request
def handle_options():
    if request.method == 'OPTIONS':
        # Create a response for preflight requests
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

# Test endpoint
@api.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'API is working!', 'status': 'ok'}), 200

@api.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'meta': {'code': 400},
                'response': {'errors': ['No data provided']}
            }), 400
        
        # Validate required fields
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        print(f"DEBUG: Received data: {data}")
        print(f"DEBUG: name='{name}', email='{email}', password='{password[:5]}...'")
        
        if not email:
            return jsonify({
                'meta': {'code': 400},
                'response': {'errors': ['Email is required']}
            }), 400
            
        if not password:
            return jsonify({
                'meta': {'code': 400},
                'response': {'errors': ['Password is required']}
            }), 400
            
        if not name:
            return jsonify({
                'meta': {'code': 400},
                'response': {'errors': ['Name is required']}
            }), 400
        
        # Check password length
        if len(password) < 6:
            return jsonify({
                'meta': {'code': 400},
                'response': {'errors': ['Password must be at least 6 characters long']}
            }), 400
        
        # Check if user already exists
        if datastore.find_user(email=email):
            return jsonify({
                'meta': {'code': 400},
                'response': {'errors': ['User with this email already exists']}
            }), 400
        
        # Get or create user role
        user_role = datastore.find_role('user')
        if not user_role:
            user_role = datastore.create_role(name='user', description='Regular user role')
            db.session.commit()
        
        # Create user directly using the User model to avoid Flask-Security's email triggers
        from datetime import datetime
        import uuid

        print(f"DEBUG: About to create user with name='{name}'")
        
        user = datastore.create_user(
            email=email,
            password=hash_password(password),
            name=name,
            active=True,
            confirmed_at=datetime.utcnow(),
            fs_uniquifier=str(uuid.uuid4())
        )
        
        print(f"DEBUG: Created user object with name='{user.name}'")
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        print(f"DEBUG: After flush, user.name='{user.name}'")
        
        # Add user role manually using the roles relationship
        user.roles.append(user_role)
        db.session.commit()
        
        return jsonify({
            'meta': {'code': 201},
            'response': {
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'active': user.active
                }
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'meta': {'code': 500},
            'response': {'errors': ['Registration failed']}
        }), 500

@api.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()

        
        if not data:
            print("No data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        # Accept both 'email' and 'identity' for flexibility
        email = data.get('email') or data.get('identity')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = datastore.find_user(email=email)
        
        if not user or not verify_password(password, user.password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.active:
            return jsonify({'error': 'Account is disabled'}), 401
        
        # Login user
        login_user(user, remember=data.get('remember', False))
        
        return jsonify({
            'meta': {'code': 200},
            'response': {
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'authentication_token': user.get_auth_token(),
                    'roles': [role.name for role in user.roles]
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@api.route('/auth/logout', methods=['POST'])
@auth_required()
def logout():
    """Logout user"""
    try:
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@api.route('/auth/me', methods=['GET'])
@auth_required()
def get_current_user():
    """Get current user info"""
    try:
        return jsonify({
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email,
                'username': current_user.username,
                'roles': [role.name for role in current_user.roles],
                'active': current_user.active
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user info'}), 500

@api.route('/auth/change-password', methods=['POST'])
@auth_required()
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not verify_password(current_password, current_user.password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        current_user.password = hash_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Change password error: {str(e)}")
        return jsonify({'error': 'Failed to change password'}), 500

# Parking lot routes
@api.route('/parking-lots', methods=['GET'])
def get_parking_lots():
    """Get all parking lots"""
    try:
        from models import Parking_lot
        lots = Parking_lot.query.all()
        
        return jsonify({
            'parking_lots': [{
                'id': lot.id,
                'name': lot.name,
                'location': lot.location,
                'capacity': lot.capacity,
                'available_spots': len([spot for spot in lot.spots if not spot.is_occupied])
            } for lot in lots]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get parking lots error: {str(e)}")
        return jsonify({'error': 'Failed to get parking lots'}), 500

@api.route('/reservations', methods=['GET'])
@auth_required()
def get_user_reservations():
    """Get current user's reservations"""
    try:
        reservations = current_user.reservations
        
        return jsonify({
            'reservations': [{
                'id': res.id,
                'parking_lot': res.parking_spot.parking_lot.name,
                'spot_number': res.parking_spot.spot_number,
                'start_time': res.start_time.isoformat(),
                'end_time': res.end_time.isoformat(),
                'status': res.status,
                'created_at': res.created_at.isoformat()
            } for res in reservations]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get reservations error: {str(e)}")
        return jsonify({'error': 'Failed to get reservations'}), 500

# Error handlers
@api.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@api.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden access'}), 403

@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
