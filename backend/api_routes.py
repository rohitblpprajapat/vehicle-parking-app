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
            
            # Calculate duration and cost information
            if res.actual_duration_hours and res.final_cost:
                # Use actual values for completed reservations
                duration_hours = res.actual_duration_hours
                cost = res.final_cost
            else:
                # Use estimated values for active reservations
                duration_hours = (res.end_time - res.start_time).total_seconds() / 3600
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
                'hourly_rate': res.hourly_rate or parking_lot.price_per_hour,
                'created_at': res.created_at.isoformat(),
                
                # Enhanced cost breakdown
                'reserved_duration_hours': res.reserved_duration_hours,
                'actual_duration_hours': res.actual_duration_hours,
                'estimated_cost': round(res.estimated_cost, 2) if res.estimated_cost else None,
                'final_cost': round(res.final_cost, 2) if res.final_cost else None,
                
                # Enhanced timestamps
                'occupied_at': res.occupied_at.isoformat() if res.occupied_at else None,
                'released_at': res.released_at.isoformat() if res.released_at else None
            }
            
            reservation_list.append(reservation_data)
        
        return jsonify({
            'reservations': reservation_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get reservations error: {str(e)}")
        return jsonify({'error': 'Failed to get reservations'}), 500

@api.route('/reservations/history', methods=['GET'])
@auth_required('token', 'session')
def get_user_parking_history():
    """Get detailed parking history with cost breakdown for current user"""
    try:
        # Get query parameters for filtering
        status = request.args.get('status')  # Filter by status
        start_date = request.args.get('start_date')  # Filter from date
        end_date = request.args.get('end_date')  # Filter to date
        limit = request.args.get('limit', 50, type=int)  # Default 50 records
        offset = request.args.get('offset', 0, type=int)  # For pagination
        
        # Build query
        query = Reservation.query.filter_by(user_id=current_user.id)
        
        # Apply filters
        if status:
            query = query.filter(Reservation.status == status)
        if start_date:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Reservation.created_at >= start_dt)
        if end_date:
            from datetime import datetime
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Reservation.created_at <= end_dt)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        reservations = query.order_by(Reservation.created_at.desc()).offset(offset).limit(limit).all()
        
        # Calculate summary statistics
        total_spent = sum(res.final_cost or res.estimated_cost or 0 for res in current_user.reservations)
        total_hours = sum(res.actual_duration_hours or res.reserved_duration_hours or 0 for res in current_user.reservations)
        completed_reservations = len([res for res in current_user.reservations if res.status == 'completed'])
        
        history_data = []
        for res in reservations:
            parking_lot = res.parking_spot.parking_lot
            
            # Calculate cost breakdown
            estimated_cost = res.estimated_cost or 0
            final_cost = res.final_cost or estimated_cost
            cost_difference = final_cost - estimated_cost if res.final_cost else 0
            
            history_item = {
                'id': res.id,
                'parking_lot': {
                    'id': parking_lot.id,
                    'name': parking_lot.name,
                    'location': parking_lot.location
                },
                'parking_spot': {
                    'id': res.parking_spot.id,
                    'spot_number': res.parking_spot.spot_number
                },
                'timestamps': {
                    'created_at': res.created_at.isoformat(),
                    'start_time': res.start_time.isoformat(),
                    'end_time': res.end_time.isoformat(),
                    'occupied_at': res.occupied_at.isoformat() if res.occupied_at else None,
                    'released_at': res.released_at.isoformat() if res.released_at else None
                },
                'duration': {
                    'reserved_hours': res.reserved_duration_hours,
                    'actual_hours': res.actual_duration_hours,
                    'difference_hours': (res.actual_duration_hours - res.reserved_duration_hours) if (res.actual_duration_hours and res.reserved_duration_hours) else None
                },
                'cost_breakdown': {
                    'hourly_rate': res.hourly_rate,
                    'estimated_cost': round(estimated_cost, 2),
                    'final_cost': round(final_cost, 2),
                    'cost_difference': round(cost_difference, 2),
                    'currency': 'USD'
                },
                'status': res.status
            }
            
            history_data.append(history_item)
        
        return jsonify({
            'history': history_data,
            'summary': {
                'total_reservations': total_count,
                'completed_reservations': completed_reservations,
                'total_spent': round(total_spent, 2),
                'total_hours_parked': round(total_hours, 2),
                'average_cost_per_hour': round(total_spent / total_hours, 2) if total_hours > 0 else 0
            },
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total_count': total_count
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get parking history error: {str(e)}")
        return jsonify({'error': 'Failed to get parking history'}), 500

@api.route('/user/spending-summary', methods=['GET'])
@auth_required('token', 'session')
def get_user_spending_summary():
    """Get user's parking spending summary and statistics"""
    try:
        # Get date range parameters
        days = request.args.get('days', 30, type=int)  # Default last 30 days
        
        from datetime import datetime, timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user's reservations in the specified period
        reservations = Reservation.query.filter_by(user_id=current_user.id).filter(
            Reservation.created_at >= start_date
        ).all()
        
        # Calculate statistics
        total_reservations = len(reservations)
        completed_reservations = [res for res in reservations if res.status == 'completed']
        active_reservations = [res for res in reservations if res.status == 'active']
        cancelled_reservations = [res for res in reservations if res.status == 'cancelled']
        
        total_spent = sum(res.final_cost or res.estimated_cost or 0 for res in reservations)
        total_hours = sum(res.actual_duration_hours or res.reserved_duration_hours or 0 for res in reservations)
        
        # Calculate savings/overcharges
        estimated_total = sum(res.estimated_cost or 0 for res in completed_reservations)
        final_total = sum(res.final_cost or 0 for res in completed_reservations)
        savings = estimated_total - final_total  # Positive means user paid less than estimated
        
        # Group spending by parking lot
        lot_spending = {}
        for res in reservations:
            lot_name = res.parking_spot.parking_lot.name
            cost = res.final_cost or res.estimated_cost or 0
            if lot_name not in lot_spending:
                lot_spending[lot_name] = {'total_cost': 0, 'visits': 0, 'total_hours': 0}
            lot_spending[lot_name]['total_cost'] += cost
            lot_spending[lot_name]['visits'] += 1
            lot_spending[lot_name]['total_hours'] += res.actual_duration_hours or res.reserved_duration_hours or 0
        
        # Convert to list and sort by spending
        lot_breakdown = [
            {
                'lot_name': lot_name,
                'total_spent': round(data['total_cost'], 2),
                'visits': data['visits'],
                'total_hours': round(data['total_hours'], 2),
                'average_cost_per_visit': round(data['total_cost'] / data['visits'], 2) if data['visits'] > 0 else 0
            }
            for lot_name, data in lot_spending.items()
        ]
        lot_breakdown.sort(key=lambda x: x['total_spent'], reverse=True)
        
        # Hourly usage analysis
        hourly_usage = {}
        for hour in range(24):
            hourly_usage[hour] = 0
        
        for res in reservations:
            if res.start_time:
                hour = res.start_time.hour
                hourly_usage[hour] += 1
        
        hourly_usage_data = [
            {'hour': hour, 'count': count}
            for hour, count in hourly_usage.items()
        ]
        
        # Daily usage analysis (day of week)
        daily_usage = {}
        for day in range(7):  # 0 = Monday, 6 = Sunday
            daily_usage[day] = 0
        
        for res in reservations:
            if res.start_time:
                day_of_week = res.start_time.weekday()
                daily_usage[day_of_week] += 1
        
        daily_usage_data = [
            {'day_of_week': day, 'count': count}
            for day, count in daily_usage.items()
        ]
        
        # Get previous month data for trend comparison
        prev_month_start = start_date - timedelta(days=30)
        prev_month_end = start_date
        prev_month_reservations = Reservation.query.filter_by(user_id=current_user.id).filter(
            Reservation.created_at >= prev_month_start,
            Reservation.created_at < prev_month_end
        ).count()
        
        return jsonify({
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_reservations': total_reservations,
                'completed_reservations': len(completed_reservations),
                'active_reservations': len(active_reservations),
                'cancelled_reservations': len(cancelled_reservations),
                'total_spent': round(total_spent, 2),
                'total_hours_parked': round(total_hours, 2),
                'average_cost_per_hour': round(total_spent / total_hours, 2) if total_hours > 0 else 0,
                'average_cost_per_reservation': round(total_spent / total_reservations, 2) if total_reservations > 0 else 0,
                'savings_vs_estimate': round(savings, 2)  # Positive means saved money, negative means paid more
            },
            'spending_by_parking_lot': lot_breakdown,
            'hourly_usage': hourly_usage_data,
            'daily_usage': daily_usage_data,
            'previous_month_reservations': prev_month_reservations,
            'recent_activity': [
                {
                    'id': res.id,
                    'parking_lot': res.parking_spot.parking_lot.name,
                    'spot_number': res.parking_spot.spot_number,
                    'date': res.created_at.isoformat(),
                    'duration_hours': res.actual_duration_hours or res.reserved_duration_hours,
                    'cost': round(res.final_cost or res.estimated_cost or 0, 2),
                    'status': res.status
                }
                for res in sorted(reservations, key=lambda x: x.created_at, reverse=True)[:10]
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get spending summary error: {str(e)}")
        return jsonify({'error': 'Failed to get spending summary'}), 500

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
        
        # Calculate initial cost estimate
        estimated_cost = parking_lot.price_per_hour * duration_hours
        
        reservation = Reservation(
            user_id=current_user.id,
            spot_id=available_spot.id,
            start_time=start_time,
            end_time=end_time,
            status='active',
            reserved_duration_hours=duration_hours,
            estimated_cost=estimated_cost,
            hourly_rate=parking_lot.price_per_hour
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
        
        # Mark the parking spot as occupied and track arrival time
        reservation.parking_spot.is_occupied = True
        reservation.occupied_at = datetime.utcnow()
        
        # Update start_time to actual arrival time for accurate billing
        reservation.start_time = reservation.occupied_at
        
        db.session.commit()
        
        return jsonify({
            'message': 'Spot marked as occupied',
            'reservation': {
                'id': reservation.id,
                'spot_number': reservation.parking_spot.spot_number,
                'occupied_at': reservation.occupied_at.isoformat(),
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
        release_time = datetime.utcnow()
        
        # Calculate duration from when user actually occupied the spot
        if reservation.occupied_at:
            actual_duration = (release_time - reservation.occupied_at).total_seconds() / 3600  # hours
        else:
            # Fallback to original start time if occupied_at is not set
            actual_duration = (release_time - reservation.start_time).total_seconds() / 3600  # hours
        
        # Calculate final cost based on actual duration
        parking_lot = reservation.parking_spot.parking_lot
        final_cost = parking_lot.price_per_hour * actual_duration
        
        # Update reservation with final details
        reservation.end_time = release_time
        reservation.released_at = release_time
        reservation.status = 'completed'
        reservation.actual_duration_hours = actual_duration
        reservation.final_cost = final_cost
        
        # Mark spot as available
        reservation.parking_spot.is_occupied = False
        
        db.session.commit()
        
        return jsonify({
            'message': 'Spot released successfully',
            'reservation': {
                'id': reservation.id,
                'spot_number': reservation.parking_spot.spot_number,
                'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat(),
                'occupied_at': reservation.occupied_at.isoformat() if reservation.occupied_at else None,
                'released_at': reservation.released_at.isoformat(),
                'duration_hours': round(actual_duration, 2),
                'actual_duration_hours': round(actual_duration, 2),
                'estimated_cost': round(reservation.estimated_cost, 2) if reservation.estimated_cost else 0,
                'final_cost': round(final_cost, 2),
                'total_cost': round(final_cost, 2),
                'hourly_rate': reservation.hourly_rate,
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
            # Calculate cost information
            estimated_cost = reservation.estimated_cost or 0
            final_cost = reservation.final_cost or estimated_cost
            
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
                },
                'timestamps': {
                    'occupied_at': reservation.occupied_at.isoformat() if reservation.occupied_at else None,
                    'released_at': reservation.released_at.isoformat() if reservation.released_at else None
                },
                'duration': {
                    'reserved_hours': reservation.reserved_duration_hours,
                    'actual_hours': reservation.actual_duration_hours
                },
                'cost_breakdown': {
                    'hourly_rate': reservation.hourly_rate,
                    'estimated_cost': round(estimated_cost, 2),
                    'final_cost': round(final_cost, 2)
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

@api.route('/admin/parking-history', methods=['GET'])
@roles_required('admin')
def get_admin_parking_history():
    """Get comprehensive parking history with cost analysis for admin"""
    try:
        # Get query parameters
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query with joins
        query = db.session.query(Reservation, ParkingSpot, Parking_lot, User).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            Parking_lot, ParkingSpot.lot_id == Parking_lot.id
        ).join(
            User, Reservation.user_id == User.id
        )
        
        # Apply filters
        if user_id:
            query = query.filter(Reservation.user_id == user_id)
        if status:
            query = query.filter(Reservation.status == status)
        if start_date:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Reservation.created_at >= start_dt)
        if end_date:
            from datetime import datetime
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Reservation.created_at <= end_dt)
        
        # Get total count and summary statistics
        total_count = query.count()
        all_reservations = query.all()
        
        # Calculate system-wide statistics
        total_revenue = sum(res.final_cost or res.estimated_cost or 0 for res, spot, lot, user in all_reservations)
        total_hours = sum(res.actual_duration_hours or res.reserved_duration_hours or 0 for res, spot, lot, user in all_reservations)
        completed_count = len([res for res, spot, lot, user in all_reservations if res.status == 'completed'])
        active_count = len([res for res, spot, lot, user in all_reservations if res.status == 'active'])
        cancelled_count = len([res for res, spot, lot, user in all_reservations if res.status == 'cancelled'])
        
        # Apply pagination and ordering
        paginated_reservations = query.order_by(Reservation.created_at.desc()).offset(offset).limit(limit).all()
        
        history_data = []
        for reservation, spot, lot, user in paginated_reservations:
            # Calculate cost breakdown
            estimated_cost = reservation.estimated_cost or 0
            final_cost = reservation.final_cost or estimated_cost
            cost_difference = final_cost - estimated_cost if reservation.final_cost else 0
            
            history_item = {
                'id': reservation.id,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                },
                'parking_lot': {
                    'id': lot.id,
                    'name': lot.name,
                    'location': lot.location,
                    'current_hourly_rate': lot.price_per_hour
                },
                'parking_spot': {
                    'id': spot.id,
                    'spot_number': spot.spot_number
                },
                'timestamps': {
                    'created_at': reservation.created_at.isoformat(),
                    'start_time': reservation.start_time.isoformat(),
                    'end_time': reservation.end_time.isoformat(),
                    'occupied_at': reservation.occupied_at.isoformat() if reservation.occupied_at else None,
                    'released_at': reservation.released_at.isoformat() if reservation.released_at else None
                },
                'duration': {
                    'reserved_hours': reservation.reserved_duration_hours,
                    'actual_hours': reservation.actual_duration_hours,
                    'difference_hours': (reservation.actual_duration_hours - reservation.reserved_duration_hours) if (reservation.actual_duration_hours and reservation.reserved_duration_hours) else None
                },
                'cost_breakdown': {
                    'hourly_rate_at_reservation': reservation.hourly_rate,
                    'estimated_cost': round(estimated_cost, 2),
                    'final_cost': round(final_cost, 2),
                    'cost_difference': round(cost_difference, 2),
                    'revenue_generated': round(final_cost, 2)
                },
                'status': reservation.status
            }
            
            history_data.append(history_item)
        
        return jsonify({
            'parking_history': history_data,
            'system_summary': {
                'total_reservations': total_count,
                'completed_reservations': completed_count,
                'active_reservations': active_count,
                'cancelled_reservations': cancelled_count,
                'total_revenue': round(total_revenue, 2),
                'total_hours_parked': round(total_hours, 2),
                'average_revenue_per_hour': round(total_revenue / total_hours, 2) if total_hours > 0 else 0,
                'average_revenue_per_reservation': round(total_revenue / total_count, 2) if total_count > 0 else 0
            },
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total_count': total_count
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get admin parking history error: {str(e)}")
        return jsonify({'error': 'Failed to fetch parking history'}), 500

# ==================== ADMIN ANALYTICS ROUTES ====================

@api.route('/admin/analytics', methods=['GET'])
@roles_required('admin')
def get_admin_analytics():
    """Get comprehensive analytics for admin dashboard"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Get date range
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Total revenue and bookings
        reservations = Reservation.query.filter(
            Reservation.created_at >= start_date,
            Reservation.status.in_(['completed', 'active'])
        ).all()
        
        total_revenue = sum(res.final_cost or 0 for res in reservations)
        total_bookings = len(reservations)
        
        # Calculate average occupancy
        parking_lots = Parking_lot.query.all()
        total_spots = sum(lot.capacity for lot in parking_lots)
        active_reservations = Reservation.query.filter(Reservation.status == 'active').count()
        average_occupancy = (active_reservations / total_spots * 100) if total_spots > 0 else 0
        
        # Active users (users with reservations in the period)
        active_users = len(set(res.user_id for res in reservations))
        
        # Revenue over time (daily)
        revenue_by_date = {}
        booking_trends = {}
        for res in reservations:
            date_key = res.created_at.strftime('%Y-%m-%d')
            if date_key not in revenue_by_date:
                revenue_by_date[date_key] = 0
                booking_trends[date_key] = 0
            revenue_by_date[date_key] += res.final_cost or 0
            booking_trends[date_key] += 1
        
        # Convert to sorted lists
        revenue_over_time = [
            {'date': date, 'revenue': revenue}
            for date, revenue in sorted(revenue_by_date.items())
        ]
        
        booking_trends_data = [
            {'date': date, 'bookings': bookings}
            for date, bookings in sorted(booking_trends.items())
        ]
        
        # Parking lot performance
        lot_performance = []
        for lot in parking_lots:
            lot_reservations = [res for res in reservations if res.parking_spot.parking_lot_id == lot.id]
            lot_revenue = sum(res.final_cost or 0 for res in lot_reservations)
            lot_bookings = len(lot_reservations)
            lot_occupancy = (len([res for res in lot_reservations if res.status == 'active']) / lot.capacity * 100) if lot.capacity > 0 else 0
            avg_duration = sum(res.actual_duration_hours or res.reserved_duration_hours or 0 for res in lot_reservations) / len(lot_reservations) if lot_reservations else 0
            
            lot_performance.append({
                'id': lot.id,
                'name': lot.name,
                'revenue': lot_revenue,
                'bookings': lot_bookings,
                'occupancy': lot_occupancy,
                'avgDuration': avg_duration,
                'revenuePerHour': lot_revenue / (avg_duration * len(lot_reservations)) if avg_duration > 0 and lot_reservations else 0
            })
        
        # Sort by revenue
        lot_performance.sort(key=lambda x: x['revenue'], reverse=True)
        
        # Hourly occupancy pattern
        hourly_occupancy = {}
        for hour in range(24):
            hourly_reservations = [res for res in reservations 
                                 if res.start_time and res.start_time.hour == hour]
            hourly_occupancy[hour] = len(hourly_reservations)
        
        hourly_occupancy_data = [
            {'hour': hour, 'occupancy': count}
            for hour, count in hourly_occupancy.items()
        ]
        
        # User activity (new users and active users by date)
        user_activity = {}
        all_users = User.query.filter(User.created_at >= start_date).all()
        for user in all_users:
            date_key = user.created_at.strftime('%Y-%m-%d')
            if date_key not in user_activity:
                user_activity[date_key] = {'new_users': 0, 'active_users': 0}
            user_activity[date_key]['new_users'] += 1
        
        # Add active users per day
        for res in reservations:
            date_key = res.created_at.strftime('%Y-%m-%d')
            if date_key in user_activity:
                user_activity[date_key]['active_users'] += 1
        
        user_activity_data = [
            {'date': date, 'new_users': data['new_users'], 'active_users': data['active_users']}
            for date, data in sorted(user_activity.items())
        ]
        
        # Recent high-value transactions
        recent_transactions = []
        high_value_reservations = sorted(reservations, key=lambda x: x.final_cost or 0, reverse=True)[:20]
        for res in high_value_reservations:
            recent_transactions.append({
                'id': res.id,
                'date': res.created_at.isoformat(),
                'userName': res.user.name,
                'parkingLot': res.parking_spot.parking_lot.name,
                'duration': res.actual_duration_hours or res.reserved_duration_hours or 0,
                'amount': res.final_cost or 0,
                'status': res.status.title()
            })
        
        return jsonify({
            'summary': {
                'total_revenue': total_revenue,
                'total_bookings': total_bookings,
                'average_occupancy': average_occupancy,
                'active_users': active_users
            },
            'revenue_over_time': revenue_over_time,
            'booking_trends': booking_trends_data,
            'parking_lots': lot_performance,
            'hourly_occupancy': hourly_occupancy_data,
            'user_activity': user_activity_data,
            'recent_transactions': recent_transactions
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get admin analytics error: {str(e)}")
        return jsonify({'error': 'Failed to fetch analytics data'}), 500

@api.route('/admin/analytics/previous', methods=['GET'])
@roles_required('admin')
def get_admin_analytics_previous():
    """Get analytics for the previous period for comparison"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Get date ranges
        from datetime import datetime, timedelta
        end_date = datetime.now() - timedelta(days=days)
        start_date = end_date - timedelta(days=days)
        
        # Get reservations for previous period
        reservations = Reservation.query.filter(
            Reservation.created_at >= start_date,
            Reservation.created_at < end_date,
            Reservation.status.in_(['completed', 'active'])
        ).all()
        
        total_revenue = sum(res.final_cost or 0 for res in reservations)
        total_bookings = len(reservations)
        
        # Calculate average occupancy for previous period
        parking_lots = Parking_lot.query.all()
        total_spots = sum(lot.capacity for lot in parking_lots)
        prev_active_reservations = len([res for res in reservations if res.status == 'active'])
        average_occupancy = (prev_active_reservations / total_spots * 100) if total_spots > 0 else 0
        
        # Active users in previous period
        active_users = len(set(res.user_id for res in reservations))
        
        return jsonify({
            'total_revenue': total_revenue,
            'total_bookings': total_bookings,
            'average_occupancy': average_occupancy,
            'active_users': active_users
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get admin analytics previous error: {str(e)}")
        return jsonify({'error': 'Failed to fetch previous analytics data'}), 500

@api.route('/admin/reports/revenue', methods=['GET'])
@roles_required('admin')
def export_revenue_report():
    """Export revenue report as CSV"""
    try:
        days = request.args.get('days', 30, type=int)
        
        from datetime import datetime, timedelta
        import csv
        from io import StringIO
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        reservations = Reservation.query.filter(
            Reservation.created_at >= start_date,
            Reservation.status.in_(['completed', 'active'])
        ).all()
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'User', 'Parking Lot', 'Spot', 'Duration Hours', 'Amount', 'Status'])
        
        # Write data
        for res in reservations:
            writer.writerow([
                res.created_at.strftime('%Y-%m-%d %H:%M'),
                res.user.name,
                res.parking_spot.parking_lot.name,
                res.parking_spot.spot_number,
                res.actual_duration_hours or res.reserved_duration_hours or 0,
                res.final_cost or 0,
                res.status
            ])
        
        # Create response
        from flask import Response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=revenue-report-{days}days.csv'}
        )
        
    except Exception as e:
        current_app.logger.error(f"Export revenue report error: {str(e)}")
        return jsonify({'error': 'Failed to export revenue report'}), 500

@api.route('/admin/reports/occupancy', methods=['GET'])
@roles_required('admin')
def export_occupancy_report():
    """Export occupancy report as CSV"""
    try:
        days = request.args.get('days', 30, type=int)
        
        from datetime import datetime, timedelta
        import csv
        from io import StringIO
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        parking_lots = Parking_lot.query.all()
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Parking Lot', 'Total Capacity', 'Active Reservations', 'Occupancy %', 'Total Revenue'])
        
        # Write data
        for lot in parking_lots:
            active_reservations = Reservation.query.filter(
                Reservation.parking_spot.has(parking_lot_id=lot.id),
                Reservation.status == 'active'
            ).count()
            
            total_revenue = sum(
                res.final_cost or 0 for res in Reservation.query.filter(
                    Reservation.parking_spot.has(parking_lot_id=lot.id),
                    Reservation.created_at >= start_date,
                    Reservation.status.in_(['completed', 'active'])
                ).all()
            )
            
            occupancy = (active_reservations / lot.capacity * 100) if lot.capacity > 0 else 0
            
            writer.writerow([
                lot.name,
                lot.capacity,
                active_reservations,
                f"{occupancy:.1f}",
                f"{total_revenue:.2f}"
            ])
        
        # Create response
        from flask import Response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=occupancy-report-{days}days.csv'}
        )
        
    except Exception as e:
        current_app.logger.error(f"Export occupancy report error: {str(e)}")
        return jsonify({'error': 'Failed to export occupancy report'}), 500

@api.route('/admin/reports/users', methods=['GET'])
@roles_required('admin')
def export_user_report():
    """Export user activity report as CSV"""
    try:
        days = request.args.get('days', 30, type=int)
        
        from datetime import datetime, timedelta
        import csv
        from io import StringIO
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        users = User.query.all()
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['User Name', 'Email', 'Join Date', 'Total Reservations', 'Total Spent', 'Last Activity'])
        
        # Write data
        for user in users:
            user_reservations = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.created_at >= start_date
            ).all()
            
            total_spent = sum(res.final_cost or 0 for res in user_reservations)
            last_activity = max([res.created_at for res in user_reservations]) if user_reservations else user.created_at
            
            writer.writerow([
                user.name,
                user.email,
                user.created_at.strftime('%Y-%m-%d'),
                len(user_reservations),
                f"{total_spent:.2f}",
                last_activity.strftime('%Y-%m-%d %H:%M')
            ])
        
        # Create response
        from flask import Response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=user-report-{days}days.csv'}
        )
        
    except Exception as e:
        current_app.logger.error(f"Export user report error: {str(e)}")
        return jsonify({'error': 'Failed to export user report'}), 500

@api.route('/admin/reports/predictive', methods=['GET'])
@roles_required('admin')
def generate_predictive_report():
    """Generate predictive analysis report"""
    try:
        from datetime import datetime, timedelta
        import statistics
        
        # Get historical data for analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # 3 months of data
        
        reservations = Reservation.query.filter(
            Reservation.created_at >= start_date,
            Reservation.status.in_(['completed', 'active'])
        ).all()
        
        # Revenue prediction based on trends
        monthly_revenue = {}
        for res in reservations:
            month_key = res.created_at.strftime('%Y-%m')
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += res.final_cost or 0
        
        revenue_values = list(monthly_revenue.values())
        avg_monthly_revenue = statistics.mean(revenue_values) if revenue_values else 0
        revenue_trend = (revenue_values[-1] - revenue_values[0]) / len(revenue_values) if len(revenue_values) > 1 else 0
        
        # Occupancy prediction
        parking_lots = Parking_lot.query.all()
        total_capacity = sum(lot.capacity for lot in parking_lots)
        current_occupancy = Reservation.query.filter(Reservation.status == 'active').count()
        occupancy_rate = (current_occupancy / total_capacity * 100) if total_capacity > 0 else 0
        
        # Peak hours analysis
        hourly_usage = {}
        for res in reservations:
            if res.start_time:
                hour = res.start_time.hour
                if hour not in hourly_usage:
                    hourly_usage[hour] = 0
                hourly_usage[hour] += 1
        
        peak_hours = sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate predictions
        predictions = {
            'revenue_forecast': {
                'next_month_predicted': avg_monthly_revenue + revenue_trend,
                'trend': 'increasing' if revenue_trend > 0 else 'decreasing',
                'confidence': min(90, max(60, 80 - abs(revenue_trend) * 10))
            },
            'occupancy_forecast': {
                'current_rate': occupancy_rate,
                'predicted_peak_occupancy': min(100, occupancy_rate * 1.2),
                'recommended_capacity_expansion': max(0, (current_occupancy * 1.5) - total_capacity)
            },
            'peak_hours': [
                {'hour': f"{hour}:00", 'usage_count': count}
                for hour, count in peak_hours
            ],
            'recommendations': [
                'Consider dynamic pricing during peak hours' if peak_hours else 'Implement time-based pricing',
                'Expand capacity in high-demand locations' if occupancy_rate > 80 else 'Optimize current capacity',
                'Implement loyalty programs to increase revenue' if revenue_trend < 0 else 'Continue current growth strategies'
            ]
        }
        
        return jsonify(predictions), 200
        
    except Exception as e:
        current_app.logger.error(f"Generate predictive report error: {str(e)}")
        return jsonify({'error': 'Failed to generate predictive report'}), 500

# ==================== USER EXPORT ROUTES ====================

@api.route('/user/export-report', methods=['GET'])
@auth_required('token', 'session')
def export_user_report():
    """Export user's personal parking report as CSV"""
    try:
        days = request.args.get('days', 30, type=int)
        
        from datetime import datetime, timedelta
        import csv
        from io import StringIO
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        reservations = Reservation.query.filter(
            Reservation.user_id == current_user.id,
            Reservation.created_at >= start_date
        ).all()
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Parking Lot', 'Spot Number', 'Start Time', 'End Time', 'Duration Hours', 'Amount', 'Status'])
        
        # Write data
        for res in reservations:
            writer.writerow([
                res.created_at.strftime('%Y-%m-%d'),
                res.parking_spot.parking_lot.name,
                res.parking_spot.spot_number,
                res.start_time.strftime('%H:%M') if res.start_time else 'N/A',
                res.end_time.strftime('%H:%M') if res.end_time else 'N/A',
                res.actual_duration_hours or res.reserved_duration_hours or 0,
                res.final_cost or 0,
                res.status
            ])
        
        # Create response
        from flask import Response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=personal-parking-report-{days}days.csv'}
        )
        
    except Exception as e:
        current_app.logger.error(f"Export user report error: {str(e)}")
        return jsonify({'error': 'Failed to export personal report'}), 500

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
