#!/bin/bash

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Initialize database
python -c "
from app import app
from database import db
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')
"

# Start the application
PORT=${PORT:-8000}
exec gunicorn --bind=0.0.0.0:$PORT --timeout 600 --workers 1 app:app
