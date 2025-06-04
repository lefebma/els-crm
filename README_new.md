# ELS CRM - Customer Relationship Management System

A comprehensive web-based CRM application built with Flask, featuring lead management, account tracking, contact management, and opportunity pipeline functionality. Ready for deployment to Azure with secure authentication and database integration.

## ✨ Features

- **User Authentication**: Secure login/logout with password hashing
- **Lead Management**: Track and qualify potential customers through different stages (MAL, MQL, SAL, SQL)
- **Lead Conversion**: Convert qualified leads into accounts, contacts, and opportunities
- **Account Management**: Manage customer company information and details
- **Contact Management**: Track individual contacts within accounts
- **Opportunity Pipeline**: Manage sales opportunities with stages and forecasting
- **Responsive Design**: Mobile-friendly interface using Tailwind CSS
- **REST API**: Complete API for all CRUD operations
- **Data Validation**: Input validation and error handling
- **Azure Ready**: Pre-configured for Azure App Service deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Azure CLI (for deployment)
- Azure Developer CLI (azd)

### Local Development

1. **Clone and Setup**
   ```bash
   cd "/path/to/your/project/directory"
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   # .env file is already configured for SQLite local development
   # Update SECRET_KEY for production
   ```

3. **Initialize Database**
   ```bash
   python -c "from app import app; from database import db; app.app_context().push(); db.create_all()"
   ```

4. **Create Sample Data** (Optional)
   ```bash
   python create_sample_data.py
   ```

5. **Run Application**
   ```bash
   python app.py
   # Access at http://localhost:5001
   ```

6. **Login with Sample Data**
   - Username: `admin`
   - Password: `admin123`

### Run Tests

```bash
python -m unittest test_app -v
```

## 🏗️ Architecture

### Frontend
- **Framework**: Flask with Jinja2 templates
- **Styling**: Tailwind CSS for responsive design
- **JavaScript**: Vanilla JS for interactive components
- **Components**: Modal forms, data tables, navigation

### Backend
- **Framework**: Flask with Blueprints for modular organization
- **Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (production)
- **Authentication**: Flask-Login with password hashing
- **Validation**: Custom validation framework
- **API**: RESTful endpoints for all operations

### Database Schema
- **Users**: Authentication and user management
- **Leads**: Prospect tracking with conversion capability
- **Accounts**: Customer company information
- **Contacts**: Individual contacts within accounts
- **Opportunities**: Sales pipeline and deal tracking

## 🔧 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Leads
- `GET /api/leads` - List all leads
- `POST /api/leads` - Create new lead
- `PUT /api/leads/<id>` - Update lead
- `POST /api/leads/<id>/convert` - Convert lead to account/contact/opportunity

### Accounts
- `GET /api/accounts` - List all accounts
- `POST /api/accounts` - Create new account
- `PUT /api/accounts/<id>` - Update account

### Contacts
- `GET /api/contacts` - List all contacts
- `POST /api/contacts` - Create new contact
- `PUT /api/contacts/<id>` - Update contact

### Opportunities
- `GET /api/opportunities` - List all opportunities
- `POST /api/opportunities` - Create new opportunity
- `PUT /api/opportunities/<id>` - Update opportunity

## 🚀 Azure Deployment

This application is configured for deployment to Azure using Azure Developer CLI (azd).

### Prerequisites for Deployment

1. **Install Azure Developer CLI**
   ```bash
   # macOS
   brew install azd
   
   # Windows
   winget install Microsoft.AzureDeveloperCLI
   ```

2. **Azure CLI Login**
   ```bash
   az login
   azd auth login
   ```

### Deployment Steps

1. **Initialize Azure Environment**
   ```bash
   azd init
   # Follow prompts to select subscription and region
   ```

2. **Deploy to Azure**
   ```bash
   azd up
   # This will:
   # - Create Azure resources (App Service, PostgreSQL, Key Vault)
   # - Deploy the application
   # - Configure environment variables
   ```

3. **Access Your Application**
   - The deployment will provide a URL to your live application
   - Default admin user will be created automatically

### Azure Resources Created

- **App Service**: Hosts the Flask application
- **PostgreSQL Flexible Server**: Production database
- **Key Vault**: Secure storage for secrets and connection strings
- **Managed Identity**: Secure authentication between services

### Environment Variables (Production)

The following environment variables are automatically configured in Azure:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Application secret key
- `AZURE_KEY_VAULT_URL`: Key Vault URL for secrets

### Database Migration to Production

When deploying to Azure, the application automatically:
- Creates all database tables
- Can optionally create sample data for testing

## 🔒 Security Features

- **Password Hashing**: Werkzeug security for password protection
- **Session Management**: Flask-Login for secure sessions
- **Input Validation**: Comprehensive data validation
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Azure Managed Identity**: Secure service-to-service authentication
- **Key Vault Integration**: Secure secrets management

## 📊 Data Model

### Lead Lifecycle
1. **MAL** (Marketing Accepted Lead) - Initial interest
2. **MQL** (Marketing Qualified Lead) - Meets qualification criteria
3. **SAL** (Sales Accepted Lead) - Sales team accepts for follow-up
4. **SQL** (Sales Qualified Lead) - Ready for conversion

### Conversion Process
- Lead → Account (Company information)
- Lead → Contact (Individual person)
- Lead → Opportunity (Sales opportunity)

## 🧪 Testing

The application includes comprehensive unit tests covering:
- User authentication and management
- Lead CRUD operations and conversion
- Account, Contact, and Opportunity management
- Data validation and error handling
- API endpoint functionality

Run tests with:
```bash
python -m unittest test_app -v
```

## 🔧 Development

### Project Structure
```
├── app.py                 # Main Flask application
├── database.py           # Database configuration
├── models.py             # SQLAlchemy models
├── validation.py         # Input validation utilities
├── requirements.txt      # Python dependencies
├── routes/               # Application routes
│   ├── auth.py          # Authentication routes
│   ├── main.py          # Main application routes
│   └── api.py           # REST API endpoints
├── templates/           # Jinja2 templates
├── infra/              # Azure infrastructure (Bicep)
└── test_app.py         # Unit tests
```

### Adding New Features

1. **Database Models**: Add to `models.py`
2. **API Endpoints**: Add to `routes/api.py`
3. **Web Pages**: Add templates and routes
4. **Validation**: Add to `validation.py`
5. **Tests**: Add to `test_app.py`

### Local Development Tips

- Use SQLite for local development (configured in .env)
- Enable debug mode for development
- Use sample data script for testing
- Run tests before committing changes

## 📦 Dependencies

### Core Dependencies
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Flask-Login**: Authentication
- **Flask-WTF**: Form handling and CSRF protection
- **Werkzeug**: Password hashing
- **psycopg2**: PostgreSQL adapter
- **python-dotenv**: Environment variable management

### Development Dependencies
- **Gunicorn**: Production WSGI server
- **Email-validator**: Email validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section below
2. Review Azure deployment logs
3. Check application logs in Azure App Service

### Troubleshooting

**Database Connection Issues:**
- Verify PostgreSQL server is running
- Check connection string in Key Vault
- Ensure firewall rules allow connections

**Authentication Problems:**
- Check secret key configuration
- Verify session configuration
- Clear browser cookies and cache

**Deployment Issues:**
- Check Azure CLI authentication
- Verify subscription permissions
- Review azd deployment logs

**Local Development:**
- Ensure all dependencies are installed
- Check .env file configuration
- Verify database is initialized
