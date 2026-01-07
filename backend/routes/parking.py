from flask import Blueprint, jsonify, current_app
from flask_security import auth_required
from models import Parking_lot, ParkingSpot

parking_bp = Blueprint('parking', __name__)

def calculate_available_spots(lot):
    """Calculate truly available spots (not occupied and no active reservations)"""
    available_count = 0
    for spot in lot.spots:
        if not spot.is_occupied:
            has_active_reservation = any(res.status == 'active' for res in spot.reservations)
            if not has_active_reservation:
                available_count += 1
    return available_count

from redis_cache import cached, CacheConfig

@parking_bp.route('/parking-lots', methods=['GET'])
@cached(timeout=CacheConfig.PARKING_LOTS_TIMEOUT, key_prefix=CacheConfig.PARKING_LOTS_KEY)
def get_parking_lots():
    """Get all parking lots"""
    try:
        lots = Parking_lot.query.all()
        
        return {
            'parking_lots': [{
                'id': lot.id,
                'name': lot.name,
                'location': lot.location,
                'capacity': lot.capacity,
                'price_per_hour': lot.price_per_hour,
                'available_spots': calculate_available_spots(lot)
            } for lot in lots]
        }
        
    except Exception as e:
        current_app.logger.error(f"Get parking lots error: {str(e)}")
        return jsonify({'error': 'Failed to get parking lots'}), 500

@parking_bp.route('/parking-lots/<int:lot_id>', methods=['GET'])
@auth_required('token', 'session')
def get_parking_lot_details(lot_id):
    """Get parking lot details for regular users"""
    try:
        lot = Parking_lot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        
        return jsonify({
            'parking_lot': {
                'id': lot.id,
                'name': lot.name,
                'location': lot.location,
                'capacity': lot.capacity,
                'price_per_hour': lot.price_per_hour,
                'available_spots': calculate_available_spots(lot)
            },
            'spots': [{
                'id': spot.id,
                'spot_number': spot.spot_number,
                'is_occupied': spot.is_occupied
            } for spot in spots]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get parking lot details error: {str(e)}")
        return jsonify({'error': 'Failed to get parking lot details'}), 500
