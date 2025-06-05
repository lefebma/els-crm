#!/usr/bin/env python3
"""
Database initialization script for ELS CRM
This script creates all necessary database tables and sample data
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Account, Contact, Lead, Opportunity, Task
from app import create_app

def init_database():
    """Initialize the database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all existing tables and recreate them
        db.drop_all()
        db.create_all()
        
        print("Database tables created successfully!")
        
        # Create sample admin user
        print("Creating sample admin user...")
        admin_user = User(
            username='admin',
            email='admin@elscrm.com',
            first_name='Admin',
            last_name='User',
            password_hash=generate_password_hash('admin123')
        )
        
        # Create demo user
        demo_user = User(
            username='demo',
            email='demo@elscrm.com',
            first_name='Demo',
            last_name='User',
            password_hash=generate_password_hash('demo123')
        )
        
        db.session.add(admin_user)
        db.session.add(demo_user)
        db.session.commit()
        
        print("Sample users created:")
        print("- Admin: username=admin, password=admin123")
        print("- Demo: username=demo, password=demo123")
        
        # Create sample data
        print("Creating sample data...")
        
        # Sample Account
        sample_account = Account(
            name='Acme Corporation',
            industry='Technology',
            phone='555-0123',
            email='info@acme.com',
            website='https://acme.com',
            address='123 Business St, Tech City, TC 12345',
            user_id=demo_user.id
        )
        db.session.add(sample_account)
        db.session.commit()
        
        # Sample Contact
        sample_contact = Contact(
            first_name='John',
            last_name='Smith',
            email='john.smith@acme.com',
            phone='555-0124',
            position='CTO',
            company='Acme Corporation',
            account_id=sample_account.id,
            user_id=demo_user.id
        )
        db.session.add(sample_contact)
        
        # Sample Lead
        sample_lead = Lead(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@prospect.com',
            phone='555-0125',
            company='Prospect Inc',
            position='CEO',
            source='Website',
            status='New',
            user_id=demo_user.id
        )
        db.session.add(sample_lead)
        
        # Sample Opportunity
        sample_opportunity = Opportunity(
            name='Enterprise Software License',
            amount=50000.00,
            stage='Proposal',
            probability=75,
            close_date='2025-07-01',
            description='Large enterprise software licensing deal',
            account_id=sample_account.id,
            user_id=demo_user.id
        )
        db.session.add(sample_opportunity)
        
        # Sample Task
        sample_task = Task(
            title='Follow up with John Smith',
            description='Schedule demo call for next week',
            status='Pending',
            priority='High',
            due_date='2025-06-10',
            contact_id=sample_contact.id,
            user_id=demo_user.id
        )
        db.session.add(sample_task)
        
        db.session.commit()
        print("Sample data created successfully!")
        print("\nDatabase initialization complete! 🎉")
        print("\nYou can now log in with:")
        print("- Username: demo, Password: demo123")
        print("- Username: admin, Password: admin123")

if __name__ == '__main__':
    init_database()
