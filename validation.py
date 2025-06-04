"""Validation utilities for the CRM application."""
import re
from datetime import datetime
from flask import jsonify


def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    # Remove common formatting characters
    cleaned = re.sub(r'[^\d+\-\(\)\s]', '', phone)
    # Check if it has reasonable length and characters
    return 7 <= len(re.sub(r'[^\d]', '', cleaned)) <= 15


def validate_required_fields(data, required_fields):
    """Validate that required fields are present and not empty"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == '':
            missing_fields.append(field)
    return missing_fields


def validate_lead_data(data):
    """Validate lead data"""
    errors = []
    
    # Check required fields
    required_fields = ['companyName', 'contactPerson', 'email']
    missing = validate_required_fields(data, required_fields)
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")
    
    # Validate email format
    if 'email' in data and data['email'] and not validate_email(data['email']):
        errors.append("Invalid email format")
    
    # Validate phone format
    if 'phone' in data and data['phone'] and not validate_phone(data['phone']):
        errors.append("Invalid phone number format")
    
    # Validate stage
    valid_stages = ['MAL', 'MQL', 'SAL', 'SQL']
    if 'stage' in data and data['stage'] and data['stage'] not in valid_stages:
        errors.append(f"Invalid stage. Must be one of: {', '.join(valid_stages)}")
    
    return errors


def validate_account_data(data):
    """Validate account data"""
    errors = []
    
    # Check required fields
    required_fields = ['companyName']
    missing = validate_required_fields(data, required_fields)
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")
    
    return errors


def validate_contact_data(data):
    """Validate contact data"""
    errors = []
    
    # Check required fields
    required_fields = ['firstName', 'lastName', 'email', 'accountId']
    missing = validate_required_fields(data, required_fields)
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")
    
    # Validate email format
    if 'email' in data and data['email'] and not validate_email(data['email']):
        errors.append("Invalid email format")
    
    return errors


def validate_opportunity_data(data):
    """Validate opportunity data"""
    errors = []
    
    # Check required fields
    required_fields = ['name', 'companyId', 'contactId']
    missing = validate_required_fields(data, required_fields)
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")
    
    # Validate sales stage
    valid_stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
    if 'salesStage' in data and data['salesStage'] and data['salesStage'] not in valid_stages:
        errors.append(f"Invalid sales stage. Must be one of: {', '.join(valid_stages)}")
    
    # Validate forecast percentage
    if 'forecast' in data and data['forecast']:
        forecast = data['forecast'].rstrip('%')
        try:
            forecast_num = float(forecast)
            if not 0 <= forecast_num <= 100:
                errors.append("Forecast must be between 0% and 100%")
        except ValueError:
            errors.append("Invalid forecast format")
    
    # Validate date format
    if 'closeDate' in data and data['closeDate']:
        try:
            datetime.strptime(data['closeDate'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid close date format. Use YYYY-MM-DD")
    
    if 'contractDate' in data and data['contractDate']:
        try:
            datetime.strptime(data['contractDate'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid contract date format. Use YYYY-MM-DD")
    
    return errors


def validation_error_response(errors):
    """Return a standardized validation error response"""
    return jsonify({
        'error': 'Validation failed',
        'details': errors
    }), 400


def handle_database_error(e, operation="operation"):
    """Handle database errors consistently"""
    print(f"Database error during {operation}: {str(e)}")
    return jsonify({
        'error': f'Database error occurred during {operation}',
        'message': 'Please try again or contact support if the problem persists'
    }), 500
