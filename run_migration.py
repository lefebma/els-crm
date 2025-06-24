#!/usr/bin/env python3
"""
Run database migration on Azure production database
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the migration script
from migrate_add_amount import migrate_add_amount_column

if __name__ == "__main__":
    print("Starting database migration on Azure...")
    print(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    
    success = migrate_add_amount_column()
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
    
    sys.exit(0 if success else 1)
