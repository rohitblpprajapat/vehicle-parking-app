from flask import Blueprint, request, jsonify, current_app
from flask_security import login_user, logout_user, auth_required, current_user, hash_password, roles_required
from flask_security.utils import verify_password
from models import db, User, Role, Parking_lot, ParkingSpot, Reservation
from sec import datastore
import secrets
from functools import wraps
from datetime import datetime

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

# Add a global OPTIONS handler for CORS preflight requests
@api.before_request
def handle_options():
    if request.method == 'OPTIONS':
        # Create a response for preflight requests
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Authentication-Token')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

# Test endpoint
@api.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'API is working!', 'status': 'ok'}), 200

# Debug endpoint to check user roles
@api.route('/debug/user', methods=['GET'])
@auth_required('token', 'session')
def debug_user():
    return jsonify({
        'user': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'roles': [role.name for role in current_user.roles],
            'is_admin': current_user.has_role('admin')
        }
    }), 200

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
        
        user = User(
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
        
        print(f"DEBUG: After flush, user.name='{user.name}', user.id='{user.id}'")
        
        # Add user role using Flask-Security's datastore method
        datastore.add_role_to_user(user, user_role)
        db.session.commit()
        
        print(f"DEBUG: After role assignment, user roles: {[role.name for role in user.roles]}")
        
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
@auth_required('token', 'session')
def logout():
    """Logout user"""
    try:
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@api.route('/auth/me', methods=['GET'])
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
        return jsonify({'error': 'Failed to get user info'}), 500

@api.route('/auth/change-password', methods=['POST'])
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
def calculate_available_spots(lot):
    """Calculate truly available spots (not occupied and no active reservations)"""
    available_count = 0
    for spot in lot.spots:
        # Check if spot is not occupied and has no active reservations
        if not spot.is_occupied:
            has_active_reservation = any(res.status == 'active' for res in spot.reservations)
            if not has_active_reservation:
                available_count += 1
    return available_count

@api.route('/parking-lots', methods=['GET'])
def get_parking_lots():
    """Get all parking lots"""
    try:
        lots = Parking_lot.query.all()
        
        return jsonify({
            'parking_lots': [{
                'id': lot.id,
                'name': lot.name,
                'location': lot.location,
                'capacity': lot.capacity,
                'price_per_hour': lot.price_per_hour,
                'available_spots': calculate_available_spots(lot)
            } for lot in lots]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get parking lots error: {str(e)}")
        return jsonify({'error': 'Failed to get parking lots'}), 500

@api.route('/reservations', methods=['GET'])
@auth_required('token', 'session')
def get_user_reservations():
    """Get current user's reservations"""
    try:
        reservations = current_user.reservations
        
        reservation_list = []
        for res in reservations:
            parking_lot = res.parking_spot.parking_lot
            
            # Calculate duration in hours
            duration_hours = (res.end_time - res.start_time).total_seconds() / 3600
            
            # Calculate cost
            cost = parking_lot.price_per_hour * duration_hours
            
            # Check if spot is currently occupied
            is_occupied = res.parking_spot.is_occupied
            
            reservation_data = {
                'id': res.id,
                'parking_lot': parking_lot.name,
                'spot_number': res.parking_spot.spot_number,
                'reservation_time': res.created_at.isoformat(),
                'start_time': res.start_time.isoformat(),
                'end_time': res.end_time.isoformat(),
                'expires_at': res.end_time.isoformat(),
                'duration': round(duration_hours, 2),
                'cost': round(cost, 2),
                'status': res.status,
                'is_occupied': is_occupied,
                'hourly_rate': parking_lot.price_per_hour,
                'created_at': res.created_at.isoformat()
            }
            
            # Add occupied_at if the reservation is occupied (simulated)
            if is_occupied:
                reservation_data['occupied_at'] = res.start_time.isoformat()
            
            reservation_list.append(reservation_data)
        
        return jsonify({
            'reservations': reservation_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get reservations error: {str(e)}")
        return jsonify({'error': 'Failed to get reservations'}), 500

@api.route('/reservations', methods=['POST'])
@auth_required('token', 'session')
def create_reservation():
    """Auto-allocate and reserve the first available spot in a parking lot"""
    try:
        data = request.get_json()
        lot_id = data.get('lot_id')
        duration_hours = data.get('duration_hours', 1)  # Default 1 hour
        
        if not lot_id:
            return jsonify({'error': 'Parking lot ID is required'}), 400
        
        # Find the parking lot
        parking_lot = Parking_lot.query.get_or_404(lot_id)
        
        # Find the first available spot (not occupied and no active reservations)
        available_spot = ParkingSpot.query.filter_by(
            lot_id=lot_id, 
            is_occupied=False
        ).filter(
            ~ParkingSpot.reservations.any(Reservation.status == 'active')
        ).first()
        
        if not available_spot:
            return jsonify({'error': 'No available spots in this parking lot'}), 400
        
        # Check if user already has an active reservation in this lot
        existing_reservation = Reservation.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).join(ParkingSpot).filter_by(lot_id=lot_id).first()
        
        if existing_reservation:
            return jsonify({'error': 'You already have an active reservation in this parking lot'}), 400
        
        # Create reservation
        from datetime import datetime, timedelta
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=duration_hours)
        
        reservation = Reservation(
            user_id=current_user.id,
            spot_id=available_spot.id,
            start_time=start_time,
            end_time=end_time,
            status='active'
        )
        
        # Don't mark spot as occupied yet - only mark as occupied when user arrives
        # The spot is now "reserved" through the active reservation
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'message': 'Spot reserved successfully',
            'reservation': {
                'id': reservation.id,
                'parking_lot': parking_lot.name,
                'spot_number': available_spot.spot_number,
                'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat(),
                'status': reservation.status,
                'price_per_hour': parking_lot.price_per_hour,
                'total_cost': parking_lot.price_per_hour * duration_hours
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create reservation error: {str(e)}")
        return jsonify({'error': 'Failed to create reservation'}), 500

@api.route('/reservations/<int:reservation_id>/occupy', methods=['POST', 'PUT'])
@auth_required('token', 'session')
def occupy_spot(reservation_id):
    """Mark a reserved spot as occupied (user has arrived)"""
    try:
        reservation = Reservation.query.filter_by(
            id=reservation_id,
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found or not accessible'}), 404
        
        # Check if spot is already occupied
        if reservation.parking_spot.is_occupied:
            return jsonify({'error': 'Spot is already occupied'}), 400
        
        # Mark the parking spot as occupied and update timestamp
        reservation.parking_spot.is_occupied = True
        
        # Update timestamp to track when user actually arrived
        # For now, we'll use the reservation start_time update to track occupation
        # In a real system, you might want to add an occupied_at field to the Reservation model
        reservation.start_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Spot marked as occupied',
            'reservation': {
                'id': reservation.id,
                'spot_number': reservation.parking_spot.spot_number,
                'occupied_at': reservation.start_time.isoformat(),
                'status': reservation.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Occupy spot error: {str(e)}")
        return jsonify({'error': 'Failed to occupy spot'}), 500

@api.route('/reservations/<int:reservation_id>/release', methods=['POST', 'PUT'])
@auth_required('token', 'session')
def release_spot(reservation_id):
    """Release an occupied spot and complete the reservation"""
    try:
        reservation = Reservation.query.filter_by(
            id=reservation_id,
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found or not accessible'}), 404
        
        # Calculate actual duration and cost
        from datetime import datetime
        release_time = datetime.utcnow()
        actual_duration = (release_time - reservation.start_time).total_seconds() / 3600  # hours
        
        # Update reservation
        reservation.end_time = release_time
        reservation.status = 'completed'
        
        # Mark spot as available
        reservation.parking_spot.is_occupied = False
        
        # Calculate final cost
        parking_lot = reservation.parking_spot.parking_lot
        total_cost = parking_lot.price_per_hour * actual_duration
        
        db.session.commit()
        
        return jsonify({
            'message': 'Spot released successfully',
            'reservation': {
                'id': reservation.id,
                'spot_number': reservation.parking_spot.spot_number,
                'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat(),
                'duration_hours': round(actual_duration, 2),
                'actual_duration_hours': round(actual_duration, 2),
                'total_cost': round(total_cost, 2),
                'final_cost': round(total_cost, 2),
                'status': reservation.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Release spot error: {str(e)}")
        return jsonify({'error': 'Failed to release spot'}), 500

@api.route('/reservations/<int:reservation_id>/extend', methods=['POST', 'PUT'])
@auth_required('token', 'session')
def extend_reservation(reservation_id):
    """Extend an active reservation"""
    try:
        data = request.get_json()
        additional_hours = data.get('additional_hours', 1)
        
        reservation = Reservation.query.filter_by(
            id=reservation_id,
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found or not accessible'}), 404
        
        # Extend the end time
        from datetime import timedelta
        reservation.end_time += timedelta(hours=additional_hours)
        
        db.session.commit()
        
        parking_lot = reservation.parking_spot.parking_lot
        additional_cost = parking_lot.price_per_hour * additional_hours
        
        return jsonify({
            'message': 'Reservation extended successfully',
            'reservation': {
                'id': reservation.id,
                'new_end_time': reservation.end_time.isoformat(),
                'new_expires_at': reservation.end_time.isoformat(),
                'additional_cost': additional_cost,
                'status': reservation.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Extend reservation error: {str(e)}")
        return jsonify({'error': 'Failed to extend reservation'}), 500


@api.route('/reservations/<int:reservation_id>/cancel', methods=['POST'])
@auth_required('token', 'session')
def cancel_reservation(reservation_id):
    """Cancel an active reservation"""
    try:
        reservation = Reservation.query.filter_by(
            id=reservation_id,
            user_id=current_user.id
        ).first()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found or not accessible'}), 404
        
        # Only allow cancellation of active reservations that haven't been occupied
        if reservation.status not in ['active']:
            return jsonify({'error': 'Only active reservations can be cancelled'}), 400
        
        # For now, we'll assume any active reservation that started can't be cancelled
        # In a real system, you'd check if the user has actually arrived at the spot
        if datetime.utcnow() >= reservation.start_time:
            return jsonify({'error': 'Cannot cancel a reservation that has already started'}), 400
        
        # Update reservation status to cancelled
        reservation.status = 'cancelled'
        
        # Make the parking spot available again
        reservation.parking_spot.is_occupied = False
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation cancelled successfully',
            'reservation': {
                'id': reservation.id,
                'status': reservation.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Cancel reservation error: {str(e)}")
        return jsonify({'error': 'Failed to cancel reservation'}), 500

# ==================== ADMIN ROUTES ====================

@api.route('/admin/dashboard', methods=['GET'])
@roles_required('admin')
def admin_dashboard():
    print("admin dashboard function is called")
    """Get admin dashboard data with all parking lot statuses"""
    try:
        lots = Parking_lot.query.all()
        total_spots = sum(lot.capacity for lot in lots)
        occupied_spots = sum(len([spot for spot in lot.spots if spot.is_occupied]) for lot in lots)
        reserved_spots = sum(len([spot for spot in lot.spots for res in spot.reservations if res.status == 'active' and not spot.is_occupied]) for lot in lots)
        available_spots = total_spots - occupied_spots - reserved_spots
        
        # Get user statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(active=True).count()
        admin_users = User.query.join(User.roles).filter(Role.name == 'admin').count()
        
        # Get reservation statistics
        total_reservations = Reservation.query.count()
        active_reservations = Reservation.query.filter_by(status='active').count()
        completed_reservations = Reservation.query.filter_by(status='completed').count()
        
        dashboard_data = {
            'summary': {
                'total_parking_lots': len(lots),
                'total_spots': total_spots,
                'occupied_spots': occupied_spots,
                'available_spots': available_spots,
                'occupancy_rate': (occupied_spots / total_spots * 100) if total_spots > 0 else 0,
                'total_users': total_users,
                'active_users': active_users,
                'admin_users': admin_users,
                'total_reservations': total_reservations,
                'active_reservations': active_reservations,
                'completed_reservations': completed_reservations
            },
            'parking_lots': [{
                'id': lot.id,
                'name': lot.name,
                'location': lot.location,
                'capacity': lot.capacity,
                'price_per_hour': lot.price_per_hour,
                'occupied_spots': len([spot for spot in lot.spots if spot.is_occupied]),
                'available_spots': calculate_available_spots(lot),
                'occupancy_rate': (len([spot for spot in lot.spots if spot.is_occupied]) / lot.capacity * 100) if lot.capacity > 0 else 0,
                'spots': [{
                    'id': spot.id,
                    'spot_number': spot.spot_number,
                    'is_occupied': spot.is_occupied,
                    'is_reserved': any(res.status == 'active' for res in spot.reservations)
                } for spot in lot.spots]
            } for lot in lots]
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Admin dashboard error: {str(e)}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500

@api.route('/admin/parking-lots', methods=['GET'])
@roles_required('admin')
def get_admin_parking_lots():
    """Get all parking lots for admin management"""
    try:
        lots = Parking_lot.query.all()
        
        parking_lots_data = [{
            'id': lot.id,
            'name': lot.name,
            'location': lot.location,
            'capacity': lot.capacity,
            'price_per_hour': lot.price_per_hour,
            'occupied_spots': len([spot for spot in lot.spots if spot.is_occupied]),
            'available_spots': calculate_available_spots(lot),
            'occupancy_rate': (len([spot for spot in lot.spots if spot.is_occupied]) / lot.capacity * 100) if lot.capacity > 0 else 0
        } for lot in lots]
        
        return jsonify({
            'parking_lots': parking_lots_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get admin parking lots error: {str(e)}")
        return jsonify({'error': 'Failed to get parking lots'}), 500

@api.route('/admin/parking-lots', methods=['POST'])
@roles_required('admin')
def create_parking_lot():
    """Create a new parking lot"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        name = data.get('name', '').strip()
        location = data.get('location', '').strip()
        capacity = data.get('capacity')
        price_per_hour = data.get('price_per_hour', 5.0)
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        if not capacity or capacity <= 0:
            return jsonify({'error': 'Valid capacity is required'}), 400
        
        # Check if parking lot with same name exists
        if Parking_lot.query.filter_by(name=name).first():
            return jsonify({'error': 'Parking lot with this name already exists'}), 400
        
        # Create parking lot
        parking_lot = Parking_lot(
            name=name,
            location=location,
            capacity=capacity,
            price_per_hour=float(price_per_hour)
        )
        
        db.session.add(parking_lot)
        db.session.flush()  # Get the ID
        
        # Create parking spots
        for i in range(1, capacity + 1):
            spot = ParkingSpot(
                lot_id=parking_lot.id,
                spot_number=f"A{i:03d}"  # Format: A001, A002, etc.
            )
            db.session.add(spot)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking lot created successfully',
            'parking_lot': {
                'id': parking_lot.id,
                'name': parking_lot.name,
                'location': parking_lot.location,
                'capacity': parking_lot.capacity,
                'price_per_hour': parking_lot.price_per_hour
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create parking lot error: {str(e)}")
        return jsonify({'error': 'Failed to create parking lot'}), 500

@api.route('/admin/parking-lots/<int:lot_id>', methods=['PUT'])
@roles_required('admin')
def update_parking_lot(lot_id):
    """Update a parking lot"""
    try:
        lot = Parking_lot.query.get_or_404(lot_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'error': 'Name cannot be empty'}), 400
            # Check if another lot has this name
            existing = Parking_lot.query.filter(Parking_lot.name == name, Parking_lot.id != lot_id).first()
            if existing:
                return jsonify({'error': 'Parking lot with this name already exists'}), 400
            lot.name = name
        
        if 'location' in data:
            location = data['location'].strip()
            if not location:
                return jsonify({'error': 'Location cannot be empty'}), 400
            lot.location = location
        
        if 'price_per_hour' in data:
            try:
                lot.price_per_hour = float(data['price_per_hour'])
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid price per hour'}), 400
        
        # Handle capacity changes
        if 'capacity' in data:
            new_capacity = data['capacity']
            if new_capacity <= 0:
                return jsonify({'error': 'Capacity must be greater than 0'}), 400
            
            current_capacity = lot.capacity
            
            if new_capacity > current_capacity:
                # Add new spots
                for i in range(current_capacity + 1, new_capacity + 1):
                    spot = ParkingSpot(
                        lot_id=lot.id,
                        spot_number=f"A{i:03d}"
                    )
                    db.session.add(spot)
            elif new_capacity < current_capacity:
                # Remove spots (only unoccupied ones)
                spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot.id)\
                    .filter_by(is_occupied=False)\
                    .order_by(ParkingSpot.id.desc())\
                    .limit(current_capacity - new_capacity).all()
                
                if len(spots_to_remove) < (current_capacity - new_capacity):
                    return jsonify({'error': 'Cannot reduce capacity: some spots are occupied'}), 400
                
                for spot in spots_to_remove:
                    db.session.delete(spot)
            
            lot.capacity = new_capacity
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking lot updated successfully',
            'parking_lot': {
                'id': lot.id,
                'name': lot.name,
                'location': lot.location,
                'capacity': lot.capacity,
                'price_per_hour': lot.price_per_hour,
                'available_spots': calculate_available_spots(lot)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update parking lot error: {str(e)}")
        return jsonify({'error': 'Failed to update parking lot'}), 500

@api.route('/admin/parking-lots/<int:lot_id>', methods=['DELETE'])
@roles_required('admin')
def delete_parking_lot(lot_id):
    """Delete a parking lot"""
    try:
        lot = Parking_lot.query.get_or_404(lot_id)
        
        # Check if any spots are occupied
        occupied_spots = [spot for spot in lot.spots if spot.is_occupied]
        if occupied_spots:
            return jsonify({'error': 'Cannot delete parking lot: some spots are occupied'}), 400
        
        db.session.delete(lot)  # Cascade will delete all spots
        db.session.commit()
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete parking lot error: {str(e)}")
        return jsonify({'error': 'Failed to delete parking lot'}), 500

@api.route('/admin/parking-lots/<int:lot_id>/spots', methods=['GET'])
@roles_required('admin')
def get_parking_lot_spots(lot_id):
    """Get all spots for a specific parking lot"""
    try:
        lot = Parking_lot.query.get_or_404(lot_id)
        
        spots_data = {
            'parking_lot': {
                'id': lot.id,
                'name': lot.name,
                'location': lot.location,
                'capacity': lot.capacity,
                'price_per_hour': lot.price_per_hour
            },
            'spots': [{
                'id': spot.id,
                'spot_number': spot.spot_number,
                'is_occupied': spot.is_occupied,
                'current_reservation': None
            } for spot in lot.spots]
        }
        
        return jsonify(spots_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get parking lot spots error: {str(e)}")
        return jsonify({'error': 'Failed to get parking lot spots'}), 500

# Admin User Management Routes
@api.route('/admin/users', methods=['GET'])
@roles_required('admin')
def get_all_users():
    """Get all users for admin management"""
    try:
        users = User.query.all()
        
        users_data = []
        for user in users:
            # Get user's booking history count
            reservations_count = Reservation.query.filter_by(user_id=user.id).count()
            active_reservations = Reservation.query.filter_by(user_id=user.id, status='active').count()
            
            # Get user roles
            user_roles = [role.name for role in user.roles]
            
            users_data.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'username': user.username,
                'active': user.active,
                'confirmed_at': user.confirmed_at.isoformat() if user.confirmed_at else None,
                'roles': user_roles,
                'total_reservations': reservations_count,
                'active_reservations': active_reservations,
                'created_at': user.fs_uniquifier  # Using fs_uniquifier as a proxy for creation time
            })
        
        return jsonify({
            'users': users_data,
            'total_count': len(users_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get all users error: {str(e)}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@api.route('/admin/users/<int:user_id>/toggle-status', methods=['PUT'])
@roles_required('admin')
def toggle_user_status(user_id):
    """Activate or deactivate a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deactivating themselves
        current_user_id = current_user.id if current_user.is_authenticated else None
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        # Prevent deactivating other admins (optional security measure)
        if 'admin' in [role.name for role in user.roles]:
            return jsonify({'error': 'Cannot deactivate admin accounts'}), 400
        
        # Toggle user status
        user.active = not user.active
        db.session.commit()
        
        status = 'activated' if user.active else 'deactivated'
        return jsonify({
            'message': f'User {user.email} has been {status}',
            'user': {
                'id': user.id,
                'email': user.email,
                'active': user.active
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Toggle user status error: {str(e)}")
        return jsonify({'error': 'Failed to toggle user status'}), 500

@api.route('/admin/users/<int:user_id>/reservations', methods=['GET'])
@roles_required('admin')
def get_admin_user_reservations(user_id):
    """Get all reservations for a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get reservations with related data
        reservations = db.session.query(Reservation, ParkingSpot, Parking_lot).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            Parking_lot, ParkingSpot.lot_id == Parking_lot.id
        ).filter(
            Reservation.user_id == user_id
        ).order_by(Reservation.created_at.desc()).all()
        
        reservations_data = []
        for reservation, spot, lot in reservations:
            reservations_data.append({
                'id': reservation.id,
                'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat(),
                'status': reservation.status,
                'created_at': reservation.created_at.isoformat(),
                'parking_lot': {
                    'id': lot.id,
                    'name': lot.name,
                    'location': lot.location
                },
                'parking_spot': {
                    'id': spot.id,
                    'spot_number': spot.spot_number
                }
            })
        
        return jsonify({
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            },
            'reservations': reservations_data,
            'total_count': len(reservations_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user reservations error: {str(e)}")
        return jsonify({'error': 'Failed to fetch user reservations'}), 500

@api.route('/admin/reservations', methods=['GET'])
@roles_required('admin')
def get_all_reservations():
    """Get all reservations across all users"""
    try:
        # Get query parameters
        status = request.args.get('status')  # Filter by status
        user_id = request.args.get('user_id')  # Filter by user
        limit = request.args.get('limit', 50, type=int)  # Default 50 reservations
        offset = request.args.get('offset', 0, type=int)  # For pagination
        
        # Build query
        query = db.session.query(Reservation, ParkingSpot, Parking_lot, User).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            Parking_lot, ParkingSpot.lot_id == Parking_lot.id
        ).join(
            User, Reservation.user_id == User.id
        )
        
        # Apply filters
        if status:
            query = query.filter(Reservation.status == status)
        if user_id:
            query = query.filter(Reservation.user_id == user_id)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        reservations = query.order_by(Reservation.created_at.desc()).offset(offset).limit(limit).all()
        
        reservations_data = []
        for reservation, spot, lot, user in reservations:
            reservations_data.append({
                'id': reservation.id,
                'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat(),
                'status': reservation.status,
                'created_at': reservation.created_at.isoformat(),
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                },
                'parking_lot': {
                    'id': lot.id,
                    'name': lot.name,
                    'location': lot.location
                },
                'parking_spot': {
                    'id': spot.id,
                    'spot_number': spot.spot_number
                }
            })
        
        return jsonify({
            'reservations': reservations_data,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get all reservations error: {str(e)}")
        return jsonify({'error': 'Failed to fetch reservations'}), 500

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
