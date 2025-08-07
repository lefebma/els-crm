#!/usr/bin/env python3
"""
Production debugging script for Azure deployment
Helps identify common issues with PostgreSQL connectivity and configuration
"""

import os
import sys
import traceback
from datetime import datetime

def print_separator(title):
    """Print a nice separator with title"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def debug_environment():
    """Debug environment variables and configuration"""
    print_separator("ENVIRONMENT CONFIGURATION")
    
    # Check critical environment variables
    env_vars = [
        'DATABASE_URL',
        'POSTGRES_PASSWORD', 
        'SECRET_KEY',
        'FLASK_APP',
        'FLASK_ENV',
        'PYTHONPATH'
    ]
    
    print("📋 Environment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"   {var}: {'*' * 8} (hidden)")
            elif 'DATABASE_URL' in var:
                # Show database type and host without credentials
                if value.startswith('postgresql://'):
                    try:
                        host_part = value.split('@')[1].split('/')[0] if '@' in value else 'unknown'
                        print(f"   {var}: postgresql://***@{host_part}/***")
                    except:
                        print(f"   {var}: postgresql://*** (parse error)")
                else:
                    print(f"   {var}: {value}")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: ❌ NOT SET")
    
    # Check Python environment
    print(f"\n🐍 Python Environment:")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    print(f"   Working directory: {os.getcwd()}")
    print(f"   Current time: {datetime.now()}")

def debug_imports():
    """Debug Python imports"""
    print_separator("PYTHON IMPORTS")
    
    # Test critical imports
    imports_to_test = [
        ('flask', 'Flask'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_login', 'Flask-Login'),
        ('werkzeug.security', 'Werkzeug Security'),
        ('psycopg2', 'PostgreSQL adapter (psycopg2)'),
    ]
    
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"   ✅ {description}: Available")
        except ImportError as e:
            print(f"   ❌ {description}: Missing - {e}")
        except Exception as e:
            print(f"   ⚠️  {description}: Error - {e}")

def debug_database():
    """Debug database connection"""
    print_separator("DATABASE CONNECTION")
    
    try:
        # Test basic database URL parsing
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            return False
        
        print(f"Database type: {'PostgreSQL' if database_url.startswith('postgresql://') else 'SQLite'}")
        
        # Test SQLAlchemy engine creation
        from sqlalchemy import create_engine, text
        print("   Testing engine creation...")
        
        # Prepare connection arguments
        engine_kwargs = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
        
        if database_url.startswith('postgresql://'):
            # Inject password for PostgreSQL
            postgres_password = os.getenv('POSTGRES_PASSWORD')
            if postgres_password and '@' in database_url:
                parts = database_url.split('@')
                if ':' not in parts[0].split('//')[-1]:  # No password in URL
                    username_part = parts[0]
                    host_part = '@'.join(parts[1:])
                    database_url = f"{username_part}:{postgres_password}@{host_part}"
                    print("   ✅ Password injected into connection string")
            
            if '?sslmode=' not in database_url:
                database_url += '?sslmode=require'
                print("   ✅ SSL mode added to connection string")
            
            engine_kwargs['connect_args'] = {
                'sslmode': 'require',
                'connect_timeout': 10
            }
        
        # Create engine
        engine = create_engine(database_url, **engine_kwargs)
        print("   ✅ SQLAlchemy engine created")
        
        # Test connection
        print("   Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
            if test_value == 1:
                print("   ✅ Database connection successful!")
                
                # Get database info
                if database_url.startswith('postgresql://'):
                    try:
                        # Get PostgreSQL version
                        version_result = conn.execute(text("SELECT version()"))
                        version = version_result.scalar()
                        print(f"   📋 PostgreSQL version: {version[:60]}...")
                        
                        # Get current database
                        db_result = conn.execute(text("SELECT current_database()"))
                        current_db = db_result.scalar()
                        print(f"   📋 Current database: {current_db}")
                        
                        # Get current user
                        user_result = conn.execute(text("SELECT current_user"))
                        current_user = user_result.scalar()
                        print(f"   📋 Current user: {current_user}")
                        
                        # Test table listing
                        tables_result = conn.execute(text("""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public'
                            ORDER BY table_name
                        """))
                        tables = [row[0] for row in tables_result]
                        print(f"   📋 Existing tables: {tables}")
                        
                    except Exception as info_error:
                        print(f"   ⚠️  Could not get database info: {info_error}")
                else:
                    print("   ✅ SQLite connection successful")
                
                return True
            else:
                print(f"   ❌ Connection test failed - got {test_value}")
                return False
                
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        print(f"   📋 Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

def debug_flask_app():
    """Debug Flask application creation"""
    print_separator("FLASK APPLICATION")
    
    try:
        print("   Creating Flask app...")
        from app import create_app
        app = create_app()
        print("   ✅ Flask app created successfully")
        
        print(f"   App name: {app.name}")
        print(f"   Debug mode: {app.debug}")
        print(f"   Testing mode: {app.testing}")
        
        # Test app context
        with app.app_context():
            print("   ✅ App context working")
            
            # Test database initialization
            from models import db, User
            print("   ✅ Models imported successfully")
            
            # Test database operations
            print("   Testing database operations...")
            try:
                user_count = User.query.count()
                print(f"   ✅ Database query successful - {user_count} users")
                return True
            except Exception as db_error:
                print(f"   ❌ Database query failed: {db_error}")
                return False
                
    except Exception as e:
        print(f"   ❌ Flask app creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main debugging function"""
    print("🔍 ELS CRM Production Debugging Script")
    print(f"Started at: {datetime.now()}")
    
    # Run all debugging checks
    debug_environment()
    debug_imports()
    db_success = debug_database()
    flask_success = debug_flask_app()
    
    # Summary
    print_separator("SUMMARY")
    print(f"Database connection: {'✅ SUCCESS' if db_success else '❌ FAILED'}")
    print(f"Flask application: {'✅ SUCCESS' if flask_success else '❌ FAILED'}")
    
    overall_success = db_success and flask_success
    
    if overall_success:
        print("\n🎉 All checks passed! The application should work correctly.")
    else:
        print("\n💥 Some checks failed. Please review the errors above.")
        print("\nCommon solutions:")
        print("1. Check that POSTGRES_PASSWORD environment variable is set")
        print("2. Verify database server is accessible from this network")
        print("3. Confirm database user has proper permissions")
        print("4. Check VNet configuration if using private endpoints")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
