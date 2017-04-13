#/usr/bin/python env
import sys
import os
import json
from collections import OrderedDict
from optparse import OptionParser

# Process Script Parameters
parser = OptionParser()
parser.add_option("-n", "--template-name", action="store", type="string", dest="template_name", help="Template Name: 1nic, 2nic, cluster_base, etc..." )
parser.add_option("-l", "--license-type", action="store", type="string", dest="license_type", help="License Type: BYOL or PAYG" )
parser.add_option("-m", "--stack-type", action="store", type="string", dest="stack_type", default="new", help="Networking Stack Type: new or existing" )
parser.add_option("-t", "--template-location", action="store", type="string", dest="template_location", help="Template Location: such as ../experimental/standalone/1nic/PAYG/" )
parser.add_option("-s", "--script-location", action="store", type="string", dest="script_location", help="Script Location: such as ../experimental/standalone/1nic/" )
parser.add_option("-v", "--solution-location", action="store", type="string", dest="solution_location", default="experimental", help="Solution location: experimental or supported" )

(options, args) = parser.parse_args()
template_name = options.template_name
license_type = options.license_type
stack_type = options.stack_type
template_location = options.template_location
script_location = options.script_location
solution_location = options.solution_location

## Specify meta file and file to create(should be argument)
metafile = 'base.azuredeploy.json'
metafile_params = 'base.azuredeploy.parameters.json'
createdfile = template_location + 'azuredeploy.json'
createdfile_params = template_location + 'azuredeploy.parameters.json'

## Static Variable Defaults
nic_reference = ""
command_to_execute = ""

## Static Variable Assignment ##
content_version = '2.0.0.0'
f5_networks_tag = 'v2.0.0.0'
f5_cloud_libs_tag = 'develop'
f5_cloud_libs_azure_tag = 'v1.0.0'

install_cloud_libs = """[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit\nfi\necho loaded verifyHash\nscript_loc="/var/lib/waagent/custom-script/download/0/"\nconfig_loc="/config/cloud/"\nhashed_file_list="<HASHED_FILE_LIST>"\nfor file in $hashed_file_list; do\necho "verifying $file"\n/usr/bin/tmsh run cli script verifyHash $file\nif [ $? != 0 ]; then\necho "$file is not valid"\nexit 1\nfi\necho "verified $file"\ndone\necho "expanding $hashed_file_list"\ntar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/node_modules\n<TAR_LIST>touch /config/cloud/cloudLibsReady', variables('singleQuote'))]"""
hashed_file_list = "${config_loc}f5-cloud-libs.tar.gz"
additional_tar_list = ""
if template_name in ('ltm_autoscale'):
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz"
    additional_tar_list = "tar xvfz /config/cloud/f5-cloud-libs-azure.tar.gz -C /config/cloud/node_modules/f5-cloud-libs/node_modules\n"
elif template_name in ('waf_autoscale'):
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz ${script_loc}deploy_waf.sh ${script_loc}f5.http.v1.2.0rc7.tmpl ${script_loc}f5.policy_creator.tmpl ${script_loc}asm-policy.tar.gz"
    additional_tar_list = "tar xvfz /config/cloud/f5-cloud-libs-azure.tar.gz -C /config/cloud/node_modules/f5-cloud-libs/node_modules\n"
#### Temp empty hashed file list when testing new cloud libs....
hashed_file_list = ""
install_cloud_libs = install_cloud_libs.replace('<HASHED_FILE_LIST>', hashed_file_list)
install_cloud_libs = install_cloud_libs.replace('<TAR_LIST>', additional_tar_list)
instance_type_list = ["Standard_A2", "Standard_A3", "Standard_A4", "Standard_A5", "Standard_A6", "Standard_A7", "Standard_A8", "Standard_A9", "Standard_D2", "Standard_D3", "Standard_D4", "Standard_D11", "Standard_D12", "Standard_D13", "Standard_D14", "Standard_D2_v2", "Standard_D3_v2", "Standard_D4_v2", "Standard_D5_v2", "Standard_D11_v2", "Standard_D12_v2", "Standard_D13_v2", "Standard_D14_v2", "Standard_D15_v2", "Standard_F2", "Standard_F4", "Standard_F8"]
tags = { "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }
tag_values = {"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}
api_version = "[variables('apiVersion')]"
compute_api_version = "[variables('computeApiVersion')]"
network_api_version = "[variables('networkApiVersion')]"
storage_api_version = "[variables('storageApiVersion')]"
insights_api_version = "[variables('insightsApiVersion')]"
location = "[variables('location')]"
default_payg_bw = '200m'
nic_port_map = "[variables('bigIpNicPortMap')['1'].Port]"
default_instance = "Standard_D2_v2"

# Update port map variable if deploying multi_nic template
if template_name in ('2nic'):
    nic_port_map = "[variables('bigIpNicPortMap')['2'].Port]"
if template_name in ('3nic'):
    nic_port_map = "[variables('bigIpNicPortMap')['3'].Port]"

# Update allowed instances available based on solution
if template_name in ('waf_autoscale'):
    disallowed_instance_list = ["Standard_A2", "Standard_F2"]
    for instance in disallowed_instance_list:
        instance_type_list.remove(instance)
# This solution requires a minimum of 3 nic's, some instance types only support two
if template_name in ('3nic'):
    default_instance = "Standard_D3_v2"
    disallowed_instance_list = ["Standard_A2", "Standard_D2", "Standard_D2_v2", "Standard_F2"]
    for instance in disallowed_instance_list:
        instance_type_list.remove(instance)


## Set BIG-IP versions to allow ##
default_big_ip_version = '13.0.000'
allowed_big_ip_versions = ["latest", "13.0.000"]
# Acount for difference in PAYG and BYOL in 12.1 release
if license_type == 'PAYG':
    allowed_big_ip_versions += ["12.1.22"]
elif license_type == 'BYOL':
    allowed_big_ip_versions += ["12.1.21"]
version_port_map = { "latest": { "Port": 8443 }, "13.0.000": { "Port": 8443 }, "12.1.21": { "Port": 443 }, "12.1.22": { "Port": 443 }, "443": { "Port": 443 } }

## Determine PAYG/BYOL variables
sku_to_use = "[concat('f5-bigip-virtual-edition-', variables('imageNameToLower'),'-byol')]"
offer_to_use = "f5-big-ip"
image_to_use = "[parameters('bigIpVersion')]"
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
    data['parameters']['numberOfInstances'] = {"type": "int", "defaultValue": 2, "allowedValues": [ 2 ], "metadata": { "description": "The number of BIG-IP VEs that will be deployed in front of your application" } }
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    data['parameters']['vmScaleSetMinCount'] = {"type": "int", "defaultValue": 2, "allowedValues": [1, 2, 3, 4, 5, 6], "metadata": { "description": "The minimum(and default) number of BIG-IP VEs that will be deployed into the VM Scale Set" } }
    data['parameters']['vmScaleSetMaxCount'] = {"type": "int", "defaultValue": 4, "allowedValues": [2, 3, 4, 5, 6, 7, 8], "metadata": { "description": "The number of maximum BIG-IP VEs that can be deployed into the VM Scale Set" } }
    data['parameters']['scaleOutThroughput'] = {"type": "int", "defaultValue": 90, "allowedValues": [50, 55, 60, 65, 70, 75, 80, 85, 90, 95], "metadata": { "description": "The percentange of 'Network Out' Throughput to scale out on.  This will be factored as a percentage of the F5 PAYG image bandwidth(Mbps) size chosen" } }
    data['parameters']['scaleInThroughput'] = {"type": "int", "defaultValue": 10, "allowedValues": [5, 10, 15, 20, 25, 30, 35, 40, 45], "metadata": { "description": "The percentange of 'Network Out' Throughput to scale in on.  This will be factored as a percentage of the F5 PAYG image bandwidth(Mbps) size chosen" } }
    data['parameters']['scaleTimeWindow'] = {"type": "int", "defaultValue": 10, "allowedValues": [5, 10, 15, 30], "metadata": { "description": "The time window required to trigger a scale event(up and down), this is used to determine the amount of time needed for a threshold to be breached as well as to prevent flapping" } }
data['parameters']['adminUsername'] = {"type": "string", "defaultValue": "azureuser", "metadata": {"description": "User name for the Virtual Machine"}}
data['parameters']['adminPassword'] = {"type": "securestring", "metadata": { "description": "Password to login to the Virtual Machine" } }
data['parameters']['dnsLabel'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "Unique DNS Name for the Public IP used to access the Virtual Machine" } }
if template_name in ('2nic', '3nic'):
    data['parameters']['dnsLabelPrefix'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "Unique DNS Name prefix for the Public IP(s) used to access the data plan for application traffic objects(Virtual Servers, etc...)" } }
