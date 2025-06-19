from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import uuid

from database import db

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    organization_id = db.Column(db.String(36), nullable=True)  # Shared organization ID
    is_admin = db.Column(db.Boolean, default=False)  # Admin can invite others
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

def get_organization_filter(user):
    """Get the appropriate filter for organization-based data access"""
    if user.organization_id:
        return {'organization_id': user.organization_id}
    else:
        # Fallback to user-specific data for users without organization
        return {'created_by': user.id}

def set_organization_data(record, user):
    """Set organization data when creating new records"""
    if user.organization_id:
        record.organization_id = user.organization_id
    record.created_by = user.id
    return record

def create_organization_for_user(user):
    """Create a new organization ID for a user and make them admin"""
    import uuid
    organization_id = str(uuid.uuid4())
    user.organization_id = organization_id
    user.is_admin = True
    return organization_id

class Lead(db.Model):
    """Lead model - prospects that haven't been qualified yet"""
    __tablename__ = 'leads'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    source = db.Column(db.String(100))
    stage = db.Column(db.String(20), default='MQL')  # MQL, SAL, SQL
    notes = db.Column(db.Text)
    is_converted = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.Date, default=date.today)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.String(36), nullable=True)  # Shared organization
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='leads')
    
    def to_dict(self):
        return {
            'id': self.id,
            'companyName': self.company_name,
            'contactPerson': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'source': self.source,
            'stage': self.stage,
            'notes': self.notes,
            'isConverted': self.is_converted,
            'createdDate': self.created_date.isoformat() if self.created_date else None
        }

class Account(db.Model):
    """Account model - qualified companies we do business with"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = db.Column(db.String(200), nullable=False)
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    province_state = db.Column(db.String(100))
    postal_zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    account_planning_fields = db.Column(db.Text)
    create_date = db.Column(db.Date, default=date.today)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.String(36), nullable=True)  # Shared organization
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='accounts')
    contacts = db.relationship('Contact', backref='account', lazy=True)
    opportunities = db.relationship('Opportunity', backref='account', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'companyName': self.company_name,
            'addressLine1': self.address_line1,
            'addressLine2': self.address_line2,
            'city': self.city,
            'provinceState': self.province_state,
            'postalZipCode': self.postal_zip_code,
            'country': self.country,
            'description': self.description,
            'notes': self.notes,
            'accountPlanningFields': self.account_planning_fields,
            'createDate': self.create_date.isoformat() if self.create_date else None
        }

class Contact(db.Model):
    """Contact model - individual people at accounts"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    title = db.Column(db.String(200))
    notes = db.Column(db.Text)
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False)
    training_received = db.Column(db.String(200))
    last_contact = db.Column(db.Date)
    create_date = db.Column(db.Date, default=date.today)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.String(36), nullable=True)  # Shared organization
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='contacts')
    opportunities = db.relationship('Opportunity', backref='contact', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'title': self.title,
            'notes': self.notes,
            'accountId': self.account_id,
            'trainingReceived': self.training_received,
            'lastContact': self.last_contact.isoformat() if self.last_contact else None,
            'createDate': self.create_date.isoformat() if self.create_date else None
        }

class Opportunity(db.Model):
    """Opportunity model - potential sales deals"""
    __tablename__ = 'opportunities'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    sales_stage = db.Column(db.String(50), default='Prospecting')
    forecast = db.Column(db.String(10), default='0%')
    company_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False)
    contact_id = db.Column(db.String(36), db.ForeignKey('contacts.id'), nullable=False)
    next_steps = db.Column(db.Text)
    close_date = db.Column(db.Date)
    contract_date = db.Column(db.Date)
    requirements = db.Column(db.Text)
    created_date = db.Column(db.Date, default=date.today)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.String(36), nullable=True)  # Shared organization
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='opportunities')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'salesStage': self.sales_stage,
            'forecast': self.forecast,
            'companyId': self.company_id,
            'contactId': self.contact_id,
            'nextSteps': self.next_steps,
            'closeDate': self.close_date.isoformat() if self.close_date else None,
            'contractDate': self.contract_date.isoformat() if self.contract_date else None,
            'requirements': self.requirements,
            'createdDate': self.created_date.isoformat() if self.created_date else None
        }
