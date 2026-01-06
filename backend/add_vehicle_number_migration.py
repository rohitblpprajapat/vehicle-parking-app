import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
if not os.path.exists(db_path):
    # Try alternate location if instance folder structure is different
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')

print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(reservation)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'vehicle_number' in columns:
        print("Column 'vehicle_number' already exists in 'reservation' table.")
    else:
        print("Adding 'vehicle_number' column to 'reservation' table...")
        cursor.execute("ALTER TABLE reservation ADD COLUMN vehicle_number VARCHAR(20)")
        conn.commit()
        print("Column added successfully.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
