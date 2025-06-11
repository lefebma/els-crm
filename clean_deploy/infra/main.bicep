targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Name of the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// Optional parameters to override the default azd resource naming conventions
param appServicePlanName string = ''
param appServiceName string = ''
param postgresServerName string = ''
param keyVaultName string = ''

@description('Id of the user or app to assign application roles')
param principalId string = ''

// Variables
var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = uniqueString(subscription().id, resourceGroup().id, environmentName)
var tags = { 'azd-env-name': environmentName }

// User-assigned managed identity for the app service
module userAssignedIdentity './core/security/userassignedidentity.bicep' = {
  name: 'user-assigned-identity'
  params: {
    name: 'id-${resourceToken}'
    location: location
    tags: tags
  }
}

// Create a variable for the PostgreSQL server name to reuse
var postgresServerName_calculated = !empty(postgresServerName) ? postgresServerName : '${abbrs.dBforPostgreSQLServers}${resourceToken}'

// Virtual Network for secure networking
module vnet './core/network/virtualnetwork.bicep' = {
  name: 'vnet'
  params: {
    name: 'vnet-${resourceToken}'
    location: location
    tags: tags
  }
}

// Private DNS Zone for PostgreSQL Flexible Server
module privateDnsZone './core/network/privatednszone.bicep' = {
  name: 'private-dns-zone'
  params: {
    name: 'privatelink.postgres.database.azure.com'
    tags: tags
    virtualNetworkId: vnet.outputs.id
  }
}

// App Service Plan
module appServicePlan './core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  params: {
    name: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    location: location
    tags: tags
    sku: {
      name: 'B1'
      capacity: 1
    }
  }
}

// PostgreSQL Flexible Server
module postgresDb './core/database/postgresql/flexibleserver.bicep' = {
  name: 'postgres'
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
    // VNet integration for secure private access
    delegatedSubnetResourceId: vnet.outputs.postgresSubnetId
    privateDnsZoneId: privateDnsZone.outputs.id
  }
}

// Key Vault for secrets
module keyVault './core/security/keyvault.bicep' = {
  name: 'keyvault'
  params: {
    name: !empty(keyVaultName) ? keyVaultName : '${abbrs.keyVaultVaults}${resourceToken}'
    location: location
    tags: tags
    principalId: principalId
  }
}

// The application frontend
module web './core/host/appservice.bicep' = {
  name: 'web'
  params: {
    name: !empty(appServiceName) ? appServiceName : '${abbrs.webSitesAppService}web-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'web' })
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.11'
    managedIdentity: true
    userAssignedIdentityId: userAssignedIdentity.outputs.id
    serviceName: 'web'
    // VNet integration for secure access to PostgreSQL
    subnetId: vnet.outputs.appSubnetId
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
output AZURE_RESOURCE_GROUP string = resourceGroup().name
output RESOURCE_GROUP_ID string = resourceGroup().id

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = ''
output AZURE_CONTAINER_REGISTRY_NAME string = ''

output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = web.outputs.identityPrincipalId
output SERVICE_WEB_NAME string = web.outputs.name
output SERVICE_WEB_URI string = web.outputs.uri

output POSTGRES_SERVER_NAME string = postgresDb.outputs.name
output POSTGRES_DATABASE_NAME string = 'crm'

output KEY_VAULT_NAME string = keyVault.outputs.name
output KEY_VAULT_URI string = keyVault.outputs.uri

// VNet outputs for reference
output VNET_NAME string = vnet.outputs.name
output VNET_ID string = vnet.outputs.id
output PRIVATE_DNS_ZONE_NAME string = privateDnsZone.outputs.name

// Additional required outputs
output DATABASE_URL string = 'postgresql://crmadmin@${postgresDb.outputs.fqdn}:5432/crm?sslmode=require'
output SECRET_KEY string = '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=secret-key)'
