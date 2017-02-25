#/usr/bin/python env
import sys
import os
import json
from collections import OrderedDict
from optparse import OptionParser

# Process Script Parameters
parser = OptionParser()
parser.add_option("-n", "--template-name", action="store", type="string", dest="template_name", help="Template Name: 1nic, 2nic_limited, cluster_base, etc..." )
parser.add_option("-l", "--license-type", action="store", type="string", dest="license_type", default="BYOL", help="License Type: BYOL or PAYG" )
parser.add_option("-t", "--template-location", action="store", type="string", dest="template_location", help="Template Location: such as ../experimental/standalone/1nic/PAYG/" )
parser.add_option("-s", "--script-location", action="store", type="string", dest="script_location", help="Script Location: such as ../experimental/standalone/1nic/" )

(options, args) = parser.parse_args()
template_name = options.template_name
license_type = options.license_type
template_location = options.template_location
script_location = options.script_location

## Specify meta file and file to create(should be argument)
metafile = 'base.azuredeploy.json'
metafile_params = 'base.azuredeploy.parameters.json'
createdfile = template_location + 'azuredeploy.json'
createdfile_params = template_location + 'azuredeploy.parameters.json'

## Static Variable Defaults
nic_reference = ""
command_to_execute = ""

## Static Variable Assignment ##
content_version = '1.1.0.0'
instance_type_list = "Standard_A2", "Standard_A3", "Standard_A4", "Standard_A9", "Standard_A11", "Standard_D2", "Standard_D3", "Standard_D4", "Standard_D12", "Standard_D13", "Standard_D14", "Standard_D2_v2", "Standard_D3_v2", "Standard_D4_v2", "Standard_D5_v2", "Standard_D12_v2", "Standard_D13_v2", "Standard_D14_v2", "Standard_D15_v2", "Standard_F2", "Standard_F4"
tags = { "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }
tag_values = {"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}
api_version = "[variables('apiVersion')]"
compute_api_version = "[variables('computeApiVersion')]"
network_api_version = "[variables('networkApiVersion')]"
storage_api_version = "[variables('storageApiVersion')]"
insights_api_version = "[variables('insightsApiVersion')]"
location = "[variables('location')]"
default_payg_bw = '200m'

## Determine PAYG/BYOL variables
sku_to_use = "[concat('f5-bigip-virtual-edition-', variables('imageNameToLower'),'-byol')]"
offer_to_use = "f5-big-ip"
image_to_use = "13.0.000"
license1_command = "' --license ', parameters('licenseKey1'),"
license2_command = "' --license ', parameters('licenseKey2'),"
if license_type == 'PAYG':
    sku_to_use = "[concat('f5-bigip-virtual-edition-', parameters('licensedBandwidth'), '-', variables('imageNameToLower'),'-hourly')]"
    offer_to_use = "f5-big-ip-hourly"
    license1_command = ''
    license2_command = ''


## Load "Meta File(s)" for modification ##
with open(metafile, 'r') as base:
    data = json.load(base, object_pairs_hook=OrderedDict)
with open(metafile_params, 'r') as base_params:
    data_params = json.load(base_params, object_pairs_hook=OrderedDict)


############### Create/Modify ARM Objects ###############
data['contentVersion'] = content_version
data_params['contentVersion'] = content_version

########## ARM Parameters ##########
if template_name == 'cluster_base':
    data['parameters']['numberOfInstances'] = {"type": "int", "defaultValue": 2, "allowedValues": [ 2 ], "metadata": { "description": "The number of BIG-IP VEs that will be deployed in front of your application." } }
if template_name == 'ltm_autoscale':
    data['parameters']['vmScaleSetCount'] = {"type": "int", "defaultValue": 2, "allowedValues": [1, 2, 3, 4], "metadata": { "description": "The number of BIG-IP VEs that will be deployed into the VM Scale Set(Capacity)" } }
    data['parameters']['scaleOutThroughput'] = {"type": "int", "defaultValue": 90, "allowedValues": [50, 55, 60, 65, 70, 75, 80, 85, 90, 95], "metadata": { "description": "The percentange of 'Network In' Throughput to scale out on.  This will be factored from the image bandwidth size chosen." } }
    data['parameters']['scaleInThroughput'] = {"type": "int", "defaultValue": 5, "allowedValues": [5, 10, 15, 20, 25, 30, 35, 40, 45], "metadata": { "description": "The percentange of 'Network In' Throughput to scale in on.  This will be factored from the image bandwidth size chosen." } }
data['parameters']['adminUsername'] = {"type": "string", "defaultValue": "azureuser", "metadata": {"description": "User name for the Virtual Machine."}}
data['parameters']['adminPassword'] = {"type": "securestring", "metadata": { "description": "Password to login to the Virtual Machine." } }
data['parameters']['dnsLabel'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "Unique DNS Name for the Public IP used to access the Virtual Machine." } }
if template_name in ('1nic', '2nic_limited'):
    data['parameters']['instanceName'] = {"type": "string", "defaultValue": "f5vm01", "metadata": { "description": "Name of the VM"}}
data['parameters']['instanceType'] = {"type": "string", "defaultValue": "Standard_D2_v2", "allowedValues": instance_type_list, "metadata": {"description": "Size of the VM"}}
data['parameters']['imageName'] = {"type": "string", "defaultValue": "Good", "allowedValues": [ "Good", "Better", "Best" ], "metadata": { "description": "F5 SKU(IMAGE) to Deploy"}}
if license_type == 'BYOL':
    data['parameters']['licenseKey1'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "The license token for the F5 BIG-IP(BYOL)" } }
    if template_name == 'cluster_base':
        for license_key in ['licenseKey2']:
            data['parameters'][license_key] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "The license token for the F5 BIG-IP(BYOL). This field is required when deploying two or more devices" } }
