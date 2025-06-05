#!/bin/bash

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Start the Flask application with Gunicorn
gunicorn --bind=0.0.0.0 --timeout 600 app_simple_working:app
