param name string
param location string = resourceGroup().location
param tags object = {}

param appServicePlanId string
param runtimeName string
param runtimeVersion string
param managedIdentity bool = false
param userAssignedIdentityId string = ''
param appSettings object = {}
param serviceName string = 'web'

// VNet integration parameters
param subnetId string = ''

resource appService 'Microsoft.Web/sites@2022-03-01' = {
  name: name
  location: location
  tags: union(tags, { 'azd-service-name': serviceName })
  kind: 'app,linux'
  identity: managedIdentity && !empty(userAssignedIdentityId) ? {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  } : managedIdentity ? { type: 'SystemAssigned' } : null
  properties: {
    serverFarmId: appServicePlanId
    siteConfig: {
      linuxFxVersion: '${runtimeName}|${runtimeVersion}'
      alwaysOn: false
      ftpsState: 'Disabled'
      appCommandLine: 'bash startup_azure.sh'
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
      }
      appSettings: [for key in items(appSettings): {
        name: key.key
        value: key.value
      }]
    }
    httpsOnly: true
  }
}

// VNet integration for the app service
resource vnetIntegration 'Microsoft.Web/sites/networkConfig@2022-03-01' = if (!empty(subnetId)) {
  parent: appService
  name: 'virtualNetwork'
  properties: {
    subnetResourceId: subnetId
    swiftSupported: true
  }
}

output id string = appService.id
output name string = appService.name
output uri string = 'https://${appService.properties.defaultHostName}'
output identityPrincipalId string = managedIdentity && !empty(userAssignedIdentityId) ? reference(userAssignedIdentityId, '2023-01-31').principalId : (managedIdentity ? appService.identity.principalId : '')