elif license_type == 'PAYG':
    data['parameters']['licensedBandwidth'] = {"type": "string", "defaultValue": default_payg_bw, "allowedValues": [ "25m", "200m", "1g" ], "metadata": { "description": "PAYG licensed bandwidth to allocate for this image."}}
if template_name == 'ltm_autoscale':
    data['parameters']['tenantId'] = { "type": "string", "metadata": { "description": "Your Azure service principal application tenant ID" } }
    data['parameters']['clientId'] = { "type": "string", "metadata": { "description": "Your Azure service principal application client ID" } }
    data['parameters']['servicePrincipalSecret'] = { "type": "securestring", "metadata": { "description": "Your Azure service principal application secret" } }
data['parameters']['restrictedSrcAddress'] = {"type": "string", "defaultValue": "*", "metadata": { "description": "Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources." } }
data['parameters']['tagValues'] = {"type": "object", "defaultValue": tag_values}

# Some modifications once parameters have been defined
for parameter in data['parameters']:
    # Sort azuredeploy.json parameters alphabetically
    sorted_param = json.dumps(data['parameters'][parameter], sort_keys=True, ensure_ascii=False)
    data['parameters'][parameter] = json.loads(sorted_param, object_pairs_hook=OrderedDict)
    # Add parameters into parameters file as well
    try:
        data_params['parameters'][parameter] = {"value": data['parameters'][parameter]['defaultValue']}
    except:
        data_params['parameters'][parameter] = {"value": 'GEN_UNIQUE'}

########## ARM Variables ##########
data['variables']['apiVersion'] = "2015-06-15"
data['variables']['computeApiVersion'] = "2015-06-15"
data['variables']['networkApiVersion'] = "2015-06-15"
data['variables']['storageApiVersion'] = "2015-06-15"
if template_name in ('ltm_autoscale'):
    data['variables']['computeApiVersion'] = "2016-04-30-preview"
    data['variables']['networkApiVersion'] = "2016-06-01"
    data['variables']['storageApiVersion'] = "2015-06-15"
    data['variables']['insightsApiVersion'] = "2015-04-01"
