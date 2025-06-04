# ELS CRM - Python Flask Application

A comprehensive Customer Relationship Management (CRM) system built with Python Flask, designed for lead management, account tracking, contact management, and opportunity pipeline tracking.

## Features

- **User Authentication**: Secure login and registration system
- **Lead Management**: Track and convert marketing and sales leads
- **Account Management**: Manage company accounts with detailed information
- **Contact Management**: Maintain contact records linked to accounts
- **Opportunity Tracking**: Monitor sales opportunities through the pipeline
- **Lead Conversion**: Convert qualified leads into accounts, contacts, and opportunities
- **Modern UI**: Responsive design using Tailwind CSS

## Technology Stack

- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: HTML5, CSS3 (Tailwind), Vanilla JavaScript
- **Authentication**: Flask-Login
- **Deployment**: Azure App Service with PostgreSQL Flexible Server
- **Infrastructure**: Azure Bicep templates

## Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (for production)
- Azure CLI (for deployment)

### Local Development

1. **Clone and setup the environment:**
   ```bash
   git clone <repository-url>
   cd "ELS CRM"
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URL=sqlite:///crm.db
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

### Creating Your First User

1. Navigate to `/auth/register` to create a new user account
2. Fill in the required information
3. Login with your credentials
4. Start managing your CRM data!

## Application Structure

```
├── app.py                 # Main Flask application
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── routes/
│   ├── auth.py          # Authentication routes
│   ├── main.py          # Main application routes
│   └── api.py           # REST API endpoints
├── templates/
│   ├── base.html        # Base template
│   ├── dashboard.html   # Dashboard view
│   ├── leads.html       # Lead management
│   ├── accounts.html    # Account management
│   ├── contacts.html    # Contact management
│   ├── opportunities.html # Opportunity management
│   └── auth/            # Authentication templates
├── infra/               # Azure infrastructure files
│   ├── main.bicep       # Main Bicep template
│   └── core/            # Reusable Bicep modules
└── azure.yaml           # Azure Developer CLI configuration
```

## Database Schema

The application uses four main entities:

- **Users**: System users with authentication
- **Leads**: Potential customers in various qualification stages
- **Accounts**: Qualified companies/organizations
- **Contacts**: Individual people at accounts
- **Opportunities**: Sales deals in the pipeline

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Leads
- `GET /api/leads` - List all leads
- `POST /api/leads` - Create new lead
- `PUT /api/leads/{id}` - Update lead
- `POST /api/leads/{id}/convert` - Convert lead to account/contact/opportunity

### Accounts
- `GET /api/accounts` - List all accounts
- `POST /api/accounts` - Create new account
- `PUT /api/accounts/{id}` - Update account

### Contacts
- `GET /api/contacts` - List all contacts
- `POST /api/contacts` - Create new contact
- `PUT /api/contacts/{id}` - Update contact

### Opportunities
- `GET /api/opportunities` - List all opportunities
- `POST /api/opportunities` - Create new opportunity
- `PUT /api/opportunities/{id}` - Update opportunity

## Azure Deployment

### Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Azure Developer CLI](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)

### Deploy to Azure

1. **Login to Azure:**
   ```bash
   az login
   azd auth login
   ```

2. **Initialize the project:**
   ```bash
   azd init
   ```

3. **Deploy the application:**
   ```bash
   azd up
   ```

This will:
- Create an Azure Resource Group
- Deploy a PostgreSQL Flexible Server
- Create an Azure App Service
- Set up Azure Key Vault for secrets
- Configure networking and security
- Deploy your application code

### Infrastructure

The Azure deployment includes:

- **App Service**: Hosts the Flask application
- **PostgreSQL Flexible Server**: Production database
- **Key Vault**: Secure storage for connection strings and secrets
- **Managed Identity**: Secure authentication between services

## Security Features

- Password hashing using Werkzeug
- Session-based authentication with Flask-Login
- CSRF protection with Flask-WTF
- Secure headers and HTTPS enforcement
- Azure Key Vault integration for secrets
- Database connection encryption

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please create an issue in the repository or contact the development team.
