from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Lead, Account, Contact, Opportunity
from database import db
from datetime import datetime
import uuid
from validation import (
    validate_lead_data, validate_account_data, validate_contact_data, 
    validate_opportunity_data, validation_error_response, handle_database_error
)

api_bp = Blueprint('api', __name__)

# Lead API endpoints
@api_bp.route('/leads', methods=['GET'])
@login_required
def get_leads():
    """Get all leads for current user"""
    leads = Lead.query.filter_by(created_by=current_user.id, is_converted=False).all()
    return jsonify([lead.to_dict() for lead in leads])

@api_bp.route('/leads', methods=['POST'])
@login_required
def create_lead():
    """Create a new lead"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate input data
    validation_errors = validate_lead_data(data)
    if validation_errors:
        return validation_error_response(validation_errors)
    
    lead = Lead(
        company_name=data['companyName'],
        contact_person=data['contactPerson'],
        email=data['email'],
        phone=data.get('phone', ''),
        source=data.get('source', ''),
        stage=data.get('stage', 'MAL'),
        notes=data.get('notes', ''),
        created_by=current_user.id
    )
    
    try:
        db.session.add(lead)
        db.session.commit()
        return jsonify(lead.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create lead'}), 500

@api_bp.route('/leads/<lead_id>', methods=['PUT'])
@login_required
def update_lead(lead_id):
    """Update a lead"""
    lead = Lead.query.filter_by(id=lead_id, created_by=current_user.id).first()
    if not lead:
        return jsonify({'error': 'Lead not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'companyName' in data:
        lead.company_name = data['companyName']
    if 'contactPerson' in data:
        lead.contact_person = data['contactPerson']
    if 'email' in data:
        lead.email = data['email']
    if 'phone' in data:
        lead.phone = data['phone']
    if 'source' in data:
        lead.source = data['source']
    if 'stage' in data:
        lead.stage = data['stage']
    if 'notes' in data:
        lead.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify(lead.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update lead'}), 500

@api_bp.route('/leads/<lead_id>/convert', methods=['POST'])
@login_required
def convert_lead(lead_id):
    """Convert lead to account, contact, and opportunity"""
    lead = Lead.query.filter_by(id=lead_id, created_by=current_user.id).first()
    if not lead:
        return jsonify({'error': 'Lead not found'}), 404
    
    if lead.is_converted:
        return jsonify({'error': 'Lead already converted'}), 400
    
    try:
        # Create Account
        account = Account(
            company_name=lead.company_name,
            description=f'Account created from lead: {lead.company_name}',
            notes=lead.notes,
            created_by=current_user.id
        )
        db.session.add(account)
        db.session.flush()  # Get the account ID
        
        # Create Contact
        name_parts = lead.contact_person.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        contact = Contact(
            first_name=first_name,
            last_name=last_name,
            email=lead.email,
            account_id=account.id,
            notes=f'Contact created from lead: {lead.contact_person}',
            last_contact=datetime.utcnow().date(),
            created_by=current_user.id
        )
        db.session.add(contact)
        db.session.flush()  # Get the contact ID
        
        # Create Opportunity
        opportunity = Opportunity(
            name=f'Opportunity for {lead.company_name}',
            sales_stage='Prospecting',
            forecast='0%',
            company_id=account.id,
            contact_id=contact.id,
            next_steps='Initial outreach and discovery call',
            requirements=f'Initial requirements from lead: {lead.notes or "No specific requirements noted yet."}',
            created_by=current_user.id
        )
        db.session.add(opportunity)
        
        # Mark lead as converted
        lead.is_converted = True
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lead converted successfully',
            'account_id': account.id,
            'contact_id': contact.id,
            'opportunity_id': opportunity.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to convert lead'}), 500

# Account API endpoints
@api_bp.route('/accounts', methods=['GET'])
@login_required
def get_accounts():
    """Get all accounts for current user"""
    accounts = Account.query.filter_by(created_by=current_user.id).all()
    return jsonify([account.to_dict() for account in accounts])

@api_bp.route('/accounts', methods=['POST'])
@login_required
def create_account():
    """Create a new account"""
    data = request.get_json()
    
    if not data.get('companyName'):
        return jsonify({'error': 'Company Name is required'}), 400
    
    account = Account(
        company_name=data['companyName'],
        address_line1=data.get('addressLine1', ''),
        address_line2=data.get('addressLine2', ''),
        city=data.get('city', ''),
        province_state=data.get('provinceState', ''),
        postal_zip_code=data.get('postalZipCode', ''),
        country=data.get('country', ''),
        description=data.get('description', ''),
        notes=data.get('notes', ''),
        account_planning_fields=data.get('accountPlanningFields', ''),
        created_by=current_user.id
    )
    
    try:
        db.session.add(account)
        db.session.commit()
        return jsonify(account.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create account'}), 500

@api_bp.route('/accounts/<account_id>', methods=['PUT'])
@login_required
def update_account(account_id):
    """Update an account"""
    account = Account.query.filter_by(id=account_id, created_by=current_user.id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    for field_map in [
        ('companyName', 'company_name'),
        ('addressLine1', 'address_line1'),
        ('addressLine2', 'address_line2'),
        ('city', 'city'),
        ('provinceState', 'province_state'),
        ('postalZipCode', 'postal_zip_code'),
        ('country', 'country'),
        ('description', 'description'),
        ('notes', 'notes'),
        ('accountPlanningFields', 'account_planning_fields')
    ]:
        if field_map[0] in data:
            setattr(account, field_map[1], data[field_map[0]])
    
    try:
        db.session.commit()
        return jsonify(account.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update account'}), 500

# Contact API endpoints
@api_bp.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    """Get all contacts for current user"""
    contacts = Contact.query.filter_by(created_by=current_user.id).all()
    return jsonify([contact.to_dict() for contact in contacts])

@api_bp.route('/contacts', methods=['POST'])
@login_required
def create_contact():
    """Create a new contact"""
    data = request.get_json()
    
    required_fields = ['firstName', 'lastName', 'email', 'accountId']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'First Name, Last Name, Email, and Account are required'}), 400
    
    # Verify account belongs to user
    account = Account.query.filter_by(id=data['accountId'], created_by=current_user.id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    contact = Contact(
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        title=data.get('title', ''),
        notes=data.get('notes', ''),
        account_id=data['accountId'],
        training_received=data.get('trainingReceived', ''),
        last_contact=datetime.strptime(data['lastContact'], '%Y-%m-%d').date() if data.get('lastContact') else None,
        created_by=current_user.id
    )
    
    try:
        db.session.add(contact)
        db.session.commit()
        return jsonify(contact.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create contact'}), 500

@api_bp.route('/contacts/<contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    """Update a contact"""
    contact = Contact.query.filter_by(id=contact_id, created_by=current_user.id).first()
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'firstName' in data:
        contact.first_name = data['firstName']
    if 'lastName' in data:
        contact.last_name = data['lastName']
    if 'email' in data:
        contact.email = data['email']
    if 'title' in data:
        contact.title = data['title']
    if 'notes' in data:
        contact.notes = data['notes']
    if 'accountId' in data:
        # Verify account belongs to user
        account = Account.query.filter_by(id=data['accountId'], created_by=current_user.id).first()
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        contact.account_id = data['accountId']
    if 'trainingReceived' in data:
        contact.training_received = data['trainingReceived']
    if 'lastContact' in data:
        contact.last_contact = datetime.strptime(data['lastContact'], '%Y-%m-%d').date() if data['lastContact'] else None
    
    try:
        db.session.commit()
        return jsonify(contact.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update contact'}), 500

# Opportunity API endpoints
@api_bp.route('/opportunities', methods=['GET'])
@login_required
def get_opportunities():
    """Get all opportunities for current user"""
    opportunities = Opportunity.query.filter_by(created_by=current_user.id).all()
    return jsonify([opportunity.to_dict() for opportunity in opportunities])

@api_bp.route('/opportunities', methods=['POST'])
@login_required
def create_opportunity():
    """Create a new opportunity"""
    data = request.get_json()
    
    required_fields = ['name', 'companyId', 'contactId']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Opportunity Name, Company, and Contact are required'}), 400
    
    # Verify account and contact belong to user
    account = Account.query.filter_by(id=data['companyId'], created_by=current_user.id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    contact = Contact.query.filter_by(id=data['contactId'], created_by=current_user.id).first()
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    opportunity = Opportunity(
        name=data['name'],
        sales_stage=data.get('salesStage', 'Prospecting'),
        forecast=data.get('forecast', '0%'),
        company_id=data['companyId'],
        contact_id=data['contactId'],
        next_steps=data.get('nextSteps', ''),
        close_date=datetime.strptime(data['closeDate'], '%Y-%m-%d').date() if data.get('closeDate') else None,
        contract_date=datetime.strptime(data['contractDate'], '%Y-%m-%d').date() if data.get('contractDate') else None,
        requirements=data.get('requirements', ''),
        created_by=current_user.id
    )
    
    try:
        db.session.add(opportunity)
        db.session.commit()
        return jsonify(opportunity.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create opportunity'}), 500

@api_bp.route('/opportunities/<opportunity_id>', methods=['PUT'])
@login_required
def update_opportunity(opportunity_id):
    """Update an opportunity"""
    opportunity = Opportunity.query.filter_by(id=opportunity_id, created_by=current_user.id).first()
    if not opportunity:
        return jsonify({'error': 'Opportunity not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        opportunity.name = data['name']
    if 'salesStage' in data:
        opportunity.sales_stage = data['salesStage']
    if 'forecast' in data:
        opportunity.forecast = data['forecast']
    if 'companyId' in data:
        # Verify account belongs to user
        account = Account.query.filter_by(id=data['companyId'], created_by=current_user.id).first()
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        opportunity.company_id = data['companyId']
    if 'contactId' in data:
        # Verify contact belongs to user
        contact = Contact.query.filter_by(id=data['contactId'], created_by=current_user.id).first()
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        opportunity.contact_id = data['contactId']
    if 'nextSteps' in data:
        opportunity.next_steps = data['nextSteps']
    if 'closeDate' in data:
        opportunity.close_date = datetime.strptime(data['closeDate'], '%Y-%m-%d').date() if data['closeDate'] else None
    if 'contractDate' in data:
        opportunity.contract_date = datetime.strptime(data['contractDate'], '%Y-%m-%d').date() if data['contractDate'] else None
    if 'requirements' in data:
        opportunity.requirements = data['requirements']
    
    try:
        db.session.commit()
        return jsonify(opportunity.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update opportunity'}), 500
