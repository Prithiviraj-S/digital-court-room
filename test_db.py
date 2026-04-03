import sqlite3
import os

db_path = 'justice_system.db'

# Check if file exists
if os.path.exists(db_path):
    print(f"✓ Database file exists: {db_path}")
    file_size = os.path.getsize(db_path)
    print(f"✓ File size: {file_size} bytes")
else:
    print(f"✗ Database file does not exist")
    exit(1)

# Try to connect
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables/
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"✓ Database connected successfully")
    print(f"✓ Tables found: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check rows in each table
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  {table[0]}: {count} rows")
    
    conn.close()
    print("✓ Database is healthy")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"✗ Database may be corrupted")
/*  +  
