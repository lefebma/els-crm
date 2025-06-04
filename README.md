# ELS CRM Application

A comprehensive Customer Relationship Management (CRM) web application built with Flask, featuring lead management, account tracking, contact management, and opportunity tracking with Azure deployment readiness.

## Features

- **User Authentication**: Secure login/logout with Flask-Login
- **Lead Management**: Create, view, edit, and delete leads
- **Account Management**: Manage customer accounts with detailed information
- **Contact Management**: Track contacts associated with accounts
- **Opportunity Tracking**: Monitor sales opportunities and pipeline
- **Lead Conversion**: Convert leads to accounts, contacts, and opportunities
- **Responsive UI**: Modern interface built with Tailwind CSS
- **REST API**: Complete CRUD API endpoints for all entities

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
1. Clone the repository and navigate to the directory
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python -c "from app import app; from database import db; app.app_context().push(); db.create_all()"
   ```
5. Create sample data (optional):
   ```bash
   python create_sample_data.py
   ```
6. Run the application:
   ```bash
   python app.py
   ```
7. Access the application at `http://localhost:5001`

### Default Credentials (if using sample data)
- **Username**: admin
- **Password**: admin123

## Technology Stack
- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Authentication**: Flask-Login with password hashing
- **Testing**: pytest with Flask-Testing
- **Deployment**: Azure App Service with PostgreSQL