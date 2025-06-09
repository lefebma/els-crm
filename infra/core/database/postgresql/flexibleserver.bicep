param name string
param location string = resourceGroup().location
param tags object = {}

param sku object = {
  name: 'Standard_B1ms'
  tier: 'Burstable'
}

param storage object = {
  storageSizeGB: 32
}

param version string = '14'
param administratorLogin string
@secure()
param administratorLoginPassword string
param databaseNames array = []

// VNet integration parameters
param delegatedSubnetResourceId string = ''
param privateDnsZoneId string = ''

resource postgresqlServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    version: version
    storage: storage
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Enabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    // VNet integration for private access
    network: !empty(delegatedSubnetResourceId) ? {
      delegatedSubnetResourceId: delegatedSubnetResourceId
      privateDnsZoneArmResourceId: privateDnsZoneId
    } : null
  }
}

// Note: Firewall rules are not compatible with VNet integration
// When using VNet integration, access is controlled through the virtual network

resource postgresqlDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2022-12-01' = [for databaseName in databaseNames: {
  parent: postgresqlServer
  name: databaseName
  properties: {
    charset: 'utf8'
    collation: 'en_US.utf8'
  }
}]

output id string = postgresqlServer.id
output name string = postgresqlServer.name
output fqdn string = postgresqlServer.properties.fullyQualifiedDomainName
output connectionString string = 'postgresql://${administratorLogin}@${postgresqlServer.properties.fullyQualifiedDomainName}:5432/${databaseNames[0]}?sslmode=require'
