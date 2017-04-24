#!/usr/bin/env node

var fs = require('fs');
var credentialsFile = JSON.parse(fs.readFileSync('/config/cloud/azCredentials', 'utf8'));

var subscriptionId = credentialsFile.subscriptionId;
var clientId = credentialsFile.clientId;
var tenantId = credentialsFile.tenantId;
var secret = credentialsFile.secret;
var resourceGroup = credentialsFile.resourceGroup;

var async = require('async');
var util = require('util');
var msRestAzure = require('ms-rest-azure');
var credentials = new msRestAzure.ApplicationTokenCredentials(clientId, tenantId, secret);

var networkManagementClient = require('azure-arm-network');
var networkClient = new networkManagementClient(credentials, subscriptionId);

var iControl = require('icontrol');
var bigip = new iControl({
     host: 'localhost',
     proto: 'https',
     port: 8443,
     strict: false,
     debug: false
});

var routeFilter = fs.readFileSync('/config/cloud/managedRoutes', 'utf8').replace(/(\r\n|\n|\r)/gm,"").split(',');
var routeTableTags = fs.readFileSync('/config/cloud/routeTableTag', 'utf8').replace(/(\r\n|\n|\r)/gm,"").split('\n');

var extIpName = '-ext-pip';
var extIpConfigName = '-ext-ipconfig';
var selfIpConfigName = '-self-ipconfig';

function listResources(operationCallback) {
     async.parallel([
          function (callback) {
               networkClient.routeTables.listAll(function (err, result) {
                    if (err) return callback(err);
                    callback(null, result);
               });
          },
          function (callback) {
               bigip.list('/net/self/self_3nic', function (err, result) {
                    if (err) return callback(err);
                    callback(null, result);
               });
          },
          function (callback) {
               networkClient.networkInterfaces.list(resourceGroup, function (err, result) {
                    if (err) return callback(err);
                    callback(null, result);
               });
          },
          function (callback) {
               networkClient.publicIPAddresses.list(resourceGroup, function (err, result) {
                    if (err) return callback(err);
                    callback(null, result);
               });
          },
          function (callback) {
               bigip.list('/net/self/self_2nic', function (err, result) {
                    if (err) return callback(err);
                    callback(null, result);
               });
          }
     ],
     function (err, results) {
          if (err) return console.log('Error getting IP info: ', err);         
          matchRoutes(null, results[0], results[1]);
          matchNics(null, results[2], results[3], results[4]);
          return;
     });
     return;
}

function matchRoutes(err, routeTables, self) {
     if (err) return console.log('Match error: ', err);
     
     var self = self.address;
     var fields = self.split('/');
     var selfIp = fields[0];    
     
     for ( var t in routeTables ) {
          if ( routeTables[t].tags && routeTables[t].tags.f5_ha ) {
               var tag = routeTables[t].tags.f5_ha;

               if ( routeTableTags.indexOf(tag) !== -1 ) {
                    var routeTableGroup = routeTables[t].id.split("/")[4];
                    var routeTableName = routeTables[t].name;
                    var routes = routeTables[t].routes
                    
                    for ( var r in routes ) {
                         if ( routeFilter.indexOf(routes[r].addressPrefix) !== -1 ) {                    
                              var routeName = routes[r].name;                    
                              routes[r].nextHopType = 'VirtualAppliance';
                              routes[r].nextHopIpAddress = selfIp;
                              var routeParams = routes[r];
                              
                              updateRoutes(null, routeTableGroup, routeTableName, routeName, routeParams);
                         }
                    }
               }
          } 
     }
}

function updateRoutes(err, routeTableGroup, routeTableName, routeName, routeParams) {  
     if (err) return console.log('Update error: ', err); 
     
     networkClient.routes.beginCreateOrUpdate(routeTableGroup, routeTableName, routeName, routeParams, function (err, result) {
          if (err) return console.log('Update error: ', err);
     }); 
}

function matchNics(err, nics, pips, self) {
     if (err) return console.log('List Error: ', err);
     
     var self = self.address;
     var fields = self.split('/');
     var selfIp = fields[0];    
     
     for ( var i in nics ) {
          var ipConfigurations = nics[i].ipConfigurations;          
          for ( var p in ipConfigurations ) {
               if ( ipConfigurations[p].privateIPAddress === selfIp ) {
                    var myNicName = nics[i].name;
                    var myNicConfig = nics[i];
               }
               if ( ipConfigurations[p].privateIPAddress !== selfIp && ipConfigurations[p].id.includes(selfIpConfigName) ) {
                    var theirNicName = nics[i].name;
                    var theirNicConfig = nics[i];
               }
          }
     }
     
     var orphanedPipsArr = [];
     
     for ( var p in pips ) {
          if ( pips[p].tags.f5_privateIp && pips[p].tags.f5_extSubnetId && pips[p].name.includes(extIpName) ) {
               var pip = {};
               pip.id = pips[p].id;               
               var pipName = pips[p].name;
               var name = pipName.replace(extIpName, extIpConfigName);
               var pipPrivate = pips[p].tags.f5_privateIp;               
               var subnet = {};
               subnet.id = pips[p].tags.f5_extSubnetId;
               
               if ( !pips[p].ipConfiguration ) {                
                    orphanedPipsArr.push({    
                         'name': name,
                         'privateIPAllocationMethod': 'Static',
                         'privateIPAddress': pipPrivate, 
                         'primary': false, 
                         'publicIPAddress': pip, 
                         'subnet': subnet
                    }); 
               }              
          }
     }
     
     switchIpConfigs(null, myNicConfig, theirNicConfig, myNicName, theirNicName, selfIp, orphanedPipsArr);
}

