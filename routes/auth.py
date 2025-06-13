from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import User
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
            else:
                username = request.form.get('username')
                password = request.form.get('password')
            
            if not username or not password:
                if request.content_type == 'application/json':
                    return jsonify({'success': False, 'message': 'Username and password are required'}), 400
                flash('Username and password are required', 'error')
                return render_template('auth/login.html')
            
            # Add database error handling
            try:
                user = User.query.filter_by(username=username).first()
            except Exception as e:
                print(f"Database error during user lookup: {e}")
                if request.content_type == 'application/json':
                    return jsonify({'success': False, 'message': 'Database error occurred'}), 500
                flash('A database error occurred. Please try again.', 'error')
                return render_template('auth/login.html')
            
            if user and user.check_password(password):
                try:
                    login_user(user)
                    if request.content_type == 'application/json':
                        return jsonify({'success': True, 'message': 'Login successful'})
                    return redirect(url_for('main.dashboard'))
                except Exception as e:
                    print(f"Login error: {e}")
                    if request.content_type == 'application/json':
                        return jsonify({'success': False, 'message': 'Login failed'}), 500
                    flash('Login failed. Please try again.', 'error')
                    return render_template('auth/login.html')
            else:
                if request.content_type == 'application/json':
                    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
                flash('Invalid username or password', 'error')
        
        except Exception as e:
            print(f"Unexpected error in login route: {e}")
            if request.content_type == 'application/json':
                return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # Validation
        if not all([username, email, password, first_name, last_name]):
            message = 'All fields are required'
            if request.content_type == 'application/json':
                return jsonify({'success': False, 'message': message}), 400
            flash(message, 'error')
            return render_template('auth/register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            message = 'Username already exists'
            if request.content_type == 'application/json':
                return jsonify({'success': False, 'message': message}), 400
            flash(message, 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            message = 'Email already registered'
            if request.content_type == 'application/json':
                return jsonify({'success': False, 'message': message}), 400
            flash(message, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            message = 'Registration successful'
            if request.content_type == 'application/json':
                return jsonify({'success': True, 'message': message})
            flash(message, 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            import traceback
            traceback.print_exc()
            message = f'Registration failed: {str(e)}'
            if request.content_type == 'application/json':
                return jsonify({'success': False, 'message': message}), 500
            flash(message, 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
