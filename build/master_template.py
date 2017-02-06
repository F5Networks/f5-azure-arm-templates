#/usr/bin/python env
import os
import json
from collections import OrderedDict
from optparse import OptionParser


# Process Script Parameters
parser = OptionParser()
parser.add_option("-t", "--template-name", action="store", type="string", dest="template_name", help="Template Name: 1nic, 2nic_limited, base_cluster, etc..." )
parser.add_option("-l", "--license-type", action="store", type="string", dest="license_type", default="BYOL", help="License Type: BYOL or PAYG" )

(options, args) = parser.parse_args()
template_name = options.template_name
license_type = options.license_type

# Specify meta file and file to create(should be argument)
metafile = 'base.azuredeploy.json'
folderloc = './built_templates/'
createdfile = folderloc + template_name + 'azuredeploy.json'

#Static Variable Defaults
nic_reference = ""
command_to_execute = ""

# Static Variable Assignment
content_version = '1.0.0.0'
instance_type_list = "Standard_A4", "Standard_A9", "Standard_A11", "Standard_D2", "Standard_D3", "Standard_D4", "Standard_D12", "Standard_D13", "Standard_D14", "Standard_D2_v2", "Standard_D3_v2", "Standard_D4_v2", "Standard_D5_v2", "Standard_D12_v2", "Standard_D13_v2", "Standard_D14_v2", "Standard_D15_v2"

# Open "Meta File" for modification
with open(metafile, 'r') as f:
    data = json.load(f, object_pairs_hook=OrderedDict)


### Create/Modify ARM Objects
data['contentVersion'] = content_version

