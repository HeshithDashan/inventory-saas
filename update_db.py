import sqlite3
import os

db_path = os.path.join('instance', 'inventory.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS store_settings (
                id INTEGER PRIMARY KEY,
                shop_name TEXT,
                address TEXT,
                phone TEXT,
                header_text TEXT,
                footer_text TEXT
            )
        ''')
        conn.commit()
        print(f"✅ Store Settings table added successfully to {db_path}!")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Error: {e}")

    conn.close()
else:
    print(f"❌ Error:  {db_path}")