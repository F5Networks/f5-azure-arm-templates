#/usr/bin/python env
import os
import json
from collections import OrderedDict
from optparse import OptionParser

# Process Script Parameters
parser = OptionParser()
parser.add_option("-t", "--template-name", action="store", type="string", dest="template_name", help="Template Name: 1nic, 2nic_limited, cluster_base, etc..." )
parser.add_option("-l", "--license-type", action="store", type="string", dest="license_type", default="BYOL", help="License Type: BYOL or PAYG" )
parser.add_option("-z", "--template-location", action="store", type="string", dest="template_location", help="Template Location: such as ../experimental/standalone/1nic/" )

(options, args) = parser.parse_args()
template_name = options.template_name
license_type = options.license_type
template_location = options.template_location

# Specify meta file and file to create(should be argument)
metafile = 'base.azuredeploy.json'
metafile_params = 'base.azuredeploy.parameters.json'
createdfile = template_location + 'azuredeploy.json'
createdfile_params = template_location + 'azuredeploy.parameters.json'

#Static Variable Defaults
nic_reference = ""
command_to_execute = ""

# Static Variable Assignment
content_version = '1.0.0.0'
instance_type_list = "Standard_A4", "Standard_A9", "Standard_A11", "Standard_D2", "Standard_D3", "Standard_D4", "Standard_D12", "Standard_D13", "Standard_D14", "Standard_D2_v2", "Standard_D3_v2", "Standard_D4_v2", "Standard_D5_v2", "Standard_D12_v2", "Standard_D13_v2", "Standard_D14_v2", "Standard_D15_v2", "Standard_F2", "Standard_F4"
tags = { "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }
api_version = "[variables('apiVersion')]"
location = "[variables('location')]"

# Load "Meta File(s)" for modification
with open(metafile, 'r') as base:
    data = json.load(base, object_pairs_hook=OrderedDict)
with open(metafile_params, 'r') as base_params:
    data_params = json.load(base_params, object_pairs_hook=OrderedDict)


### Create/Modify ARM Objects ###
data['contentVersion'] = content_version
data_params['contentVersion'] = content_version

## ARM Parameters ##
if template_name == 'cluster_base':
    data['parameters']['solutionDeploymentName'] = {"type": "string", "metadata": {"description": "A unique name for this deployment."}}
    data['parameters']['numberOfInstances'] = {"type": "int", "defaultValue": 2, "allowedValues": [ 2 ], "metadata": { "description": "The number of BIG-IP VEs that will be deployed in front of your application." } }
    data['parameters']['solutionDeploymentName'] = {"type": "string", "metadata": { "description": "A unique name for this deployment." } }
data['parameters']['adminUsername'] = {"type": "string", "defaultValue": "azureuser", "metadata": {"description": "User name for the Virtual Machine."}}
data['parameters']['adminPassword'] = {"type": "securestring", "metadata": { "description": "Password to login to the Virtual Machine." } }
data['parameters']['dnsLabel'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "Unique DNS Name for the Public IP used to access the Virtual Machine." } }
if template_name in ('1nic', '2nic_limited'):
    data['parameters']['instanceName'] = {"type": "string", "defaultValue": "f5vm01", "metadata": { "description": "Name of the VM"}}
