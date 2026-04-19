import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from config.database import get_db_connection

try:
    print("Testing DB connection...")
    conn = get_db_connection()
    print("Connection successful!")
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE()")
    db_name = cursor.fetchone()[0]
    print(f"Connected to database: {db_name}")
    conn.close()
    
    # Check env vars
    print(f"DB_USER from env: {os.getenv('DB_USER')}")
    print(f"Computed DB_USER (should be root): root")
    
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
