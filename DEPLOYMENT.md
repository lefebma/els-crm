# ELS CRM Deployment Guide

This guide provides step-by-step instructions for deploying the ELS CRM application to Azure using Azure Developer CLI (azd).

## Prerequisites

Before starting the deployment process, ensure you have:

1. **Azure Subscription**: An active Azure subscription with appropriate permissions
2. **Azure CLI**: Installed and configured on your machine
3. **Azure Developer CLI (azd)**: Latest version installed
4. **Git**: For source code management
5. **Local Environment**: The application running successfully locally

## Pre-Deployment Checklist

### 1. Verify Local Environment

```bash
# Test the application locally
cd "/Users/marclefebvre/Projects/ELS CRM"
python app.py

# Run tests
python -m unittest test_app -v

# Verify database initialization
python -c "from app import app; from database import db; app.app_context().push(); db.create_all()"
```

### 2. Update Environment Configuration

Ensure your `.env` file has a strong secret key for production:

```bash
# Generate a strong secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Update `.env`:
```
SECRET_KEY=your-generated-strong-secret-key-here
```

### 3. Verify Azure Configuration Files

Check that all Azure configuration files are in place:

- `azure.yaml` - Azure Developer CLI configuration
- `infra/main.bicep` - Main infrastructure template
- `infra/core/` - Reusable Bicep modules
- `startup.sh` - Azure App Service startup script

## Deployment Steps

### Step 1: Install Azure Developer CLI

**macOS:**
```bash
brew install azd
```

**Windows:**
```bash
winget install Microsoft.AzureDeveloperCLI
```

**Linux:**
```bash
curl -fsSL https://aka.ms/install-azd.sh | bash
```

### Step 2: Authenticate with Azure

```bash
# Login to Azure CLI
az login

# Login to Azure Developer CLI
azd auth login

# Verify authentication
az account show
```

### Step 3: Initialize Azure Environment

```bash
# Navigate to project directory
cd "/Users/marclefebvre/Projects/ELS CRM"

# Initialize azd environment
azd init

# Follow the prompts:
# - Choose "Use code in the current directory"
# - Select your Azure subscription
# - Choose a region (e.g., East US, West US 2, Canada Central)
# - Provide an environment name (e.g., "els-crm-prod")
```

### Step 4: Configure Environment Variables

```bash
# Set required environment variables
azd env set SECRET_KEY "your-generated-strong-secret-key-here"
azd env set FLASK_ENV "production"

# Optional: Set database administrator credentials
azd env set DB_ADMIN_USERNAME "crm_admin"
azd env set DB_ADMIN_PASSWORD "YourSecurePassword123!"
```

### Step 5: Deploy Infrastructure and Application

```bash
# Deploy everything in one command
azd up

# This will:
# 1. Create Azure Resource Group
# 2. Deploy PostgreSQL Flexible Server
# 3. Create Azure App Service and App Service Plan
# 4. Set up Azure Key Vault
# 5. Configure Managed Identity
# 6. Deploy the application code
# 7. Configure environment variables
```

The deployment process typically takes 10-15 minutes.

### Step 6: Verify Deployment

1. **Check Deployment Status:**
   ```bash
   azd show
   ```

2. **Access Your Application:**
   The deployment will output the application URL. Open it in your browser.

3. **Monitor Logs:**
   ```bash
   # View application logs
   azd logs

   # Or access logs through Azure Portal
   ```

## Post-Deployment Configuration

### 1. Initialize Database

If the database needs to be initialized manually:

```bash
# Access the Azure App Service SSH console or use Azure CLI
az webapp ssh --resource-group <resource-group-name> --name <app-service-name>

# Inside the container, run:
python -c "from app import app; from database import db; app.app_context().push(); db.create_all()"
```

### 2. Create Initial Admin User

You can create an admin user through the web interface at:
`https://your-app-url.azurewebsites.net/auth/register`

### 3. Configure Custom Domain (Optional)

```bash
# Add custom domain
az webapp config hostname add \
  --resource-group <resource-group-name> \
  --webapp-name <app-service-name> \
  --hostname yourdomain.com

# Configure SSL certificate
az webapp config ssl bind \
  --resource-group <resource-group-name> \
  --name <app-service-name> \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

## Monitoring and Maintenance

### Application Insights

The deployment includes Application Insights for monitoring:

1. **Access Application Insights:**
   - Go to Azure Portal
   - Navigate to your Resource Group
   - Open Application Insights resource

2. **Key Metrics to Monitor:**
   - Request rate and response times
   - Failure rate and exceptions
   - Database connection health
   - User activity and sessions

### Database Maintenance

```bash
# Connect to PostgreSQL database
az postgres flexible-server connect \
  --name <postgres-server-name> \
  --admin-user <admin-username> \
  --database-name crm

