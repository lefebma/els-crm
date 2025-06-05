from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Lead, Account, Contact, Opportunity, User
from database import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Main dashboard view"""
    # Get counts for dashboard
    leads_count = Lead.query.filter_by(created_by=current_user.id, is_converted=False).count()
    accounts_count = Account.query.filter_by(created_by=current_user.id).count()
    contacts_count = Contact.query.filter_by(created_by=current_user.id).count()
    opportunities_count = Opportunity.query.filter_by(created_by=current_user.id).count()
    
    return render_template('dashboard.html', 
                         leads_count=leads_count,
                         accounts_count=accounts_count,
                         contacts_count=contacts_count,
                         opportunities_count=opportunities_count)

@main_bp.route('/leads')
@login_required
def leads():
    """Leads management page"""
    return render_template('leads.html')

@main_bp.route('/accounts')
@login_required
def accounts():
    """Accounts management page"""
    return render_template('accounts.html')

@main_bp.route('/contacts')
@login_required
def contacts():
    """Contacts management page"""
    return render_template('contacts.html')

@main_bp.route('/opportunities')
@login_required
def opportunities():
    """Opportunities management page"""
    return render_template('opportunities.html')

@main_bp.route('/db-test')
def db_test():
    """Test database connectivity and show basic info"""
    try:
        # Test database connection
        result = db.session.execute(db.text('SELECT 1')).scalar()
        
        # Test table existence
        user_count = User.query.count()
        
        # Get database URL (masked for security)
        db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        db_type = 'PostgreSQL' if 'postgresql' in db_url else 'SQLite' if 'sqlite' in db_url else 'Unknown'
        
        return f"""
        <h2>Database Test Results</h2>
        <p><strong>Database Type:</strong> {db_type}</p>
        <p><strong>Connection Test:</strong> {'✅ Success' if result == 1 else '❌ Failed'}</p>
        <p><strong>User Table:</strong> {user_count} users found</p>
        <p><strong>Database URL:</strong> {db_url[:50]}...</p>
        <hr>
        <p><a href="/">Return to Home</a></p>
        """
    except Exception as e:
        return f"""
        <h2>Database Test - ERROR</h2>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><strong>Error Type:</strong> {type(e).__name__}</p>
        <hr>
        <p><a href="/">Return to Home</a></p>
        """