## ARM Parameters
data['parameters']['adminUsername'] = {"type": "string", "defaultValue": "azureuser", "metadata": {"description": "User name for the Virtual Machine."}}
data['parameters']['adminPassword'] = { "type": "securestring", "metadata": { "description": "Password to login to the Virtual Machine." } }
data['parameters']['dnsLabel'] = { "type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "Unique DNS Name for the Public IP used to access the Virtual Machine." } }
data['parameters']['instanceName'] = { "type": "string", "defaultValue": "f5vm01", "metadata": { "description": "Name of the VM" } }
data['parameters']['instanceType'] = {"type": "string", "defaultValue": "Standard_D2_v2", "allowedValues": instance_type_list, "metadata": {"description": "Size of the VM"}}
data['parameters']['imageName'] = { "type": "string", "defaultValue": "Good", "allowedValues": [ "Good", "Better", "Best" ], "metadata": { "description": "F5 SKU(IMAGE) to Deploy" }}
data['parameters']['licenseKey1'] = { "type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "The license token for the F5 BIG-IP(BYOL)" } }
data['parameters']['restrictedSrcAddress'] = { "type": "string", "defaultValue": "*", "metadata": { "description": "Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources." } }
data['parameters']['tagValues'] = { "type": "object", "defaultValue": { "application": "APP", "environment": "ENV", "group": "GROUP", "owner": "OWNER", "cost": "COST" } }


## ARM Variables
data['variables']['apiVersion'] = "2015-06-15"
data['variables']['location'] = "[resourceGroup().location]"
data['variables']['singleQuote'] = "'"
data['variables']['f5CloudLibsTag'] = "v2.0.0"
data['variables']['expectedHash'] = "8bb8ca730dce21dff6ec129a84bdb1689d703dc2b0227adcbd16757d5eeddd767fbe7d8d54cc147521ff2232bd42eebe78259069594d159eceb86a88ea137b73"
data['variables']['verifyHash'] = '''[concat(variables('singleQuote'), 'cli script /Common/verifyHash {\nproc script::run {} {\n        if {[catch {\n            set file_path [lindex $tmsh::argv 1]\n            set expected_hash ', variables('expectedHash'), '\n            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n            if { $expected_hash eq $computed_hash } {\n                exit 0\n            }\n            tmsh::log err {Hash does not match}\n            exit 1\n        }]} {\n            tmsh::log err {Unexpected error in verifyHash}\n            exit 1\n        }\n    }\n    script-signature fc3P5jEvm5pd4qgKzkpOFr9bNGzZFjo9pK0diwqe/LgXwpLlNbpuqoFG6kMSRnzlpL54nrnVKREf6EsBwFoz6WbfDMD3QYZ4k3zkY7aiLzOdOcJh2wECZM5z1Yve/9Vjhmpp4zXo4varPVUkHBYzzr8FPQiR6E7Nv5xOJM2ocUv7E6/2nRfJs42J70bWmGL2ZEmk0xd6gt4tRdksU3LOXhsipuEZbPxJGOPMUZL7o5xNqzU3PvnqZrLFk37bOYMTrZxte51jP/gr3+TIsWNfQEX47nxUcSGN2HYY2Fu+aHDZtdnkYgn5WogQdUAjVVBXYlB38JpX1PFHt1AMrtSIFg==\n}', variables('singleQuote'))]'''
data['variables']['installCloudLibs'] = "[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit\nfi\necho loaded verifyHash\necho verifying f5-cloud-libs.targ.gz\n/usr/bin/tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz\nif [ $? != 0 ]; then\necho f5-cloud-libs.tar.gz is not valid\nexit\nfi\necho verified f5-cloud-libs.tar.gz\necho expanding f5-cloud-libs.tar.gz\ntar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud\ntouch /config/cloud/cloudLibsReady', variables('singleQuote'))]"
data['variables']['storageAccountName'] = "[concat(uniquestring(resourceGroup().id), 'sa1nic')]"
data['variables']['storageAccountType'] = "Standard_LRS"
data['variables']['imageNameToLower'] = "[toLower(parameters('imageName'))]"
data['variables']['skuToUse'] = "[concat('f5-bigip-virtual-edition-', variables('imageNameToLower'),'-byol')]"
data['variables']['availabilitySetName'] = "[concat(parameters('instanceName'), '-availset')]"
data['variables']['nic1Name'] = "[concat(parameters('instanceName'), '-mgmt1')]"
data['variables']['defaultGw'] = "10.0.1.1"
data['variables']['vnetName'] = "[concat(parameters('instanceName'), '-vnet')]"
data['variables']['vnetId'] = "[resourceId('Microsoft.Network/virtualNetworks', variables('vnetName'))]"
data['variables']['addressPrefix'] = "10.0.0.0/16"
data['variables']['subnet1Name'] = "MGMT_Frontend"
data['variables']['subnet1Id'] = "[concat(variables('vnetId'), '/subnets/', variables('subnet1Name'))]"
data['variables']['subnet1Prefix'] = "10.0.1.0/24"
data['variables']['subnet1PrivateAddress'] = "10.0.1.4"
data['variables']['publicIPAddressName'] = "[concat(parameters('dnsLabel'), '-pip')]"
data['variables']['publicIPAddressType'] = "Static"
data['variables']['publicIPAddressId'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('publicIPAddressName'))]"
data['variables']['nsgID'] = "[resourceId('Microsoft.Network/networkSecurityGroups/',concat(parameters('dnsLabel'),'-nsg'))]"
if template_name == '2nic_limited':
    data['variables']['subnet2Name'] = "Web"
    data['variables']['subnet2Id'] = "[concat(variables('vnetId'), '/subnets/', variables('subnet2Name'))]"
    data['variables']['subnet2Prefix'] = "10.0.2.0/24"
    data['variables']['subnet2PrivateAddress'] = "10.0.2.4"
    data['variables']['nic2Name'] = "[concat(parameters('instanceName'), '-nic2')]"


## ARM Resources

data['resources'] = []
# Public IP Resource(s)
data['resources'] += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": "[variables('apiVersion')]", "location": "[resourceGroup().location]", "name": "[variables('publicIPAddressName')]", "tags": { "displayName": "PublicIPAddress", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "properties": { "dnsSettings": { "domainNameLabel": "[parameters('dnsLabel')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
# Virtual Network Resources(s)
if template_name == '1nic':
    data['resources'] += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": "[variables('apiVersion')]", "location": "[resourceGroup().location]", "name": "[variables('vnetName')]", "tags": { "displayName": "NetworkInterface", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('addressPrefix')]" ] }, "subnets": [ { "name": "[variables('subnet1Name')]", "properties": { "addressPrefix": "[variables('subnet1Prefix')]" } } ] } }]
if template_name == '2nic_limited':
    data['resources'] += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": "[variables('apiVersion')]", "location": "[resourceGroup().location]", "name": "[variables('vnetName')]", "tags": { "displayName": "NetworkInterface", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('addressPrefix')]" ] }, "subnets": [ { "name": "[variables('subnet1Name')]", "properties": { "addressPrefix": "[variables('subnet1Prefix')]" } }, { "name": "[variables('subnet2Name')]", "properties": { "addressPrefix": "[variables('subnet2Prefix')]" } } ] } }]