data['variables']['location'] = "[resourceGroup().location]"
data['variables']['singleQuote'] = "'"
data['variables']['f5CloudLibsTag'] = "v2.1.0"
data['variables']['verifyHash'] = '''[concat(variables('singleQuote'), 'cli script /Common/verifyHash {\nproc script::run {} {\n        if {[catch {\n            set hashes(f5-cloud-libs.tar.gz) a6a9db3b89bbd014413706f22fa619c3717fac41fc99ffe875589c90e9b85a05cea227c134ea6e5b519c8fee0d12f2175368e75917f31f447ece3d92f31814af\n            set hashes(f5-cloud-libs-aws.tar.gz) 90058095cc536a057378a90ed19c3afe0cecd9034e1d1816745bd5ad837939623fad034ebd2ee9bdf594f33358b50c50f49a18c2ee7588ba89645142f2217330\n            set hashes(asm-policy-linux.tar.gz) 63b5c2a51ca09c43bd89af3773bbab87c71a6e7f6ad9410b229b4e0a1c483d46f1a9fff39d9944041b02ee9260724027414de592e99f4c2475415323e18a72e0\n            set hashes(f5.http.v1.2.0rc4.tmpl) 47c19a83ebfc7bd1e9e9c35f3424945ef8694aa437eedd17b6a387788d4db1396fefe445199b497064d76967b0d50238154190ca0bd73941298fc257df4dc034\n            set hashes(f5.http.v1.2.0rc6.tmpl) 811b14bffaab5ed0365f0106bb5ce5e4ec22385655ea3ac04de2a39bd9944f51e3714619dae7ca43662c956b5212228858f0592672a2579d4a87769186e2cbfe\n\n            set file_path [lindex $tmsh::argv 1]\n            set file_name [file tail $file_path]\n\n            if {![info exists hashes($file_name)]} {\n                tmsh::log err "No hash found for $file_name"\n                exit 1\n            }\n\n            set expected_hash $hashes($file_name)\n            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n            if { $expected_hash eq $computed_hash } {\n                exit 0\n            }\n            tmsh::log err "Hash does not match for $file_path"\n            exit 1\n        }]} {\n            tmsh::log err {Unexpected error in verifyHash}\n            exit 1\n        }\n    }\n    script-signature OmyfJKVQkBj+Ks6SdIc2+UNxM2xFCK4MGizGysivShzeRof0EFlEUTQiZveZ4v2SElofUp5DMVKiTIIkM00kZ7LnwqvLYIOztDFNAtMGwO6/B/zA8jLhkfnA2xzxu9fFgFn3OEsc8QwbfFS1AqCMyyacbbiczJycHtu3z0a/8sqCgiZtcQ4iXqBP4fz+8HKLA36U0jpmW+z0gQQUwpiC+AfFWcAarXMtmpwLzScldnaZ5RLo0MG8EGrHmXiWjndSR/Ii9b3+vnHnceD6+sw7e7LXPvz+jV9/rFyEQOA1QNpv0Cy4SJcuY9NRjV9KNdBobJ5N+h2PZBlgaIdLMACAVQ==\n}', variables('singleQuote'))]'''
data['variables']['installCloudLibs'] = "[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit\nfi\necho loaded verifyHash\necho verifying f5-cloud-libs.targ.gz\n/usr/bin/tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz\nif [ $? != 0 ]; then\necho f5-cloud-libs.tar.gz is not valid\nexit\nfi\necho verified f5-cloud-libs.tar.gz\necho expanding f5-cloud-libs.tar.gz\ntar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud\ntouch /config/cloud/cloudLibsReady', variables('singleQuote'))]"
data['variables']['newStorageAccountName'] = "[concat(uniquestring(resourceGroup().id), 'stor')]"
data['variables']['storageAccountType'] = "Standard_LRS"
data['variables']['dnsLabel'] = "[toLower(parameters('dnsLabel'))]"
data['variables']['imageNameToLower'] = "[toLower(parameters('imageName'))]"
data['variables']['skuToUse'] = sku_to_use
data['variables']['offerToUse'] = offer_to_use
data['variables']['availabilitySetName'] = "[concat(variables('dnsLabel'), '-avset')]"
data['variables']['nicName'] = "[concat(variables('dnsLabel'), '-nic')]"
data['variables']['defaultGw'] = "10.0.1.1"
data['variables']['virtualNetworkName'] = "[concat(variables('dnsLabel'), '-vnet')]"
data['variables']['vnetId'] = "[resourceId('Microsoft.Network/virtualNetworks', variables('virtualNetworkName'))]"
data['variables']['vnetAddressPrefix'] = "10.0.0.0/16"
data['variables']['nsgID'] = "[resourceId('Microsoft.Network/networkSecurityGroups/',concat(variables('dnsLabel'),'-nsg'))]"
data['variables']['publicIPAddressName'] = "[concat(variables('dnsLabel'), '-pip')]"
data['variables']['publicIPAddressId'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('publicIPAddressName'))]"
data['variables']['publicIPAddressType'] = "Static"
data['variables']['subnetName'] = "[concat(variables('dnsLabel'),'-subnet')]"
data['variables']['subnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('subnetName'))]"
data['variables']['subnetPrefix'] = "10.0.1.0/24"

if template_name in ('1nic', '2nic_limited'):
    data['variables']['subnetPrivateAddress'] = "10.0.1.4"
    data['variables']['instanceName'] = "[toLower(parameters('instanceName'))]"
if template_name == '2nic_limited':
    data['variables']['subnet2Name'] = "[concat(variables('dnsLabel'),'-subnet2')]"
    data['variables']['subnet2Id'] = "[concat(variables('vnetId'), '/subnets/', variables('subnet2Name'))]"
    data['variables']['subnet2Prefix'] = "10.0.2.0/24"
    data['variables']['subnet2PrivateAddress'] = "10.0.2.4"
    data['variables']['nic2Name'] = "[concat(variables('dnsLabel'), '-nic2')]"
if template_name in ('cluster_base', 'ltm_autoscale'):
    data['variables']['ipAddress'] = "10.0.1."
    data['variables']['loadBalancerName'] = "[concat(variables('dnsLabel'),'-alb')]"
    data['variables']['deviceNamePrefix'] = "[concat(variables('dnsLabel'),'-device')]"
    data['variables']['lbID'] = "[resourceId('Microsoft.Network/loadBalancers',variables('loadBalancerName'))]"
    data['variables']['frontEndIPConfigID'] = "[concat(variables('lbID'),'/frontendIPConfigurations/loadBalancerFrontEnd')]"
if template_name in ('ltm_autoscale'):
    data['variables']['vmssName'] = "[concat(parameters('dnsLabel'),'-vmss')]"
    data['variables']['newDataStorageAccountName'] = "[concat(parameters('dnsLabel'),'data000')]"
    data['variables']['subscriptionID'] = "[subscription().subscriptionId]"
    data['variables']['tenantID'] = "[subscription().tenantId]"
    data['variables']['25m'] = 26214400
    data['variables']['200m'] = 209715200
    data['variables']['1g'] = 1073741824
    data['variables']['scaleOutCalc'] = "[mul(variables(parameters('licensedBandwidth')), parameters('scaleOutThroughput'))]"
    data['variables']['scaleInCalc'] = "[mul(variables(parameters('licensedBandwidth')), parameters('scaleInThroughput'))]"
    data['variables']['scaleOutNetwork'] = "[div(variables('scaleOutCalc'), 100)]"
    data['variables']['scaleInNetwork'] = "[div(variables('scaleInCalc'), 100)]"


########## ARM Resources ##########
resources_list = []
## Public IP Resource(s) ##
if template_name in ('1nic', '2nic_limited', 'cluster_base', 'ltm_autoscale'):
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[variables('publicIPAddressName')]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[variables('dnsLabel')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]

## Virtual Network Resources(s) ##
if template_name in ('1nic', 'cluster_base'):
    subnets = [{ "name": "[variables('subnetName')]", "properties": { "addressPrefix": "[variables('subnetPrefix')]" } }]
if template_name == '2nic_limited':
    subnets = [{ "name": "[variables('subnetName')]", "properties": { "addressPrefix": "[variables('subnetPrefix')]" } }, { "name": "[variables('subnet2Name')]", "properties": { "addressPrefix": "[variables('subnet2Prefix')]" } }]
if template_name in ('1nic', '2nic_limited', 'cluster_base'):
    resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

if template_name in ('ltm_autoscale'):
    subnets = [{ "name": "[variables('subnetName')]", "properties": { "addressPrefix": "[variables('subnetPrefix')]", "networkSecurityGroup": {"id": "[variables('nsgID')]"} } }]
    resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/networkSecurityGroups/', variables('dnsLabel'),'-nsg')]" ], "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

## Network Interface Resource(s) ##
if template_name in ('1nic', '2nic_limited'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": [ "[variables('vnetId')]", "[variables('publicIPAddressId')]", "[concat('Microsoft.Network/networkSecurityGroups/', variables('dnsLabel'),'-nsg')]" ], "location": location, "name": "[variables('nicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[variables('nsgID')]" }, "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('subnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": { "Id": "[variables('publicIPAddressId')]" }, "subnet": { "id": "[variables('subnetId')]" } } } ] } }]
if template_name == '2nic_limited':
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": [ "[variables('vnetId')]" ], "location": location, "name": "[variables('nic2Name')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig2')]", "properties": { "privateIPAddress": "[variables('subnet2PrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('subnet2Id')]" } } } ] } }]
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkInterfaces", "name": "[concat(variables('nicName'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/guimgt',copyindex())]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/sshmgt',copyindex())]", "[concat('Microsoft.Network/networkSecurityGroups/', variables('dnsLabel'),'-nsg')]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "niccopy" }, "properties": { "networkSecurityGroup": { "id": "[variables('nsgID')]" }, "ipConfigurations": [ { "name": "ipconfig1", "properties": { "privateIPAllocationMethod": "Static", "privateIPAddress": "[concat(variables('ipAddress'),add(4,copyindex()))]", "subnet": { "id": "[variables('subnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('lbID'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ], "loadBalancerInboundNatRules": [ { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'guimgt',copyIndex())]" }, { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'sshmgt',copyIndex())]" } ] } } ] } }]

## Network Security Group Resource(s) ##
if template_name in ('1nic', '2nic_limited', 'cluster_base', 'ltm_autoscale'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-nsg')]", "tags": tags, "properties": { "securityRules": [ { "name": "mgmt_allow_8443", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "8443", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "ssh_allow_22", "properties": { "description": "", "priority": 102, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } } ] } }]

## Load Balancer Resource(s) ##
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('publicIPAddressName'))]" ], "location": location, "tags": tags, "name": "[variables('loadBalancerName')]", "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('publicIPAddressId')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ] }, "type": "Microsoft.Network/loadBalancers" }]
if template_name == 'ltm_autoscale':
    resources_list += [{ "apiVersion": network_api_version, "name": "[variables('loadBalancerName')]", "type": "Microsoft.Network/loadBalancers", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('publicIPAddressName'))]" ], "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('publicIPAddressID')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ], "inboundNatPools": [ { "name": "sshnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPortRangeStart": 50001, "frontendPortRangeEnd": 50100, "backendPort": 22 } }, { "name": "mgmtnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPortRangeStart": 50101, "frontendPortRangeEnd": 50200, "backendPort": 8443 } } ] } }]

