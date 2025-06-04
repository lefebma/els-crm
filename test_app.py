"""Unit tests for the CRM application."""
import unittest
import tempfile
import os
from app import app
from database import db
from models import User, Lead, Account, Contact, Opportunity
import json


class CRMTestCase(unittest.TestCase):
    """Test cases for CRM application"""

    def setUp(self):
        """Set up test fixtures"""
        self.db_fd, app.config['DATABASE_URL'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_URL']
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Create test user
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User'
            )
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def tearDown(self):
        """Clean up after tests"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE_URL'])

    def login(self, username='testuser', password='testpass'):
        """Helper method to login"""
        return self.app.post('/auth/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        """Helper method to logout"""
        return self.app.get('/auth/logout', follow_redirects=True)

    def test_login_logout(self):
        """Test user login and logout"""
        # Test login
        rv = self.login()
        assert b'Dashboard' in rv.data
        
        # Test logout
        rv = self.logout()
        assert b'Login' in rv.data

    def test_invalid_login(self):
        """Test invalid login"""
        rv = self.login('invalid', 'wrong')
        assert b'Invalid username or password' in rv.data

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        rv = self.app.get('/')
        assert rv.status_code == 302  # Redirect to login

    def test_create_lead(self):
        """Test creating a new lead"""
        self.login()
        
        lead_data = {
            'companyName': 'Test Company',
            'contactPerson': 'John Doe',
            'email': 'john@testcompany.com',
            'phone': '555-1234',
            'source': 'Website',
            'stage': 'MAL',
            'notes': 'Test lead'
        }
        
        rv = self.app.post('/api/leads', 
                          data=json.dumps(lead_data),
                          content_type='application/json')
        
        assert rv.status_code == 201
        data = json.loads(rv.data)
        assert data['companyName'] == 'Test Company'
        assert data['contactPerson'] == 'John Doe'

    def test_get_leads(self):
        """Test retrieving leads"""
        self.login()
        
        # Create a test lead first
        with app.app_context():
            lead = Lead(
                company_name='Test Lead Company',
                contact_person='Jane Smith',
                email='jane@testlead.com',
                phone='555-5678',
                source='Referral',
                stage='MQL',
                created_by=self.user_id
            )
            db.session.add(lead)
            db.session.commit()
        
        rv = self.app.get('/api/leads')
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert len(data) > 0
        assert any(lead['companyName'] == 'Test Lead Company' for lead in data)

    def test_update_lead(self):
        """Test updating a lead"""
        self.login()
        
        # Create a test lead first
        with app.app_context():
            lead = Lead(
                company_name='Update Test Company',
                contact_person='Bob Johnson',
                email='bob@updatetest.com',
                phone='555-9999',
                source='Trade Show',
                stage='MAL',
                created_by=self.user_id
            )
            db.session.add(lead)
            db.session.commit()
            lead_id = lead.id
        
        # Update the lead
        update_data = {
            'companyName': 'Updated Company Name',
            'stage': 'SQL'
        }
        
        rv = self.app.put(f'/api/leads/{lead_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
        
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert data['companyName'] == 'Updated Company Name'
        assert data['stage'] == 'SQL'

    def test_convert_lead(self):
        """Test lead conversion functionality"""
        self.login()
        
        # Create a test lead first
        with app.app_context():
            lead = Lead(
                company_name='Convert Test Company',
                contact_person='Alice Convert',
                email='alice@converttest.com',
                phone='555-1111',
                source='Website',
                stage='SQL',
                created_by=self.user_id
            )
            db.session.add(lead)
            db.session.commit()
            lead_id = lead.id
        
        # Convert the lead
        convert_data = {
            'opportunityName': 'Test Opportunity',
            'salesStage': 'Prospecting',
            'forecast': '25%',
            'closeDate': '2025-12-31',
            'requirements': 'Test requirements'
        }
        
        rv = self.app.post(f'/api/leads/{lead_id}/convert',
                          data=json.dumps(convert_data),
                          content_type='application/json')
        
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert 'account' in data
        assert 'contact' in data
        assert 'opportunity' in data
        assert data['account']['companyName'] == 'Convert Test Company'
        assert data['contact']['firstName'] == 'Alice'
        assert data['contact']['lastName'] == 'Convert'
        assert data['opportunity']['name'] == 'Test Opportunity'

    def test_create_account(self):
        """Test creating a new account"""
        self.login()
        
        account_data = {
            'companyName': 'Test Account Company',
            'addressLine1': '123 Test Street',
            'city': 'Test City',
            'provinceState': 'TS',
            'postalZipCode': '12345',
            'country': 'Test Country',
            'description': 'Test account description',
            'notes': 'Test notes'
        }
        
        rv = self.app.post('/api/accounts',
                          data=json.dumps(account_data),
                          content_type='application/json')
        
        assert rv.status_code == 201
        data = json.loads(rv.data)
        assert data['companyName'] == 'Test Account Company'
        assert data['city'] == 'Test City'

    def test_user_model(self):
        """Test User model functionality"""
        with app.app_context():
            user = User(
                username='modeltest',
                email='model@test.com',
                first_name='Model',
                last_name='Test'
            )
            user.set_password('testpass123')
            
            # Test password hashing
            assert user.check_password('testpass123')
            assert not user.check_password('wrongpass')
            
            # Test string representation
            assert str(user) == '<User modeltest>'

    def test_lead_model(self):
        """Test Lead model functionality"""
        with app.app_context():
            lead = Lead(
                company_name='Model Test Company',
                contact_person='Model Tester',
                email='model@testcompany.com',
                phone='555-0000',
                source='Test',
                stage='MAL',
                created_by=self.user_id
            )
            
            # Test to_dict method
            lead_dict = lead.to_dict()
            assert lead_dict['companyName'] == 'Model Test Company'
            assert lead_dict['contactPerson'] == 'Model Tester'
            assert lead_dict['stage'] == 'MAL'

    def test_api_authentication_required(self):
        """Test that API endpoints require authentication"""
        # Test without login
        rv = self.app.get('/api/leads')
        assert rv.status_code == 302  # Redirect to login
        
        rv = self.app.post('/api/leads', data='{}', content_type='application/json')
        assert rv.status_code == 302  # Redirect to login


if __name__ == '__main__':
    unittest.main()
