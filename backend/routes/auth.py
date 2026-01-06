from flask import Blueprint, request, jsonify, current_app
from flask_security import login_user, logout_user, auth_required, current_user, hash_password
from flask_security.utils import verify_password
from models import db, User
from sec import datastore
import uuid
from datetime import datetime
from utils import get_ist_now


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'meta': {'code': 400},
                'response': {'errors': ['No data provided']}
            }), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email:
            return jsonify({'meta': {'code': 400}, 'response': {'errors': ['Email is required']}}), 400
        if not password:
            return jsonify({'meta': {'code': 400}, 'response': {'errors': ['Password is required']}}), 400
        if not name:
            return jsonify({'meta': {'code': 400}, 'response': {'errors': ['Name is required']}}), 400
        
        if len(password) < 6:
            return jsonify({'meta': {'code': 400}, 'response': {'errors': ['Password must be at least 6 characters long']}}), 400
        
        if datastore.find_user(email=email):
            return jsonify({'meta': {'code': 400}, 'response': {'errors': ['User with this email already exists']}}), 400
        
        user_role = datastore.find_role('user')
        if not user_role:
            user_role = datastore.create_role(name='user', description='Regular user role')
            db.session.commit()
        
        user = User(
            email=email,
            password=hash_password(password),
            name=name,
            active=True,
            confirmed_at=get_ist_now(),
            fs_uniquifier=str(uuid.uuid4())
        )
        
        db.session.add(user)
        db.session.flush()
        
        datastore.add_role_to_user(user, user_role)
        db.session.commit()
        
        return jsonify({
            'meta': {'code': 201},
            'response': {
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'active': user.active,
                    'roles': [role.name for role in user.roles]
                }
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'meta': {'code': 500}, 'response': {'errors': ['Registration failed']}}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email') or data.get('identity')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'meta': {'code': 400}, 'response': {'errors': ['Email and password are required']}}), 400

        
        user = datastore.find_user(email=email)
        if not user:
            return jsonify({'meta': {'code': 401}, 'response': {'errors': ['User not found']}}), 401
        
        if not user or not verify_password(password, user.password):
            return jsonify({'meta': {'code': 401}, 'response': {'errors': ['Invalid credentials']}}), 401
        
        if not user.active:
            return jsonify({'meta': {'code': 401}, 'response': {'errors': ['Account is disabled']}}), 401

        
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
        return jsonify({'meta': {'code': 500}, 'response': {'errors': ['Login failed']}}), 500


@auth_bp.route('/logout', methods=['POST'])
@auth_required('token', 'session')
def logout():
    """Logout user"""
    try:
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'meta': {'code': 500}, 'response': {'errors': ['Logout failed']}}), 500


@auth_bp.route('/me', methods=['GET'])
@auth_required('token', 'session')
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
        return jsonify({'meta': {'code': 500}, 'response': {'errors': ['Failed to get user info']}}), 500


@auth_bp.route('/change-password', methods=['POST'])
@auth_required('token', 'session')
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
        
        if not verify_password(current_password, current_user.password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        current_user.password = hash_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Change password error: {str(e)}")
        return jsonify({'meta': {'code': 500}, 'response': {'errors': ['Failed to change password']}}), 500

