"""Sample data for testing the CRM application."""
from app import app
from database import db
from models import User, Lead, Account, Contact, Opportunity
from datetime import datetime, date
import uuid

def create_sample_data():
    """Create sample data for testing"""
    with app.app_context():
        # Create a sample user
        user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User'
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        
        print(f"Created user: {user.username}")
        
        # Create sample leads
        leads_data = [
            {
                'company_name': 'TechCorp Solutions',
                'contact_person': 'John Smith',
                'email': 'john.smith@techcorp.com',
                'phone': '555-0101',
                'source': 'Website',
                'stage': 'MAL',
                'notes': 'Interested in our enterprise solution'
            },
            {
                'company_name': 'Digital Innovations Inc',
                'contact_person': 'Sarah Johnson',
                'email': 'sarah@digitalinnovations.com',
                'phone': '555-0102',
                'source': 'Referral',
                'stage': 'MQL',
                'notes': 'High potential lead from partner referral'
            },
            {
                'company_name': 'Global Manufacturing Ltd',
                'contact_person': 'Mike Wilson',
                'email': 'mike.wilson@globalmfg.com',
                'phone': '555-0103',
                'source': 'Trade Show',
                'stage': 'SQL',
                'notes': 'Met at industry conference, ready for demo'
            }
        ]
        
        for lead_data in leads_data:
            lead = Lead(
                company_name=lead_data['company_name'],
                contact_person=lead_data['contact_person'],
                email=lead_data['email'],
                phone=lead_data['phone'],
                source=lead_data['source'],
                stage=lead_data['stage'],
                notes=lead_data['notes'],
                created_by=user.id
            )
            db.session.add(lead)
        
        db.session.commit()
        print("Created sample leads")
        
        # Create sample accounts
        accounts_data = [
            {
                'company_name': 'Acme Corporation',
                'address_line1': '123 Business Ave',
                'city': 'New York',
                'province_state': 'NY',
                'postal_zip_code': '10001',
                'country': 'USA',
                'description': 'Large enterprise software company',
                'notes': 'Established customer since 2020'
            },
            {
                'company_name': 'Future Systems LLC',
                'address_line1': '456 Tech Street',
                'city': 'San Francisco',
                'province_state': 'CA',
                'postal_zip_code': '94105',
                'country': 'USA',
                'description': 'Cloud infrastructure provider',
                'notes': 'Growing startup with high potential'
            }
        ]
        
        for account_data in accounts_data:
            account = Account(
                company_name=account_data['company_name'],
                address_line1=account_data['address_line1'],
                city=account_data['city'],
                province_state=account_data['province_state'],
                postal_zip_code=account_data['postal_zip_code'],
                country=account_data['country'],
                description=account_data['description'],
                notes=account_data['notes'],
                created_by=user.id
            )
            db.session.add(account)
        
        db.session.commit()
        print("Created sample accounts")
        
        # Get created accounts for contacts and opportunities
        acme = Account.query.filter_by(company_name='Acme Corporation').first()
        future_systems = Account.query.filter_by(company_name='Future Systems LLC').first()
        
        # Create sample contacts
        contacts_data = [
            {
                'first_name': 'Alice',
                'last_name': 'Brown',
                'email': 'alice.brown@acme.com',
                'title': 'CTO',
                'account_id': acme.id,
                'notes': 'Technical decision maker'
            },
            {
                'first_name': 'Bob',
                'last_name': 'Davis',
                'email': 'bob.davis@acme.com',
                'title': 'VP of Operations',
                'account_id': acme.id,
                'notes': 'Budget approval authority'
            },
            {
                'first_name': 'Carol',
                'last_name': 'Martinez',
                'email': 'carol@futuresystems.com',
                'title': 'CEO',
                'account_id': future_systems.id,
                'notes': 'Company founder and decision maker'
            }
        ]
        
        for contact_data in contacts_data:
            contact = Contact(
                first_name=contact_data['first_name'],
                last_name=contact_data['last_name'],
                email=contact_data['email'],
                title=contact_data['title'],
                account_id=contact_data['account_id'],
                notes=contact_data['notes'],
                created_by=user.id
            )
            db.session.add(contact)
        
        db.session.commit()
        print("Created sample contacts")
        
        # Get created contacts for opportunities
        alice = Contact.query.filter_by(email='alice.brown@acme.com').first()
        carol = Contact.query.filter_by(email='carol@futuresystems.com').first()
        
        # Create sample opportunities
        opportunities_data = [
            {
                'name': 'Enterprise Software Upgrade',
                'sales_stage': 'Proposal',
                'forecast': '75%',
                'company_id': acme.id,
                'contact_id': alice.id,
                'next_steps': 'Deliver final proposal by Friday',
                'close_date': date(2025, 7, 15),
                'requirements': 'Full enterprise suite with 500 user licenses'
            },
            {
                'name': 'Cloud Migration Project',
                'sales_stage': 'Negotiation',
                'forecast': '90%',
                'company_id': future_systems.id,
                'contact_id': carol.id,
                'next_steps': 'Contract review with legal team',
                'close_date': date(2025, 6, 30),
                'requirements': 'Migration of legacy systems to cloud platform'
            }
        ]
        
        for opp_data in opportunities_data:
            opportunity = Opportunity(
                name=opp_data['name'],
                sales_stage=opp_data['sales_stage'],
                forecast=opp_data['forecast'],
                company_id=opp_data['company_id'],
                contact_id=opp_data['contact_id'],
                next_steps=opp_data['next_steps'],
                close_date=opp_data['close_date'],
                requirements=opp_data['requirements'],
                created_by=user.id
            )
            db.session.add(opportunity)
        
        db.session.commit()
        print("Created sample opportunities")
        
        print("\nSample data creation completed!")
        print("Login credentials:")
        print("Username: admin")
        print("Password: admin123")

if __name__ == '__main__':
    create_sample_data()
