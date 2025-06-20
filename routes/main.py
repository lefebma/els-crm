from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from models import Lead, Account, Contact, Opportunity, User, get_organization_filter, set_organization_data, create_organization_for_user
from database import db
import csv
from io import StringIO
from datetime import datetime, date

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Main dashboard view"""
    try:
        # Get organization filter
        org_filter = get_organization_filter(current_user)
        
        # Get counts for dashboard using organization filter
        leads_count = Lead.query.filter_by(**org_filter, is_converted=False).count()
        accounts_count = Account.query.filter_by(**org_filter).count()
        contacts_count = Contact.query.filter_by(**org_filter).count()
        opportunities_count = Opportunity.query.filter_by(**org_filter).count()
        
        return render_template('dashboard.html', 
                             leads_count=leads_count,
                             accounts_count=accounts_count,
                             contacts_count=contacts_count,
                             opportunities_count=opportunities_count)
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {e}")
        flash('Error loading dashboard. Please try logging in again.', 'error')
        return redirect(url_for('auth.login'))

@main_bp.route('/leads')
@login_required
def leads():
    """Leads management page"""
    org_filter = get_organization_filter(current_user)
    leads = Lead.query.filter_by(**org_filter).all()
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
                source=request.form.get('source'),
                stage=request.form.get('stage', 'MQL'),  # Use stage field directly
                created_by=current_user.id
            )
            # Set organization data
            lead = set_organization_data(lead, current_user)
            db.session.add(lead)
            db.session.commit()
            flash('Lead added successfully!', 'success')
            return redirect(url_for('main.leads'))
        except Exception as e:
            flash(f'Error adding lead: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_lead.html')

@main_bp.route('/leads/edit/<lead_id>', methods=['GET', 'POST'])
@login_required
def edit_lead(lead_id):
    """Edit an existing lead"""
    # Find the lead using organization filter
    org_filter = get_organization_filter(current_user)
    lead = Lead.query.filter_by(id=lead_id, **org_filter).first()
    if not lead:
        flash('Lead not found or access denied', 'error')
        return redirect(url_for('main.leads'))
    
    if request.method == 'GET':
        # Display the edit form
        return render_template('edit_lead.html', lead=lead)
    
    # Handle POST request (form submission)
    try:
        # Get all form fields
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        company_name = request.form.get('company_name')
        phone = request.form.get('phone')
        source = request.form.get('source')
        stage = request.form.get('stage')
        
        # Validate required fields
        if not contact_person or not email or not stage:
            flash('Please fill in all required fields (Contact Person, Email, and Stage)', 'error')
            return render_template('edit_lead.html', lead=lead)
        
        # Update the lead fields
        lead.contact_person = contact_person.strip()
        lead.email = email.strip()
        lead.company_name = company_name.strip() if company_name else None
        lead.phone = phone.strip() if phone else None
        lead.source = source.strip() if source else None
        lead.stage = stage
        
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
    org_filter = get_organization_filter(current_user)
    accounts = Account.query.filter_by(**org_filter).all()
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
            # Set organization data
            account = set_organization_data(account, current_user)
            db.session.add(account)
            db.session.commit()
            flash('Account added successfully!', 'success')
            return redirect(url_for('main.accounts'))
        except Exception as e:
            flash(f'Error adding account: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_account.html')

@main_bp.route('/accounts/edit/<account_id>', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    """Edit an existing account"""
    # Find the account using organization filter
    org_filter = get_organization_filter(current_user)
    account = Account.query.filter_by(id=account_id, **org_filter).first()
    if not account:
        flash('Account not found or access denied', 'error')
        return redirect(url_for('main.accounts'))
    
    if request.method == 'GET':
        # Get contacts associated with this account
        contacts = Contact.query.filter_by(account_id=account.id).filter_by(**org_filter).all()
        # Display the edit form
        return render_template('edit_account.html', account=account, contacts=contacts)
    
    # Handle POST request (form submission)
    try:
        # Get all form fields
        company_name = request.form.get('company_name')
        description = request.form.get('description')
        address_line1 = request.form.get('address_line1')
        address_line2 = request.form.get('address_line2')
        city = request.form.get('city')
        state = request.form.get('state')
        postal_code = request.form.get('postal_code')
        country = request.form.get('country')
        notes = request.form.get('notes')
        market_segment = request.form.get('market_segment')
        customer_since = request.form.get('customer_since')
        last_activity = request.form.get('last_activity')
        next_activity = request.form.get('next_activity')
        
        # Validate required fields
        if not company_name:
            flash('Company name is required', 'error')
            # Get contacts for display even in error case
            contacts = Contact.query.filter_by(account_id=account.id).filter_by(**org_filter).all()
            return render_template('edit_account.html', account=account, contacts=contacts)
        
        # Update the account fields
        account.company_name = company_name.strip()
        account.description = description.strip() if description else None
        account.address_line1 = address_line1.strip() if address_line1 else None
        account.address_line2 = address_line2.strip() if address_line2 else None
        account.city = city.strip() if city else None
        account.state = state.strip() if state else None
        account.postal_code = postal_code.strip() if postal_code else None
        account.country = country.strip() if country else None
        account.notes = notes.strip() if notes else None
        account.market_segment = market_segment.strip() if market_segment else None
        account.customer_since = customer_since.strip() if customer_since else None
        account.last_activity = last_activity.strip() if last_activity else None
        account.next_activity = next_activity.strip() if next_activity else None
        
        db.session.commit()
        flash('Account updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating account: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.accounts'))

@main_bp.route('/contacts')
@login_required
def contacts():
    """Contacts management page"""
    org_filter = get_organization_filter(current_user)
    contacts = Contact.query.filter_by(**org_filter).all()
    return render_template('contacts.html', contacts=contacts)

@main_bp.route('/contacts/add', methods=['GET', 'POST'])
@login_required
def add_contact():
    """Add new contact"""
    if request.method == 'POST':
        try:
            # Get organization filter for accounts
            org_filter = get_organization_filter(current_user)
            
            # Get or create a default account for this organization
            account = Account.query.filter_by(**org_filter).first()
            if not account:
                # Create a default account
                account = Account(
                    company_name="Default Company",
                    created_by=current_user.id
                )
                # Set organization data
                account = set_organization_data(account, current_user)
                db.session.add(account)
                db.session.commit()  # Commit to get the ID
            
            # Create the contact
            contact = Contact(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                email=request.form['email'],
                phone=request.form.get('phone'),
                title=request.form.get('job_title'),  # Map job_title to title
                account_id=account.id,  # Use the account's ID directly
                created_by=current_user.id
            )
            # Set organization data
            contact = set_organization_data(contact, current_user)
            db.session.add(contact)
            db.session.commit()
            flash('Contact added successfully!', 'success')
            return redirect(url_for('main.contacts'))
        except Exception as e:
            flash(f'Error adding contact: {str(e)}', 'error')
            db.session.rollback()
    
    # Get accounts for this organization
    org_filter = get_organization_filter(current_user)
    accounts = Account.query.filter_by(**org_filter).all()
    return render_template('add_contact.html', accounts=accounts)

@main_bp.route('/contacts/edit/<contact_id>', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    """Edit existing contact"""
    # Find the contact using organization filter
    org_filter = get_organization_filter(current_user)
    contact = Contact.query.filter_by(id=contact_id, **org_filter).first()
    if not contact:
        flash('Contact not found or access denied', 'error')
        return redirect(url_for('main.contacts'))
    
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            title = request.form.get('title')
            notes = request.form.get('notes')
            account_id = request.form.get('account_id')
            training_received = request.form.get('training_received')
            last_contact_date = request.form.get('last_contact')
            
            # Validate required fields
            if not first_name or not last_name or not email:
                flash('First name, last name, and email are required', 'error')
                accounts = Account.query.filter_by(**org_filter).all()
                return render_template('edit_contact.html', contact=contact, accounts=accounts)
            
            # Validate account if provided
            if account_id:
                account = Account.query.filter_by(id=account_id, **org_filter).first()
                if not account:
                    flash('Invalid account selected', 'error')
                    accounts = Account.query.filter_by(**org_filter).all()
                    return render_template('edit_contact.html', contact=contact, accounts=accounts)
            
            # Update the contact fields
            contact.first_name = first_name.strip()
            contact.last_name = last_name.strip()
            contact.email = email.strip()
            contact.phone = phone.strip() if phone else None
            contact.title = title.strip() if title else None
            contact.notes = notes.strip() if notes else None
            if account_id:
                contact.account_id = account_id
            contact.training_received = training_received.strip() if training_received else None
            
            # Handle last contact date
            if last_contact_date:
                try:
                    from datetime import datetime
                    contact.last_contact = datetime.strptime(last_contact_date, '%Y-%m-%d').date()
                except ValueError:
                    contact.last_contact = None
            
            db.session.commit()
            flash('Contact updated successfully!', 'success')
            return redirect(url_for('main.contacts'))
            
        except Exception as e:
            flash(f'Error updating contact: {str(e)}', 'error')
            db.session.rollback()
    
    # GET request - show the edit form
    accounts = Account.query.filter_by(**org_filter).all()
    return render_template('edit_contact.html', contact=contact, accounts=accounts)

@main_bp.route('/opportunities')
@login_required
def opportunities():
    """Opportunities management page"""
    org_filter = get_organization_filter(current_user)
    opportunities = Opportunity.query.filter_by(**org_filter).options(
        db.joinedload(Opportunity.account)
    ).all()
    return render_template('opportunities.html', opportunities=opportunities)

@main_bp.route('/opportunities/add', methods=['GET', 'POST'])
@login_required
def add_opportunity():
    """Add new opportunity"""
    if request.method == 'POST':
        try:
            # Get organization filter
            org_filter = get_organization_filter(current_user)
            
            # Get or create a default account for this organization
            account = Account.query.filter_by(**org_filter).first()
            if not account:
                account = Account(
                    company_name="Default Company",
                    created_by=current_user.id
                )
                account = set_organization_data(account, current_user)
                db.session.add(account)
                db.session.commit()
            
            # Get or create a default contact for the account
            contact = Contact.query.filter_by(account_id=account.id, **org_filter).first()
            if not contact:
                contact = Contact(
                    first_name="Default",
                    last_name="Contact",
                    email="default@example.com",
                    account_id=account.id,
                    created_by=current_user.id
                )
                contact = set_organization_data(contact, current_user)
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
            opportunity = set_organization_data(opportunity, current_user)
            db.session.add(opportunity)
            db.session.commit()
            flash('Opportunity added successfully!', 'success')
            return redirect(url_for('main.opportunities'))
        except Exception as e:
            flash(f'Error adding opportunity: {str(e)}', 'error')
            db.session.rollback()
    
    # Get accounts and contacts for this organization
    org_filter = get_organization_filter(current_user)
    accounts = Account.query.filter_by(**org_filter).all()
    contacts = Contact.query.filter_by(**org_filter).all()
    return render_template('add_opportunity.html', accounts=accounts, contacts=contacts)

@main_bp.route('/opportunities/edit/<opportunity_id>', methods=['GET', 'POST'])
@login_required
def edit_opportunity(opportunity_id):
    """Edit an existing opportunity"""
    # Find the opportunity using organization filter
    org_filter = get_organization_filter(current_user)
    opportunity = Opportunity.query.filter_by(id=opportunity_id, **org_filter).first()
    if not opportunity:
        flash('Opportunity not found or access denied', 'error')
        return redirect(url_for('main.opportunities'))
    
    if request.method == 'GET':
        # Get accounts and contacts for this organization for dropdowns
        accounts = Account.query.filter_by(**org_filter).all()
        contacts = Contact.query.filter_by(**org_filter).all()
        return render_template('edit_opportunity.html', opportunity=opportunity, accounts=accounts, contacts=contacts)
    
    # Handle POST request (form submission)
    try:
        # Get all form fields
        name = request.form.get('name')
        sales_stage = request.form.get('sales_stage')
        forecast = request.form.get('forecast')
        company_id = request.form.get('company_id')
        contact_id = request.form.get('contact_id')
        requirements = request.form.get('requirements')
        close_date_str = request.form.get('close_date')
        next_steps = request.form.get('next_steps')
        
        # Validate required fields
        if not name or not sales_stage:
            flash('Please fill in all required fields (Name and Sales Stage)', 'error')
            accounts = Account.query.filter_by(**org_filter).all()
            contacts = Contact.query.filter_by(**org_filter).all()
            return render_template('edit_opportunity.html', opportunity=opportunity, accounts=accounts, contacts=contacts)
        
        # Parse close date
        close_date = None
        if close_date_str:
            try:
                from datetime import datetime
                close_date = datetime.strptime(close_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'error')
                accounts = Account.query.filter_by(**org_filter).all()
                contacts = Contact.query.filter_by(**org_filter).all()
                return render_template('edit_opportunity.html', opportunity=opportunity, accounts=accounts, contacts=contacts)
        
        # Update the opportunity fields
        opportunity.name = name.strip()
        opportunity.sales_stage = sales_stage
        opportunity.forecast = forecast.strip() if forecast else '50%'
        opportunity.company_id = company_id if company_id else opportunity.company_id
        opportunity.contact_id = contact_id if contact_id else opportunity.contact_id
        opportunity.requirements = requirements.strip() if requirements else None
        opportunity.close_date = close_date
        opportunity.next_steps = next_steps.strip() if next_steps else None
        
        db.session.commit()
        flash('Opportunity updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating opportunity: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.opportunities'))

@main_bp.route('/leads/export')
@login_required
def export_leads():
    """Export leads to CSV"""
    org_filter = get_organization_filter(current_user)
    leads = Lead.query.filter_by(**org_filter).all()
    
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
    org_filter = get_organization_filter(current_user)
    lead = Lead.query.filter_by(id=lead_id, **org_filter).first()
    if not lead:
        flash("Lead not found or access denied.", "error")
        return redirect(url_for("main.leads"))
    if lead.is_converted:
        flash("Lead already converted.", "info")
        return redirect(url_for("main.leads"))
    try:
        # Create account
        account = Account(
            company_name=lead.company_name, 
            description=f"Converted from lead: {lead.company_name}", 
            notes=lead.notes,
            created_by=current_user.id
        )
        account = set_organization_data(account, current_user)
        db.session.add(account)
        db.session.flush()
        
        # Create contact
        name_parts = lead.contact_person.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        contact = Contact(
            first_name=first_name, 
            last_name=last_name, 
            email=lead.email, 
            phone=lead.phone,
            account_id=account.id, 
            last_contact=date.today(),
            created_by=current_user.id
        )
        contact = set_organization_data(contact, current_user)
        db.session.add(contact)
        db.session.flush()
        
        # Create opportunity
        opportunity = Opportunity(
            name=f"Opportunity for {lead.company_name}", 
            sales_stage="Prospecting", 
            forecast="0%", 
            company_id=account.id, 
            contact_id=contact.id, 
            next_steps=f"Follow up on converted lead from {lead.stage} stage", 
            requirements=f"Converted from lead: {lead.notes or 'No specific requirements noted.'}",
            created_by=current_user.id
        )
        opportunity = set_organization_data(opportunity, current_user)
        db.session.add(opportunity)
        
        lead.is_converted = True
        db.session.commit()
        flash(f"Lead '{lead.contact_person}' successfully converted to Account, Contact, and Opportunity!", "success")
        # Redirect to opportunities page as specified in conversion logic
        return redirect(url_for("main.opportunities"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error converting lead: {str(e)}", "error")
    return redirect(url_for("main.leads"))

@main_bp.route('/admin/migrate-database', methods=['POST'])
def migrate_database():
    """Emergency migration endpoint - DISABLED for security"""
    return jsonify({'error': 'Migration endpoint disabled for security'}), 403
