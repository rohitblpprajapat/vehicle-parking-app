from celery_worker import celery
from flask_mail import Message
from flask import current_app, render_template_string
from models import User, Reservation, db
from datetime import datetime, timedelta
import logging

# Logger
logger = logging.getLogger(__name__)

@celery.task
def send_monthly_report(user_id):
    """
    Background task to generate and send a monthly parking report.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found for monthly report")
            return

        # Simple logic: Get reservations from last 30 days
        last_month = datetime.utcnow() - timedelta(days=30)
        recent_reservations = Reservation.query.filter(
            Reservation.user_id == user.id,
            Reservation.created_at >= last_month
        ).all()

        total_spent = sum(r.final_cost or 0 for r in recent_reservations)
        total_hours = sum(r.actual_duration_hours or 0 for r in recent_reservations)

        # In a real app, use a proper template file
        html_body = f"""
        <h1>Monthly Parking Report</h1>
        <p>Hello {user.email},</p>
        <p>Here is your summary for the last 30 days:</p>
        <ul>
            <li>Total Reservations: {len(recent_reservations)}</li>
            <li>Total Spent: ${total_spent:.2f}</li>
            <li>Total Hours: {total_hours:.2f}</li>
        </ul>
        <p>Thank you for using Vehicle Parking App!</p>
        """

        # Import mail inside task to avoid circular imports if defined globally in app.py
        from app import app
        from flask_mail import Mail
        mail = Mail(app) # Re-init or get from extension if possible, but context is key

        msg = Message(
            subject="Your Monthly Parking Report",
            recipients=[user.email],
            html=html_body,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        
        # In dev/suppress mode, this just logs
        mail.send(msg)
        logger.info(f"Monthly report sent to {user.email}")
        print(f"------------ MOCK EMAIL TO {user.email} ------------")
        print(html_body)
        print("----------------------------------------------------")

    except Exception as e:
        logger.error(f"Failed to send monthly report to user {user_id}: {str(e)}")


@celery.task
def check_reservation_expiry():
    """
    Periodic task to check for reservations expiring in 15 minutes.
    """
    try:
        # Check active reservations expiring between now and 15 mins from now
        now = datetime.utcnow()
        threshold = now + timedelta(minutes=15)
        
        expiring_reservations = Reservation.query.filter(
            Reservation.status == 'active',
            Reservation.end_time > now,
            Reservation.end_time <= threshold,
            # Ideally add a flag 'expiry_notified' to avoid spamming 
            # But for simple demo we just log
        ).all()
        
        if not expiring_reservations:
            return "No expiring reservations found."

        count = 0
        for res in expiring_reservations:
            user = User.query.get(res.user_id)
            if user:
                logger.info(f"Notify user {user.email} -> Spot expires in <15 mins!")
                # Here we would send an email or push notification
                print(f"ALERT: User {user.email}, your reservation {res.id} expires at {res.end_time}!")
                count += 1
        
        return f"Checked expiry: Notified {count} users."

    except Exception as e:
        logger.error(f"Expiry check failed: {str(e)}")