data['parameters']['instanceType'] = {"type": "string", "defaultValue": "Standard_D2_v2", "allowedValues": instance_type_list, "metadata": {"description": "Size of the VM"}}
data['parameters']['imageName'] = { "type": "string", "defaultValue": "Good", "allowedValues": [ "Good", "Better", "Best" ], "metadata": { "description": "F5 SKU(IMAGE) to Deploy"}}
data['parameters']['licenseKey1'] = { "type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "The license token for the F5 BIG-IP(BYOL)" } }
if template_name == 'cluster_base':
    data['parameters']['licenseKey2'] = { "type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "The license token for the second F5 BIG-IP(BYOL). This field is required when deploying two or more devices" } }
data['parameters']['restrictedSrcAddress'] = { "type": "string", "defaultValue": "*", "metadata": { "description": "Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources." } }
data['parameters']['tagValues'] = { "type": "object", "defaultValue": { "application": "APP", "environment": "ENV", "group": "GROUP", "owner": "OWNER", "cost": "COST" } }

# Add Parameters into parameters file as well
param_default_value = 'GEN_UNIQUE'
for parameter in data['parameters']:
    try:
        data_params['parameters'][parameter] = {"value": data['parameters'][parameter]['defaultValue']}
    except:
        data_params['parameters'][parameter] = {"value": param_default_value}

## ARM Variables ##
data['variables']['apiVersion'] = "2015-06-15"
data['variables']['location'] = "[resourceGroup().location]"
data['variables']['singleQuote'] = "'"
data['variables']['f5CloudLibsTag'] = "v2.1.0"
data['variables']['verifyHash'] = '''[concat(variables('singleQuote'), 'cli script /Common/verifyHash {\nproc script::run {} {\n        if {[catch {\n            set hashes(f5-cloud-libs.tar.gz) a6a9db3b89bbd014413706f22fa619c3717fac41fc99ffe875589c90e9b85a05cea227c134ea6e5b519c8fee0d12f2175368e75917f31f447ece3d92f31814af\n            set hashes(f5-cloud-libs-aws.tar.gz) 90058095cc536a057378a90ed19c3afe0cecd9034e1d1816745bd5ad837939623fad034ebd2ee9bdf594f33358b50c50f49a18c2ee7588ba89645142f2217330\n            set hashes(asm-policy-linux.tar.gz) 63b5c2a51ca09c43bd89af3773bbab87c71a6e7f6ad9410b229b4e0a1c483d46f1a9fff39d9944041b02ee9260724027414de592e99f4c2475415323e18a72e0\n            set hashes(f5.http.v1.2.0rc4.tmpl) 47c19a83ebfc7bd1e9e9c35f3424945ef8694aa437eedd17b6a387788d4db1396fefe445199b497064d76967b0d50238154190ca0bd73941298fc257df4dc034\n            set hashes(f5.http.v1.2.0rc6.tmpl) 811b14bffaab5ed0365f0106bb5ce5e4ec22385655ea3ac04de2a39bd9944f51e3714619dae7ca43662c956b5212228858f0592672a2579d4a87769186e2cbfe\n\n            set file_path [lindex $tmsh::argv 1]\n            set file_name [file tail $file_path]\n\n            if {![info exists hashes($file_name)]} {\n                tmsh::log err "No hash found for $file_name"\n                exit 1\n            }\n\n            set expected_hash $hashes($file_name)\n            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n            if { $expected_hash eq $computed_hash } {\n                exit 0\n            }\n            tmsh::log err "Hash does not match for $file_path"\n            exit 1\n        }]} {\n            tmsh::log err {Unexpected error in verifyHash}\n            exit 1\n        }\n    }\n    script-signature OmyfJKVQkBj+Ks6SdIc2+UNxM2xFCK4MGizGysivShzeRof0EFlEUTQiZveZ4v2SElofUp5DMVKiTIIkM00kZ7LnwqvLYIOztDFNAtMGwO6/B/zA8jLhkfnA2xzxu9fFgFn3OEsc8QwbfFS1AqCMyyacbbiczJycHtu3z0a/8sqCgiZtcQ4iXqBP4fz+8HKLA36U0jpmW+z0gQQUwpiC+AfFWcAarXMtmpwLzScldnaZ5RLo0MG8EGrHmXiWjndSR/Ii9b3+vnHnceD6+sw7e7LXPvz+jV9/rFyEQOA1QNpv0Cy4SJcuY9NRjV9KNdBobJ5N+h2PZBlgaIdLMACAVQ==\n}', variables('singleQuote'))]'''
data['variables']['installCloudLibs'] = "[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit\nfi\necho loaded verifyHash\necho verifying f5-cloud-libs.targ.gz\n/usr/bin/tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz\nif [ $? != 0 ]; then\necho f5-cloud-libs.tar.gz is not valid\nexit\nfi\necho verified f5-cloud-libs.tar.gz\necho expanding f5-cloud-libs.tar.gz\ntar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud\ntouch /config/cloud/cloudLibsReady', variables('singleQuote'))]"
data['variables']['newStorageAccountName'] = "[concat(uniquestring(resourceGroup().id), 'stor')]"
data['variables']['storageAccountType'] = "Standard_LRS"
data['variables']['dnsLabel'] = "[toLower(parameters('dnsLabel'))]"
data['variables']['instanceName'] = "[toLower(parameters('instanceName'))]"
data['variables']['imageNameToLower'] = "[toLower(parameters('imageName'))]"
data['variables']['skuToUse'] = "[concat('f5-bigip-virtual-edition-', variables('imageNameToLower'),'-byol')]"
data['variables']['availabilitySetName'] = "[concat(variables('instanceName'), '-avset')]"
data['variables']['nic1Name'] = "[concat(variables('instanceName'), '-mgmt1')]"
data['variables']['defaultGw'] = "10.0.1.1"
data['variables']['virtualNetworkName'] = "[concat(variables('instanceName'), '-vnet')]"
data['variables']['vnetId'] = "[resourceId('Microsoft.Network/virtualNetworks', variables('virtualNetworkName'))]"
data['variables']['vnetAddressPrefix'] = "10.0.0.0/16"
data['variables']['nsgID'] = "[resourceId('Microsoft.Network/networkSecurityGroups/',concat(variables('dnsLabel'),'-nsg'))]"
if template_name in ('1nic', '2nic_limited'):
    data['variables']['subnet1Name'] = "MGMT_Frontend"
    data['variables']['subnet1Id'] = "[concat(variables('vnetId'), '/subnets/', variables('subnet1Name'))]"
    data['variables']['subnet1Prefix'] = "10.0.1.0/24"
    data['variables']['subnet1PrivateAddress'] = "10.0.1.4"
    data['variables']['publicIPAddressName'] = "[concat(variables('dnsLabel'), '-pip')]"
    data['variables']['publicIPAddressType'] = "Static"
    data['variables']['publicIPAddressId'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('publicIPAddressName'))]"

if template_name == '2nic_limited':
    data['variables']['subnet2Name'] = "Web"
    data['variables']['subnet2Id'] = "[concat(variables('vnetId'), '/subnets/', variables('subnet2Name'))]"
    data['variables']['subnet2Prefix'] = "10.0.2.0/24"
    data['variables']['subnet2PrivateAddress'] = "10.0.2.4"
    data['variables']['nic2Name'] = "[concat(variables('instanceName'), '-nic2')]"

if template_name == 'cluster_base':
    data['variables']['subnetName'] = "[concat(parameters('dnsLabel'),'-subNet')]"
    data['variables']['subnetPrefix'] = "10.10.1.0/24"
    data['variables']['ipAddress'] = "10.10.1."
    data['variables']['nicNamePrefix'] = "[concat(parameters('dnsLabel'),'-nic')]"
    data['variables']['loadBalancerName'] = "[concat(parameters('dnsLabel'),'-alb')]"
    data['variables']['deviceNamePrefix'] = "[concat(parameters('dnsLabel'),'-device')]"
    data['variables']['lbID'] = "[concat(parameters('dnsLabel'),'-alb')]"
    data['variables']['frontEndIPConfigID'] = "[concat(variables('lbID'),'/frontendIPConfigurations/loadBalancerFrontEnd')]"
    data['variables']['guiMgtID'] = "[concat(variables('lbID'),'/inboundNatRules/guimgt')]"
    data['variables']['sshMgtID'] = "[concat(variables('lbID'),'/inboundNatRules/sshmgt')]"
    data['variables']['publicIPID'] = "[resourceId('Microsoft.Network/publicIPAddresses',parameters('dnsLabel'))]"
    data['variables']['subnetRef'] = "[concat(variables('vnetID'),'/subnets/',variables('subnetName'))]"


## ARM Resources ##

resources_list = []
# Public IP Resource(s)
if template_name in ('1nic', '2nic_limited'):
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": api_version, "location": location, "name": "[variables('publicIPAddressName')]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[variables('dnsLabel')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]

if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/publicIPAddresses", "name": "[parameters('dnsLabel')]", "location": location, "tags": tags, "properties": { "publicIPAllocationMethod": "Dynamic", "dnsSettings": { "domainNameLabel": "[parameters('dnsLabel')]" } } }]

# Virtual Network Resources(s)
if template_name == '1nic':
    resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": [ { "name": "[variables('subnet1Name')]", "properties": { "addressPrefix": "[variables('subnet1Prefix')]" } } ] } }]
if template_name == '2nic_limited':
    resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": [ { "name": "[variables('subnet1Name')]", "properties": { "addressPrefix": "[variables('subnet1Prefix')]" } }, { "name": "[variables('subnet2Name')]", "properties": { "addressPrefix": "[variables('subnet2Prefix')]" } } ] } }]
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/virtualNetworks", "name": "[variables('virtualNetworkName')]", "location": location, "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": [ { "name": "[variables('subnetName')]", "properties": { "addressPrefix": "[variables('subnetPrefix')]" } } ] } }]

# Network Interface Resource(s)
if template_name in ('1nic', '2nic_limited'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": [ "[variables('vnetId')]", "[variables('publicIPAddressId')]", "[concat('Microsoft.Network/networkSecurityGroups/', variables('dnsLabel'),'-nsg')]" ], "location": location, "name": "[variables('nic1Name')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[variables('nsgID')]" }, "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('subnet1PrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": { "Id": "[variables('publicIPAddressId')]" }, "subnet": { "id": "[variables('subnet1Id')]" } } } ] } }]

if template_name == '2nic_limited':
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": [ "[variables('vnetId')]" ], "location": location, "name": "[variables('nic2Name')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig2')]", "properties": { "privateIPAddress": "[variables('subnet2PrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('subnet2Id')]" } } } ] } }]
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkInterfaces", "name": "[concat(variables('nicNamePrefix'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/guimgt',copyindex())]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/sshmgt',copyindex())]", "[concat('Microsoft.Network/networkSecurityGroups/', parameters('dnsLabel'),'-nsg')]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "niccopy" }, "properties": { "networkSecurityGroup": { "id": "[variables('nsgID')]" }, "ipConfigurations": [ { "name": "ipconfig1", "properties": { "privateIPAllocationMethod": "Static", "privateIPAddress": "[concat(variables('ipAddress'),add(4,copyindex()))]", "subnet": { "id": "[variables('subnetRef')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('lbID'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ], "loadBalancerInboundNatRules": [ { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'guimgt',copyIndex())]" }, { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'sshmgt',copyIndex())]" } ] } } ] } }]

# Network Security Group Resource(s)
if template_name in ('1nic', '2nic_limited'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-nsg')]", "tags": tags, "properties": { "securityRules": [ { "name": "mgmt_allow_443", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "443", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "ssh_allow_22", "properties": { "description": "", "priority": 102, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } } ] } }]

if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "name": "[concat(parameters('dnsLabel'), '-nsg')]", "location": location, "tags": tags, "properties": { "securityRules": [ { "name": "mgmt_allow_443", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "443", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "ssh_allow_22", "properties": { "description": "", "priority": 102, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } } ] } }]

# Load Balancer Resource(s)
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', parameters('dnsLabel'))]" ], "location": location, "tags": tags, "name": "[variables('loadBalancerName')]", "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('publicIPID')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ] }, "type": "Microsoft.Network/loadBalancers" }]

# Load Balancer Inbound NAT Rule(s)
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('loadBalancerName'),'/guimgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPort": "[copyIndex(8443)]", "backendPort": 443, "enableFloatingIP": False } }]

# Availability Set Resource(s)
if template_name in ('1nic', '2nic_limited'):
    resources_list += [{ "apiVersion": api_version, "location": location, "name": "[variables('availabilitySetName')]", "tags": tags, "type": "Microsoft.Compute/availabilitySets" }]

if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "location": location, "tags": tags, "name": "[variables('availabilitySetName')]", "type": "Microsoft.Compute/availabilitySets" }]

# Storage Account Resource(s)
if template_name in ('1nic', '2nic_limited'):
    resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": api_version, "location": location, "name": "[variables('newStorageAccountName')]", "tags": tags, "properties": { "accountType": "[variables('storageAccountType')]" } }]

if template_name == 'cluster_base':
    resources_list += [{ "name": "[variables('newStorageAccountName')]", "type": "Microsoft.Storage/storageAccounts", "location": location, "tags": { "displayName": "StorageAccount", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "apiVersion": api_version, "properties": { "accountType": "Standard_LRS" } }]

# Compute/VM Resource(s)
if template_name == '1nic':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nic1Name'))]", "properties": { "primary": True } }]
if template_name == '2nic_limited':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nic1Name'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nic2Name'))]", "properties": { "primary": False } }]
if template_name in ('1nic', '2nic_limited'):
    resources_list += [{"apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "dependsOn": [ "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('nic1Name'))]" ], "location": location, "name": "[variables('instanceName')]", "tags": tags, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "f5-big-ip" }, "properties": { "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newStorageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  nic_reference }, "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "osProfile": { "computerName": "[variables('instanceName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "f5-big-ip", "sku": "[variables('skuToUse')]", "version": "latest" }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'), '.blob.core.windows.net/vhds/', variables('instanceName'), '.vhd')]" } } } } }]

