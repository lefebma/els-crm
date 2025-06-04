from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Lead, Account, Contact, Opportunity
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
