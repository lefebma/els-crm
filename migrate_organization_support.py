#!/usr/bin/env python3
"""
Database migration to add organization support
Adds organization_id and is_admin columns to support user sharing
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add organization support columns to database"""
    db_path = 'instance/crm.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please ensure the app has been initialized.")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting organization support migration...")
        
        # Check and add organization_id and is_admin to users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]
        
        if 'organization_id' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN organization_id VARCHAR(36)")
            print("✅ Added organization_id column to users table")
        else:
            print("✅ organization_id column already exists in users table")
            
        if 'is_admin' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            print("✅ Added is_admin column to users table")
        else:
            print("✅ is_admin column already exists in users table")
        
        # Add organization_id to leads table
        cursor.execute("PRAGMA table_info(leads)")
        lead_columns = [column[1] for column in cursor.fetchall()]
        
        if 'organization_id' not in lead_columns:
            cursor.execute("ALTER TABLE leads ADD COLUMN organization_id VARCHAR(36)")
            print("✅ Added organization_id column to leads table")
        else:
            print("✅ organization_id column already exists in leads table")
        
        # Add organization_id to accounts table
        cursor.execute("PRAGMA table_info(accounts)")
        account_columns = [column[1] for column in cursor.fetchall()]
        
        if 'organization_id' not in account_columns:
            cursor.execute("ALTER TABLE accounts ADD COLUMN organization_id VARCHAR(36)")
            print("✅ Added organization_id column to accounts table")
        else:
            print("✅ organization_id column already exists in accounts table")
        
        # Add organization_id to contacts table
        cursor.execute("PRAGMA table_info(contacts)")
        contact_columns = [column[1] for column in cursor.fetchall()]
        
        if 'organization_id' not in contact_columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN organization_id VARCHAR(36)")
            print("✅ Added organization_id column to contacts table")
        else:
            print("✅ organization_id column already exists in contacts table")
        
        # Add organization_id to opportunities table
        cursor.execute("PRAGMA table_info(opportunities)")
        opportunity_columns = [column[1] for column in cursor.fetchall()]
        
        if 'organization_id' not in opportunity_columns:
            cursor.execute("ALTER TABLE opportunities ADD COLUMN organization_id VARCHAR(36)")
            print("✅ Added organization_id column to opportunities table")
        else:
            print("✅ organization_id column already exists in opportunities table")
        
        conn.commit()
        
        print("\n📋 Current table structures:")
        
        # Show current table structures
        for table in ['users', 'leads', 'accounts', 'contacts', 'opportunities']:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"  {table}: {', '.join(columns)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Organization Support Migration")
    print("=" * 50)
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\n📝 What's New:")
        print("• Users can now belong to organizations for shared data access")
        print("• Users can be designated as administrators")
        print("• All CRM data (leads, accounts, contacts, opportunities) supports organization sharing")
        print("• Existing data remains intact and accessible")
        print("\n🔄 Next Steps:")
        print("1. Restart the Flask application")
        print("2. Existing users can set up organizations via the User Management page")
        print("3. Administrators can invite new users to share CRM data")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
