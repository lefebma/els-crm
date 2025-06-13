#!/bin/bash

# Azure App Service startup script
echo "Starting ELS CRM application..."

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export FLASK_APP=app.py

# Navigate to the app directory
cd /home/site/wwwroot

# Initialize the database
echo "Initializing database..."
python -c "
try:
    from app import app
    with app.app_context():
        from models import db, User
        db.create_all()
        
        # Check if users exist
        user_count = User.query.count()
        print(f'User count: {user_count}')
        
        if user_count == 0:
            print('Creating initial users...')
            demo_user = User(
                username='demo',
                email='demo@elscrm.com', 
                first_name='Demo',
                last_name='User'
            )
            demo_user.set_password('demo123')
            
            admin_user = User(
                username='admin',
                email='admin@elscrm.com',
                first_name='Admin', 
                last_name='User',
                is_admin=True
            )
            admin_user.set_password('admin123')
            
            db.session.add(demo_user)
            db.session.add(admin_user)
            db.session.commit()
            print('Initial users created successfully')
        else:
            print('Users already exist')
            
except Exception as e:
    print(f'Database initialization error: {e}')
    import traceback
    traceback.print_exc()
"

echo "Database initialization completed"

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 600 --keep-alive 2 --max-requests 1000 app:app