## Load Balancer Inbound NAT Rule(s) ##
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('loadBalancerName'),'/guimgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPort": "[copyIndex(8443)]", "backendPort": 8443, "enableFloatingIP": False } }]
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('loadBalancerName'),'/sshmgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPort": "[copyIndex(8022)]", "backendPort": 22, "enableFloatingIP": False } }]

## Availability Set Resource(s) ##
if template_name in ('1nic', '2nic_limited', 'cluster_base'):
    resources_list += [{ "apiVersion": api_version, "location": location, "name": "[variables('availabilitySetName')]", "tags": tags, "type": "Microsoft.Compute/availabilitySets" }]

## Storage Account Resource(s) ##
if template_name in ('1nic', '2nic_limited', 'cluster_base', 'ltm_autoscale'):
    resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "location": location, "name": "[variables('newStorageAccountName')]", "tags": tags, "properties": { "accountType": "[variables('storageAccountType')]" } }]
if template_name in ('ltm_autoscale'):
    resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "location": location, "name": "[variables('newDataStorageAccountName')]", "tags": tags, "properties": { "accountType": "[variables('storageAccountType')]" } }]

## Compute/VM Resource(s) ##
if template_name == '1nic':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nicName'))]", "properties": { "primary": True } }]
if template_name == '2nic_limited':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nic2Name'))]", "properties": { "primary": False } }]
if template_name in ('1nic', '2nic_limited'):
    resources_list += [{"apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "dependsOn": [ "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('nicName'))]" ], "location": location, "name": "[variables('instanceName')]", "tags": tags, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newStorageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  nic_reference }, "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "osProfile": { "computerName": "[variables('instanceName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'), '.blob.core.windows.net/vhds/', variables('instanceName'), '.vhd')]" } } } } }]