function switchIpConfigs(err, myNicConfig, theirNicConfig, myNicName, theirNicName, selfIp, orphanedPipsArr) {   
     if (err) return console.log('Associate public IP Error: ', err);
     
     var ourLocation = myNicConfig.location;     
     var theirNicArr = [];
     var myNicArr = [];
     
     for ( var c in theirNicConfig.ipConfigurations ) {          
          var theirName = theirNicConfig.ipConfigurations[c].name;
          var theirPrivateIpMethod = theirNicConfig.ipConfigurations[c].privateIPAllocationMethod;
          var theirPrivateIp = theirNicConfig.ipConfigurations[c].privateIPAddress;
          var theirPrimary = theirNicConfig.ipConfigurations[c].primary;
          var theirSubnetId = theirNicConfig.ipConfigurations[c].subnet;
          var theirPublicIpId = theirNicConfig.ipConfigurations[c].publicIPAddress; 
          theirNicArr.push({
               'name': theirName, 
               'privateIPAllocationMethod': theirPrivateIpMethod,
               'privateIPAddress': theirPrivateIp, 
               'primary': theirPrimary, 
               'publicIPAddress': theirPublicIpId,
               'subnet': theirSubnetId
          });   
     }
     
     for ( var c in myNicConfig.ipConfigurations ) {         
          var myName = myNicConfig.ipConfigurations[c].name;
          var myPrivateIpMethod = myNicConfig.ipConfigurations[c].privateIPAllocationMethod;
          var myPrivateIp = myNicConfig.ipConfigurations[c].privateIPAddress;
          var myPrimary = myNicConfig.ipConfigurations[c].primary;
          var mySubnetId = myNicConfig.ipConfigurations[c].subnet;
          var myPublicIpId = myNicConfig.ipConfigurations[c].publicIPAddress; 
          myNicArr.push({
               'name': myName, 
               'privateIPAllocationMethod': myPrivateIpMethod,
               'privateIPAddress': myPrivateIp, 
               'primary': myPrimary, 
               'publicIPAddress': myPublicIpId,
               'subnet': mySubnetId
          });    
     }
    
     for ( var i=theirNicArr.length-1; i>=0; i-- ) {
          if ( theirNicArr[i].name.includes(extIpConfigName) ) {           
               myNicArr.push({
                    'name': theirNicArr[i].name, 
                    'privateIPAllocationMethod': theirNicArr[i].privateIPAllocationMethod, 
                    'privateIPAddress': theirNicArr[i].privateIPAddress, 
                    'primary': theirNicArr[i].primary, 
                    'publicIPAddress': theirNicArr[i].publicIPAddress,
                    'subnet': theirNicArr[i].subnet
               }); 
               theirNicArr.splice(i, 1);
          }
     }
     
     for ( var i=orphanedPipsArr.length-1; i>=0; i-- ) {          
          myNicArr.push({
               'name': orphanedPipsArr[i].name, 
               'privateIPAllocationMethod': orphanedPipsArr[i].privateIPAllocationMethod, 
               'privateIPAddress': orphanedPipsArr[i].privateIPAddress, 
               'primary': orphanedPipsArr[i].primary, 
               'publicIPAddress': orphanedPipsArr[i].publicIPAddress,
               'subnet': orphanedPipsArr[i].subnet
          }); 
     }
     
     var theirNicParams = { location: ourLocation, ipConfigurations:theirNicArr };    
     var myNicParams = { location: ourLocation, ipConfigurations:myNicArr };
     
     disassociateIpConfigs(null, myNicName, theirNicName, myNicParams, theirNicParams);
     
}

function disassociateIpConfigs(err, myNicName, theirNicName, myNicParams, theirNicParams) {   
     if (err) return console.log('Disassociate IP configs Error: ', err);
     async.parallel([
          function (callback) {
               networkClient.networkInterfaces.createOrUpdate(resourceGroup, theirNicName, theirNicParams, function (err, result) {
                    if (err) return callback(err);
                    callback(null, result);
               });
          }
     ],
     function (err, results) {
          if (err) return console.log('Error disassociating IP configs: ', err);         
          associateIpConfigs(null, myNicName, myNicParams);
     });
     return;
}

function associateIpConfigs(err, myNicName, myNicParams) {   
     if (err) return console.log('Associate IP configs Error: ', err);
     async.parallel([
          function (callback) {
               networkClient.networkInterfaces.createOrUpdate(resourceGroup, myNicName, myNicParams, function (err, result) {
                    if (err) return callback(err);
                    callback(null, result);
               });
          }
     ],
     function (err, results) {
          if (err) return console.log('Error associating IP configs: ', err);         
          return;
     });
     return;
}

listResources();