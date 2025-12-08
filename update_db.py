import sqlite3
import os

db_path = os.path.join('instance', 'inventory.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:

        
        conn.commit()
        print(f"✅ Store Settings table added successfully to {db_path}!")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Error: {e}")

    conn.close()
else:
    print(f"❌ Error: Database not found at {db_path}")