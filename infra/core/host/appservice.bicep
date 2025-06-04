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

output id string = appService.id
output name string = appService.name
output uri string = 'https://${appService.properties.defaultHostName}'
output identityPrincipalId string = managedIdentity && !empty(userAssignedIdentityId) ? reference(userAssignedIdentityId, '2023-01-31').principalId : (managedIdentity ? appService.identity.principalId : '')