if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "name": "[concat(variables('deviceNamePrefix'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('nicNamePrefix'), copyindex())]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "devicecopy" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "f5-big-ip" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "osProfile": { "computerName": "[concat(variables('deviceNamePrefix'),copyindex())]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "f5-big-ip", "sku": "[variables('skuToUse')]", "version": "latest" }, "osDisk": { "name": "[concat('osdisk',copyindex())]", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'),'.blob.core.windows.net/',variables('newStorageAccountName'),'/osDisk',copyindex(),'.vhd')]" }, "caching": "ReadWrite", "createOption": "FromImage" } }, "networkProfile": { "networkInterfaces": [ { "id": "[concat(resourceId('Microsoft.Network/networkInterfaces',variables('nicNamePrefix')),copyindex())]" } ] }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newstorageAccountName'),'.blob.core.windows.net')]" } } } }]

# Compute/VM Extension Resource(s)
if template_name == '1nic':
    command_to_execute = "[concat('mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null /config/cloud/passwd; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', parameters('adminPassword'), ' >> /config/cloud/passwd; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host ', variables('subnet1PrivateAddress'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), ' --license ', parameters('licenseKey1'), ' --ntp pool.ntp.org --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; rm -f /config/cloud/passwd')]"
if template_name == '2nic_limited':
    command_to_execute = "[concat('mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null /config/cloud/passwd; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', parameters('adminPassword'), ' >> /config/cloud/passwd; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host ', variables('subnet1PrivateAddress'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), ' --license ', parameters('licenseKey1'), ' --ntp pool.ntp.org --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; f5-rest-node /config/cloud/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('subnet1PrivateAddress'), ' -u admin -p ', parameters('adminPassword'), ' --multi-nic --default-gw ', variables('defaultGw'), ' --vlan vlan_mgmt,1.0 --vlan vlan_1,1.1 --self-ip self_mgmt,', variables('subnet1PrivateAddress'), ',vlan_mgmt --self-ip self_1,', variables('subnet2PrivateAddress'), ',vlan_1 --log-level debug --background --force-reboot; rm -f /config/cloud/passwd')]"
