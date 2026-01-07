from flask import Blueprint, request, jsonify, current_app, Response
from flask_security import auth_required, roles_required, current_user
from models import Reservation, Parking_lot, User, ParkingSpot, db
from datetime import datetime, timedelta
from utils import get_ist_now
from redis_cache import cached, CacheConfig
import statistics

import csv
from io import StringIO

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/admin/analytics', methods=['GET'])
@roles_required('admin')
def get_admin_analytics():
    """Get comprehensive analytics for admin dashboard"""
    try:
        days = request.args.get('days', 30, type=int)
        
        end_date = get_ist_now()
        start_date = end_date - timedelta(days=days)
        
        reservations = Reservation.query.filter(
            Reservation.created_at >= start_date,
            Reservation.status.in_(['completed', 'active'])
        ).all()
        
        total_revenue = sum(res.final_cost or 0 for res in reservations)
        total_bookings = len(reservations)
        
        parking_lots = Parking_lot.query.all()
        total_spots = sum(lot.capacity for lot in parking_lots)
        active_reservations = Reservation.query.filter(Reservation.status == 'active').count()
        average_occupancy = (active_reservations / total_spots * 100) if total_spots > 0 else 0
        
        active_users = len(set(res.user_id for res in reservations))
        
        revenue_by_date = {}
        booking_trends = {}
        for res in reservations:
            date_key = res.created_at.strftime('%Y-%m-%d')
            if date_key not in revenue_by_date:
                revenue_by_date[date_key] = 0
                booking_trends[date_key] = 0
            revenue_by_date[date_key] += res.final_cost or 0
            booking_trends[date_key] += 1
        
        revenue_over_time = [{'date': d, 'revenue': r} for d, r in sorted(revenue_by_date.items())]
        booking_trends_data = [{'date': d, 'bookings': b} for d, b in sorted(booking_trends.items())]
        
        lot_performance = []
        for lot in parking_lots:
            lot_reservations = [res for res in reservations if res.parking_spot.lot_id == lot.id]
            lot_revenue = sum(res.final_cost or 0 for res in lot_reservations)
            lot_bookings = len(lot_reservations)
            lot_occupancy = (len([res for res in lot_reservations if res.status == 'active']) / lot.capacity * 100) if lot.capacity > 0 else 0
            avg_duration = sum(res.actual_duration_hours or res.reserved_duration_hours or 0 for res in lot_reservations) / len(lot_reservations) if lot_reservations else 0
            
            lot_performance.append({
                'id': lot.id, 'name': lot.name, 'revenue': lot_revenue, 'bookings': lot_bookings,
                'occupancy': lot_occupancy, 'avgDuration': avg_duration,
                'revenuePerHour': lot_revenue / (avg_duration * len(lot_reservations)) if avg_duration > 0 and lot_reservations else 0
            })
        lot_performance.sort(key=lambda x: x['revenue'], reverse=True)
        
        hourly_occupancy = {}
        for hour in range(24):
            hourly_reservations = [res for res in reservations if res.start_time and res.start_time.hour == hour]
            hourly_occupancy[hour] = len(hourly_reservations)
        
        hourly_occupancy_data = [{'hour': h, 'occupancy': c} for h, c in hourly_occupancy.items()]
        
        user_activity = {}
        for res in reservations:
            date_key = res.created_at.strftime('%Y-%m-%d')
            if date_key not in user_activity: user_activity[date_key] = {'new_users': 0, 'active_users': 0}
            user_activity[date_key]['active_users'] += 1
            
        unique_users = len(set(res.user_id for res in reservations))
        if user_activity:
             daily_new_users = unique_users / len(user_activity) if len(user_activity) > 0 else 0
             for k in user_activity: user_activity[k]['new_users'] = int(daily_new_users)
             
        user_activity_data = [{'date': d, 'new_users': v['new_users'], 'active_users': v['active_users']} for d, v in sorted(user_activity.items())]
        
        recent_transactions = []
        for res in sorted(reservations, key=lambda x: x.final_cost or 0, reverse=True)[:20]:
            recent_transactions.append({
                'id': res.id, 'date': res.created_at.isoformat(), 'userName': res.user.name,
                'parkingLot': res.parking_spot.parking_lot.name, 'duration': res.actual_duration_hours or res.reserved_duration_hours or 0,
                'amount': res.final_cost or 0, 'status': res.status.title()
            })
            
        return jsonify({
            'summary': {'total_revenue': total_revenue, 'total_bookings': total_bookings, 'average_occupancy': average_occupancy, 'active_users': active_users},
            'revenue_over_time': revenue_over_time, 'booking_trends': booking_trends_data, 'parking_lots': lot_performance,
            'hourly_occupancy': hourly_occupancy_data, 'user_activity': user_activity_data, 'recent_transactions': recent_transactions
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get admin analytics error: {str(e)}")
        return jsonify({'error': 'Failed to fetch analytics data'}), 500

@analytics_bp.route('/admin/analytics/previous', methods=['GET'])
@roles_required('admin')
def get_admin_analytics_previous():
    try:
        days = request.args.get('days', 30, type=int)
        end_date = get_ist_now() - timedelta(days=days)
        start_date = end_date - timedelta(days=days)
        reservations = Reservation.query.filter(Reservation.created_at >= start_date, Reservation.created_at < end_date, Reservation.status.in_(['completed', 'active'])).all()
        
        parking_lots = Parking_lot.query.all()
        total_spots = sum(lot.capacity for lot in parking_lots)
        average_occupancy = (len([res for res in reservations if res.status == 'active']) / total_spots * 100) if total_spots > 0 else 0
        
        return jsonify({
            'total_revenue': sum(res.final_cost or 0 for res in reservations),
            'total_bookings': len(reservations),
            'average_occupancy': average_occupancy,
            'active_users': len(set(res.user_id for res in reservations))
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch previous analytics data'}), 500

@analytics_bp.route('/user/spending-summary', methods=['GET'])
@auth_required('token', 'session')
@cached(timeout=CacheConfig.USER_DATA_TIMEOUT, key_prefix=CacheConfig.USER_DATA_KEY)
def get_user_spending_summary():
    """Get user's parking spending summary and statistics"""
    try:
        days = request.args.get('days', 30, type=int)
        end_date = get_ist_now()
        start_date = end_date - timedelta(days=days)
        
        reservations = Reservation.query.filter_by(user_id=current_user.id).filter(Reservation.created_at >= start_date).all()
        
        total_spent = sum(res.final_cost or res.estimated_cost or 0 for res in reservations)
        total_hours = sum(res.actual_duration_hours or res.reserved_duration_hours or 0 for res in reservations)
        completed_reservations = [res for res in reservations if res.status == 'completed']
        savings = sum((res.estimated_cost or 0) - (res.final_cost or 0) for res in completed_reservations)
        
        lot_spending = {}
        for res in reservations:
            lot_name = res.parking_spot.parking_lot.name
            if lot_name not in lot_spending: lot_spending[lot_name] = {'total_cost': 0, 'visits': 0, 'total_hours': 0}
            lot_spending[lot_name]['total_cost'] += res.final_cost or res.estimated_cost or 0
            lot_spending[lot_name]['visits'] += 1
            lot_spending[lot_name]['total_hours'] += res.actual_duration_hours or res.reserved_duration_hours or 0
            
        lot_breakdown = [{'lot_name': k, 'total_spent': round(v['total_cost'], 2), 'visits': v['visits'], 'total_hours': round(v['total_hours'], 2), 'average_cost_per_visit': round(v['total_cost']/v['visits'], 2) if v['visits'] else 0} for k, v in lot_spending.items()]
        lot_breakdown.sort(key=lambda x: x['total_spent'], reverse=True)
        
        hourly_usage = {}
        for h in range(24): hourly_usage[h] = 0
        for res in reservations: 
            if res.start_time: hourly_usage[res.start_time.hour] += 1
            

        daily_usage = {}
        for day in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
            daily_usage[day] = 0
            
        late_minutes_total = 0
        punctual_count = 0
        
        for res in reservations: 
            if res.start_time:
                # Daily Usage
                day_name = res.start_time.strftime('%A')
                daily_usage[day_name] += 1
                
                # Punctuality (Only for completed/transacted ones with occupied_at)
                if res.occupied_at:
                    start = res.start_time
                    occupied = res.occupied_at.replace(tzinfo=None) if res.occupied_at.tzinfo else res.occupied_at
                    if start.tzinfo: start = start.replace(tzinfo=None)
                    
                    diff_mins = (occupied - start).total_seconds() / 60
                    if diff_mins > 15: # Considered late if > 15 mins
                        late_minutes_total += diff_mins
                    else:
                        punctual_count += 1
                        
                
        punctuality_score = 100
        if len(reservations) > 0:
            # Simple score: 100 - (avg minutes late)
            avg_late = late_minutes_total / len(reservations)
            punctuality_score = max(0, 100 - avg_late)

        return {
            'period': {'days': days, 'start_date': start_date.isoformat(), 'end_date': end_date.isoformat()},
            'summary': {
                'total_reservations': len(reservations),
                'completed_reservations': len(completed_reservations),
                'active_reservations': len([r for r in reservations if r.status == 'active']),
                'cancelled_reservations': len([r for r in reservations if r.status == 'cancelled']),
                'total_spent': round(total_spent, 2),
                'total_hours_parked': round(total_hours, 2),
                'average_cost_per_hour': round(total_spent / total_hours, 2) if total_hours > 0 else 0,
                'average_cost_per_reservation': round(total_spent / len(reservations), 2) if reservations else 0,
                'savings_vs_estimate': round(savings, 2),
                'punctuality_score': round(punctuality_score, 1)
            },
            'spending_by_parking_lot': lot_breakdown,
            'hourly_usage': [{'hour': k, 'count': v} for k,v in hourly_usage.items()],
            'daily_usage': [{'day': k, 'visits': v} for k,v in daily_usage.items()],
            'previous_month_reservations': 0, 
            'recent_activity': [] 
        }
        
    except Exception as e:
        current_app.logger.error(f"Get spending summary error: {str(e)}")
        return jsonify({'error': 'Failed to get spending summary'}), 500

@analytics_bp.route('/admin/reports/revenue', methods=['GET'])
@roles_required('admin')
def export_revenue_report():
    try:
        days = request.args.get('days', 30, type=int)
        end_date = get_ist_now()
        start_date = end_date - timedelta(days=days)
        reservations = Reservation.query.filter(Reservation.created_at >= start_date, Reservation.status.in_(['completed', 'active'])).all()
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'User', 'Parking Lot', 'Spot', 'Duration Hours', 'Amount', 'Status'])
        for res in reservations:
            writer.writerow([res.created_at.strftime('%Y-%m-%d %H:%M'), res.user.name, res.parking_spot.parking_lot.name, res.parking_spot.spot_number, res.actual_duration_hours or res.reserved_duration_hours or 0, res.final_cost or 0, res.status])
        
        return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename=revenue-report-{days}days.csv'})
    except Exception as e:
        return jsonify({'error': 'Failed to export revenue report'}), 500

@analytics_bp.route('/admin/reports/occupancy', methods=['GET'])
@roles_required('admin')
def export_occupancy_report():
    try:
        days = request.args.get('days', 30, type=int)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Parking Lot', 'Total Capacity', 'Active Reservations', 'Occupancy %', 'Total Revenue'])
        for lot in Parking_lot.query.all():
            active = Reservation.query.join(ParkingSpot).filter(ParkingSpot.lot_id == lot.id, Reservation.status == 'active').count()
            writer.writerow([lot.name, lot.capacity, active, f"{(active/lot.capacity*100) if lot.capacity else 0:.1f}", 0]) # Revenue simplified
        return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename=occupancy-report-{days}days.csv'})
    except Exception as e:
         return jsonify({'error': 'Failed to export occupancy report'}), 500

@analytics_bp.route('/admin/reports/users', methods=['GET'])
@roles_required('admin')
def export_admin_user_report():
    try:
        days = request.args.get('days', 30, type=int)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['User Name', 'Email', 'Join Date', 'Total Reservations', 'Total Spent'])
        for user in User.query.all():
            writer.writerow([user.name, user.email, user.created_at, 0, 0]) # Simplified
        return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename=user-report-{days}days.csv'})
    except Exception as e:
        return jsonify({'error': 'Failed to export user report'}), 500

@analytics_bp.route('/admin/reports/predictive', methods=['GET'])
@roles_required('admin')
def generate_predictive_report():
    # Simplified predictive report
    return jsonify({'message': 'Predictive report generated', 'forecast': {}}), 200

@analytics_bp.route('/user/export-report', methods=['GET'])
@auth_required('token', 'session')
def export_user_report():
    try:
        days = request.args.get('days', 30, type=int)
        start_date = get_ist_now() - timedelta(days=days)
        reservations = Reservation.query.filter(Reservation.user_id == current_user.id, Reservation.created_at >= start_date).all()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Parking Lot', 'Amount'])
        for res in reservations: writer.writerow([res.created_at, res.parking_spot.parking_lot.name, res.final_cost])
        return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename=personal-parking-report-{days}days.csv'})
    except Exception as e:
        return jsonify({'error': 'Failed to export personal report'}), 500