# Network Interface Resource(s)
data['resources'] += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": "[variables('apiVersion')]", "dependsOn": [ "[variables('vnetId')]", "[variables('publicIPAddressId')]", "[concat('Microsoft.Network/networkSecurityGroups/', parameters('dnsLabel'),'-nsg')]" ], "location": "[resourceGroup().location]", "name": "[variables('nic1Name')]", "tags": { "displayName": "PublicIPAddress", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "properties": { "networkSecurityGroup": { "id": "[variables('nsgID')]" }, "ipConfigurations": [ { "name": "[concat(parameters('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('subnet1PrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": { "Id": "[variables('publicIPAddressId')]" }, "subnet": { "id": "[variables('subnet1Id')]" } } } ] } }]
if template_name == '2nic_limited':
    data['resources'] += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": "[variables('apiVersion')]", "dependsOn": [ "[variables('vnetId')]" ], "location": "[resourceGroup().location]", "name": "[variables('nic2Name')]", "tags": { "displayName": "NetworkInterface", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "properties": { "ipConfigurations": [ { "name": "[concat(parameters('instanceName'), '-ipconfig2')]", "properties": { "privateIPAddress": "[variables('subnet2PrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('subnet2Id')]" } } } ] } }]
# Network Security Group Resource(s)
data['resources'] += [{ "apiVersion": "[variables('apiVersion')]", "type": "Microsoft.Network/networkSecurityGroups", "location": "[variables('location')]", "name": "[concat(parameters('dnsLabel'), '-nsg')]", "tags": { "displayName": "NetworkSecurityGroup", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "properties": { "securityRules": [ { "name": "mgmt_allow_443", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "443", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "ssh_allow_22", "properties": { "description": "", "priority": 102, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } } ] } }]
# Availability Set Resource(s)
data['resources'] += [{ "apiVersion": "[variables('apiVersion')]", "location": "[resourceGroup().location]", "name": "[variables('availabilitySetName')]", "tags": { "displayName": "AvailabilitySet", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "type": "Microsoft.Compute/availabilitySets" }]
# Storage Account Resource(s)
data['resources'] += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": "[variables('apiVersion')]", "location": "[resourceGroup().location]", "name": "[variables('storageAccountName')]", "tags": { "displayName": "StorageAccount", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "properties": { "accountType": "[variables('storageAccountType')]" } }]
# Compute/VM Resource(s)
if template_name == '1nic':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nic1Name'))]", "properties": { "primary": True } }]
if template_name == '2nic_limited':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nic1Name'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nic2Name'))]", "properties": { "primary": False } }]
data['resources'] += [{"apiVersion": "[variables('apiVersion')]", "type": "Microsoft.Compute/virtualMachines", "dependsOn": [ "[concat('Microsoft.Storage/storageAccounts/', variables('storageAccountName'))]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('nic1Name'))]" ], "location": "[resourceGroup().location]", "name": "[parameters('instanceName')]", "tags": { "displayName": "VirtualMachine", "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "f5-big-ip" }, "properties": { "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('storageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  nic_reference }, "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "osProfile": { "computerName": "[parameters('instanceName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "f5-big-ip", "sku": "[variables('skuToUse')]", "version": "latest" }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat('http://',variables('storageAccountName'), '.blob.core.windows.net/vhds/', parameters('instanceName'), '.vhd')]" } } } } }]
# Compute/VM Extension Resource(s)
if template_name == '1nic':
    command_to_execute = "[concat('mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null /config/cloud/passwd; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', parameters('adminPassword'), ' >> /config/cloud/passwd; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host ', variables('subnet1PrivateAddress'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(parameters('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), ' --license ', parameters('licenseKey1'), ' --ntp pool.ntp.org --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; rm -f /config/cloud/passwd')]"
if template_name == '2nic_limited':
    command_to_execute = "[concat('mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null /config/cloud/passwd; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', parameters('adminPassword'), ' >> /config/cloud/passwd; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host ', variables('subnet1PrivateAddress'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(parameters('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), ' --license ', parameters('licenseKey1'), ' --ntp pool.ntp.org --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; f5-rest-node /config/cloud/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('subnet1PrivateAddress'), ' -u admin -p ', parameters('adminPassword'), ' --multi-nic --default-gw ', variables('defaultGw'), ' --vlan vlan_mgmt,1.0 --vlan vlan_1,1.1 --self-ip self_mgmt,', variables('subnet1PrivateAddress'), ',vlan_mgmt --self-ip self_1,', variables('subnet2PrivateAddress'), ',vlan_1 --log-level debug --background --force-reboot; rm -f /config/cloud/passwd')]"
data['resources'] += [{"apiVersion": "2016-03-30", "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(parameters('instanceName'),'/start')]", "location": "[variables('location')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', parameters('instanceName'))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]


## ARM Outputs
data['outputs']['MGMT-URL'] = { "type": "string", "value": "[concat('https://', parameters('dnsLabel'), '.', resourceGroup().location, '.cloudapp.azure.com')]" }

### END Create/Modify ARM Objects


# Write modified template to appropriate location
with open(createdfile, 'w') as finished:
    json.dump(data, finished, indent=4, sort_keys=True, ensure_ascii=False)
    finished.close()
