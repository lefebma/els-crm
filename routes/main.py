from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from models import Lead, Account, Contact, Opportunity, User
from database import db
import csv
from io import StringIO

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
    leads = Lead.query.filter_by(created_by=current_user.id).all()
    return render_template('leads.html', leads=leads)

@main_bp.route('/leads/add', methods=['GET', 'POST'])
@login_required
def add_lead():
    """Add new lead"""
    if request.method == 'POST':
        try:
            # Map form fields to model fields
            contact_person = f"{request.form['first_name']} {request.form['last_name']}"
            lead = Lead(
                contact_person=contact_person,
                company_name=request.form.get('company', 'Unknown'),
                email=request.form['email'],
                phone=request.form.get('phone'),
                stage=request.form.get('status', 'MAL'),  # Map status to stage
                created_by=current_user.id
            )
            db.session.add(lead)
            db.session.commit()
            flash('Lead added successfully!', 'success')
            return redirect(url_for('main.leads'))
        except Exception as e:
            flash(f'Error adding lead: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_lead.html')

@main_bp.route('/accounts')
@login_required
def accounts():
    """Accounts management page"""
    accounts = Account.query.filter_by(created_by=current_user.id).all()
    return render_template('accounts.html', accounts=accounts)

@main_bp.route('/accounts/add', methods=['GET', 'POST'])
@login_required
def add_account():
    """Add new account"""
    if request.method == 'POST':
        try:
            # Map form fields to model fields
            account = Account(
                company_name=request.form['name'],  # Map name to company_name
                description=request.form.get('industry'),  # Map industry to description
                address_line1=request.form.get('address'),
                created_by=current_user.id
            )
            db.session.add(account)
            db.session.commit()
            flash('Account added successfully!', 'success')
            return redirect(url_for('main.accounts'))
        except Exception as e:
            flash(f'Error adding account: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_account.html')

@main_bp.route('/contacts')
@login_required
def contacts():
    """Contacts management page"""
    contacts = Contact.query.filter_by(created_by=current_user.id).all()
    return render_template('contacts.html', contacts=contacts)

@main_bp.route('/contacts/add', methods=['GET', 'POST'])
@login_required
def add_contact():
    """Add new contact"""
    if request.method == 'POST':
        try:
            # Get or create a default account for this user
            account = Account.query.filter_by(created_by=current_user.id).first()
            print(f"DEBUG: Found account: {account}")
            if not account:
                # Create a default account
                account = Account(
                    company_name="Default Company",
                    created_by=current_user.id
                )
                db.session.add(account)
                db.session.commit()  # Commit to get the ID
                print(f"DEBUG: Created new account: {account.id}")
            else:
                print(f"DEBUG: Using existing account: {account.id}")
            
            # Create the contact
            print(f"DEBUG: About to create contact with account_id: {account.id}")
            contact = Contact(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                email=request.form['email'],
                title=request.form.get('job_title'),  # Map job_title to title
                account_id=account.id,  # Use the account's ID directly
                created_by=current_user.id
            )
            print(f"DEBUG: Contact object created with account_id: {contact.account_id}")
            db.session.add(contact)
            db.session.commit()
            flash('Contact added successfully!', 'success')
            return redirect(url_for('main.contacts'))
        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            flash(f'Error adding contact: {str(e)}', 'error')
            db.session.rollback()
    
    accounts = Account.query.filter_by(created_by=current_user.id).all()
    return render_template('add_contact.html', accounts=accounts)

@main_bp.route('/opportunities')
@login_required
def opportunities():
    """Opportunities management page"""
    opportunities = Opportunity.query.filter_by(created_by=current_user.id).options(
        db.joinedload(Opportunity.account)
    ).all()
    return render_template('opportunities.html', opportunities=opportunities)

@main_bp.route('/opportunities/add', methods=['GET', 'POST'])
@login_required
def add_opportunity():
    """Add new opportunity"""
    if request.method == 'POST':
        try:
            # Get or create a default account for this user
            account = Account.query.filter_by(created_by=current_user.id).first()
            if not account:
                account = Account(
                    company_name="Default Company",
                    created_by=current_user.id
                )
                db.session.add(account)
                db.session.commit()
            
            # Get or create a default contact for the account
            contact = Contact.query.filter_by(created_by=current_user.id, account_id=account.id).first()
            if not contact:
                contact = Contact(
                    first_name="Default",
                    last_name="Contact",
                    email="default@example.com",
                    account_id=account.id,
                    created_by=current_user.id
                )
                db.session.add(contact)
                db.session.commit()
            
            # Create the opportunity
            opportunity = Opportunity(
                name=request.form['name'],
                sales_stage=request.form.get('stage', 'prospecting'),
                forecast=request.form.get('probability', '50'),
                company_id=account.id,
                contact_id=contact.id,
                requirements=request.form.get('description'),
                created_by=current_user.id
            )
            db.session.add(opportunity)
            db.session.commit()
            flash('Opportunity added successfully!', 'success')
            return redirect(url_for('main.opportunities'))
        except Exception as e:
            flash(f'Error adding opportunity: {str(e)}', 'error')
            db.session.rollback()
    
    accounts = Account.query.filter_by(created_by=current_user.id).all()
    contacts = Contact.query.filter_by(created_by=current_user.id).all()
    return render_template('add_opportunity.html', accounts=accounts, contacts=contacts)

@main_bp.route('/leads/export')
@login_required
def export_leads():
    """Export leads to CSV"""
    leads = Lead.query.filter_by(created_by=current_user.id).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Contact Person', 'Company', 'Email', 'Phone', 'Stage', 'Created Date'])
    
    # Write data
    for lead in leads:
        writer.writerow([
            lead.contact_person,
            lead.company_name or '',
            lead.email,
            lead.phone or '',
            lead.stage,
            lead.created_date.strftime('%Y-%m-%d') if lead.created_date else ''
        ])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=leads_export.csv'
    
    return response

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