if template_name in ('1nic', '2nic', '3nic'):
    data['parameters']['instanceName'] = {"type": "string", "defaultValue": "f5vm01", "metadata": { "description": "Name of the VM"}}
data['parameters']['instanceType'] = {"type": "string", "defaultValue": default_instance, "allowedValues": instance_type_list, "metadata": {"description": "Size of the VM"}}
data['parameters']['imageName'] = {"type": "string", "defaultValue": "Good", "allowedValues": [ "Good", "Better", "Best" ], "metadata": { "description": "F5 SKU(IMAGE) to Deploy"}}
# WAF-like templates need the 'Best' Image, stil prompt as a parameter so they are aware of what they are paying for with PAYG
if template_name in ('waf_autoscale'):
    data['parameters']['imageName'] = {"type": "string", "defaultValue": "Best", "allowedValues": [ "Best" ], "metadata": { "description": "F5 SKU(IMAGE) to Deploy, 'Best' is the only option as ASM is required"}}
data['parameters']['bigIpVersion'] = {"type": "string", "defaultValue": default_big_ip_version, "allowedValues": allowed_big_ip_versions, "metadata": { "description": "F5 BIG-IP Version to use"}}
if license_type == 'BYOL':
    data['parameters']['licenseKey1'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "The license token for the F5 BIG-IP(BYOL)" } }
    if template_name == 'cluster_base':
        for license_key in ['licenseKey2']:
            data['parameters'][license_key] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "The license token for the F5 BIG-IP(BYOL). This field is required when deploying two or more devices" } }
elif license_type == 'PAYG':
    data['parameters']['licensedBandwidth'] = {"type": "string", "defaultValue": default_payg_bw, "allowedValues": [ "25m", "200m", "1g" ], "metadata": { "description": "PAYG licensed bandwidth(Mbps) image to deploy"}}

if template_name in ('2nic', '3nic'):
    data['parameters']['numberOfExternalIps'] = {"type": "int", "defaultValue": 1, "allowedValues": [1, 2, 3, 4, 5, 6, 7, 8], "metadata": { "description": "The number of public/private IP's to deploy for the application traffic(external) nic on the BIG-IP to be used for virtual servers." } }
    if stack_type == 'new':
        data['parameters']['vnetAddressPrefix'] = {"type": "string", "defaultValue": "10.0", "metadata": { "description": "The start of the CIDR block used by the BIG-IP's when create the Vnet and subnets.  What is supplied MUST be just the first two octets of the /16 virtual network that will be created.  Such as '10.0' or 192.168', etc..." } }
