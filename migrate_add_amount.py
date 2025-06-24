#!/usr/bin/env python3
"""
Migration script to add amount column to opportunities table
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db

def migrate_add_amount_column():
    """Add amount column to opportunities table"""
    with app.app_context():
        try:
            # Check if the column already exists
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('opportunities')
            column_names = [col['name'] for col in columns]
            
            if 'amount' not in column_names:
                print("Adding amount column to opportunities table...")
                
                # Add the amount column using text() for raw SQL
                from sqlalchemy import text
                db.session.execute(text('''
                    ALTER TABLE opportunities 
                    ADD COLUMN amount NUMERIC(15, 2);
                '''))
                db.session.commit()
                
                print("✅ Successfully added amount column to opportunities table")
            else:
                print("ℹ️  Amount column already exists in opportunities table")
                
        except Exception as e:
            print(f"❌ Error adding amount column: {str(e)}")
            db.session.rollback()
            return False
        
        return True

if __name__ == "__main__":
    success = migrate_add_amount_column()
    sys.exit(0 if success else 1)
