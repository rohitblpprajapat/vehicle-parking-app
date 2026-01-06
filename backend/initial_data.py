from models import db, User, Role, Parking_lot, ParkingSpot
from flask_security import hash_password
from sec import datastore

def create_initial_data():
    """Create initial data for the application."""
    # Create roles first
    admin_role = datastore.find_or_create_role(name='admin', description='Administrator role')
    user_role = datastore.find_or_create_role(name='user', description='Regular user role')
    db.session.commit()  # Commit roles first
    
    # Create admin user if it doesn't exist
    admin_user = datastore.find_user(email='admin@parking.com')
    if not admin_user:
        admin_user = datastore.create_user(
            name='Admin User',
            username='admin',
            email='admin@parking.com',
            password=hash_password('admin123'),
            active=True
        )
        datastore.add_role_to_user(admin_user, admin_role)
        print(f"Created admin user: {admin_user.email} with role: {admin_role.name}")
    
    # Create a test user if it doesn't exist
    test_user = datastore.find_user(email='user@parking.com')
    if not test_user:
        test_user = datastore.create_user(
            name='Ravi Sharma',
            username='ravisharma',
            email='user@parking.com',
            password=hash_password('password123'),
            active=True
        )
        datastore.add_role_to_user(test_user, user_role)
        print(f"Created test user: {test_user.email} with role: {user_role.name}")
    
    db.session.commit()  # Commit users and roles
    
    # Create parking lots if they don't exist
    parking_lots_data = [
        {'name': 'Connaught Place Parking', 'location': 'New Delhi', 'capacity': 100, 'price_per_hour': 50.0},
        {'name': 'Phoenix Mall Parking', 'location': 'Mumbai', 'capacity': 200, 'price_per_hour': 30.0},
        {'name': 'Cyber Hub Parking', 'location': 'Gurgaon', 'capacity': 80, 'price_per_hour': 80.0},
        {'name': 'Brigade Road Parking', 'location': 'Bangalore', 'capacity': 150, 'price_per_hour': 60.0},
    ]
    
    for lot_data in parking_lots_data:
        existing_lot = Parking_lot.query.filter_by(name=lot_data['name']).first()
        if not existing_lot:
            lot = Parking_lot(
                name=lot_data['name'],
                location=lot_data['location'],
                capacity=lot_data['capacity'],
                price_per_hour=lot_data['price_per_hour']
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