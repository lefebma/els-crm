#!/usr/bin/env python3
"""
Migration script to add amount column to opportunities table in production
"""
import os
import psycopg2
from psycopg2 import sql

# Production database connection details
DB_HOST = "psqlgoozh6ngfyubm.postgres.database.azure.com"
DB_NAME = "crmdb"
DB_USER = "crmadmin"
DB_PASSWORD = "ozln5fh2vq45yAa1!"
DB_PORT = 5432

def migrate_add_amount_column():
    """Add amount column to opportunities table"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'opportunities' AND column_name = 'amount';
        """)
        
        if cursor.fetchone():
            print("ℹ️  Amount column already exists in opportunities table")
        else:
            print("Adding amount column to opportunities table...")
            
            # Add the amount column
            cursor.execute("""
                ALTER TABLE opportunities 
                ADD COLUMN amount NUMERIC(15, 2);
            """)
            
            conn.commit()
            print("✅ Successfully added amount column to opportunities table")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding amount column: {str(e)}")
        return False

if __name__ == "__main__":
    success = migrate_add_amount_column()
    exit(0 if success else 1) 