from models import db, User, Role, Parking_lot, ParkingSpot
from flask_security import hash_password
from sec import datastore

def create_initial_data():
    """Create initial data for the application."""
    # Create roles
    admin_role = datastore.find_or_create_role(name='admin', description='Administrator role')
    user_role = datastore.find_or_create_role(name='user', description='Regular user role')
    
    # Create admin user if it doesn't exist
    if not datastore.find_user(email='admin@parking.com'):
        admin_user = datastore.create_user(
            name='Admin User',
            username='admin',
            email='admin@parking.com',
            password=hash_password('admin123'),
            roles=[admin_role]
        )
        print(f"Created admin user: {admin_user.email}")
    
    # Create a test user if it doesn't exist
    if not datastore.find_user(email='user@parking.com'):
        test_user = datastore.create_user(
            name='Test User',
            username='testuser',
            email='user@parking.com',
            password=hash_password('password123'),
            roles=[user_role]
        )
        print(f"Created test user: {test_user.email}")
    
    # Create parking lots if they don't exist
    parking_lots_data = [
        {'name': 'Central Plaza Parking', 'location': 'Downtown', 'capacity': 100},
        {'name': 'Mall Parking Garage', 'location': 'Shopping Mall', 'capacity': 200},
        {'name': 'Business District Lot', 'location': 'Uptown', 'capacity': 80},
        {'name': 'City Center Parking', 'location': 'Downtown', 'capacity': 150},
    ]
    
    for lot_data in parking_lots_data:
        existing_lot = Parking_lot.query.filter_by(name=lot_data['name']).first()
        if not existing_lot:
            lot = Parking_lot(
                name=lot_data['name'],
                location=lot_data['location'],
                capacity=lot_data['capacity']
            )
            db.session.add(lot)
            db.session.flush()  # Get the ID
            
            # Create parking spots for each lot
            for i in range(1, lot_data['capacity'] + 1):
                spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=f"{chr(65 + (i-1)//50)}-{(i-1)%50 + 1:02d}",  # A-01, A-02, etc.
                    is_occupied=False
                )
                db.session.add(spot)
            
            print(f"Created parking lot: {lot.name} with {lot_data['capacity']} spots")
    
    db.session.commit()
    print("Initial data created successfully!")