if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "name": "[concat(variables('deviceNamePrefix'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('nicName'), copyindex())]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "devicecopy" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "osProfile": { "computerName": "[concat(variables('deviceNamePrefix'),copyindex())]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "name": "[concat('osdisk',copyindex())]", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'),'.blob.core.windows.net/',variables('newStorageAccountName'),'/osDisk',copyindex(),'.vhd')]" }, "caching": "ReadWrite", "createOption": "FromImage" } }, "networkProfile": { "networkInterfaces": [ { "id": "[concat(resourceId('Microsoft.Network/networkInterfaces',variables('nicName')),copyindex())]" } ] }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newstorageAccountName'),'.blob.core.windows.net')]" } } } }]

## Compute/VM Extension Resource(s) ##
command_to_execute = ''; command_to_execute2 = ''
if template_name == '1nic':
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('subnetPrivateAddress'), ' --port 8443 -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp pool.ntp.org --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; rm -f /config/cloud/passwd')]"
if template_name == '2nic_limited':
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('subnetPrivateAddress'), ' --ssl-port 8443 -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp pool.ntp.org --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; f5-rest-node /config/cloud/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('subnetPrivateAddress'), ' --port 8443 -u admin -p ', parameters('adminPassword'), ' --multi-nic --default-gw ', variables('defaultGw'), ' --vlan vlan_mgmt,1.0 --vlan vlan_1,1.1 --self-ip self_mgmt,', variables('subnetPrivateAddress'), ',vlan_mgmt --self-ip self_1,', variables('subnet2PrivateAddress'), ',vlan_1 --log-level debug --background --force-reboot; rm -f /config/cloud/passwd')]"
if template_name == 'cluster_base':
    # Two Extensions for Cluster
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('ipAddress'), 4), ' --port 8443 -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), <LICENSE1_COMMAND> ' --ntp pool.ntp.org --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('ipAddress'), 4), ' --port 8443 -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('ipAddress'), 4), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), ' --auto-sync --save-on-auto-sync; rm -f /config/cloud/passwd')]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('ipAddress'), 5), ' --port 8443 -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), copyindex(1), '.azuresecurity.com'), <LICENSE2_COMMAND> ' --ntp pool.ntp.org --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('ipAddress'), 5), ' --port 8443 -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('ipAddress'), 5), ' --join-group --device-group Sync --sync --remote-host ', concat(variables('ipAddress'), 4), ' --remote-user admin --remote-password-url file:///config/cloud/passwd; rm -f /config/cloud/passwd')]"
# Base command to execute
base_cmd_to_execute = "'mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null /config/cloud/passwd; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', parameters('adminPassword'), ' >> /config/cloud/passwd; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host '"
command_to_execute = command_to_execute.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute)
command_to_execute2 = command_to_execute2.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute)
# String map license 1/2 if needed for BYOL
command_to_execute = command_to_execute.replace('<LICENSE1_COMMAND>', license1_command)
command_to_execute2 = command_to_execute2.replace('<LICENSE2_COMMAND>', license2_command)

if template_name in ('1nic', '2nic_limited'):
    resources_list += [{"apiVersion": "2016-03-30", "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('instanceName'),'/start')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('instanceName'))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
if template_name == 'cluster_base':
    # Two Extensions for Cluster
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('deviceNamePrefix'),0,'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),0)]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "copy": { "name": "extensionLoop", "count": "[sub(parameters('numberOfInstances'), 1)]" }, "name": "[concat(variables('deviceNamePrefix'),add(copyindex(),1),'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),add(copyindex(),1))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute2 } } }]

