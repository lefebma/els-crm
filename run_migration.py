#!/usr/bin/env python3
"""
Simple migration script to add amount column to opportunities table
"""
import os
import psycopg2
from psycopg2 import sql

def run_migration():
    """Add amount column to opportunities table"""
    try:
        # Get database connection details from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not found")
            return False
            
        # Parse the database URL
        # Format: postgresql://username:password@host:port/database
        if database_url.startswith('postgresql://'):
            # Extract components
            parts = database_url.replace('postgresql://', '').split('@')
            if len(parts) != 2:
                print("❌ Invalid DATABASE_URL format")
                return False
                
            user_pass = parts[0]
            host_db = parts[1]
            
            if ':' in user_pass:
                username, password = user_pass.split(':', 1)
            else:
                username = user_pass
                password = os.getenv('POSTGRES_PASSWORD', '')
                
            if '/' in host_db:
                host_port, database = host_db.split('/', 1)
            else:
                host_port = host_db
                database = 'crmdb'
                
            if ':' in host_port:
                host, port = host_port.split(':')
            else:
                host = host_port
                port = '5432'
                
            # Remove any query parameters from database name
            if '?' in database:
                database = database.split('?')[0]
                
            print(f"Connecting to: {host}:{port}/{database} as {username}")
            
            # Connect to the database
            conn = psycopg2.connect(
                host=host,
                database=database,
                user=username,
                password=password,
                port=port,
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
    success = run_migration()
    exit(0 if success else 1)
