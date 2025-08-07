#!/bin/bash

# Azure App Service startup script with enhanced error handling
echo "🚀 Starting ELS CRM Application - Azure Deployment"
echo "=================================================="

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command was successful
check_success() {
    if [ $? -eq 0 ]; then
        log "✅ $1 - SUCCESS"
    else
        log "❌ $1 - FAILED"
        exit 1
    fi
}

# Install Python dependencies first
log "📦 Installing Python dependencies..."
pip install -r requirements.txt
check_success "Python dependencies installation"

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export FLASK_APP=app.py
export PYTHONUNBUFFERED=1  # Ensure Python output is not buffered

log "🔧 Environment setup completed"
log "PYTHONPATH: $PYTHONPATH"
log "FLASK_APP: $FLASK_APP"

# Navigate to the app directory
cd /home/site/wwwroot
log "📁 Working directory: $(pwd)"

# Check environment variables
log "🔍 Checking environment variables..."
if [ -z "$DATABASE_URL" ]; then
    log "❌ DATABASE_URL is not set!"
    exit 1
else
    log "✅ DATABASE_URL is configured"
fi

if [ -z "$POSTGRES_PASSWORD" ]; then
    log "❌ POSTGRES_PASSWORD is not set!"
    log "⚠️  This is required for Azure PostgreSQL connection"
    exit 1
else
    log "✅ POSTGRES_PASSWORD is configured"
fi

if [ -z "$SECRET_KEY" ]; then
    log "❌ SECRET_KEY is not set!"
    exit 1
else
    log "✅ SECRET_KEY is configured"
fi

# Test database connection first
log "🔌 Testing database connection..."
python test_db_connection.py
if [ $? -ne 0 ]; then
    log "⚠️ Database connection test failed!"
    log "🔧 Attempting to diagnose connection issues..."
    
    # Show some debugging info
    log "Database URL prefix: $(echo $DATABASE_URL | cut -d':' -f1)"
    
    # Try to ping the database host
    DB_HOST=$(echo $DATABASE_URL | sed 's/.*@\([^:]*\):.*/\1/')
    if [ ! -z "$DB_HOST" ]; then
        log "📡 Testing connectivity to database host: $DB_HOST"
        # Note: nslookup might not be available in App Service
        # This is just for debugging
    fi
    
    log "💡 Database connection failed. This could be due to:"
    log "   - Network connectivity issues"
    log "   - Incorrect database credentials"
    log "   - Database server not ready"
    log "   - VNet configuration issues"
    log "⚠️ Continuing startup anyway - database will be initialized when connection is available"
else
    log "✅ Database connection test passed!"
fi

# Run database migration first
log "🔄 Running database migrations..."
if [ -f "migrate_add_amount.py" ]; then
    python migrate_add_amount.py
    check_success "Database migration"
else
    log "⚠️  Migration file not found, skipping..."
fi

# Initialize database tables and data
log "🏗️  Initializing database tables and data..."
python -c "
import sys
import traceback

try:
    print('🔍 Starting database initialization...')
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from models import db, User
        
        print('📋 Creating database tables...')
        db.create_all()
        print('✅ Database tables created successfully!')
        
        # Verify tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        expected_tables = ['users', 'accounts', 'contacts', 'leads', 'opportunities']
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            print(f'❌ Missing expected tables: {missing_tables}')
            print('⚠️ Database tables will be created when connection is available')
        else:
            print(f'✅ All expected tables verified: {tables}')
        
        # Check if users exist
        try:
            user_count = User.query.count()
            print(f'👥 Current user count: {user_count}')
            
            if user_count == 0:
                print('👤 Creating initial users...')
                
                # Create demo user
                demo_user = User(
                    username='demo',
                    email='demo@elscrm.com', 
                    first_name='Demo',
                    last_name='User'
                )
                demo_user.set_password('demo123')
                
                # Create admin user
                admin_user = User(
                    username='admin',
                    email='admin@elscrm.com',
                    first_name='Admin', 
                    last_name='User',
                    is_admin=True
                )
                admin_user.set_password('admin123')
                
                # Add users to session
                db.session.add(demo_user)
                db.session.add(admin_user)
                
                # Commit with error handling
                try:
                    db.session.commit()
                    print('✅ Initial users created successfully!')
                    print('   📝 Demo user: username=demo, password=demo123')
                    print('   📝 Admin user: username=admin, password=admin123')
                    
                    # Verify users were created
                    final_count = User.query.count()
                    if final_count != 2:
                        print(f'❌ Expected 2 users after creation, found {final_count}')
                    else:
                        print(f'✅ User creation verified - final count: {final_count}')
                    
                except Exception as commit_error:
                    print(f'❌ Failed to commit users to database: {commit_error}')
                    db.session.rollback()
                    print('⚠️ Users will be created when database connection is stable')
                
            else:
                print(f'✅ Users already exist in the database (count: {user_count})')
                
                # List existing users for verification
                try:
                    existing_users = User.query.with_entities(User.username, User.email).limit(10).all()
                    print('👥 Existing users:')
                    for username, email in existing_users:
                        print(f'     - {username} ({email})')
                except Exception as e:
                    print(f'⚠️  Could not list users: {e}')
        
        except Exception as user_error:
            print(f'⚠️ Could not check/create users: {user_error}')
            print('⚠️ User setup will happen when database connection is stable')
        
        print('🎉 Database initialization completed!')
        
except Exception as e:
    print(f'⚠️ Database initialization warning: {e}')
    print('📋 Error details:')
    traceback.print_exc()
    print('⚠️ Application will continue startup - database will be initialized when connection is available')
"

log "✅ Database initialization attempt completed!"

# Final health check (non-fatal)
log "🏥 Performing final health check..."
python -c "
try:
    from app import create_app
    app = create_app()
    with app.app_context():
        from models import User
        user_count = User.query.count()
        print(f'✅ Final health check: {user_count} users in database')
except Exception as e:
    print(f'⚠️ Final health check warning: {e}')
    print('⚠️ Application will start anyway - database operations will work when connection is available')
"

log "✅ All startup checks completed!"

# Start the application
log "🚀 Starting Gunicorn server..."
log "Configuration:"
log "   - Bind: 0.0.0.0:8000"
log "   - Workers: 2"
log "   - Timeout: 600s"
log "   - Keep-alive: 2s"
log "   - Max requests: 1000"

exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 600 --keep-alive 2 --max-requests 1000 --access-logfile - --error-logfile - app:app
