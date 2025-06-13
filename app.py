from flask import Flask
import os
from werkzeug.security import generate_password_hash

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'azure-production-secret-2025')
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for local development
    # Use PostgreSQL from environment or fall back to SQLite for local development
    default_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'crm.db')
    database_url = os.getenv('DATABASE_URL', f'sqlite:///{default_db_path}')
    
    # Handle PostgreSQL URL configuration for Azure
    if database_url.startswith('postgresql://'):
        # For Azure PostgreSQL, we need to inject the password from Key Vault
        postgres_password = os.getenv('POSTGRES_PASSWORD')
        if postgres_password:
            # Parse the URL to inject the password
            # Format: postgresql://username@host:port/database?params
            # Target: postgresql://username:password@host:port/database?params
            if '@' in database_url and ':' not in database_url.split('@')[0].split('//')[-1]:
                # Split at @ and inject password before @
                parts = database_url.split('@')
                username_part = parts[0]  # postgresql://username
                host_part = '@'.join(parts[1:])  # host:port/database?params
                database_url = f"{username_part}:{postgres_password}@{host_part}"
        
        # Azure PostgreSQL requires SSL
        if '?sslmode=' not in database_url:
            database_url += '?sslmode=require'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require'
        } if database_url.startswith('postgresql://') else {}
    }

    print(f"Database URL: {database_url[:50]}..." if len(database_url) > 50 else f"Database URL: {database_url}")
    print(f"POSTGRES_PASSWORD environment variable: {'Present' if os.getenv('POSTGRES_PASSWORD') else 'Missing'}")
    if database_url.startswith('postgresql://'):
        print(f"PostgreSQL URL detected - Password injection: {'Applied' if postgres_password else 'Skipped'}")

    # Initialize extensions
    from database import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            print(f"Error loading user {user_id}: {e}")
            return None

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.api import api_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/users')

    # Error handlers
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return "Internal server error. Please try again later.", 500
    
    @app.errorhandler(404)
    def not_found_error(error):
        return "Page not found.", 404

    return app

# Initialize Flask app
app = create_app()

# Create tables and initialize data on startup
def init_database():
    """Initialize database tables and create demo user if needed"""
    with app.app_context():
        try:
            from models import db, User
            
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Check if any users exist
            user_count = User.query.count()
            print(f"Current user count: {user_count}")
            
            # Create demo user if no users exist
            if user_count == 0:
                print("No users found, creating demo and admin users...")
                
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
                
                db.session.add(demo_user)
                db.session.add(admin_user)
                db.session.commit()
                print("Demo and admin users created successfully")
                print("Demo user: username=demo, password=demo123")
                print("Admin user: username=admin, password=admin123")
            else:
                print("Users already exist in database")
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Don't fail startup, just log the error
            import traceback
            traceback.print_exc()

# Initialize database on startup
init_database()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