if template_name in ('waf_autoscale'):
    data['parameters']['solutionDeploymentName'] = { "type": "string", "metadata": { "description": "A unique name for this deployment." } }
    data['parameters']['applicationProtocols'] = { "type": "string", "defaultValue": "http-https", "metadata": { "description": "The protocol(s) used by your application." }, "allowedValues" : [ "http", "https", "http-https", "https-offload" ] }
    data['parameters']['applicationAddress'] = { "type": "string", "metadata": { "description": "The public IP address or DNS FQDN of the application that this WAF will protect." } }
    data['parameters']['applicationServiceFqdn'] = { "type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "If deploying in front of an Azure App Service, the FQDN of the public application." } }
    data['parameters']['applicationPort'] = { "type": "string", "defaultValue": "80", "metadata": { "description": "If deploying an HTTP application, the port on which your service listens for unencrypted traffic. This field is not required when deploying https only." } }
    data['parameters']['applicationSecurePort'] = { "type": "string", "defaultValue": "443", "metadata": { "description": "If deploying an HTTPS application, the port on which your service listens for encrypted traffic. This field is not required when deploying http only." } }
    data['parameters']['sslCert'] = { "type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "The SSL certificate .pfx file corresponding to public facing VIP." } }
    data['parameters']['sslPswd'] = { "type": "securestring", "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "The SSL certificate .pfx password corresponding to the certificate provided above." } }
    data['parameters']['applicationType'] = { "type": "string", "defaultValue": "Linux", "metadata": { "description": "Is your application running on a Linux OS or a Windows OS?" }, "allowedValues": [ "Windows", "Linux" ] }
    data['parameters']['blockingLevel'] = { "type": "string", "defaultValue": "medium", "metadata": { "description": "Please select how aggressive you would like the blocking level of this WAF to be.  Remember that the more aggressive the blocking level, the more potential there is for false-positives that the WAF might detect. Select Custom to specify your own security policy below." }, "allowedValues": [ "low", "medium", "high", "off", "custom" ] }
    data['parameters']['customPolicy'] = { "type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "Specify the publicly available URL of a custom ASM security policy in XML format. This policy will be applied in place of the standard High/Medium/Low policy as indicated above." } }
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    data['parameters']['tenantId'] = { "type": "string", "metadata": { "description": "Your Azure service principal application tenant ID" } }
    data['parameters']['clientId'] = { "type": "string", "metadata": { "description": "Your Azure service principal application client ID" } }
    data['parameters']['servicePrincipalSecret'] = { "type": "securestring", "metadata": { "description": "Your Azure service principal application secret" } }

data['parameters']['restrictedSrcAddress'] = {"type": "string", "defaultValue": "*", "metadata": { "description": "Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources" } }
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
data['variables']['bigIpNicPortMap'] = { "1": { "Port": "[parameters('bigIpVersion')]" }, "2": { "Port": "443" }, "3": { "Port": "443" }, "4": { "Port": "443" }, "5": { "Port": "443" }, "6": { "Port": "443" } }
data['variables']['bigIpVersionPortMap'] = version_port_map
data['variables']['apiVersion'] = "2015-06-15"
data['variables']['computeApiVersion'] = "2015-06-15"
data['variables']['networkApiVersion'] = "2015-06-15"
data['variables']['storageApiVersion'] = "2015-06-15"
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    data['variables']['computeApiVersion'] = "2016-04-30-preview"
    data['variables']['networkApiVersion'] = "2016-06-01"
    data['variables']['storageApiVersion'] = "2015-06-15"
    data['variables']['insightsApiVersion'] = "2015-04-01"
data['variables']['location'] = "[resourceGroup().location]"
data['variables']['singleQuote'] = "'"
data['variables']['f5CloudLibsTag'] = f5_cloud_libs_tag
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    data['variables']['f5CloudLibsAzureTag'] = f5_cloud_libs_azure_tag
    data['variables']['f5NetworksTag'] = f5_networks_tag
    data['variables']['f5NetworksSolutionScripts'] = "[concat('https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/', variables('f5NetworksTag'), '/" + solution_location + "/autoscale/waf/deploy_scripts/')]"
data['variables']['verifyHash'] = '''[concat(variables('singleQuote'), 'cli script /Common/verifyHash {\nproc script::run {} {\n        if {[catch {\n            set hashes(f5-cloud-libs.tar.gz) 489d460d2e5fcd401ce12f19b1d753a6bee30483cd0bf2b7548b7f8fe3caf5b727af96f013733cbd08b0c109e0cf535a29288d473b84cc834369204d5be5edc9\n            set hashes(f5-cloud-libs-aws.tar.gz) 0b602d069a6647e8268c7afc5201259058c4df545cdee5212bf1f6c2d24b11421201282c11e047b1df9b144a012312de45a07fcf28bd0d8cd3d3a86698774925\n            set hashes(f5-cloud-libs-azure.tar.gz) 16d2ce2086883ed5b47a3ba4e79541fd1a4bb64513222cf3a459297c2474d0bfc71a161ba2b8571707e1a6b273badaaf2c847993d0e60a4b52cd8c62cb03aba6\n            set hashes(asm-policy-linux.tar.gz) 63b5c2a51ca09c43bd89af3773bbab87c71a6e7f6ad9410b229b4e0a1c483d46f1a9fff39d9944041b02ee9260724027414de592e99f4c2475415323e18a72e0\n            set hashes(f5.http.v1.2.0rc4.tmpl) 47c19a83ebfc7bd1e9e9c35f3424945ef8694aa437eedd17b6a387788d4db1396fefe445199b497064d76967b0d50238154190ca0bd73941298fc257df4dc034\n            set hashes(f5.http.v1.2.0rc6.tmpl) 811b14bffaab5ed0365f0106bb5ce5e4ec22385655ea3ac04de2a39bd9944f51e3714619dae7ca43662c956b5212228858f0592672a2579d4a87769186e2cbfe\n            set hashes(f5.http.v1.2.0rc7.tmpl) 21f413342e9a7a281a0f0e1301e745aa86af21a697d2e6fdc21dd279734936631e92f34bf1c2d2504c201f56ccd75c5c13baa2fe7653213689ec3c9e27dff77d\n            set hashes(f5.aws_advanced_ha.v1.3.0rc1.tmpl) 9e55149c010c1d395abdae3c3d2cb83ec13d31ed39424695e88680cf3ed5a013d626b326711d3d40ef2df46b72d414b4cb8e4f445ea0738dcbd25c4c843ac39d\n            set hashes(asm-policy.tar.gz) 2d39ec60d006d05d8a1567a1d8aae722419e8b062ad77d6d9a31652971e5e67bc4043d81671ba2a8b12dd229ea46d205144f75374ed4cae58cefa8f9ab6533e6\n            set hashes(deploy_waf.sh) 4db3176b45913a5e7ccf42ab9c7ac9d7de115cdbd030b9e735946f92456b6eb433087ed0e98ac4981c76d475cd38f4de49cd98c063e13d50328a270e5b3daa4a\n            set hashes(f5.policy_creator.tmpl) 54d265e0a573d3ae99864adf4e054b293644e48a54de1e19e8a6826aa32ab03bd04c7255fd9c980c3673e9cd326b0ced513665a91367add1866875e5ef3c4e3a\n\n            set file_path [lindex $tmsh::argv 1]\n            set file_name [file tail $file_path]\n\n            if {![info exists hashes($file_name)]} {\n                tmsh::log err "No hash found for $file_name"\n                exit 1\n            }\n\n            set expected_hash $hashes($file_name)\n            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n            if { $expected_hash eq $computed_hash } {\n                exit 0\n            }\n            tmsh::log err "Hash does not match for $file_path"\n            exit 1\n        }]} {\n            tmsh::log err {Unexpected error in verifyHash}\n            exit 1\n        }\n    }\n    script-signature prKQi8FeX98kCcFaMwIdwgYADdAjZo6iNTnnckguwe5IVysTEVe4vR2HPLJlDzU25dU17sQvDNIX52K0VYN4LEkAuSMeMTmr2LnlRWcGEJ4YUo9lKMdKzMzJaznlScwaR4P5mEdJC0ygq8jinOIlkauLbqmAElNtxWpb+XLnR2R83vMl/y9/LGxCxrvqE3ZuXvyuKqpAlhS+AN5ZQBDFvlTgQi52KJWpw+3i7oalz5dsjbAs2gRARtZ57Pa8OD5Oz54Q1UDxuzPVNH+CY4vt93JKmduMBsT3F41RUFDmRzosjmBY/Ic9O7oLVlKwOusDeqqqlfOM5CxcVMXwB3oxxQ==\n    signing-key /Common/f5-irule\n}', variables('singleQuote'))]'''
data['variables']['installCloudLibs'] = install_cloud_libs
data['variables']['newStorageAccountName'] = "[concat(uniquestring(resourceGroup().id), 'stor')]"
data['variables']['storageAccountType'] = "Standard_LRS"
data['variables']['dnsLabel'] = "[toLower(parameters('dnsLabel'))]"
data['variables']['imageNameToLower'] = "[toLower(parameters('imageName'))]"
data['variables']['skuToUse'] = sku_to_use
data['variables']['offerToUse'] = offer_to_use
data['variables']['bigIpNicPortValue'] = nic_port_map
data['variables']['bigIpMgmtPort'] = "[variables('bigIpVersionPortMap')[variables('bigIpNicPortValue')].Port]"
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

if template_name in ('1nic', '2nic', '3nic'):
    data['variables']['subnetPrivateAddress'] = "10.0.1.4"
    data['variables']['instanceName'] = "[toLower(parameters('instanceName'))]"
if template_name in ('2nic', '3nic'):
    data['variables']['nicName'] = "[concat(variables('dnsLabel'), '-mgmt0')]"
    data['variables']['defaultGw'] = "[concat(parameters('vnetAddressPrefix'),'.2.1')]"
    data['variables']['vnetAddressPrefix'] = "[concat(parameters('vnetAddressPrefix'),'.0.0/16')]"
    data['variables']['subnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.1.0/24')]"
    data['variables']['subnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.1.4')]"
    data['variables']['dnsLabelPrefix'] = "[toLower(parameters('dnsLabelPrefix'))]"
    data['variables']['nsg2ID'] = "[resourceId('Microsoft.Network/networkSecurityGroups/',concat(variables('dnsLabel'),'-nsg2'))]"
    data['variables']['publicIPAddressName'] = "[concat(variables('dnsLabel'), '-mgmt-pip')]"
    data['variables']['publicIPAddressNamePrefix'] = "[concat(variables('dnsLabel'), '-ext-pip')]"
    data['variables']['publicIPAddressIdPrefix'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('publicIPAddressNamePrefix'))]"
    data['variables']['extNicName'] = "[concat(variables('dnsLabel'), '-ext0')]"
    data['variables']['extSubnetName'] = "[concat(variables('dnsLabel'),'-subnet2')]"
    data['variables']['extSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('extsubnetName'))]"
    data['variables']['extSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.2.0/24')]"
    data['variables']['extSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.2.4')]"
    data['variables']['extSubnetPrivateAddressPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.2.')]"
    if template_name in ('3nic'):
        data['variables']['intNicName'] = "[concat(variables('dnsLabel'), '-int0')]"
        data['variables']['intSubnetName'] = "[concat(variables('dnsLabel'),'-subnet3')]"
        data['variables']['intSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('intsubnetName'))]"
        data['variables']['intSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.3.0/24')]"
        data['variables']['intSubnetPrivateAdress'] = "[concat(parameters('vnetAddressPrefix'), '.3.4')]"
    data['variables']['numberOfExternalIps'] = "[add(parameters('numberOfExternalIps'), 1)]"
    data['variables']['ipconfigArray'] = [{ "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": {"PublicIpAddress": { "Id": "[concat(variables('publicIPAddressIdPrefix'), 2)]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ipconfig2')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('publicIPAddressIdPrefix'), 3)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 5)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ipconfig3')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('publicIPAddressIdPrefix'), 4)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 6)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ipconfig4')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('publicIPAddressIdPrefix'), 5)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 7)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ipconfig5')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('publicIPAddressIdPrefix'), 6)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 8)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ipconfig6')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('publicIPAddressIdPrefix'), 7)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 9)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ipconfig7')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('publicIPAddressIdPrefix'), 8)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 10)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ipconfig8')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('publicIPAddressIdPrefix'), 9)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 11)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
if template_name in ('cluster_base', 'ltm_autoscale', 'waf_autoscale'):
    data['variables']['ipAddress'] = "10.0.1."
    data['variables']['loadBalancerName'] = "[concat(variables('dnsLabel'),'-alb')]"
    data['variables']['deviceNamePrefix'] = "[concat(variables('dnsLabel'),'-device')]"
    data['variables']['lbID'] = "[resourceId('Microsoft.Network/loadBalancers',variables('loadBalancerName'))]"
    data['variables']['frontEndIPConfigID'] = "[concat(variables('lbID'),'/frontendIPConfigurations/loadBalancerFrontEnd')]"
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    data['variables']['bigIpMgmtPort'] = 8443
    data['variables']['vmssName'] = "[concat(parameters('dnsLabel'),'-vmss')]"
    data['variables']['newDataStorageAccountName'] = "[concat(uniquestring(resourceGroup().id), 'data000')]"
    data['variables']['subscriptionID'] = "[subscription().subscriptionId]"
    data['variables']['25m'] = 26214400
    data['variables']['200m'] = 209715200
    data['variables']['1g'] = 1073741824
    data['variables']['scaleOutCalc'] = "[mul(variables(parameters('licensedBandwidth')), parameters('scaleOutThroughput'))]"
    data['variables']['scaleInCalc'] = "[mul(variables(parameters('licensedBandwidth')), parameters('scaleInThroughput'))]"
    data['variables']['scaleOutNetworkBits'] = "[div(variables('scaleOutCalc'), 100)]"
    data['variables']['scaleInNetworkBits'] = "[div(variables('scaleInCalc'), 100)]"
    data['variables']['scaleOutNetworkBytes'] = "[div(variables('scaleOutNetworkBits'), 8)]"
    data['variables']['scaleInNetworkBytes'] = "[div(variables('scaleInNetworkBits'), 8)]"
    data['variables']['timeWindow'] = "[concat('PT', parameters('scaleTimeWindow'), 'M')]"
if template_name in ('waf_autoscale'):
    data['variables']['lbTcpProbeNameHttp'] = "tcp_probe_http"
    data['variables']['lbTcpProbeIdHttp'] = "[concat(variables('lbID'),'/probes/',variables('lbTcpProbeNameHttp'))]"
    data['variables']['lbTcpProbeNameHttps'] = "tcp_probe_https"
    data['variables']['lbTcpProbeIdHttps'] = "[concat(variables('lbID'),'/probes/',variables('lbTcpProbeNameHttps'))]"
    data['variables']['httpBackendPort'] = 880
    data['variables']['httpsBackendPort'] = 8445
    data['variables']['commandArgs'] = "[concat('-m ', parameters('applicationProtocols'), ' -d ', parameters('solutionDeploymentName'), ' -n ', parameters('applicationAddress'), ' -j 880 -k 8445 -h ', parameters('applicationPort'), ' -s ', parameters('applicationSecurePort'), ' -t ', toLower(parameters('applicationType')), ' -l ', toLower(parameters('blockingLevel')), ' -a ', parameters('customPolicy'), ' -c ', parameters('sslCert'), ' -r ', parameters('sslPswd'), ' -o ', parameters('applicationServiceFqdn'), ' -u ', parameters('adminUsername'))]"

# Sort azuredeploy.json variables alphabetically
for variables in data['variables']:
    sorted_variable = json.dumps(data['variables'][variables], sort_keys=True, ensure_ascii=False)
    data['variables'][variables] = json.loads(sorted_variable, object_pairs_hook=OrderedDict)

########## ARM Resources ##########
resources_list = []
## Public IP Resource(s) ##
if template_name in ('1nic', '2nic', '3nic', 'cluster_base', 'ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[variables('publicIPAddressName')]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[variables('dnsLabel')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
if template_name in ('2nic', '3nic'):
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('publicIPAddressNamePrefix'), copyIndex(2))]", "copy": { "count": "[variables('numberOfExternalIps')]", "name": "pipcopy"}, "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabelPrefix'), copyIndex(1))]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]

## Virtual Network Resources(s) ##
if template_name in ('1nic', 'cluster_base'):
    subnets = [{ "name": "[variables('subnetName')]", "properties": { "addressPrefix": "[variables('subnetPrefix')]" } }]
if template_name in ('2nic'):
    subnets = [{ "name": "[variables('subnetName')]", "properties": { "addressPrefix": "[variables('subnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }]
if template_name in ('3nic'):
    subnets = [{ "name": "[variables('subnetName')]", "properties": { "addressPrefix": "[variables('subnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }, { "name": "[variables('intSubnetName')]", "properties": { "addressPrefix": "[variables('intSubnetPrefix')]" } }]
if template_name in ('1nic', '2nic', '3nic', 'cluster_base'):
    resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

if template_name in ('ltm_autoscale', 'waf_autoscale'):
    subnets = [{ "name": "[variables('subnetName')]", "properties": { "addressPrefix": "[variables('subnetPrefix')]", "networkSecurityGroup": {"id": "[variables('nsgID')]"} } }]
    resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "dependsOn": [ "[variables('nsgID')]" ], "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

## Network Interface Resource(s) ##
if template_name in ('1nic', '2nic', '3nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": [ "[variables('vnetId')]", "[variables('publicIPAddressId')]", "[variables('nsgID')]" ], "location": location, "name": "[variables('nicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[variables('nsgID')]" }, "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('subnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": { "Id": "[variables('publicIPAddressId')]" }, "subnet": { "id": "[variables('subnetId')]" } } } ] } }]
if template_name in ('2nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": [ "[variables('vnetId')]", "[concat(variables('nsg2ID'))]", "pipcopy" ], "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('nsg2ID'))]" }, "ipConfigurations": "[take(variables('ipconfigArray'),variables('numberofExternalIps'))]" } } ]
if template_name in ('3nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": [ "[variables('vnetId')]", "[concat(variables('nsg2ID'))]", "pipcopy" ], "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('nsg2ID'))]" }, "ipConfigurations": "[take(variables('ipconfigArray'),variables('numberofExternalIps'))]" } }, { "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": [ "[variables('vnetId')]" ], "location": location, "name": "[variables('intNicName')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAdress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] } } ]
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkInterfaces", "name": "[concat(variables('nicName'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/guimgt',copyindex())]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/sshmgt',copyindex())]", "[variables('nsgID')]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "niccopy" }, "properties": { "networkSecurityGroup": { "id": "[variables('nsgID')]" }, "ipConfigurations": [ { "name": "ipconfig1", "properties": { "privateIPAllocationMethod": "Static", "privateIPAddress": "[concat(variables('ipAddress'),add(4,copyindex()))]", "subnet": { "id": "[variables('subnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('lbID'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ], "loadBalancerInboundNatRules": [ { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'guimgt',copyIndex())]" }, { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'sshmgt',copyIndex())]" } ] } } ] } }]

## Network Security Group Resource(s) ##
nsg_security_rules = [{ "name": "mgmt_allow_https", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('bigIpMgmtPort')]", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "ssh_allow_22", "properties": { "description": "", "priority": 102, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }]
if template_name in ('waf_autoscale'):
    nsg_security_rules += [{ "name": "app_allow_http", "properties": { "description": "", "priority": 110, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpBackendPort')]", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "app_allow_https", "properties": { "description": "", "priority": 111, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpsBackendPort')]", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }]

if template_name in ('1nic', '2nic', '3nic', 'cluster_base', 'ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-nsg')]", "tags": tags, "properties": { "securityRules": nsg_security_rules } }]
if template_name in ('2nic', '3nic'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-nsg2')]", "tags": tags, "properties": { "securityRules": "" } }]

## Load Balancer Resource(s) ##
probes_to_use = ""; lb_rules_to_use = ""
if template_name in ('waf_autoscale'):
    probes_to_use = [ { "name": "[variables('lbTcpProbeNameHttp')]", "properties": { "protocol": "Tcp", "port": "[variables('httpBackendPort')]", "intervalInSeconds": 15, "numberOfProbes": 3 } }, { "name": "[variables('lbTcpProbeNameHttps')]", "properties": { "protocol": "Tcp", "port": "[variables('httpsBackendPort')]", "intervalInSeconds": 15, "numberOfProbes": 3 } } ]
    lb_rules_to_use = [{ "Name": "app-http", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttp')]" }, "protocol": "Tcp", "frontendPort": "[parameters('applicationPort')]", "backendPort": "[variables('httpBackendPort')]", "idleTimeoutInMinutes": 15 } }, { "Name": "app-https", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttps')]" }, "protocol": "Tcp", "frontendPort": "[parameters('applicationSecurePort')]", "backendPort": "[variables('httpsBackendPort')]", "idleTimeoutInMinutes": 15 } }]

if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": network_api_version, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('publicIPAddressName'))]" ], "location": location, "tags": tags, "name": "[variables('loadBalancerName')]", "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('publicIPAddressId')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ] }, "type": "Microsoft.Network/loadBalancers" }]
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "apiVersion": network_api_version, "name": "[variables('loadBalancerName')]", "type": "Microsoft.Network/loadBalancers", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('publicIPAddressName'))]" ], "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('publicIPAddressID')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ], "inboundNatPools": [ { "name": "sshnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPortRangeStart": 50001, "frontendPortRangeEnd": 50100, "backendPort": 22 } }, { "name": "mgmtnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPortRangeStart": 50101, "frontendPortRangeEnd": 50200, "backendPort": "[variables('bigIpMgmtPort')]" } } ], "loadBalancingRules": lb_rules_to_use, "probes": probes_to_use } }]

## Load Balancer Inbound NAT Rule(s) ##
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('loadBalancerName'),'/guimgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPort": "[copyIndex(8443)]", "backendPort": "[variables('bigIpMgmtPort')]", "enableFloatingIP": False } }]
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('loadBalancerName'),'/sshmgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPort": "[copyIndex(8022)]", "backendPort": 22, "enableFloatingIP": False } }]

## Availability Set Resource(s) ##
if template_name in ('1nic', '2nic', '3nic', 'cluster_base'):
    resources_list += [{ "apiVersion": api_version, "location": location, "name": "[variables('availabilitySetName')]", "tags": tags, "type": "Microsoft.Compute/availabilitySets" }]

## Storage Account Resource(s) ##
if template_name in ('1nic', '2nic', '3nic', 'cluster_base', 'ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "location": location, "name": "[variables('newStorageAccountName')]", "tags": tags, "properties": { "accountType": "[variables('storageAccountType')]" } }]
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "location": location, "name": "[variables('newDataStorageAccountName')]", "tags": tags, "properties": { "accountType": "[variables('storageAccountType')]" } }]

## Compute/VM Resource(s) ##
depends_on = "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('nicName'))]"
depends_on = list(depends_on)
if template_name == '1nic':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nicName'))]", "properties": { "primary": True } }]
if template_name in ('2nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]")
if template_name in ('3nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('intNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]"); depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]")
if template_name in ('1nic', '2nic', '3nic'):
    resources_list += [{"apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "dependsOn": depends_on, "location": location, "name": "[variables('instanceName')]", "tags": tags, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newStorageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  nic_reference }, "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "osProfile": { "computerName": "[variables('instanceName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'), '.blob.core.windows.net/vhds/', variables('instanceName'), '.vhd')]" } } } } }]

if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "name": "[concat(variables('deviceNamePrefix'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('nicName'), copyindex())]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "devicecopy" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "osProfile": { "computerName": "[concat(variables('deviceNamePrefix'),copyindex())]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "name": "[concat('osdisk',copyindex())]", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'),'.blob.core.windows.net/',variables('newStorageAccountName'),'/osDisk',copyindex(),'.vhd')]" }, "caching": "ReadWrite", "createOption": "FromImage" } }, "networkProfile": { "networkInterfaces": [ { "id": "[concat(resourceId('Microsoft.Network/networkInterfaces',variables('nicName')),copyindex())]" } ] }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newstorageAccountName'),'.blob.core.windows.net')]" } } } }]

## Compute/VM Extension Resource(s) ##
command_to_execute = ''; command_to_execute2 = ''
if template_name == '1nic':
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('subnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp pool.ntp.org --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; rm -f /config/cloud/passwd')]"
if template_name == '2nic':
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('subnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp pool.ntp.org --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('subnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --default-gw ', variables('defaultGw'), ' --vlan name:external,nic:1.1 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), ',vlan:external --log-level debug; rm -f /config/cloud/passwd')]"
if template_name == '3nic':
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('subnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp pool.ntp.org --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('subnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --default-gw ', variables('defaultGw'), ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAdress'), ',vlan:internal --log-level debug; rm -f /config/cloud/passwd')]"
if template_name == 'cluster_base':
    # Two Extensions for Cluster
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('ipAddress'), 4), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), <LICENSE1_COMMAND> ' --ntp pool.ntp.org --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('ipAddress'), 4), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('ipAddress'), 4), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), ' --auto-sync --save-on-auto-sync; rm -f /config/cloud/passwd')]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('ipAddress'), 5), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), copyindex(1), '.azuresecurity.com'), <LICENSE2_COMMAND> ' --ntp pool.ntp.org --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('ipAddress'), 5), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('ipAddress'), 5), ' --join-group --device-group Sync --sync --remote-host ', concat(variables('ipAddress'), 4), ' --remote-user admin --remote-password-url file:///config/cloud/passwd; rm -f /config/cloud/passwd')]"
# Base command to execute
base_cmd_to_execute = "'mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; mkdir -p /config/cloud/node_modules; BIG_IP_CREDENTIALS_FILE=/config/cloud/passwd; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null $BIG_IP_CREDENTIALS_FILE; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), ' >> $BIG_IP_CREDENTIALS_FILE; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host '"
command_to_execute = command_to_execute.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute)
command_to_execute2 = command_to_execute2.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute)
# String map license 1/2 if needed for BYOL
command_to_execute = command_to_execute.replace('<LICENSE1_COMMAND>', license1_command)
command_to_execute2 = command_to_execute2.replace('<LICENSE2_COMMAND>', license2_command)

