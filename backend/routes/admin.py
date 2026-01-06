from flask import Blueprint, request, jsonify, current_app
from flask_security import roles_required, current_user
from models import db, User, Role, Parking_lot, ParkingSpot, Reservation
from routes.parking import calculate_available_spots

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@roles_required('admin')
def admin_dashboard():
    """Get admin dashboard data with all parking lot statuses"""
    try:
        lots = Parking_lot.query.all()
        total_spots = sum(lot.capacity for lot in lots)
        occupied_spots = sum(len([spot for spot in lot.spots if spot.is_occupied]) for lot in lots)
        reserved_spots = sum(len([spot for spot in lot.spots for res in spot.reservations if res.status == 'active' and not spot.is_occupied]) for lot in lots)
        available_spots = total_spots - occupied_spots - reserved_spots
        
        total_users = User.query.count()
        active_users = User.query.filter_by(active=True).count()
        admin_users = User.query.join(User.roles).filter(Role.name == 'admin').count()
        
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

@admin_bp.route('/parking-lots', methods=['GET'])
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

@admin_bp.route('/parking-lots', methods=['POST'])
@roles_required('admin')
def create_parking_lot():
    """Create a new parking lot"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        location = data.get('location', '').strip()
        capacity = data.get('capacity')
        price_per_hour = data.get('price_per_hour', 5.0)
        
        if not name: return jsonify({'error': 'Name is required'}), 400
        if not location: return jsonify({'error': 'Location is required'}), 400
        if not capacity or capacity <= 0: return jsonify({'error': 'Valid capacity is required'}), 400
        
        if Parking_lot.query.filter_by(name=name).first():
            return jsonify({'error': 'Parking lot with this name already exists'}), 400
        
        parking_lot = Parking_lot(
            name=name, location=location, capacity=capacity, price_per_hour=float(price_per_hour)
        )
        
        db.session.add(parking_lot)
        db.session.flush()
        
        for i in range(1, capacity + 1):
            spot = ParkingSpot(lot_id=parking_lot.id, spot_number=f"A{i:03d}")
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

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['PUT'])
@roles_required('admin')
def update_parking_lot(lot_id):
    """Update a parking lot"""
    try:
        lot = Parking_lot.query.get_or_404(lot_id)
        data = request.get_json()
        if not data: return jsonify({'error': 'No data provided'}), 400
        
        if 'name' in data:
            name = data['name'].strip()
            if not name: return jsonify({'error': 'Name cannot be empty'}), 400
            existing = Parking_lot.query.filter(Parking_lot.name == name, Parking_lot.id != lot_id).first()
            if existing: return jsonify({'error': 'Parking lot with this name already exists'}), 400
            lot.name = name
        
        if 'location' in data:
            location = data['location'].strip()
            if not location: return jsonify({'error': 'Location cannot be empty'}), 400
            lot.location = location
        
        if 'price_per_hour' in data:
            try: lot.price_per_hour = float(data['price_per_hour'])
            except (ValueError, TypeError): return jsonify({'error': 'Invalid price per hour'}), 400
        
        if 'capacity' in data:
            new_capacity = data['capacity']
            if new_capacity <= 0: return jsonify({'error': 'Capacity must be greater than 0'}), 400
            current_capacity = lot.capacity
            
            if new_capacity > current_capacity:
                for i in range(current_capacity + 1, new_capacity + 1):
                    spot = ParkingSpot(lot_id=lot.id, spot_number=f"A{i:03d}")
                    db.session.add(spot)
            elif new_capacity < current_capacity:
                spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot.id)\
                    .filter_by(is_occupied=False)\
                    .order_by(ParkingSpot.id.desc())\
                    .limit(current_capacity - new_capacity).all()
                if len(spots_to_remove) < (current_capacity - new_capacity):
                    return jsonify({'error': 'Cannot reduce capacity: some spots are occupied'}), 400
                for spot in spots_to_remove: db.session.delete(spot)
            
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

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['DELETE'])
@roles_required('admin')
def delete_parking_lot(lot_id):
    """Delete a parking lot"""
    try:
        lot = Parking_lot.query.get_or_404(lot_id)
        occupied_spots = [spot for spot in lot.spots if spot.is_occupied]
        if occupied_spots: return jsonify({'error': 'Cannot delete parking lot: some spots are occupied'}), 400
        db.session.delete(lot)
        db.session.commit()
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete parking lot error: {str(e)}")
        return jsonify({'error': 'Failed to delete parking lot'}), 500

@admin_bp.route('/parking-lots/<int:lot_id>/spots', methods=['GET'])
@roles_required('admin')
def get_parking_lot_spots(lot_id):
    """Get all spots for a specific parking lot"""
    try:
        lot = Parking_lot.query.get_or_404(lot_id)
        return jsonify({
            'parking_lot': {
                'id': lot.id, 'name': lot.name, 'location': lot.location, 
                'capacity': lot.capacity, 'price_per_hour': lot.price_per_hour
            },
            'spots': [{
                'id': spot.id, 'spot_number': spot.spot_number, 
                'is_occupied': spot.is_occupied, 'current_reservation': None
            } for spot in lot.spots]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get parking lot spots error: {str(e)}")
        return jsonify({'error': 'Failed to get parking lot spots'}), 500

@admin_bp.route('/users', methods=['GET'])
@roles_required('admin')
def get_all_users():
    """Get all users for admin management"""
    try:
        users = User.query.all()
        users_data = []
        for user in users:
            reservations_count = Reservation.query.filter_by(user_id=user.id).count()
            active_reservations = Reservation.query.filter_by(user_id=user.id, status='active').count()
            users_data.append({
                'id': user.id, 'name': user.name, 'email': user.email, 'username': user.username,
                'active': user.active, 'confirmed_at': user.confirmed_at.isoformat() if user.confirmed_at else None,
                'roles': [role.name for role in user.roles],
                'total_reservations': reservations_count, 'active_reservations': active_reservations,
                'created_at': user.fs_uniquifier
            })
        return jsonify({'users': users_data, 'total_count': len(users_data)}), 200
    except Exception as e:
        current_app.logger.error(f"Get all users error: {str(e)}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
@roles_required('admin')
def toggle_user_status(user_id):
    """Activate or deactivate a user"""
    try:
        user = User.query.get_or_404(user_id)
        if user_id == current_user.id if current_user.is_authenticated else None:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        if 'admin' in [role.name for role in user.roles]:
            return jsonify({'error': 'Cannot deactivate admin accounts'}), 400
        
        user.active = not user.active
        db.session.commit()
        status = 'activated' if user.active else 'deactivated'
        return jsonify({
            'message': f'User {user.email} has been {status}',
            'user': {'id': user.id, 'email': user.email, 'active': user.active}
        }), 200
    except Exception as e:
        current_app.logger.error(f"Toggle user status error: {str(e)}")
        return jsonify({'error': 'Failed to toggle user status'}), 500

@admin_bp.route('/users/<int:user_id>/reservations', methods=['GET'])
@roles_required('admin')
def get_admin_user_reservations(user_id):
    """Get all reservations for a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        reservations = db.session.query(Reservation, ParkingSpot, Parking_lot).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            Parking_lot, ParkingSpot.lot_id == Parking_lot.id
        ).filter(Reservation.user_id == user_id).order_by(Reservation.created_at.desc()).all()
        
        reservations_data = []
        for reservation, spot, lot in reservations:
            estimated_cost = reservation.estimated_cost or 0
            final_cost = reservation.final_cost or estimated_cost
            reservations_data.append({
                'id': reservation.id, 'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat(), 'status': reservation.status,
                'created_at': reservation.created_at.isoformat(),
                'parking_lot': {'id': lot.id, 'name': lot.name, 'location': lot.location},
                'parking_spot': {'id': spot.id, 'spot_number': spot.spot_number},
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
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'reservations': reservations_data, 'total_count': len(reservations_data)
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get user reservations error: {str(e)}")
        return jsonify({'error': 'Failed to fetch user reservations'}), 500

@admin_bp.route('/reservations', methods=['GET'])
@roles_required('admin')
def get_all_reservations():
    """Get all reservations across all users"""
    try:
        status = request.args.get('status')
        user_id = request.args.get('user_id')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = db.session.query(Reservation, ParkingSpot, Parking_lot, User).join(
            ParkingSpot, Reservation.spot_id == ParkingSpot.id
        ).join(
            Parking_lot, ParkingSpot.lot_id == Parking_lot.id
        ).join(
            User, Reservation.user_id == User.id
        )
        
        if status: query = query.filter(Reservation.status == status)
        if user_id: query = query.filter(Reservation.user_id == user_id)
        
        total_count = query.count()
        reservations = query.order_by(Reservation.created_at.desc()).offset(offset).limit(limit).all()
        
        reservations_data = []
        for res, spot, lot, user in reservations:
            reservations_data.append({
                'id': res.id, 'start_time': res.start_time.isoformat(),
                'end_time': res.end_time.isoformat(), 'status': res.status,
                'created_at': res.created_at.isoformat(),
                'user': {'id': user.id, 'name': user.name, 'email': user.email},
                'parking_lot': {'id': lot.id, 'name': lot.name, 'location': lot.location},
                'parking_spot': {'id': spot.id, 'spot_number': spot.spot_number}
            })
        return jsonify({
            'reservations': reservations_data, 'total_count': total_count,
            'limit': limit, 'offset': offset
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get all reservations error: {str(e)}")
        return jsonify({'error': 'Failed to fetch reservations'}), 500

@admin_bp.route('/parking-history', methods=['GET'])
@roles_required('admin')
def get_admin_parking_history():
    """Get comprehensive parking history with cost analysis for admin"""
    # ... Implementation is identical to previous monolithic file ...
    # Simplified for brevity in this response but would be full logic
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
