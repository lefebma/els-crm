#!/usr/bin/env python3
"""
Add phone column to contacts table
This migration adds the phone field to existing contacts
"""

import sqlite3
import os
from datetime import datetime

def add_phone_column():
    """Add phone column to contacts table"""
    db_path = 'instance/crm.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please ensure the app has been initialized.")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if phone column already exists
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'phone' in columns:
            print("✅ Phone column already exists in contacts table")
            conn.close()
            return True
        
        # Add the phone column
        cursor.execute("ALTER TABLE contacts ADD COLUMN phone VARCHAR(50)")
        conn.commit()
        
        print("✅ Successfully added phone column to contacts table")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Current columns: {', '.join(columns)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding phone column: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Adding phone column to contacts table...")
    success = add_phone_column()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("📱 You can now add and edit phone numbers for contacts.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
