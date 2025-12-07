import sqlite3
import os

db_path = os.path.join('instance', 'inventory.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:

        cursor.execute("ALTER TABLE product ADD COLUMN barcode TEXT")
        conn.commit()
        print(f"✅ Barcode column added successfully to {db_path}!")
    except sqlite3.OperationalError:
        print("⚠️ Barcode column already exists or error occurred.")

    conn.close()
else:
    print(f"❌ Error: Database not found at {db_path}")