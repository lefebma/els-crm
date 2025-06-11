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

@main_bp.route('/leads/edit', methods=['POST'])
@login_required
def edit_lead():
    """Edit an existing lead"""
    try:
        lead_id = request.form.get('lead_id')
        new_stage = request.form.get('stage')
        
        if not lead_id or not new_stage:
            flash('Missing lead ID or stage information', 'error')
            return redirect(url_for('main.leads'))
        
        # Find the lead and ensure it belongs to the current user
        lead = Lead.query.filter_by(id=lead_id, created_by=current_user.id).first()
        if not lead:
            flash('Lead not found or access denied', 'error')
            return redirect(url_for('main.leads'))
        
        # Update the lead's stage
        lead.stage = new_stage
        db.session.commit()
        flash('Lead updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating lead: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.leads'))

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

@main_bp.route('/leads/<lead_id>/convert', methods=['GET'])
@login_required
def convert_lead(lead_id):
    """Convert a lead via the UI (GET request)"""
    lead = Lead.query.filter_by(id=lead_id, created_by=current_user.id).first()
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("main.leads"))
    if lead.is_converted:
        flash("Lead already converted.", "info")
        return redirect(url_for("main.leads"))
    try:
        # Call a helper (or inline conversion logic) to convert the lead.
        # (For example, create an account, contact, and opportunity.)
        # (Here we assume a helper _convert_lead(lead) exists or inline conversion is performed.)
        # (If you have a helper, uncomment the next line.)
        # _convert_lead(lead)
        # (Inline conversion example (simplified) – adjust as needed):
        account = Account(company_name=lead.company_name, description=f"Converted from lead: {lead.company_name}", created_by=current_user.id)
        db.session.add(account)
        db.session.flush()
        name_parts = lead.contact_person.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        contact = Contact(first_name=first_name, last_name=last_name, email=lead.email, account_id=account.id, created_by=current_user.id)
        db.session.add(contact)
        db.session.flush()
        opportunity = Opportunity(name=f"Opportunity for {lead.company_name}", sales_stage="Prospecting", forecast="0%", company_id=account.id, contact_id=contact.id, next_steps="Initial outreach", requirements=f"Converted from lead: {lead.notes or 'No notes.'}", created_by=current_user.id)
        db.session.add(opportunity)
        lead.is_converted = True
        db.session.commit()
        flash("Lead converted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error converting lead: {str(e)}", "error")
    return redirect(url_for("main.leads"))
