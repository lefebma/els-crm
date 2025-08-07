#!/usr/bin/env python3
"""
Script to fix the DATABASE_URL in Azure App Service
"""
import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.web import WebSiteManagementClient

# Azure configuration
subscription_id = "6a4278df-a5c6-489c-a298-77b3a82455f5"
resource_group = "rg-ELS_CRM_VNET"
app_name = "appweb-goozh6ngfyubm"

# Database configuration
database_url = "postgresql://crmadmin:ozln5fh2vq45yAa1!@psqlgoozh6ngfyubm.postgres.database.azure.com:5432/crm?sslmode=require"

def update_app_settings():
    """Update the Azure App Service settings"""
    try:
        # Initialize the Azure client
        credential = DefaultAzureCredential()
        web_client = WebSiteManagementClient(credential, subscription_id)
        
        # Get current settings
        current_settings = web_client.web_apps.list_application_settings(
            resource_group, app_name
        )
        
        # Update the DATABASE_URL
        current_settings.properties['DATABASE_URL'] = database_url
        
        # Apply the settings
        result = web_client.web_apps.update_application_settings(
            resource_group, app_name, current_settings
        )
        
        print(f"✅ Successfully updated DATABASE_URL")
        print(f"New URL: {result.properties.get('DATABASE_URL', 'Not found')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating settings: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Updating Azure App Service DATABASE_URL...")
    success = update_app_settings()
    
    if success:
        print("✅ Settings updated successfully!")
        print("🔄 Please restart the app service to apply changes.")
    else:
        print("❌ Failed to update settings.") 