## Compute VM Scale Set(s) ##
if template_name == 'ltm_autoscale':
    resources_list += [{ "type": "Microsoft.Compute/virtualMachineScaleSets", "apiVersion": compute_api_version, "name": "[variables('vmssName')]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]" ], "sku": { "name": "[parameters('instanceType')]", "tier": "Standard", "capacity": "[parameters('vmScaleSetCount')]" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "upgradePolicy": { "mode": "Manual" }, "virtualMachineProfile": { "storageProfile": { "osDisk": { "vhdContainers": [ "[concat('https://', variables('newStorageAccountName'), '.blob.core.windows.net/vmss1')]" ], "name": "vmssosdisk", "caching": "ReadOnly", "createOption": "FromImage" }, "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use } }, "osProfile": { "computerNamePrefix": "[variables('vmssName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "networkProfile": { "networkInterfaceConfigurations": [ { "name": "nic1", "properties": { "primary": "true", "ipConfigurations": [ { "name": "ip1", "properties": { "subnet": { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'), '/subnets/', variables('subnetName'))]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/backendAddressPools/loadBalancerBackEnd')]" } ], "loadBalancerInboundNatPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/sshnatpool')]" }, { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/mgmtnatpool')]" } ] } } ] } } ] }, "extensionProfile": { "extensions": [ { "name":"main", "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/scripts/azure/runScripts.js')]", "[concat('https://api.github.com/repos/F5Networks/f5-cloud-libs/tarball/', variables('f5CloudLibsTag'))]", "https://raw.githubusercontent.com/edwoodjrjr/scriptdump/master/main.sh" ] }, "protectedSettings": { "commandToExecute": "[concat('bash main.sh -r ', resourceGroup().name, ' -v ', variables('vmssName'), ' -t ', parameters('tenantId'), ' -c ', parameters('clientId'), ' -p ', parameters('servicePrincipalSecret'), ' -u ', parameters('adminUsername'), ' -x ', parameters('adminPassword'), ' -s ', variables('f5CloudLibsTag'))]" } } } ] } }, "overprovision": "false" } }]

## Compute VM Scale Set(s) AutoScale Settings ##
if template_name == 'ltm_autoscale':
    resources_list += [{ "type": "Microsoft.Insights/autoscaleSettings", "apiVersion": "[variables('insightsApiVersion')]", "name": "autoscalehost", "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]" ], "properties": { "name": "autoscalehost", "targetResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "enabled": True, "profiles": [ { "name": "Profile1", "capacity": { "minimum": "[parameters('vmScaleSetCount')]", "maximum": "10", "default": "[parameters('vmScaleSetCount')]" }, "rules": [ { "metricTrigger": { "metricName": "Network In", "metricNamespace": "", "metricResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "PT5M", "timeAggregation": "Average", "operator": "GreaterThan", "threshold": "[variables('scaleOutNetwork')]" }, "scaleAction": { "direction": "Increase", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } }, { "metricTrigger": { "metricName": "Network In", "metricNamespace": "", "metricResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "PT5M", "timeAggregation": "Average", "operator": "LessThan", "threshold": "[variables('scaleInNetwork')]" }, "scaleAction": { "direction": "Decrease", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } } ] } ] } }]


## Sort resources section - Expand to choose order of resources instead of just alphabetical?
temp_sort = 'temp_sort.json'
with open(temp_sort, 'w') as temp_sorting:
    json.dump(resources_list, temp_sorting, sort_keys=True, indent=4, ensure_ascii=False)
with open(temp_sort, 'r') as temp_sorted:
    data['resources'] = json.load(temp_sorted, object_pairs_hook=OrderedDict)
    temp_sorted.close(); os.remove(temp_sort)

########## ARM Outputs ##########
if template_name in ('1nic', '2nic_limited'):
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://', variables('dnsLabel'), '.', resourceGroup().location, '.cloudapp.azure.com', ':8443')]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(variables('dnsLabel'), '.', resourceGroup().location, '.cloudapp.azure.com', ' ',22)]" }
if template_name == 'cluster_base':
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('publicIPAddressId')).dnsSettings.fqdn,':8443')]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('publicIPAddressId')).dnsSettings.fqdn,' ',8022)]" }
if template_name == 'ltm_autoscale':
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('publicIPAddressId')).dnsSettings.fqdn,':50101', ' - 50200')]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('publicIPAddressId')).dnsSettings.fqdn,' ',50001, ' - 50100')]" }

############### End Create/Modify ARM Template Objects ###############

## Write modified template(s) to appropriate location
with open(createdfile, 'w') as finished:
    json.dump(data, finished, indent=4, sort_keys=False, ensure_ascii=False)
with open(createdfile_params, 'w') as finished_params:
    json.dump(data_params, finished_params, indent=4, sort_keys=False, ensure_ascii=False)