if template_name in ('1nic', '2nic_limited'):
    resources_list += [{"apiVersion": "2016-03-30", "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('instanceName'),'/start')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('instanceName'))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]

if template_name == 'cluster_base':
    # Two Extensions for Cluster
    command_to_execute = "[concat('mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null /config/cloud/passwd; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', parameters('adminPassword'), ' >> /config/cloud/passwd; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host ', concat(variables('ipAddress'), 4), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), ' --ntp pool.ntp.org --license ', parameters('licenseKey1'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('ipAddress'), 4), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('ipAddress'), 4), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), ' --auto-sync --save-on-auto-sync; rm -f /config/cloud/passwd')]"
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('deviceNamePrefix'),0,'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),0)]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]

    command_to_execute = "[concat('mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null /config/cloud/passwd; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', parameters('adminPassword'), ' >> /config/cloud/passwd; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host ', concat(variables('ipAddress'), 5), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), copyindex(1), '.azuresecurity.com'), ' --ntp pool.ntp.org --license ', parameters('licenseKey2'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('ipAddress'), 5), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('ipAddress'), 5), ' --join-group --device-group Sync --sync --remote-host ', concat(variables('ipAddress'), 4), ' --remote-user admin --remote-password-url file:///config/cloud/passwd; rm -f /config/cloud/passwd')]"
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "copy": { "name": "extensionLoop", "count": "[sub(parameters('numberOfInstances'), 1)]" }, "name": "[concat(variables('deviceNamePrefix'),add(copyindex(),1),'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),add(copyindex(),1))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]

# Sort resources section - Expand to choose order of resources instead of just alphabetical?
temp_sort = 'temp_sort.json'
with open(temp_sort, 'w') as temp_sorting:
    json.dump(resources_list, temp_sorting, sort_keys=True, indent=4, ensure_ascii=False)
with open(temp_sort, 'r') as temp_sorted:
    data['resources'] = json.load(temp_sorted, object_pairs_hook=OrderedDict)
    temp_sorted.close(); os.remove(temp_sort)

## ARM Outputs ##
if template_name in ('1nic', '2nic_limited'):
    data['outputs']['MGMT-URL'] = { "type": "string", "value": "[concat('https://', variables('dnsLabel'), '.', resourceGroup().location, '.cloudapp.azure.com')]" }
if template_name == 'cluster_base':
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('publicIPID')).dnsSettings.fqdn,':8443')]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('publicIPID')).dnsSettings.fqdn,' ',8022)]" }

### END Create/Modify ARM Objects ###

# Write modified template(s) to appropriate location
with open(createdfile, 'w') as finished:
    json.dump(data, finished, indent=4, sort_keys=False, ensure_ascii=False)
    finished.close()
with open(createdfile_params, 'w') as finished_params:
    json.dump(data_params, finished_params, indent=4, sort_keys=False, ensure_ascii=False)
    finished_params.close()
