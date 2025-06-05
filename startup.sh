#!/bin/bash

echo "Starting ELS CRM application..."

# Create instance directory for SQLite database (for local development)
mkdir -p instance

# Use python3 command which is available in Azure App Service
PYTHON_CMD="python3"

# Check if python3 exists, fallback to python
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Using Python command: $PYTHON_CMD"

# Install dependencies
echo "Installing Python dependencies..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

# Test database connection and initialize
echo "Testing database connection..."
$PYTHON_CMD -c "
try:
    from app import create_app
    app = create_app()
    with app.app_context():
        print('✅ Database connection and initialization complete!')
except Exception as e:
    print(f'⚠️ Database initialization warning: {e}')
    print('Application will continue startup...')
"

# Start the Flask application with gunicorn for production
echo "Starting Flask application with Gunicorn..."
exec $PYTHON_CMD -m gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 600 --preload app:app
