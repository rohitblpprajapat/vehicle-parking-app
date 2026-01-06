from flask import Blueprint, request, jsonify, current_app
from flask_security import auth_required, current_user
from models import db, Parking_lot, ParkingSpot, Reservation
from redis_cache import redis_cache
from datetime import datetime, timedelta
from utils import get_ist_now


reservation_bp = Blueprint('reservations', __name__)

@reservation_bp.route('', methods=['GET'])
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
                'reserved_duration_hours': res.reserved_duration_hours,
                'actual_duration_hours': res.actual_duration_hours,
                'estimated_cost': round(res.estimated_cost, 2) if res.estimated_cost else None,
                'final_cost': round(res.final_cost, 2) if res.final_cost else None,
                'final_cost': round(res.final_cost, 2) if res.final_cost else None,
                'occupied_at': res.occupied_at.isoformat() if res.occupied_at else None,
                'released_at': res.released_at.isoformat() if res.released_at else None,
                'vehicle_number': res.vehicle_number
            }
            
            reservation_list.append(reservation_data)
        
        return jsonify({
            'reservations': reservation_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get reservations error: {str(e)}")
        return jsonify({'error': 'Failed to get reservations'}), 500

@reservation_bp.route('/history', methods=['GET'])
@auth_required('token', 'session')
def get_user_parking_history():
    """Get detailed parking history with cost breakdown for current user"""
    try:
        # Get query parameters for filtering
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = Reservation.query.filter_by(user_id=current_user.id)
        
        if status:
            query = query.filter(Reservation.status == status)
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Reservation.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Reservation.created_at <= end_dt)
        
        total_count = query.count()
        reservations = query.order_by(Reservation.created_at.desc()).offset(offset).limit(limit).all()
        
        # Calculate summary statistics
        total_spent = sum(res.final_cost or res.estimated_cost or 0 for res in current_user.reservations)
        total_hours = sum(res.actual_duration_hours or res.reserved_duration_hours or 0 for res in current_user.reservations)
        completed_reservations = len([res for res in current_user.reservations if res.status == 'completed'])
        
        history_data = []
        for res in reservations:
            parking_lot = res.parking_spot.parking_lot
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
                'status': res.status,
                'vehicle_number': res.vehicle_number
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

@reservation_bp.route('', methods=['POST'])
@auth_required('token', 'session')
def create_reservation():
    """Auto-allocate and reserve the first available spot in a parking lot"""
    try:
        data = request.get_json()
        lot_id = data.get('lot_id')
        duration_hours = data.get('duration_hours', 1)
        vehicle_number = data.get('vehicle_number')
        
        if not lot_id:
            return jsonify({'error': 'Parking lot ID is required'}), 400
            
        if not vehicle_number:
            return jsonify({'error': 'Vehicle number is required'}), 400
        
        parking_lot = Parking_lot.query.get_or_404(lot_id)
        
        available_spot = ParkingSpot.query.filter_by(
            lot_id=lot_id, 
            is_occupied=False
        ).filter(
            ~ParkingSpot.reservations.any(Reservation.status == 'active')
        ).first()
        
        if not available_spot:
            return jsonify({'error': 'No available spots in this parking lot'}), 400
        
        existing_reservation = Reservation.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).join(ParkingSpot).filter_by(lot_id=lot_id).first()
        
        if existing_reservation:
            return jsonify({'error': 'You already have an active reservation in this parking lot'}), 400
        
        start_time = get_ist_now()
        end_time = start_time + timedelta(hours=duration_hours)
        estimated_cost = parking_lot.price_per_hour * duration_hours
        
        reservation = Reservation(
            user_id=current_user.id,
            spot_id=available_spot.id,
            start_time=start_time,
            end_time=end_time,
            status='active',
            reserved_duration_hours=duration_hours,
            estimated_cost=estimated_cost,
            hourly_rate=parking_lot.price_per_hour,
            vehicle_number=vehicle_number
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        redis_cache.invalidate_pattern('parking-lots*')
        redis_cache.invalidate_pattern('user-spending*')
        redis_cache.invalidate_pattern('admin-analytics*')
        
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
                'total_cost': parking_lot.price_per_hour * duration_hours,
                'vehicle_number': reservation.vehicle_number
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create reservation error: {str(e)}")
        return jsonify({'error': 'Failed to create reservation'}), 500

@reservation_bp.route('/<int:reservation_id>/occupy', methods=['POST', 'PUT'])
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
        
        if reservation.parking_spot.is_occupied:
            return jsonify({'error': 'Spot is already occupied'}), 400
        
        reservation.parking_spot.is_occupied = True
        reservation.occupied_at = get_ist_now()
        # STRICTOR BILLING REFACTOR: Do not reset start_time.
        
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

@reservation_bp.route('/<int:reservation_id>/release', methods=['POST', 'PUT'])
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
        
        release_time = get_ist_now()
        
        if reservation.occupied_at:
            if reservation.occupied_at.tzinfo is None:
                # Handle old naive data
                from datetime import timezone
                occupied_at = reservation.occupied_at.replace(tzinfo=timezone.utc)
            else:
                occupied_at = reservation.occupied_at
            actual_duration = (release_time - occupied_at).total_seconds() / 3600
        else:
            actual_duration = 0
            
        if reservation.start_time.tzinfo is None:
             from datetime import timezone
             start_time = reservation.start_time.replace(tzinfo=timezone.utc)
        else:
             start_time = reservation.start_time
             
        elapsed_hours = (release_time - start_time).total_seconds() / 3600
        billable_hours = max(reservation.reserved_duration_hours, elapsed_hours)
        
        parking_lot = reservation.parking_spot.parking_lot
        final_cost = parking_lot.price_per_hour * billable_hours
        
        reservation.end_time = release_time
        reservation.released_at = release_time
        reservation.status = 'completed'
        reservation.actual_duration_hours = actual_duration
        reservation.final_cost = final_cost
        reservation.parking_spot.is_occupied = False
        
        db.session.commit()
        
        redis_cache.invalidate_pattern('parking-lots*')
        redis_cache.invalidate_pattern('user-spending*')
        redis_cache.invalidate_pattern('admin-analytics*')
        
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

@reservation_bp.route('/<int:reservation_id>/extend', methods=['POST', 'PUT'])
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

@reservation_bp.route('/<int:reservation_id>/cancel', methods=['POST'])
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
        
        if reservation.status not in ['active']:
            return jsonify({'error': 'Only active reservations can be cancelled'}), 400
        
        # Allow cancellation even if start time has passed, as long as it's not occupied yet (no-show)
        # if get_ist_now() >= reservation.start_time:
        #     return jsonify({'error': 'Cannot cancel a reservation that has already started'}), 400
        
        reservation.status = 'cancelled'
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