if template_name in ('1nic', '2nic', '3nic'):
    resources_list += [{"apiVersion": "2016-03-30", "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('instanceName'),'/start')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('instanceName'))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
if template_name == 'cluster_base':
    # Two Extensions for Cluster
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('deviceNamePrefix'),0,'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),0)]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "copy": { "name": "extensionLoop", "count": "[sub(parameters('numberOfInstances'), 1)]" }, "name": "[concat(variables('deviceNamePrefix'),add(copyindex(),1),'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),add(copyindex(),1))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute2 } } }]

## Compute VM Scale Set(s) ##
autoscale_file_uris = [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/dist/f5-cloud-libs-azure.tar.gz')]" ]
if template_name in ('ltm_autoscale'):
    scale_script_call = "bash /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/autoscale.sh --resourceGroup ', resourceGroup().name, ' --vmssName ', variables('vmssName'), ' --userName ', parameters('adminUsername'), ' --password $BIG_IP_CREDENTIALS_FILE --azureSecretFile $AZURE_CREDENTIALS_FILE --managementPort ', variables('bigIpMgmtPort')"
if template_name in ('waf_autoscale'):
    scale_script_call = "bash /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/autoscalewaf.sh --resourceGroup ', resourceGroup().name, ' --vmssName ', variables('vmssName'), ' --userName ', parameters('adminUsername'), ' --password $BIG_IP_CREDENTIALS_FILE --azureSecretFile $AZURE_CREDENTIALS_FILE --managementPort ', variables('bigIpMgmtPort'), ' --wafScriptArgs ', variables('singleQuote'), variables('commandArgs'), variables('singleQuote')"
    autoscale_file_uris += [ "[concat(variables('f5NetworksSolutionScripts'), 'deploy_waf.sh')]", "[concat(variables('f5NetworksSolutionScripts'), 'f5.http.v1.2.0rc7.tmpl')]", "[concat(variables('f5NetworksSolutionScripts'), 'f5.policy_creator.tmpl')]", "[concat(variables('f5NetworksSolutionScripts'), 'asm-policy.tar.gz')]" ]

if template_name in ('ltm_autoscale', 'waf_autoscale'):
    autoscale_command_to_execute = "[concat('mkdir -p /config/cloud/node_modules; AZURE_CREDENTIALS_FILE=/config/cloud/azCredentials; BIG_IP_CREDENTIALS_FILE=/config/cloud/passwd; /usr/bin/install -m 400 /dev/null $AZURE_CREDENTIALS_FILE; /usr/bin/install -m 400 /dev/null $BIG_IP_CREDENTIALS_FILE; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), ' > $BIG_IP_CREDENTIALS_FILE; echo ', variables('singleQuote'), '{\"clientId\": \"', parameters('clientId'), '\", \"tenantId\": \"', parameters('tenantId'), '\", \"secret\": \"', parameters('servicePrincipalSecret'), '\", \"subscriptionId\": \"', variables('subscriptionID'), '\", \"storageAccount\": \"', variables('newDataStorageAccountName'), '\", \"storageKey\": \"', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('newDataStorageAccountName')), variables('storageApiVersion')).key1, '\"}', variables('singleQuote'), ' > $AZURE_CREDENTIALS_FILE; cp f5-cloud-libs*.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; bash /config/installCloudLibs.sh; <SCALE_SCRIPT_CALL>)]"
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<SCALE_SCRIPT_CALL>', scale_script_call)

if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Compute/virtualMachineScaleSets", "apiVersion": compute_api_version, "name": "[variables('vmssName')]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]" ], "sku": { "name": "[parameters('instanceType')]", "tier": "Standard", "capacity": "[parameters('vmScaleSetMinCount')]" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "upgradePolicy": { "mode": "Manual" }, "virtualMachineProfile": { "storageProfile": { "osDisk": { "vhdContainers": [ "[concat('https://', variables('newStorageAccountName'), '.blob.core.windows.net/vmss1')]" ], "name": "vmssosdisk", "caching": "ReadOnly", "createOption": "FromImage" }, "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use } }, "osProfile": { "computerNamePrefix": "[variables('vmssName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "networkProfile": { "networkInterfaceConfigurations": [ { "name": "nic1", "properties": { "primary": "true", "ipConfigurations": [ { "name": "ip1", "properties": { "subnet": { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'), '/subnets/', variables('subnetName'))]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/backendAddressPools/loadBalancerBackEnd')]" } ], "loadBalancerInboundNatPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/sshnatpool')]" }, { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/mgmtnatpool')]" } ] } } ] } } ] }, "extensionProfile": { "extensions": [ { "name":"main", "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": autoscale_file_uris }, "protectedSettings": { "commandToExecute": autoscale_command_to_execute } } } ] } }, "overprovision": "false" } }]

## Compute VM Scale Set(s) AutoScale Settings ##
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Insights/autoscaleSettings", "apiVersion": "[variables('insightsApiVersion')]", "name": "autoscaleconfig", "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]" ], "properties": { "name": "autoscaleconfig", "targetResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "enabled": True, "profiles": [ { "name": "Profile1", "capacity": { "minimum": "[parameters('vmScaleSetMinCount')]", "maximum": "[parameters('vmScaleSetMaxCount')]", "default": "[parameters('vmScaleSetMinCount')]" }, "rules": [ { "metricTrigger": { "metricName": "Network Out", "metricNamespace": "", "metricResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('timeWindow')]", "timeAggregation": "Average", "operator": "GreaterThan", "threshold": "[variables('scaleOutNetworkBytes')]" }, "scaleAction": { "direction": "Increase", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } }, { "metricTrigger": { "metricName": "Network Out", "metricNamespace": "", "metricResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('timeWindow')]", "timeAggregation": "Average", "operator": "LessThan", "threshold": "[variables('scaleInNetworkBytes')]" }, "scaleAction": { "direction": "Decrease", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } } ], "notifications": [ { "operation": "Scale", "email": { "sendToSubscriptionAdministrator": False, "sendToSubscriptionCoAdministrators": False, "customEmails": "" } } ] } ] } }]


