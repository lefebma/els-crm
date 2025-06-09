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

    # Initialize extensions
    from database import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

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
            
            # Check if demo user exists, if not create it
            demo_user = User.query.filter_by(username='demo').first()
            if not demo_user:
                print("Creating demo user...")
                demo_user = User(
                    username='demo',
                    email='demo@elscrm.com',
                    first_name='Demo',
                    last_name='User',
                    password_hash=generate_password_hash('demo123')
                )
                db.session.add(demo_user)
                db.session.commit()
                print("Demo user created: username=demo, password=demo123")
            else:
                print("Demo user already exists")
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Don't fail startup, just log the error
            import traceback
            traceback.print_exc()

# Initialize database on startup
init_database()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
