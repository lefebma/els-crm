"""
User management routes for sharing access
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import User, get_organization_filter, set_organization_data, create_organization_for_user
from database import db
import uuid

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/manage')
@login_required
def manage_users():
    """User management page"""
    # Only admins can access this page
    if not current_user.is_admin:
        flash('Access denied. Only administrators can manage users.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # If user doesn't have an organization, redirect to setup
    if not current_user.organization_id:
        return redirect(url_for('users.setup_organization'))
    
    # Get all users in the same organization
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    
    return render_template('users/manage.html', users=users)

@users_bp.route('/invite', methods=['GET', 'POST'])
@login_required
def invite_user():
    """Invite a new user to the organization"""
    if not current_user.is_admin:
        flash('Access denied. Only administrators can invite users.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            is_admin = request.form.get('is_admin') == 'on'
            
            # Validate required fields
            if not all([first_name, last_name, username, email, password]):
                flash('All fields are required', 'error')
                return render_template('users/invite.html')
            
            # Check if username or email already exists
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                flash('Username or email already exists', 'error')
                return render_template('users/invite.html')
            
            # Create organization for current user if they don't have one
            if not current_user.organization_id:
                create_organization_for_user(current_user)
                db.session.commit()
            
            # Create new user
            new_user = User(
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                username=username.strip(),
                email=email.strip(),
                organization_id=current_user.organization_id,
                is_admin=is_admin
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'User {username} has been invited successfully!', 'success')
            return redirect(url_for('users.manage_users'))
            
        except Exception as e:
            flash(f'Error inviting user: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('users/invite.html')

@users_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup_organization():
    """Set up organization for current user if they don't have one"""
    if current_user.organization_id:
        flash('You already belong to an organization', 'info')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        organization_name = request.form.get('organization_name', '').strip()
        if not organization_name:
            flash('Organization name is required', 'error')
            return render_template('users/setup.html')
        
        try:
            # Create organization for user and make them admin
            organization_id = create_organization_for_user(current_user)
            
            # Explicitly ensure admin status is set
            current_user.is_admin = True
            
            # Update all existing data to belong to this organization
            from models import Lead, Account, Contact, Opportunity
            
            # Update leads
            Lead.query.filter_by(created_by=current_user.id).update({
                'organization_id': organization_id
            })
            
            # Update accounts
            Account.query.filter_by(created_by=current_user.id).update({
                'organization_id': organization_id
            })
            
            # Update contacts
            Contact.query.filter_by(created_by=current_user.id).update({
                'organization_id': organization_id
            })
            
            # Update opportunities
            Opportunity.query.filter_by(created_by=current_user.id).update({
                'organization_id': organization_id
            })
            
            db.session.commit()
            
            flash('Organization setup complete! You are now the admin and can invite other users to share access to your data.', 'success')
            return redirect(url_for('users.manage_users'))
            
        except Exception as e:
            flash(f'Error setting up organization: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('users/setup.html')

@users_bp.route('/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_user(user_id):
    """Remove a user from the organization"""
    if not current_user.is_admin:
        flash('Access denied. Only administrators can remove users.', 'error')
        return redirect(url_for('users.manage_users'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Can't remove yourself
        if user.id == current_user.id:
            flash('You cannot remove yourself from the organization', 'error')
            return redirect(url_for('users.manage_users'))
        
        # Verify user belongs to same organization
        if user.organization_id != current_user.organization_id:
            flash('User not found in your organization', 'error')
            return redirect(url_for('users.manage_users'))
        
        # Remove user from organization (don't delete user, just remove access)
        user.organization_id = None
        user.is_admin = False
        
        db.session.commit()
        
        flash(f'User {user.username} has been removed from the organization', 'success')
        
    except Exception as e:
        flash(f'Error removing user: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('users.manage_users'))

@users_bp.route('/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    if not current_user.is_admin:
        flash('Access denied. Only administrators can modify user permissions.', 'error')
        return redirect(url_for('users.manage_users'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Can't modify yourself
        if user.id == current_user.id:
            flash('You cannot modify your own admin status', 'error')
            return redirect(url_for('users.manage_users'))
        
        # Verify user belongs to same organization
        if user.organization_id != current_user.organization_id:
            flash('User not found in your organization', 'error')
            return redirect(url_for('users.manage_users'))
        
        # Toggle admin status
        user.is_admin = not user.is_admin
        
        db.session.commit()
        
        status = "granted" if user.is_admin else "revoked"
        flash(f'Admin access {status} for {user.username}', 'success')
        
    except Exception as e:
        flash(f'Error updating user permissions: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('users.manage_users'))