## Sort resources section - Expand to choose order of resources instead of just alphabetical?
temp_sort = 'temp_sort.json'
with open(temp_sort, 'w') as temp_sorting:
    json.dump(resources_list, temp_sorting, sort_keys=True, indent=4, ensure_ascii=False)
with open(temp_sort, 'r') as temp_sorted:
    data['resources'] = json.load(temp_sorted, object_pairs_hook=OrderedDict)
    temp_sorted.close(); os.remove(temp_sort)

########## ARM Outputs ##########
if template_name in ('1nic', '2nic', '3nic'):
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://', variables('dnsLabel'), '.', resourceGroup().location, '.cloudapp.azure.com', ':', variables('bigIpMgmtPort'))]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(variables('dnsLabel'), '.', resourceGroup().location, '.cloudapp.azure.com', ' ',22)]" }
if template_name == 'cluster_base':
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('publicIPAddressId')).dnsSettings.fqdn,':8443')]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('publicIPAddressId')).dnsSettings.fqdn,' ',8022)]" }
if template_name in ('ltm_autoscale', 'waf_autoscale'):
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
        param_str = ''; mandatory_cmd = ''; default_value = ''; payg_cmd = ''; byol_cmd = ''; pwd_cmd = ''; sps_cmd = ''; ssl_pwd_cmd = ''; license2_param = ''
        if language == 'powershell':
            deploy_cmd_params = ''; script_dash = ' -'
            meta_script = 'base.deploy_via_ps.ps1'; script_loc = script_location + 'Deploy_via_PS.ps1'
            base_ex = '## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth ' + default_payg_bw
            license2_param = ''
        elif language == 'bash':
            deploy_cmd_params = '"{'; script_dash = ' --'; license_check = ''; license2_check = ''
            meta_script = 'base.deploy_via_bash.sh'; script_loc = script_location + 'deploy_via_bash.sh'
            base_ex = '## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth ' + default_payg_bw
            getopt_start = 'ARGS=`getopt -o '; getopt_params_long = ' --long ';  getopt_end = ' -n $0 -- "$@"`'
            getopt_params_short = 'a:b:c:d:'; base_params = 'resourceGroupName:,azureLoginUser:,azureLoginPassword:,licenseType:,'
            mandatory_variables = ''; license_params = ''
            bash_shorthand_args = ['e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','aa','bb','cc','dd','ee','ff','gg','hh','ii','jj','kk','ll']
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
                elif parameter[0] == 'sslPswd':
                    deploy_cmd_params += '-' + parameter[0] + ' $sslpwd '
                    ssl_pwd_cmd = '\n$sslpwd = ConvertTo-SecureString -String $sslPswd -AsPlainText -Force'
                else:
                    deploy_cmd_params += '-' + parameter[0] + ' "$' + parameter[0] + '" '
            elif language == 'bash':
                # Handle bash quoting for int's in ARM template create command
                if type(parameter[1]) == int:
                    deploy_cmd_params += '\\"' + parameter[0] + '\\":{\\"value\\":$' + parameter[0] + '},'
                else:
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
                base_ex += script_dash + named_param + ' ' + '<value> '
            if template_name in ('1nic', '2nic', '3nic'):
                byol_cmd =  deploy_cmd_params + ' -licenseKey1 "$licenseKey1"'
                payg_cmd = deploy_cmd_params + ' -licensedBandwidth "$licensedBandwidth"'
            elif template_name in ('cluster_base'):
                byol_cmd = deploy_cmd_params + ' -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2"'
                payg_cmd = deploy_cmd_params + ' -licensedBandwidth "$licensedBandwidth"'
            base_deploy = '$deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose '
            deploy_cmd = 'if ($licenseType -eq "BYOL") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BYOL\\azuredeploy.json"; $parametersFilePath = ".\BYOL\\azuredeploy.parameters.json" }\n  ' + base_deploy + byol_cmd + '\n} elseif ($licenseType -eq "PAYG") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\\azuredeploy.json"; $parametersFilePath = ".\PAYG\\azuredeploy.parameters.json" }\n  ' + base_deploy + payg_cmd + '\n} else {\n  Write-Error -Message "Please select a valid license type of PAYG or BYOL."\n}'
            if template_name in ('ltm_autoscale', 'waf_autoscale'):
                deploy_cmd = base_deploy + deploy_cmd_params + ' -licensedBandwidth "$licensedBandwidth"'
        elif language == 'bash':
            license_check = '# Prompt for license key if not supplied and BYOL is selected\nif [ $licenseType == "BYOL" ]; then\n    if [ -v $licenseKey1 ] ; then\n            read -p "Please enter value for licenseKey1:" licenseKey1\n    fi\n' + license2_check + '    template_file="./BYOL/azuredeploy.json"\n    parameter_file="./BYOL/azuredeploy.parameters.json"\nfi\n'
            license_check += '# Prompt for licensed bandwidth if not supplied and PAYG is selected\nif [ $licenseType == "PAYG" ]; then\n    if [ -v $licensedBandwidth ] ; then\n            read -p "Please enter value for licensedBandwidth:" licensedBandwidth\n    fi\n    template_file="./PAYG/azuredeploy.json"\n    parameter_file="./PAYG/azuredeploy.parameters.json"\nfi'
            # Right now auto scale is only PAYG
            if template_name in ('ltm_autoscale', 'waf_autoscale'):
                license_check = '# Prompt for licensed bandwidth if not supplied and PAYG is selected\nif [ $licenseType == "PAYG" ]; then\n    if [ -v $licensedBandwidth ] ; then\n            read -p "Please enter value for licensedBandwidth:" licensedBandwidth\n    fi\n    template_file="./azuredeploy.json"\n    parameter_file="./azuredeploy.parameters.json"\nfi'
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
            if template_name in ('1nic', '2nic', '3nic'):
                byol_cmd =  create_cmd + deploy_cmd_params + '\\"licenseKey1\\":{\\"value\\":\\"$licenseKey1\\"}}"'
                payg_cmd = create_cmd + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
            if template_name in ('cluster_base'):
                byol_cmd = create_cmd + deploy_cmd_params + '\\"licenseKey1\\":{\\"value\\":\\"$licenseKey1\\"},\\"licenseKey2\\":{\\"value\\":\\"$licenseKey2\\"}}"'
                payg_cmd = create_cmd + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
            deploy_cmd = 'if [ $licenseType == "BYOL" ]; then\n    ' + byol_cmd + '\nelif [ $licenseType == "PAYG" ]; then\n    ' + payg_cmd + '\nelse\n    echo "Please select a valid license type of PAYG or BYOL."\n    exit 1\nfi'
            if template_name in ('ltm_autoscale', 'waf_autoscale'):
                deploy_cmd = create_cmd + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
        # Map necessary script items, handle encoding
        ex_cmd = base_ex.encode("utf8")
        param_str = param_str.encode("utf8")
        # Map script as needed
        script_str = script_str.replace('<EXAMPLE_CMD>', ex_cmd)
        script_str = script_str.replace('<DEPLOYMENT_CREATE>', deploy_cmd)
        script_str = script_str.replace('<PWD_CMD>', pwd_cmd)
        script_str = script_str.replace('<SPS_CMD>', sps_cmd)
        script_str = script_str.replace('<SSL_PWD_CMD>', ssl_pwd_cmd)
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
    if template_name in ('1nic', '2nic', '3nic', 'cluster_base', 'ltm_autoscale', 'waf_autoscale'):
        for script_language in ('powershell', 'bash'):
            script_creation(script_language)
############### END Create/Modify Scripts ###############