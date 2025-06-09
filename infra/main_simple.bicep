targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// Optional parameters to override the default azd resource naming conventions
param resourceGroupName string = ''
param appServicePlanName string = ''
param appServiceName string = ''
param postgresServerName string = ''
param keyVaultName string = ''

@description('Id of the user or app to assign application roles')
param principalId string = ''

// Variables
var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName))
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// User-assigned managed identity for the app service
module userAssignedIdentity './core/security/userassignedidentity.bicep' = {
  name: 'user-assigned-identity'
  scope: rg
  params: {
    name: 'id-${resourceToken}'
    location: location
    tags: tags
  }
}

// Create a variable for the PostgreSQL server name to reuse
var postgresServerName_calculated = !empty(postgresServerName) ? postgresServerName : '${abbrs.dBforPostgreSQLServers}${resourceToken}'

// Key Vault first (required for database password)
module keyVault './core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: rg
  params: {
    name: !empty(keyVaultName) ? keyVaultName : '${abbrs.keyVaultVaults}${resourceToken}'
    location: location
    tags: tags
    principalId: principalId
  }
}

// PostgreSQL Flexible Server (without VNet for now)
module postgresDb './core/database/postgresql/flexibleserver.bicep' = {
  name: 'postgres'
  scope: rg
  params: {
    name: postgresServerName_calculated
    location: location
    tags: tags
    sku: {
      name: 'Standard_B1ms'
      tier: 'Burstable'
    }
    storage: {
      storageSizeGB: 32
    }
    version: '14'
    administratorLogin: 'crmadmin'
    administratorLoginPassword: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=postgres-password)'
    databaseNames: ['crm']
    // Temporarily use public access until throttling resolves
    allowAzureIPsFirewall: true
  }
}

// The application frontend (using existing App Service Plan from different region)
module web './core/host/appservice.bicep' = {
  name: 'web'
  scope: rg
  params: {
    name: !empty(appServiceName) ? appServiceName : '${abbrs.webSitesAppService}web-${resourceToken}'
    location: 'westus2' // Use West US 2 to match existing plan
    tags: tags
    appServicePlanId: '/subscriptions/6a4278df-a5c6-489c-a298-77b3a82455f5/resourceGroups/rg-els-crm-simple/providers/Microsoft.Web/serverfarms/plan-els-crm'
    runtimeName: 'python'
    runtimeVersion: '3.11'
    managedIdentity: true
    userAssignedIdentityId: userAssignedIdentity.outputs.id
    serviceName: 'web'
    appSettings: {
      DATABASE_URL: 'postgresql://crmadmin@${postgresDb.outputs.fqdn}:5432/crm?sslmode=require'
      POSTGRES_PASSWORD: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=postgres-password)'
      SECRET_KEY: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=secret-key)'
      AZURE_KEY_VAULT_URL: keyVault.outputs.uri
      FLASK_ENV: 'production'
      FLASK_APP: 'app.py'
      SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
      ENABLE_ORYX_BUILD: 'true'
    }
  }
}

// App outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = rg.name
output RESOURCE_GROUP_ID string = rg.id

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = ''
output AZURE_CONTAINER_REGISTRY_NAME string = ''

output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = web.outputs.identityPrincipalId
output SERVICE_WEB_NAME string = web.outputs.name
output SERVICE_WEB_URI string = web.outputs.uri

output POSTGRES_SERVER_NAME string = postgresDb.outputs.name
output POSTGRES_DATABASE_NAME string = 'crm'

output KEY_VAULT_NAME string = keyVault.outputs.name
output KEY_VAULT_URI string = keyVault.outputs.uri

// Additional required outputs
output DATABASE_URL string = 'postgresql://crmadmin@${postgresDb.outputs.fqdn}:5432/crm?sslmode=require'
output SECRET_KEY string = '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=secret-key)'
