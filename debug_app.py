#!/usr/bin/env python3
"""
Debug version of the ELS CRM app to identify the login issue
"""
from flask import Flask, request, jsonify, render_template_string
import os
import traceback
from werkzeug.security import generate_password_hash, check_password_hash

# Simple HTML template for testing
SIMPLE_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Debug Login Test</title>
</head>
<body>
    <h1>Debug Login Test</h1>
    {% if error %}
        <div style="color: red; background: #ffe6e6; padding: 10px; margin: 10px 0;">
            <strong>Error:</strong> {{ error }}
        </div>
    {% endif %}
    {% if debug_info %}
        <div style="color: blue; background: #e6f3ff; padding: 10px; margin: 10px 0;">
            <strong>Debug Info:</strong><br>
            {% for info in debug_info %}
                {{ info }}<br>
            {% endfor %}
        </div>
    {% endif %}
    <form method="POST">
        <div>
            <label>Username:</label>
            <input type="text" name="username" value="demo" required>
        </div>
        <div>
            <label>Password:</label>
            <input type="password" name="password" value="demo123" required>
        </div>
        <div>
            <button type="submit">Login</button>
        </div>
    </form>
    
    <h2>Environment Check</h2>
    <ul>
        <li><strong>DATABASE_URL:</strong> {{ database_url[:50] }}...</li>
        <li><strong>POSTGRES_PASSWORD:</strong> {{ 'Present' if postgres_password else 'Missing' }}</li>
        <li><strong>SECRET_KEY:</strong> {{ 'Present' if secret_key else 'Missing' }}</li>
    </ul>
</body>
</html>
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'debug-secret-key')

# Get environment variables
database_url = os.getenv('DATABASE_URL', 'Not set')
postgres_password = os.getenv('POSTGRES_PASSWORD', '')
secret_key = os.getenv('SECRET_KEY', '')

@app.route('/', methods=['GET', 'POST'])
def login():
    debug_info = []
    error = None
    
    try:
        debug_info.append(f"Method: {request.method}")
        debug_info.append(f"Database URL: {database_url[:50]}...")
        debug_info.append(f"PostgreSQL password: {'Present' if postgres_password else 'Missing'}")
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            debug_info.append(f"Username: {username}")
            debug_info.append(f"Password length: {len(password) if password else 0}")
            
            # Test basic validation
            if not username or not password:
                error = "Username and password are required"
                return render_template_string(SIMPLE_LOGIN_TEMPLATE, 
                                            error=error, 
                                            debug_info=debug_info,
                                            database_url=database_url,
                                            postgres_password=bool(postgres_password),
                                            secret_key=bool(secret_key))
            
            # Test database connection
            try:
                debug_info.append("Testing database connection...")
                
                # Parse database URL
                if database_url.startswith('postgresql://'):
                    # Inject password if available
                    if postgres_password and '@' in database_url and ':' not in database_url.split('@')[0].split('//')[-1]:
                        parts = database_url.split('@')
                        username_part = parts[0]  # postgresql://username
                        host_part = '@'.join(parts[1:])  # host:port/database?params
                        final_db_url = f"{username_part}:{postgres_password}@{host_part}"
                        debug_info.append("Password injection applied")
                    else:
                        final_db_url = database_url
                        debug_info.append("No password injection needed or possible")
                    
                    debug_info.append(f"Final DB URL: {final_db_url[:50]}...")
                    
                    # Test connection with SQLAlchemy
                    try:
                        from sqlalchemy import create_engine, text
                        engine = create_engine(final_db_url, 
                                             connect_args={'sslmode': 'require'} if final_db_url.startswith('postgresql://') else {})
                        
                        with engine.connect() as conn:
                            result = conn.execute(text("SELECT 1"))
                            debug_info.append("Database connection successful!")
                            
                            # Test if users table exists
                            try:
                                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                                count = result.scalar()
                                debug_info.append(f"Users table exists with {count} records")
                                
                                # Try to find demo user
                                result = conn.execute(text("SELECT username, password_hash FROM users WHERE username = 'demo'"))
                                user_row = result.fetchone()
                                if user_row:
                                    debug_info.append("Demo user found in database")
                                    
                                    # Test password check
                                    stored_hash = user_row[1]
                                    if check_password_hash(stored_hash, password):
                                        debug_info.append("Password verification successful!")
                                        return jsonify({"success": True, "message": "Login successful!", "debug": debug_info})
                                    else:
                                        error = "Invalid password"
                                        debug_info.append("Password verification failed")
                                else:
                                    error = "Demo user not found in database"
                                    debug_info.append("Demo user not found")
                                    
                            except Exception as table_error:
                                error = f"Users table error: {str(table_error)}"
                                debug_info.append(f"Users table error: {str(table_error)}")
                                
                    except Exception as db_error:
                        error = f"Database connection failed: {str(db_error)}"
                        debug_info.append(f"Database connection error: {str(db_error)}")
                        
                else:
                    error = "Database URL is not PostgreSQL format"
                    debug_info.append("Database URL is not PostgreSQL format")
                    
            except Exception as conn_error:
                error = f"Connection test failed: {str(conn_error)}"
                debug_info.append(f"Connection test error: {str(conn_error)}")
                debug_info.append(f"Traceback: {traceback.format_exc()}")
                
    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        debug_info.append(f"Unexpected error: {str(e)}")
        debug_info.append(f"Traceback: {traceback.format_exc()}")
    
    return render_template_string(SIMPLE_LOGIN_TEMPLATE, 
                                error=error, 
                                debug_info=debug_info,
                                database_url=database_url,
                                postgres_password=bool(postgres_password),
                                secret_key=bool(secret_key))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