# Create database backups
az postgres flexible-server backup list \
  --resource-group <resource-group-name> \
  --name <postgres-server-name>
```

### Application Updates

To deploy application updates:

```bash
# Make your code changes locally
# Test thoroughly

# Deploy updates
azd deploy

# Or redeploy everything
azd up
```

## Scaling and Performance

### Scale App Service

```bash
# Scale up (increase VM size)
az appservice plan update \
  --resource-group <resource-group-name> \
  --name <app-service-plan-name> \
  --sku P1V2

# Scale out (increase instances)
az appservice plan update \
  --resource-group <resource-group-name> \
  --name <app-service-plan-name> \
  --number-of-workers 3
```

### Database Scaling

```bash
# Scale database compute
az postgres flexible-server update \
  --resource-group <resource-group-name> \
  --name <postgres-server-name> \
  --sku-name Standard_D2s_v3

# Scale database storage
az postgres flexible-server update \
  --resource-group <resource-group-name> \
  --name <postgres-server-name> \
  --storage-size 512
```

## Troubleshooting

### Common Issues

1. **Deployment Fails:**
   ```bash
   # Check deployment logs
   azd show
   
   # Check Azure Activity Log in Portal
   ```

2. **Application Won't Start:**
   ```bash
   # Check application logs
   azd logs
   
   # Check App Service logs in Azure Portal
   ```

3. **Database Connection Issues:**
   ```bash
   # Test database connectivity
   az postgres flexible-server connect \
     --name <postgres-server-name> \
     --admin-user <admin-username>
   ```

4. **Environment Variables Missing:**
   ```bash
   # List current environment variables
   azd env get-values
   
   # Set missing variables
   azd env set VARIABLE_NAME "value"
   azd deploy
   ```

### Debug Mode

To enable debug logging during deployment:

```bash
azd config set alpha.resourceGroupDeployments on
azd up --debug
```

## Security Considerations

### Production Hardening

1. **Update Default Passwords:**
   - Change database admin password
   - Ensure strong application secret key

2. **Network Security:**
   - Configure firewall rules for PostgreSQL
   - Enable HTTPS only for App Service
   - Consider VNet integration for enhanced security

3. **Key Vault Access:**
   - Review Key Vault access policies
   - Use Managed Identity for secure access
   - Regularly rotate secrets

4. **Monitoring:**
   - Enable Azure Security Center
   - Set up alerts for suspicious activities
   - Monitor database access logs

## Cost Optimization

### Resource Optimization

1. **Right-size Resources:**
   - Monitor usage and scale down if needed
   - Use reserved instances for production
   - Consider development/staging environments with smaller SKUs

2. **Database Optimization:**
   - Use Burstable SKUs for development
   - Enable automated backups with appropriate retention
   - Monitor storage usage and optimize as needed

## Backup and Disaster Recovery

### Automated Backups

PostgreSQL Flexible Server provides automated backups:

```bash
# List available backups
az postgres flexible-server backup list \
  --resource-group <resource-group-name> \
  --name <postgres-server-name>

# Restore from backup
az postgres flexible-server restore \
  --resource-group <resource-group-name> \
  --name <new-server-name> \
  --source-server <source-server-name> \
  --restore-time "2024-01-01T00:00:00Z"
```

### Application Code Backup

- Source code is backed up in your Git repository
- Consider multiple Git remotes for redundancy
- Tag releases for easy rollback

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly:**
   - Review application logs
   - Check performance metrics
   - Monitor database health

2. **Monthly:**
   - Review security updates
   - Analyze cost reports
   - Update dependencies if needed

3. **Quarterly:**
   - Review scaling requirements
   - Update backup strategies
   - Conduct security assessments

### Getting Help

1. **Azure Support:**
   - Create support tickets through Azure Portal
   - Use Azure Community forums

2. **Application Issues:**
   - Check application logs
   - Review code repository issues
   - Contact development team

This deployment guide should help you successfully deploy and maintain your ELS CRM application on Azure.
