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
var resourceToken = uniqueString(subscription().id, environmentName, location)
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

// Virtual Network for secure networking
module vnet './core/network/virtualnetwork.bicep' = {
  name: 'vnet'
  scope: rg
  params: {
    name: 'vnet-${resourceToken}'
    location: location
    tags: tags
  }
}

// Private DNS Zone for PostgreSQL Flexible Server
module privateDnsZone './core/network/privatednszone.bicep' = {
  name: 'private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.postgres.database.azure.com'
    tags: tags
    virtualNetworkId: vnet.outputs.id
  }
}

// The application frontend
module web './core/host/appservice.bicep' = {
  name: 'web'
  scope: rg
  params: {
    name: !empty(appServiceName) ? appServiceName : '${abbrs.webSitesAppService}web-${resourceToken}'
    location: location
    tags: tags
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

module appServicePlan './core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  scope: rg
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
    // VNet integration for secure private access
    delegatedSubnetResourceId: vnet.outputs.postgresSubnetId
    privateDnsZoneId: privateDnsZone.outputs.id
  }
}

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

// VNet outputs for reference
output VNET_NAME string = vnet.outputs.name
output VNET_ID string = vnet.outputs.id
output PRIVATE_DNS_ZONE_NAME string = privateDnsZone.outputs.name

// Additional required outputs
output DATABASE_URL string = 'postgresql://crmadmin@${postgresDb.outputs.fqdn}:5432/crm?sslmode=require'
output SECRET_KEY string = '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=secret-key)'