############### Create/Modify Scripts ###############
### Update deployment scripts and write to appropriate location ###
if script_location:
    def script_param_array(language):
        # Create Dynamic Parameter Array - (Parameter, default value, mandatory parameter flag, skip parameter flag)
        param_array = []
        for parameter in data['parameters']:
            default_value = None; mandatory = True; skip_param = False
            try:
                if data['parameters'][parameter]['defaultValue'] != 'REQUIRED':
                    default_value = data['parameters'][parameter]['defaultValue']
            except:
                default_value = None
            # Specify parameters that aren't mandatory or should be skipped
            if parameter in ('restrictedSrcAddress', 'tagValues'):
                mandatory = False
            if 'license' in parameter:
                skip_param = True
            elif parameter == 'tagValues':
                skip_param = True
            param_array.append([parameter, default_value, mandatory, skip_param])
        return param_array

    # Create Proc for script creation - Supporting Powershell and Bash
    def script_creation(language):
        if language == 'powershell':
            param_str = ''; mandatory_cmd = ''; default_value = ''; payg_cmd = ''; byol_cmd = ''; deploy_cmd_params = ''; script_dash = ' -'
            meta_script = 'base.deploy_via_ps.ps1'; script_loc = script_location + 'Deploy_via_PS.ps1'
            base_ex = '## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth ' + default_payg_bw
            license2_param = ''; pwd_cmd = ''; sps_cmd = ''
        elif language == 'bash':
            param_str = ''; mandatory_cmd = ''; default_value = ''; payg_cmd = ''; byol_cmd = ''; deploy_cmd_params = '"{'; script_dash = ' --'
            meta_script = 'base.deploy_via_bash.sh'; script_loc = script_location + 'deploy_via_bash.sh'
            base_ex = '## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth ' + default_payg_bw
            getopt_start = 'ARGS=`getopt -o '; getopt_params_long = ' --long ';  getopt_end = ' -n $0 -- "$@"`'
            getopt_params_short = 'a:b:c:d:'; base_params = 'resourceGroupName:,azureLoginUser:,azureLoginPassword:,licenseType:,'
            mandatory_variables = ''; license2_param = ''; license2_check = ''; license_params = ''; pwd_cmd = ''; sps_cmd = ''
            bash_shorthand_args = ['e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
            # Need to add bash license params prior to dynamic parameters
            # Create license parameters, expand to be a for loop?
            license_args = ['licensedBandwidth','licenseKey1']
            if template_name in ('cluster_base'):
                license2_param = 'licenseKey2:,'
                license_args.append('licenseKey2')
                license2_check += '    if [ -v $licenseKey2 ] ; then\n            read -p "Please enter value for licenseKey2:" licenseKey2\n    fi\n'
            getopt_license_params = base_params + 'licensedBandwidth:,licenseKey1:,' + license2_param
            for license_arg in license_args:
                param_str += '\n        -' + bash_shorthand_args[0] + '|--' + license_arg+ ')\n            ' + license_arg + '=$2\n            shift 2;;'
                getopt_params_short += bash_shorthand_args[0] + ':'
                del bash_shorthand_args[0]
            getopt_params_long += getopt_license_params
        else:
            return 'Only supporting powershell and bash for now!'

        # Loop through Dynamic Parameter Array
        for parameter in script_param_array(language):
            mandatory_cmd = ''; param_value = ',\n'
            # Specify any parameters that should be skipped
            if parameter[3]:
                continue
            # Specify any parameters that should be mandatory
            if parameter[2]:
                if language == 'powershell':
                    mandatory_cmd = '\n  [Parameter(Mandatory=$True)]'
                elif language == 'bash':
                    mandatory_variables += parameter[0] + ' '
            # Specify non-mandatory parameters default value
            if parameter[2] == False:
                param_value = ' = "' + str(parameter[1]) + '",\n'
            if language == 'powershell':
                param_str += mandatory_cmd + '\n  [string]\n  $' + parameter[0] + param_value
                if parameter[0] == 'adminPassword':
                    deploy_cmd_params += '-' + parameter[0] + ' $pwd '
                    pwd_cmd = '$pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force'
                elif parameter[0] == 'servicePrincipalSecret':
                    deploy_cmd_params += '-' + parameter[0] + ' $sps '
                    sps_cmd = '\n$sps = ConvertTo-SecureString -String $servicePrincipalSecret -AsPlainText -Force'
                else:
                    deploy_cmd_params += '-' + parameter[0] + ' "$' + parameter[0] + '" '
            elif language == 'bash':
                deploy_cmd_params += '\\"' + parameter[0] + '\\":{\\"value\\":\\"$' + parameter[0] + '\\"},'
                # Need to build the getopt command
                getopt_params_long += parameter[0] + ':,'
                param_str += '\n        -' + bash_shorthand_args[0] + '|--' + parameter[0] + ')\n            ' + parameter[0] + '=$2\n            shift 2;;'
                getopt_params_short += bash_shorthand_args[0] + ':'
                del bash_shorthand_args[0]
            # Add param to example command
            if parameter[1]:
                # Add quotes around restrictedSrcAddress
                if parameter[0] == 'restrictedSrcAddress':
                    parameter[1] = '"' + str(parameter[1]) + '"'
                base_ex += script_dash + parameter[0] + ' ' + str(parameter[1])
            else:
                base_ex += script_dash + parameter[0] + ' ' + '<value>'

        with open(meta_script, 'r') as script:
            script_str = script.read()
        if language == 'powershell':
            # Create license parameters, expand to be a for loop?
            if template_name in ('cluster_base'):
                license2_param = '\n\n  [string]\n  $licenseKey2 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey2"}),'
            license_params = '  [Parameter(Mandatory=$True)]\n  [string]\n  $licenseType,\n\n  [string]\n  $licensedBandwidth = $(if($licenseType -eq "PAYG") { Read-Host -prompt "licensedBandwidth"}),\n\n  [string]\n  $licenseKey1 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey1"}),' + license2_param
            # Add any additional example command script parameters
            for named_param in ['resourceGroupName']:
                base_ex += '-' + named_param + ' ' + '<value> '
            if template_name in ('1nic', '2nic_limited'):
                byol_cmd =  deploy_cmd_params + ' -licenseKey1 "$licenseKey1"'
                payg_cmd = deploy_cmd_params + ' -licensedBandwidth "$licensedBandwidth"'
            elif template_name in ('cluster_base'):
                byol_cmd = deploy_cmd_params + ' -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2"'
                payg_cmd = deploy_cmd_params + ' -licensedBandwidth "$licensedBandwidth"'
            base_deploy = '$deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose '
            deploy_cmd = 'if ($licenseType -eq "BYOL") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BYOL\\azuredeploy.json"; $parametersFilePath = ".\BYOL\\azuredeploy.parameters.json" }\n  ' + base_deploy + byol_cmd + '\n} elseif ($licenseType -eq "PAYG") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\\azuredeploy.json"; $parametersFilePath = ".\PAYG\\azuredeploy.parameters.json" }\n  ' + base_deploy + payg_cmd + '\n} else {\n  Write-Error -Message "Uh oh, something went wrong!  Please select valid license type of PAYG or BYOL."\n}'
            if template_name in ('ltm_autoscale'):
                deploy_cmd = base_deploy + deploy_cmd_params + ' -licensedBandwidth "$licensedBandwidth"'
        elif language == 'bash':
            license_check = '# Prompt for license key if not supplied and BYOL is selected\nif [ $licenseType == "BYOL" ]; then\n    if [ -v $licenseKey1 ] ; then\n            read -p "Please enter value for licenseKey1:" licenseKey1\n    fi\n' + license2_check + '    template_file="./BYOL/azuredeploy.json"\n    parameter_file="./BYOL/azuredeploy.parameters.json"\nfi\n'
            license_check += '# Prompt for license key if not supplied and PAYG is selected\nif [ $licenseType == "PAYG" ]; then\n    if [ -v $licensedBandwidth ] ; then\n            read -p "Please enter value for licensedBandwidth:" licensedBandwidth\n    fi\n    template_file="./PAYG/azuredeploy.json"\n    parameter_file="./PAYG/azuredeploy.parameters.json"\nfi'
            # Compile getopts command
            getopt_params_long = getopt_params_long[:-1]
            getopt_cmd = getopt_start + getopt_params_short + getopt_params_long + getopt_end
            # Add any additional example command script parameters
            for named_param in ['resourceGroupName','azureLoginUser','azureLoginPassword']:
                base_ex += script_dash + named_param + ' <value>'
            # Add any additional mandatory parameters
            for required_param in ['resourceGroupName', 'licenseType']:
                mandatory_variables += required_param + ' '
            # Add any additional parameters to the deployment command
            for addtl_param in ['tagValues']:
                deploy_cmd_params += '\\"' + addtl_param + '\\":{\\"value\\":$' + addtl_param + '},'
            create_cmd = 'azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p '
            if template_name in ('1nic', '2nic_limited'):
                byol_cmd =  create_cmd + deploy_cmd_params + '\\"licenseKey1\\":{\\"value\\":\\"$licenseKey1\\"}}"'
                payg_cmd = create_cmd + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
            if template_name in ('cluster_base'):
                byol_cmd = create_cmd + deploy_cmd_params + '\\"licenseKey1\\":{\\"value\\":\\"$licenseKey1\\"},\\"licenseKey2\\":{\\"value\\":\\"$licenseKey2\\"}}"'
                payg_cmd = create_cmd + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
            deploy_cmd = 'if [ $licenseType == "BYOL" ]; then\n    ' + byol_cmd + '\nelif [ $licenseType == "PAYG" ]; then\n    ' + payg_cmd + '\nelse\n    echo "Uh oh, shouldn\'t make it here! Ensure license type is either PAYG or BYOL"\n    exit 1\nfi'
            if template_name in ('ltm_autoscale'):
                deploy_cmd = create_cmd + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
        # Map necessary script items, handle encoding
        ex_cmd = base_ex.encode("utf8")
        param_str = param_str.encode("utf8")
        # Map script as needed
        script_str = script_str.replace('<EXAMPLE_CMD>', ex_cmd)
        script_str = script_str.replace('<DEPLOYMENT_CREATE>', deploy_cmd)
        script_str = script_str.replace('<PWD_CMD>', pwd_cmd)
        script_str = script_str.replace('<SPS_CMD>', sps_cmd)
        script_str = script_str.replace('<LICENSE_PARAMETERS>', license_params)
        script_str = script_str.replace('<DYNAMIC_PARAMETERS>', param_str)
        if language == 'bash':
            script_str = script_str.replace('<PARAMETERS>', getopt_cmd)
            script_str = script_str.replace('<REQUIRED_PARAMETERS>', mandatory_variables)
            script_str = script_str.replace('<LICENSE_CHECK>', license_check)
        # Write to actual script location
        with open(script_loc, 'w') as script_complete:
            script_complete.write(script_str)
        ## End Script_Creation Proc
        return language + 'Script Created'

    # Need to manually add templates to create scripts for now as a 'check'...
    if template_name in ('1nic', '2nic_limited', 'cluster_base', 'ltm_autoscale'):
        for script_language in ('powershell', 'bash'):
            script_creation(script_language)
############### END Create/Modify Scripts ###############