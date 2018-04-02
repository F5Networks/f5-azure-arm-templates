#/usr/bin/python env
import sys
import os
import json
from collections import OrderedDict
from optparse import OptionParser
import master_helper
import script_generator
import readme_generator

# Process Script Parameters
parser = OptionParser()
parser.add_option("-n", "--template-name", action="store", type="string", dest="template_name", help="Template Name: standalone_1nic, standalone_2nic, failover-lb_1nic, etc.")
parser.add_option("-l", "--license-type", action="store", type="string", dest="license_type", help="License Type: BYOL or PAYG")
parser.add_option("-m", "--stack-type", action="store", type="string", dest="stack_type", default="new_stack", help="Networking Stack Type: new_stack, existing_stack or prod_stack.")
parser.add_option("-t", "--template-location", action="store", type="string", dest="template_location", help="Template Location: such as ../experimental/standalone/1nic/PAYG/")
parser.add_option("-s", "--script-location", action="store", type="string", dest="script_location", help="Script Location: such as ../experimental/standalone/1nic/")
parser.add_option("-v", "--solution-location", action="store", type="string", dest="solution_location", default="experimental", help="Solution location: experimental or supported")
parser.add_option("-r", "--release-prep", action="store_true", dest="release_prep", default=False, help="Release Prep Flag: If passed will equal True.")

(options, args) = parser.parse_args()
template_name = options.template_name
license_type = options.license_type
stack_type = options.stack_type
template_location = options.template_location
script_location = options.script_location
solution_location = options.solution_location
release_prep = options.release_prep

## Specify meta file and file to create(should be argument)
metafile = 'files/tmpl_files/base.azuredeploy.json'
metafile_params = 'files/tmpl_files/base.azuredeploy.parameters.json'
created_file = template_location + 'azuredeploy.json'
created_file_params = template_location + 'azuredeploy.parameters.json'

## Static Variable Defaults
nic_reference = ""
command_to_execute = ""
route_add_cmd = ""

## Static Variable Assignment ##
content_version = '5.0.0.0'
f5_networks_tag = 'develop'
f5_cloud_libs_tag = 'release-4.0.0'
f5_cloud_libs_azure_tag = 'release-2.0.0'
f5_cloud_iapps_tag = 'release-2.0.0'
f5_cloud_workers_tag = 'v1.0.0'
# Set BIG-IP versions to allow
default_big_ip_version = '13.1.0200'
allowed_big_ip_versions = ["13.1.0200", "12.1.303000", "latest"]
version_port_map = {"latest": {"Port": 8443}, "13.1.0200": {"Port": 8443}, "12.1.303000": {"Port": 443}, "443": {"Port": 443}}
route_cmd_array = {"latest": "route", "13.1.0200": "route", "12.1.303000": "[concat('tmsh create sys management-route waagent_route network 168.63.129.16/32 gateway ', variables('mgmtRouteGw'), '; tmsh save sys config')]"}
network_mtu_array = {"12.1.303000": "[concat('tmsh modify net vlan internal mtu 1400; RUN_NETWORK=0; EXT_ROUTE=\"\"')]",
    "13.1.0200": "[concat('tmsh modify sys global-settings mgmt-dhcp disabled; tmsh save sys config; RUN_NETWORK=1; EXT_ROUTE=\"--route name:ext_route,gw:', variables('mgmtRouteGw'), ',network:168.63.129.16/32\"')]",
    "latest": "[concat('tmsh modify sys global-settings mgmt-dhcp disabled; tmsh save sys config; RUN_NETWORK=1; EXT_ROUTE=\"--route name:ext_route,gw:', variables('mgmtRouteGw'), ',network:168.63.129.16/32\"')]"
    }

install_cloud_libs = """[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit 1\nfi\necho loaded verifyHash\n\nconfig_loc="/config/cloud/"\nhashed_file_list="<HASHED_FILE_LIST>"\nfor file in $hashed_file_list; do\necho "verifying $file"\n/usr/bin/tmsh run cli script verifyHash $file\nif [ $? != 0 ]; then\necho "$file is not valid"\nexit 1\nfi\necho "verified $file"\ndone\necho "expanding $hashed_file_list"\ntar xfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/azure/node_modules/@f5devcentral\n<TAR_LIST>touch /config/cloud/cloudLibsReady', variables('singleQuote'))]"""

# Automate Verify Hash - the verify_hash function will go out and pull in the latest hash file
# if release-prep flag is included.  Otherwise it will pull from local verifyHash file
verify_hash = '''[concat(variables('singleQuote'), '<CLI_SCRIPT>', variables('singleQuote'))]'''
verify_hash_url = "https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/" + f5_cloud_libs_tag + "/dist/verifyHash"
verify_hash = verify_hash.replace('<CLI_SCRIPT>', master_helper.verify_hash(verify_hash_url, release_prep))

hashed_file_list = "${config_loc}f5-cloud-libs.tar.gz f5.service_discovery.tmpl f5.cloud_logger.v1.0.0.tmpl"
additional_tar_list = ""
if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'failover-api'):
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz"
    additional_tar_list = "tar xfz /config/cloud/f5-cloud-libs-azure.tar.gz -C /config/cloud/azure/node_modules/@f5devcentral\n"
elif template_name in ('autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz deploy_waf.sh f5.http.v1.2.0rc7.tmpl f5.policy_creator.tmpl asm-policy.tar.gz"
    additional_tar_list = "tar xfz /config/cloud/f5-cloud-libs-azure.tar.gz -C /config/cloud/azure/node_modules/@f5devcentral\n"

#### Empty hashed file list when testing new code ####
hashed_file_list = ""
######################################################
install_cloud_libs = install_cloud_libs.replace('<HASHED_FILE_LIST>', hashed_file_list)
install_cloud_libs = install_cloud_libs.replace('<TAR_LIST>', additional_tar_list)
instance_type_list = ["Standard_A2", "Standard_A3", "Standard_A4", "Standard_A5", "Standard_A6", "Standard_A7", "Standard_D2", "Standard_D3", "Standard_D4", "Standard_D11", "Standard_D12", "Standard_D13", "Standard_D14", "Standard_DS2", "Standard_DS3", "Standard_DS4", "Standard_DS11", "Standard_DS12", "Standard_DS13", "Standard_DS14", "Standard_D2_v2", "Standard_D3_v2", "Standard_D4_v2", "Standard_D5_v2", "Standard_D11_v2", "Standard_D12_v2", "Standard_D13_v2", "Standard_D14_v2", "Standard_D15_v2", "Standard_DS2_v2", "Standard_DS3_v2", "Standard_DS4_v2", "Standard_DS5_v2", "Standard_DS11_v2", "Standard_DS12_v2", "Standard_DS13_v2", "Standard_DS14_v2", "Standard_DS15_v2", "Standard_F2", "Standard_F4", "Standard_F8", "Standard_F2S", "Standard_F4S", "Standard_F8S", "Standard_F16S", "Standard_G2", "Standard_G3", "Standard_G4", "Standard_G5", "Standard_GS2", "Standard_GS3", "Standard_GS4", "Standard_GS5"]
tags = "[if(empty(variables('tagValues')), json('null'), variables('tagValues'))]"
static_vmss_tags = "[if(empty(variables('tagValues')), union(json('{}'), variables('staticVmssTagValues')), union(variables('tagValues'), variables('staticVmssTagValues')))]"
tag_values = {"application":"APP", "environment":"ENV", "group":"GROUP", "owner":"OWNER", "cost":"COST"}
api_version = "[variables('apiVersion')]"
compute_api_version = "[variables('computeApiVersion')]"
network_api_version = "[variables('networkApiVersion')]"
storage_api_version = "[variables('storageApiVersion')]"
location = "[variables('location')]"
default_payg_bw = '200m'
nic_port_map = "[variables('bigIpNicPortMap')['1'].Port]"
default_instance = "Standard_DS2_v2"

## Update port map variable if deploying n-nic template
if template_name in 'standalone_2nic':
    nic_port_map = "[variables('bigIpNicPortMap')['2'].Port]"
if template_name in ('standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_3nic'):
    nic_port_map = "[variables('bigIpNicPortMap')['3'].Port]"

## Update allowed instances available based on solution
disallowed_instance_list = []
if template_name in ('autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    disallowed_instance_list = ["Standard_A2", "Standard_F2"]
if template_name in ('standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_3nic'):
    default_instance = "Standard_DS3_v2"
    disallowed_instance_list = ["Standard_A2", "Standard_D2", "Standard_DS2", "Standard_D2_v2", "Standard_DS2_v2", "Standard_F2", "Standard_F2S", "Standard_G2", "Standard_GS2"]
for instance in disallowed_instance_list:
    instance_type_list.remove(instance)

## Determine if learning stack and set flags ##
learning_stack = False
if stack_type in ('learning_stack'):
    learning_stack = True
    stack_type = 'new_stack'
    
## Set stack mask commands ##
ext_mask_cmd = ''
int_mask_cmd = ''
if stack_type in ('existing_stack', 'prod_stack'):
    if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_3nic'):
        ext_mask_cmd = "skip(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, indexOf(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, '/')),"
    if template_name in ('standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_3nic'):
        int_mask_cmd = "skip(reference(variables('intSubnetRef'), variables('networkApiVersion')).addressPrefix, indexOf(reference(variables('intSubnetRef'), variables('networkApiVersion')).addressPrefix, '/')),"

## Determine PAYG/BYOL/BIGIQ variables
image_to_use = "[parameters('bigIpVersion')]"
byol_sku_to_use = "[concat('f5-bigip-virtual-edition-', variables('imageNameToLower'),'-byol')]"
byol_offer_to_use = "[concat('f5-big-ip-', variables('imageNameToLower'), '-preview')]"
payg_sku_to_use = "[concat('f5-bigip-virtual-edition-', parameters('licensedBandwidth'), '-', variables('imageNameToLower'),'-hourly')]"
payg_offer_to_use = "[concat('f5-big-ip-', variables('imageNameToLower'), '-preview')]"
license1_command = ''
license2_command = ''
big_iq_pwd_cmd = ''
bigiq_pwd_delete = ''
if license_type == 'BYOL':
    sku_to_use = byol_sku_to_use
    offer_to_use = byol_offer_to_use
    license1_command = "' --license ', parameters('licenseKey1'),"
    license2_command = "' --license ', parameters('licenseKey2'),"
elif license_type == 'PAYG':
    sku_to_use = payg_sku_to_use
    offer_to_use = payg_offer_to_use
elif license_type == 'BIGIQ' or license_type == 'BIGIQ_PAYG':
    if license_type == 'BIGIQ':
        sku_to_use = byol_sku_to_use
        offer_to_use = byol_offer_to_use
    elif license_type == 'BIGIQ_PAYG':
        sku_to_use = payg_sku_to_use
        offer_to_use = payg_offer_to_use
    big_iq_mgmt_ip_ref = ''
    big_iq_mgmt_ip_ref2 = ''
    big_iq_pwd_cmd = " echo ', variables('singleQuote'), parameters('bigIqLicensePassword'), variables('singleQuote'), ' >> /config/cloud/.bigIqPasswd; "
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
        big_iq_mgmt_ip_ref =  "reference(variables('mgmtPublicIPAddressId')).ipAddress,"
    if template_name in ('failover-lb_1nic'):
        big_iq_mgmt_ip_ref =  "reference(variables('mgmtPublicIPAddressId')).ipAddress, ' --big-ip-mgmt-port 8443',"
        big_iq_mgmt_ip_ref2 =  "reference(variables('mgmtPublicIPAddressId')).ipAddress, ' --big-ip-mgmt-port 8444',"
    if template_name in ('failover-api', 'failover-lb_3nic'):
        big_iq_mgmt_ip_ref =  "reference(concat(variables('mgmtPublicIPAddressId'), '0')).ipAddress,"
        big_iq_mgmt_ip_ref2 =  "reference(concat(variables('mgmtPublicIPAddressId'), '1')).ipAddress,"
    license1_command = "' --license-pool --big-iq-host ', parameters('bigIqLicenseHost'), ' --big-iq-user ', parameters('bigIqLicenseUsername'), ' --big-iq-password-uri file:///config/cloud/.bigIqPasswd --license-pool-name ', parameters('bigIqLicensePool'), ' --big-ip-mgmt-address ', " + big_iq_mgmt_ip_ref
    license2_command = "' --license-pool --big-iq-host ', parameters('bigIqLicenseHost'), ' --big-iq-user ', parameters('bigIqLicenseUsername'), ' --big-iq-password-uri file:///config/cloud/.bigIqPasswd --license-pool-name ', parameters('bigIqLicensePool'), ' --big-ip-mgmt-address ', " + big_iq_mgmt_ip_ref2
    bigiq_pwd_delete = ' rm -f /config/cloud/.bigIqPasswd;'
    if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
        if license_type == 'BIGIQ_PAYG':
            # Dynamic VMSS (PAYG)
            license1_command =  ", ' --externalTag key:f5ClusterTag,value:', variables('dnsLabel')"
            # Static VMSS
            static_license1_command =  ", ' --bigIqLicenseHost ', parameters('bigIqLicenseHost'), ' --bigIqLicenseUsername ', parameters('bigIqLicenseUsername'), ' --bigIqLicensePassword /config/cloud/.bigIqPasswd --bigIqLicensePool ', parameters('bigIqLicensePool'), ' --bigIpExtMgmtAddress ', reference(variables('mgmtPublicIPAddressId')).ipAddress, ' --bigIpExtMgmtPort via-api --static --natBase mgmtnatpool-static. --externalTag key:f5ClusterTag,value:', variables('dnsLabel')"
        else:
            license1_command =  ", ' --bigIqLicenseHost ', parameters('bigIqLicenseHost'), ' --bigIqLicenseUsername ', parameters('bigIqLicenseUsername'), ' --bigIqLicensePassword /config/cloud/.bigIqPasswd --bigIqLicensePool ', parameters('bigIqLicensePool'), ' --bigIpExtMgmtAddress ', reference(variables('mgmtPublicIPAddressId')).ipAddress, ' --bigIpExtMgmtPort via-api'"
        
        # Need to keep BIG-IQ password around in autoscale case for license revocation
        bigiq_pwd_delete = ''

## Check if supported or experimental
if 'supported' in created_file:
    support_type = 'supported'
else:
    support_type = 'experimental'

## Load "Meta File(s)" for modification ##
with open(metafile, 'r') as base:
    data = json.load(base, object_pairs_hook=OrderedDict)
with open(metafile_params, 'r') as base_params:
    data_params = json.load(base_params, object_pairs_hook=OrderedDict)

######################################## Create/Modify ARM Objects ########################################
data['contentVersion'] = content_version
data_params['contentVersion'] = content_version

######################################## ARM Parameters ########################################
## Pulling in a base set of variables and setting order with below call, it is a function of master_helper.py
master_helper.parameter_initialize(data)
## Set default parameters for all templates
data['parameters']['adminUsername'] = {"type": "string", "defaultValue": "azureuser", "metadata": {"description": ""}}
data['parameters']['adminPassword'] = {"type": "securestring", "metadata": {"description": ""}}
if stack_type not in ('prod_stack'):
    data['parameters']['dnsLabel'] = {"type": "string", "defaultValue": "", "metadata": {"description": ""}}
data['parameters']['instanceType'] = {"type": "string", "defaultValue": default_instance, "allowedValues": instance_type_list, "metadata": {"description": ""}}
data['parameters']['imageName'] = {"type": "string", "defaultValue": "Good", "allowedValues": ["Good", "Better", "Best"], "metadata": {"description": ""}}
data['parameters']['bigIpVersion'] = {"type": "string", "defaultValue": default_big_ip_version, "allowedValues": allowed_big_ip_versions, "metadata": {"description": ""}}
if license_type == 'BYOL':
    data['parameters']['licenseKey1'] = {"type": "string", "defaultValue": "", "metadata": {"description": ""}}
    if template_name in ('failover-lb_1nic', 'failover-lb_3nic', 'failover-api'):
        for license_key in ['licenseKey2']:
            data['parameters'][license_key] = {"type": "string", "defaultValue": "", "metadata": {"description": ""}}
if license_type == 'PAYG' or license_type == 'BIGIQ_PAYG':
    data['parameters']['licensedBandwidth'] = {"type": "string", "defaultValue": default_payg_bw, "allowedValues": ["25m", "200m", "1g"], "metadata": {"description": ""}}
if license_type == 'BIGIQ' or license_type == 'BIGIQ_PAYG':
    data['parameters']['bigIqLicenseHost'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['bigIqLicenseUsername'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['bigIqLicensePassword'] = {"type": "securestring", "metadata": {"description": ""}}
    data['parameters']['bigIqLicensePool'] = {"type": "string", "metadata": {"description": ""}}
    if license_type == 'BIGIQ_PAYG':
        data['parameters']['numberOfStaticInstances'] = {"type": "int", "allowedValues": [1, 2, 3, 4], "metadata": {"description": ""}}
data['parameters']['ntpServer'] = {"type": "string", "defaultValue": "0.pool.ntp.org", "metadata": {"description": ""}}
data['parameters']['timeZone'] = {"type": "string", "defaultValue": "UTC", "metadata": {"description": ""}}
data['parameters']['restrictedSrcAddress'] = {"type": "string", "defaultValue": "*", "metadata": {"description": ""}}
data['parameters']['tagValues'] = {"type": "object", "defaultValue": tag_values, "metadata": {"description": ""}}
data['parameters']['allowUsageAnalytics'] = {"type": "string", "defaultValue": "Yes", "allowedValues": ["Yes", "No"], "metadata": {"description": ""}}

# Set new_stack/existing_stack/prod_stack parameters for templates
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
    data['parameters']['instanceName'] = {"type": "string", "defaultValue": "f5vm01", "metadata": {"description": ""}}
if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
    data['parameters']['numberOfExternalIps'] = {"type": "int", "defaultValue": 1, "allowedValues": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "metadata": {"description": ""}}
if template_name in ('failover-lb_3nic'):
    data['parameters']['enableNetworkFailover'] = {"allowedValues": [ "No", "Yes" ], "defaultValue": "Yes", "metadata": { "description": "" }, "type": "string"}
    data['parameters']['internalLoadBalancerType'] = {"defaultValue": "Per-protocol", "allowedValues": ["Per-protocol", "All-protocol", "DO_NOT_USE"], "metadata": { "description": "" }, "type": "string"}
    data['parameters']['internalLoadBalancerProbePort'] = {"defaultValue": "3456", "metadata": { "description": "" }, "type": "string"}
if stack_type == 'new_stack':
    data['parameters']['vnetAddressPrefix'] = {"type": "string", "defaultValue": "10.0", "metadata": {"description": ""}}
elif stack_type in ('existing_stack', 'prod_stack'):
    data['parameters']['vnetName'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['vnetResourceGroupName'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['mgmtSubnetName'] = {"type": "string", "metadata": {"description": ""}}
    if template_name in ('failover-api', 'failover-lb_1nic', 'failover-lb_3nic'):
        data['parameters']['mgmtIpAddressRangeStart'] = {"metadata": {"description": ""}, "type": "string"}
    elif template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
        # Auto Scale(VM Scale Set) solutions get the IP address dynamically
        pass
    else:
        data['parameters']['mgmtIpAddress'] = {"type": "string", "metadata": {"description": ""}}
    if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
        data['parameters']['externalSubnetName'] = {"type": "string", "metadata": {"description": ""}}
        if template_name in ('failover-api', 'failover-lb_3nic'):
            data['parameters']['externalIpSelfAddressRangeStart'] = {"metadata": {"description": ""}, "type": "string"}
            data['parameters']['externalIpAddressRangeStart'] = {"type": "string", "metadata": {"description": ""}}
        else:
            data['parameters']['externalIpAddressRangeStart'] = {"type": "string", "metadata": {"description": ""}}
    if template_name in ('standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_3nic'):
        data['parameters']['internalSubnetName'] = {"type": "string", "metadata": {"description": ""}}
        if template_name in ('failover-api', 'failover-lb_3nic'):
            data['parameters']['internalIpAddressRangeStart'] = {"type": "string", "metadata": {"description": ""}}
        else:
            data['parameters']['internalIpAddress'] = {"type": "string", "metadata": {"description": ""}}
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
        data['parameters']['avSetChoice'] = {"defaultValue": "CREATE_NEW", "metadata": {"description": ""}, "type": "string"}
if stack_type in ('prod_stack'):
    data['parameters']['uniqueLabel'] = {"type": "string", "defaultValue": "", "metadata": {"description": ""}}

# Set unique solution parameters
if template_name in ('standalone_n-nic'):
    data['parameters']['numberOfAdditionalNics'] = {"type": "int", "defaultValue": 1, "allowedValues": [1, 2, 3, 4, 5], "metadata": {"description": ""}}
    data['parameters']['additionalNicLocation'] = {"type": "string", "metadata": {"description": ""}}
if template_name in ('failover-lb_1nic'):
    data['parameters']['numberOfInstances'] = {"type": "int", "defaultValue": 2, "allowedValues": [2], "metadata": {"description": ""}}
if template_name in ('failover-api'):
    data['parameters']['managedRoutes'] = {"defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}, "type": "string"}
    data['parameters']['routeTableTag'] = {"defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}, "type": "string"}
if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    if license_type == 'BIGIQ_PAYG':
        min_allowed_values = [0, 1, 2, 3, 4, 5, 6]
        max_allowed_values = [1, 2, 3, 4, 5, 6, 7, 8]
    else:
        min_allowed_values = [1, 2, 3, 4, 5, 6]
        max_allowed_values = [2, 3, 4, 5, 6, 7, 8]
    data['parameters']['vmScaleSetMinCount'] = {"type": "int", "defaultValue": 2, "allowedValues": min_allowed_values, "metadata": {"description": ""}}
    data['parameters']['vmScaleSetMaxCount'] = {"type": "int", "defaultValue": 4, "allowedValues": max_allowed_values, "metadata": {"description": ""}}
    allowedValues = ["F5_TMM_CPU", "F5_TMM_Traffic", "Host_Throughput"]
    if license_type == 'BIGIQ_PAYG':
        allowedValues = ["F5_TMM_CPU", "F5_TMM_Traffic"]
    data['parameters']['autoScaleMetric'] = {"type": "string", "defaultValue": "F5_TMM_Traffic", "allowedValues": allowedValues,  "metadata": {"description": ""}}
    data['parameters']['appInsights'] = {"type": "string", "defaultValue": "CREATE_NEW", "metadata": {"description": ""}}
    data['parameters']['calculatedBandwidth'] = {"type": "string", "defaultValue": "200m", "allowedValues": ["10m", "25m", "100m", "200m", "1g"], "metadata": {"description": ""}}
    data['parameters']['scaleOutThreshold'] = {"type": "int", "defaultValue": 90, "allowedValues": [50, 55, 60, 65, 70, 75, 80, 85, 90, 95], "metadata": {"description": ""}}
    data['parameters']['scaleInThreshold'] = {"type": "int", "defaultValue": 10, "allowedValues": [5, 10, 15, 20, 25, 30, 35, 40, 45], "metadata": {"description": ""}}
    data['parameters']['scaleTimeWindow'] = {"type": "int", "defaultValue": 10, "allowedValues": [5, 10, 15, 30], "metadata": {"description": ""}}
    data['parameters']['notificationEmail'] = {"defaultValue": "OPTIONAL", "metadata": {"description": ""}, "type": "string"}
if template_name in ('autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    # WAF-like templates need the 'Best' Image, still prompt as a parameter so they are aware of what they are paying for with PAYG
    data['parameters']['imageName'] = {"type": "string", "defaultValue": "Best", "allowedValues": ["Best"], "metadata": {"description": ""}}
    data['parameters']['solutionDeploymentName'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['applicationProtocols'] = {"type": "string", "defaultValue": "http-https", "metadata": {"description": ""}, "allowedValues" : ["http", "https", "http-https", "https-offload"]}
    data['parameters']['applicationAddress'] = {"type": "string", "metadata": { "description": ""}}
    data['parameters']['applicationServiceFqdn'] = {"type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}}
    data['parameters']['applicationPort'] = {"type": "string", "defaultValue": "80", "metadata": {"description": ""}}
    data['parameters']['applicationSecurePort'] = {"type": "string", "defaultValue": "443", "metadata": {"description": ""}}
    data['parameters']['sslCert'] = {"type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}}
    data['parameters']['sslPswd'] = {"type": "securestring", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}}
    data['parameters']['applicationType'] = {"type": "string", "defaultValue": "Linux", "metadata": {"description": ""}, "allowedValues": ["Windows", "Linux"]}
    data['parameters']['blockingLevel'] = {"type": "string", "defaultValue": "medium", "metadata": {"description": ""}, "allowedValues": ["low", "medium", "high", "off", "custom"]}
    data['parameters']['customPolicy'] = {"type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}}
if template_name in ('autoscale_ltm_via-dns', 'autoscale_waf_via-dns'):
    data['parameters']['dnsMemberIpType'] = {"type": "string", "defaultValue": "private", "allowedValues": ["private", "public"], "metadata": {"description": ""}}
    data['parameters']['dnsMemberPort'] = {"type": "string", "defaultValue": "80", "metadata": {"description": ""}}
    data['parameters']['dnsProviderHost'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['dnsProviderPort'] = {"type": "string", "defaultValue": "443", "metadata": {"description": ""}}
    data['parameters']['dnsProviderUser'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['dnsProviderPassword'] = {"type": "securestring", "metadata": {"description": ""}}
    data['parameters']['dnsProviderPool'] = {"type": "string", "defaultValue": "autoscale_pool", "metadata": {"description": ""}}
    data['parameters']['dnsProviderDataCenter'] = {"type": "string", "defaultValue": "azure_datacenter", "metadata": {"description": ""}}
# Add service principal parameters to necessary solutions
if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns', 'failover-api'):
    data['parameters']['tenantId'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['clientId'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['servicePrincipalSecret'] = {"type": "securestring", "metadata": {"description": ""}}

## Remove unecessary parameters and do a check for missing mandatory variables
master_helper.template_check(data, 'parameters')
## Fill in descriptions from YAML doc file in files/readme_files
master_helper.param_descr_update(data['parameters'], template_name)
# Some modifications once parameters have been defined
for parameter in data['parameters']:
    # Sort azuredeploy.json parameter values alphabetically
    sorted_param = json.dumps(data['parameters'][parameter], sort_keys=True, ensure_ascii=False)
    data['parameters'][parameter] = json.loads(sorted_param, object_pairs_hook=OrderedDict)
    # Add parameters into parameters file as well
    try:
        data_params['parameters'][parameter] = {"value": data['parameters'][parameter]['defaultValue']}
    except:
        data_params['parameters'][parameter] = {"value": 'GEN_UNIQUE'}

######################################## ARM Variables ########################################
## Pulling in a base set of variables and setting order with below call, it is a function of master_helper.py
master_helper.variable_initialize(data)
# Set certain default variables to unique, changing value
data['variables']['bigIpVersionPortMap'] = version_port_map
data['variables']['f5CloudLibsTag'] = f5_cloud_libs_tag
data['variables']['f5CloudLibsAzureTag'] = f5_cloud_libs_azure_tag
data['variables']['f5NetworksTag'] = f5_networks_tag
data['variables']['f5CloudIappsTag'] = f5_cloud_iapps_tag
data['variables']['verifyHash'] = verify_hash
data['variables']['installCloudLibs'] = install_cloud_libs
data['variables']['skuToUse'] = sku_to_use
data['variables']['offerToUse'] = offer_to_use
data['variables']['bigIpNicPortValue'] = nic_port_map
## Configure usage analytics variables
data['variables']['deploymentId'] = "[concat(variables('subscriptionId'), resourceGroup().id, deployment().name, variables('dnsLabel'))]"
metrics_cmd = "[concat(' --metrics customerId:${custId},deploymentId:${deployId},templateName:<TMPL_NAME>,templateVersion:<TMPL_VER>,region:', variables('location'), ',bigIpVersion:', parameters('bigIpVersion') ,',licenseType:<LIC_TYPE>,cloudLibsVersion:', variables('f5CloudLibsTag'), ',cloudName:azure')]"
if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    # Pass down to autoscale.sh for autoscale templates
    metrics_cmd = "[concat(' --usageAnalytics \\\" --metrics customerId:${custId},deploymentId:${deployId},templateName:<TMPL_NAME>,templateVersion:<TMPL_VER>,region:', variables('location'), ',bigIpVersion:', parameters('bigIpVersion') ,',licenseType:<LIC_TYPE>,cloudLibsVersion:', variables('f5CloudLibsTag'), ',cloudName:azure\\\"')]"
metrics_cmd = metrics_cmd.replace('<TMPL_NAME>', template_name + '-' + stack_type + '-' + support_type).replace('<TMPL_VER>', content_version).replace('<LIC_TYPE>', license_type)
hash_cmd = "[concat('custId=`echo \"', variables('subscriptionId'), '\"|sha512sum|cut -d \" \" -f 1`; deployId=`echo \"', variables('deploymentId'), '\"|sha512sum|cut -d \" \" -f 1`')]"
data['variables']['allowUsageAnalytics'] = { "Yes": { "hashCmd": hash_cmd, "metricsCmd": metrics_cmd}, "No": { "hashCmd": "echo AllowUsageAnalytics:No", "metricsCmd": ""} }
## Handle new_stack/existing_stack variable differences
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_1nic', 'failover-lb_3nic', 'autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
        data['variables']['instanceName'] = "[toLower(parameters('instanceName'))]"
    if template_name in ('failover-api', 'failover-lb_1nic', 'failover-lb_3nic'):
        data['variables']['newStorageAccountName1'] = "[concat(uniqueString(variables('dnsLabel'), resourceGroup().id, deployment().name), 'stor1')]"
    if template_name in ('failover-lb_3nic'):
        data['variables']['internalLoadBalancerName'] =  "[concat(variables('dnsLabel'),'-int-ilb')]"
        data['variables']["intLbId"] = "[resourceId('Microsoft.Network/loadBalancers',variables('internalLoadBalancerName'))]"
        data['variables']['failoverCmdArray'] = {"No": {"first": "[concat('tmsh modify cm device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address none')]", "second": "[concat('tmsh modify cm device ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address none')]" }, "Yes": {"first": "[concat('tmsh modify cm device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress'))]", "second": "[concat('tmsh modify cm device ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress1'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress1'))]"}}
    if template_name in ('failover-api'):
        data['variables']['failoverCmdArray'] = { "12.1.303000": "echo \"Failover db variable not required.\"", "13.1.0200": "tmsh modify sys db failover.selinuxallowscripts value enable", "latest": "tmsh modify sys db failover.selinuxallowscripts value enable" }
    if stack_type == 'new_stack':
        data['variables']['vnetId'] = "[resourceId('Microsoft.Network/virtualNetworks', variables('virtualNetworkName'))]"
        data['variables']['vnetAddressPrefix'] = "[concat(parameters('vnetAddressPrefix'),'.0.0/16')]"
        data['variables']['mgmtSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.1.0/24')]"
        data['variables']['mgmtSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.1.4')]"
        if template_name in ('standalone_1nic'):
            data['variables']['mgmtRouteGw'] = "[concat(parameters('vnetAddressPrefix'), '.1.1')]"
        if template_name in ('failover-lb_1nic'):
            data['variables']['mgmtSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.1.')]"
            data['variables']['mgmtSubnetPrivateAddressSuffix'] = 4
            data['variables']['mgmtSubnetPrivateAddressSuffix1'] = "[add(variables('mgmtSubnetPrivateAddressSuffix'), 1)]"
        if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
            data['variables']['extNsgID'] = "[resourceId('Microsoft.Network/networkSecurityGroups/',concat(variables('dnsLabel'),'-ext-nsg'))]"
            data['variables']['extSelfPublicIpAddressNamePrefix'] = "[concat(variables('dnsLabel'), '-self-pip')]"
            data['variables']['extSelfPublicIpAddressIdPrefix'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('extSelfPublicIpAddressNamePrefix'))]"
            data['variables']['extpublicIPAddressNamePrefix'] = "[concat(variables('dnsLabel'), '-ext-pip')]"
            data['variables']['extPublicIPAddressIdPrefix'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('extPublicIPAddressNamePrefix'))]"
            data['variables']['extNicName'] = "[concat(variables('dnsLabel'), '-ext')]"
            data['variables']['extSubnetName'] = "external"
            data['variables']['extSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('extsubnetName'))]"
            data['variables']['extSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.2.0/24')]"
            data['variables']['extSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.2.4')]"
            data['variables']['extSubnetPrivateAddressPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.2.')]"
            data['variables']['tmmRouteGw'] = "[concat(parameters('vnetAddressPrefix'), '.2.1')]"
            data['variables']['mgmtRouteGw'] = "[concat(parameters('vnetAddressPrefix'), '.1.1')]"
            data['variables']['routeCmdArray'] = route_cmd_array
            if template_name in ('standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
                data['variables']['intNicName'] = "[concat(variables('dnsLabel'), '-int')]"
                data['variables']['intSubnetName'] = "internal"
                data['variables']['intSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('intsubnetName'))]"
                data['variables']['intSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.3.0/24')]"
                data['variables']['intSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.3.4')]"
            if template_name in ('failover-api', 'failover-lb_3nic'):
                data['variables']['mgmtSubnetPrivateAddress1'] = "[concat(parameters('vnetAddressPrefix'), '.1.5')]"
                data['variables']['extSubnetPrivateAddress1'] = "[concat(parameters('vnetAddressPrefix'), '.2.5')]"
                data['variables']['intSubnetPrivateAddress1'] = "[concat(parameters('vnetAddressPrefix'), '.3.5')]"
                if template_name in ('failover-lb_3nic'):
                    data['variables']['intSubnetPrivateAddress2'] = "[concat(parameters('vnetAddressPrefix'), '.3.10')]"
                    data['variables']['intSubnetPrivateAddress3'] = "[concat(parameters('vnetAddressPrefix'), '.3.11')]"
                    data['variables']['internalLoadBalancerAddress'] = "[concat(parameters('vnetAddressPrefix'), '.3.50')]"
                    lb_back_end_array = [ { "id": "[concat(variables('extLbId'), '/backendAddressPools/', 'loadBalancerBackEnd')]" }, { "id": "[concat(variables('intLbId'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ]
                if template_name in ('failover-api'):
                    data['variables']['extSubnetPrivateAddressSuffixInt'] = 10
            if template_name in ('standalone_n-nic'):
                data['variables']['subnetArray'] = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }, { "name": "[variables('intSubnetName')]", "properties": { "addressPrefix": "[variables('intSubnetPrefix')]" } }]
                data['variables']['addtlSubnetArray'] = [{ "name": "[variables('addtlNicRefSplit')[0]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.4.0/24')]" } }, { "name": "[variables('addtlNicRefSplit')[1]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.5.0/24')]" } }, { "name": "[variables('addtlNicRefSplit')[2]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.6.0/24')]" } }, { "name": "[variables('addtlNicRefSplit')[3]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.7.0/24')]" } }, { "name": "[variables('addtlNicRefSplit')[4]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.8.0/24')]" } }]
    if stack_type in ('existing_stack', 'prod_stack'):
        data['variables']['virtualNetworkName'] = "[parameters('vnetName')]"
        data['variables']['vnetId'] = "[resourceId(parameters('vnetResourceGroupName'),'Microsoft.Network/virtualNetworks',variables('virtualNetworkName'))]"
        data['variables']['mgmtSubnetName'] = "[parameters('mgmtSubnetName')]"
        data['variables']['mgmtSubnetPrivateAddress'] = "[parameters('mgmtIpAddress')]"
        if template_name in ('standalone_1nic'):
            data['variables']['mgmtSubnetRef'] = "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/', parameters('vnetResourceGroupName'), '/providers/Microsoft.Network/virtualNetworks/', parameters('vnetName'), '/subnets/', parameters('mgmtSubnetName'))]"
            data['variables']['mgmtRouteGw'] = "`tmsh list sys management-route default gateway | grep gateway | sed 's/gateway //;s/ //g'`"
        if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
            data['variables']['newAvailabilitySetName'] = "[concat(variables('dnsLabel'), '-avset')]"
            data['variables']['availabilitySetName'] = "[replace(parameters('avSetChoice'), 'CREATE_NEW', variables('newAvailabilitySetName'))]"
        if template_name in ('failover-lb_1nic'):
            data['variables']['mgmtSubnetPrivateAddressPrefixArray'] = "[split(parameters('mgmtIpAddressRangeStart'), '.')]"
            data['variables']['mgmtSubnetPrivateAddressPrefix'] = "[concat(variables('mgmtSubnetPrivateAddressPrefixArray')[0], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[1], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[2], '.')]"
            data['variables']['mgmtSubnetPrivateAddressSuffix'] = "[int(variables('mgmtSubnetPrivateAddressPrefixArray')[3])]"
            data['variables']['mgmtSubnetPrivateAddressSuffix1'] = "[add(variables('mgmtSubnetPrivateAddressSuffix'), 1)]"
            data['variables']['mgmtSubnetPrivateAddress'] = "[variables('mgmtSubnetPrivateAddressPrefix')]"
            if stack_type in ('prod_stack'):
                data['variables']['externalLoadBalancerAddress'] = "[concat(variables('mgmtSubnetPrivateAddress'), add(variables('mgmtSubnetPrivateAddressSuffix1'), 1))]"
        if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
            data['variables']['extNsgID'] = "[resourceId('Microsoft.Network/networkSecurityGroups/',concat(variables('dnsLabel'),'-ext-nsg'))]"
            data['variables']['extSelfPublicIpAddressNamePrefix'] = "[concat(variables('dnsLabel'), '-self-pip')]"
            data['variables']['extSelfPublicIpAddressIdPrefix'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('extSelfPublicIpAddressNamePrefix'))]"
            data['variables']['extpublicIPAddressNamePrefix'] = "[concat(variables('dnsLabel'), '-ext-pip')]"
            data['variables']['extPublicIPAddressIdPrefix'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('extPublicIPAddressNamePrefix'))]"
            data['variables']['extNicName'] = "[concat(variables('dnsLabel'), '-ext')]"
            data['variables']['extSubnetName'] = "[parameters('externalSubnetName')]"
            data['variables']['extSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('extsubnetName'))]"
            data['variables']['extSubnetPrivateAddress'] = "[parameters('externalIpAddressRangeStart')]"
            data['variables']['extSubnetPrivateAddressPrefixArray'] = "[split(parameters('externalIpAddressRangeStart'), '.')]"
            data['variables']['extSubnetPrivateAddressPrefix'] = "[concat(variables('extSubnetPrivateAddressPrefixArray')[0], '.', variables('extSubnetPrivateAddressPrefixArray')[1], '.', variables('extSubnetPrivateAddressPrefixArray')[2], '.')]"
            data['variables']['tmmRouteGw'] = "OPTIONAL"
            data['variables']['mgmtRouteGw'] = "`tmsh list sys management-route default gateway | grep gateway | sed 's/gateway //;s/ //g'`"
            data['variables']['routeCmdArray'] = route_cmd_array
            data['variables']['extSubnetPrivateAddressSuffixInt'] = "[int(variables('extSubnetPrivateAddressPrefixArray')[3])]"
            data['variables']['extSubnetPrivateAddressSuffix0'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 1)]"
            data['variables']['extSubnetPrivateAddressSuffix1'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 2)]"
            data['variables']['extSubnetRef'] = "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/', parameters('vnetResourceGroupName'), '/providers/Microsoft.Network/virtualNetworks/', parameters('vnetName'), '/subnets/', parameters('externalSubnetName'))]"
            if template_name in ('standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
                data['variables']['intNicName'] = "[concat(variables('dnsLabel'), '-int')]"
                data['variables']['intSubnetName'] = "[parameters('internalSubnetName')]"
                data['variables']['intSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('intsubnetName'))]"
                data['variables']['intSubnetPrivateAddress'] = "[parameters('internalIpAddress')]"
                data['variables']['intSubnetRef'] = "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/', parameters('vnetResourceGroupName'), '/providers/Microsoft.Network/virtualNetworks/', parameters('vnetName'), '/subnets/', parameters('internalSubnetName'))]"
            if template_name in ('failover-api', 'failover-lb_3nic'):
                data['variables']['mgmtSubnetPrivateAddressPrefixArray'] = "[split(parameters('mgmtIpAddressRangeStart'), '.')]"
                data['variables']['mgmtSubnetPrivateAddressPrefix'] = "[concat(variables('mgmtSubnetPrivateAddressPrefixArray')[0], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[1], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[2], '.')]"
                data['variables']['mgmtSubnetPrivateAddressSuffixInt'] = "[int(variables('mgmtSubnetPrivateAddressPrefixArray')[3])]"
                data['variables']['mgmtSubnetPrivateAddressSuffix'] = "[add(variables('mgmtSubnetPrivateAddressSuffixInt'), 1)]"
                data['variables']['mgmtSubnetPrivateAddress'] = "[parameters('mgmtIpAddressRangeStart')]"
                data['variables']['mgmtSubnetPrivateAddress1'] = "[concat(variables('mgmtSubnetPrivateAddressPrefix'), variables('mgmtSubnetPrivateAddressSuffix'))]"
                data['variables']['mgmtRouteGw'] = "`tmsh list sys management-route default gateway | grep gateway | sed 's/gateway //;s/ //g'`"
                data['variables']['extSubnetSelfPrivateAddressPrefixArray'] = "[split(parameters('externalIpSelfAddressRangeStart'), '.')]"
                data['variables']['extSubnetSelfPrivateAddressPrefix'] = "[concat(variables('extSubnetSelfPrivateAddressPrefixArray')[0], '.', variables('extSubnetSelfPrivateAddressPrefixArray')[1], '.', variables('extSubnetSelfPrivateAddressPrefixArray')[2], '.')]"
                data['variables']['extSubnetSelfPrivateAddressSuffixInt'] = "[int(variables('extSubnetSelfPrivateAddressPrefixArray')[3])]"
                data['variables']['extSubnetSelfPrivateAddressSuffix'] = "[add(variables('extSubnetSelfPrivateAddressSuffixInt'), 1)]"
                data['variables']['extSubnetPrivateAddress'] = "[parameters('externalIpSelfAddressRangeStart')]"
                data['variables']['extSubnetPrivateAddress1'] = "[concat(variables('extSubnetSelfPrivateAddressPrefix'), variables('extSubnetSelfPrivateAddressSuffix'))]"
                data['variables']['intSubnetPrivateAddressPrefixArray'] = "[split(parameters('internalIpAddressRangeStart'), '.')]"
                data['variables']['intSubnetPrivateAddressPrefix'] = "[concat(variables('intSubnetPrivateAddressPrefixArray')[0], '.', variables('intSubnetPrivateAddressPrefixArray')[1], '.', variables('intSubnetPrivateAddressPrefixArray')[2], '.')]"
                data['variables']['intSubnetPrivateAddressSuffixInt'] = "[int(variables('intSubnetPrivateAddressPrefixArray')[3])]"
                data['variables']['intSubnetPrivateAddressSuffix'] = "[add(variables('intSubnetPrivateAddressSuffixInt'), 1)]"
                data['variables']['intSubnetPrivateAddress'] = "[parameters('internalIpAddressRangeStart')]"
                data['variables']['intSubnetPrivateAddress1'] = "[concat(variables('intSubnetPrivateAddressPrefix'), variables('intSubnetPrivateAddressSuffix'))]"
                if template_name in ('failover-lb_3nic'):
                    data['variables']['intSubnetPrivateAddressSuffix1'] = "[add(variables('intSubnetPrivateAddressSuffixInt'), 2)]"
                    data['variables']['intSubnetPrivateAddressSuffix2'] = "[add(variables('intSubnetPrivateAddressSuffixInt'), 3)]"
                    data['variables']['intSubnetPrivateAddressSuffix3'] = "[add(variables('intSubnetPrivateAddressSuffixInt'), 4)]"
                    data['variables']['intSubnetPrivateAddress2'] = "[concat(variables('intSubnetPrivateAddressPrefix'), variables('intSubnetPrivateAddressSuffix1'))]"
                    data['variables']['intSubnetPrivateAddress3'] = "[concat(variables('intSubnetPrivateAddressPrefix'), variables('intSubnetPrivateAddressSuffix2'))]"
                    data['variables']['internalLoadBalancerAddress'] =  "[concat(variables('intSubnetPrivateAddressPrefix'), variables('intSubnetPrivateAddressSuffix3'))]"
                    lb_back_end_array = [ { "id": "[concat(variables('extLbId'), '/backendAddressPools/', 'loadBalancerBackEnd')]" }, { "id": "[concat(variables('intLbId'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ]
    if stack_type in ('prod_stack'):
        data['variables']['dnsLabel'] = "[toLower(parameters('uniqueLabel'))]"

    # After adding variables for new_stack/existing_stack we need to add the ip config array
    if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
        data['variables']['numberOfExternalIps'] = "[parameters('numberOfExternalIps')]"
        if template_name in ('failover-lb_3nic'):
            data['variables']['backEndAddressPoolArray'] = lb_back_end_array

if template_name in ('standalone_1nic'):
    data['variables']['networkMtuArray'] = network_mtu_array
if template_name in ('standalone_n-nic'):
    data['variables']['addtlNicFillerArray'] = ["filler01", "filler02", "filler03", "filler04", "filler05"]
    data['variables']['addtlNicRefSplit'] = "[concat(split(parameters('additionalNicLocation'), ';'), variables('addtlNicFillerArray'))]"
    data['variables']['netCmd01'] = "[concat(' --vlan name:', variables('addtlNicRefSplit')[0], ',nic:1.3')]"
    data['variables']['netCmd02'] = "[concat(variables('netCmd01'), ' --vlan name:', variables('addtlNicRefSplit')[1], ',nic:1.4')]"
    data['variables']['netCmd03'] = "[concat(variables('netCmd02'), ' --vlan name:', variables('addtlNicRefSplit')[2], ',nic:1.5')]"
    data['variables']['netCmd04'] = "[concat(variables('netCmd03'), ' --vlan name:', variables('addtlNicRefSplit')[3], ',nic:1.6')]"
    data['variables']['netCmd05'] = "[concat(variables('netCmd04'), ' --vlan name:', variables('addtlNicRefSplit')[4], ',nic:1.7')]"
    data['variables']['netCmd'] = "[variables(concat('netCmd0', parameters('numberOfAdditionalNics')))]"
    data['variables']['selfNicConfigArray'] = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('intNicName'))]", "properties": { "primary": False } }]
    data['variables']['addtlNicConfigArray'] = {"copy": [{"count": 8, "input": {"id": "[resourceId('Microsoft.Network/networkInterfaces', concat(toLower(parameters('instanceName')), '-addtlNic', copyIndex('values', 1)))]", "properties": {"primary": False }}, "name": "values"}]}
if template_name in ('failover-api'):
    if stack_type == 'new_stack':
        private_ip_value = "[concat(parameters('vnetAddressPrefix'), '.2.', copyIndex('values', 10))]"
    elif stack_type in ('existing_stack', 'prod_stack'):
        private_ip_value = "[concat(split(parameters('externalIpAddressRangeStart'), '.')[0], '.', split(parameters('externalIpAddressRangeStart'), '.')[1], '.', split(parameters('externalIpAddressRangeStart'), '.')[2], '.', add(int(split(parameters('externalIpAddressRangeStart'), '.')[3]), copyIndex('values')))]"
if template_name in ('failover-lb_1nic', 'failover-lb_3nic', 'autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    data['variables']['externalLoadBalancerName'] = "[concat(variables('dnsLabel'),'-ext-alb')]"
    data['variables']['extLbId'] = "[resourceId('Microsoft.Network/loadBalancers',variables('externalLoadBalancerName'))]"
    if template_name in ('failover-lb_1nic', 'autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
        data['variables']['deviceNamePrefix'] = "[concat(variables('dnsLabel'),'-device')]"
        data['variables']['frontEndIPConfigID'] = "[concat(variables('extLbId'),'/frontendIPConfigurations/loadBalancerFrontEnd')]"
    if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
        data['variables']['appInsightsApiVersion'] = "2015-04-01"
        data['variables']['appInsightsComponentsApiVersion'] = "2015-05-01"
        data['variables']['mgmtSubnetPrivateAddress'] = "OPTIONAL"
        data['variables']['bigIpMgmtPort'] = 8443
        data['variables']['vmssName'] = "[concat(parameters('dnsLabel'),'-vmss')]"
        data['variables']['vmssId'] = "[resourceId('Microsoft.Compute/virtualMachineScaleSets', variables('vmssName'))]"
        data['variables']['newDataStorageAccountName'] = "[concat(uniqueString(variables('dnsLabel'), resourceGroup().id, deployment().name), 'data000')]"
        data['variables']['subscriptionID'] = "[subscription().subscriptionId]"
        data['variables']['autoScaleMetric'] = "[parameters('autoScaleMetric')]"
        data['variables']['scaleMetricMap'] = { "Host_Throughput": { "metricName": "Network Out", "metricResourceUri": "[variables('vmssId')]", "thresholdOut": "[variables('scaleOutNetworkBytes')]", "thresholdIn": "[variables('scaleInNetworkBytes')]"  }, "F5_TMM_CPU": { "metricName": "customMetrics/F5_TMM_CPU", "metricResourceUri": "[resourceId(variables('appInsightsNameArray')[1], 'Microsoft.Insights/components', variables('appInsightsNameArray')[0])]", "thresholdOut": "[parameters('scaleOutThreshold')]", "thresholdIn": "[parameters('scaleInThreshold')]" }, "F5_TMM_Traffic": { "metricName": "customMetrics/F5_TMM_TRAFFIC", "metricResourceUri": "[resourceId(variables('appInsightsNameArray')[1], 'Microsoft.Insights/components', variables('appInsightsNameArray')[0])]", "thresholdOut": "[variables('scaleOutNetworkBytes')]", "thresholdIn": "[variables('scaleInNetworkBytes')]" } }
        data['variables']['defaultAppInsightsLocation'] = "eastus"
        data['variables']['appInsightsLocation'] = "[split(concat(parameters('appInsights'), ':', variables('defaultAppInsightsLocation')), ':')[1]]"
        data['variables']['appInsightsName'] = "[replace(split(parameters('appInsights'), ':')[0], 'CREATE_NEW', concat(deployment().name, '-appinsights'))]"
        data['variables']['appInsightsNameArray'] = "[split(concat(variables('appInsightsName'), ';', variables('resourceGroupName')) , ';')]"
        data['variables']['10m'] = 10485760
        data['variables']['25m'] = 26214400
        data['variables']['100m'] = 104857600
        data['variables']['200m'] = 209715200
        data['variables']['1g'] = 1073741824
        data['variables']['scaleOutCalc'] = "[mul(variables(parameters('calculatedBandwidth')), parameters('scaleOutThreshold'))]"
        data['variables']['scaleInCalc'] = "[mul(variables(parameters('calculatedBandwidth')), parameters('scaleInThreshold'))]"
        data['variables']['scaleOutNetworkBits'] = "[div(variables('scaleOutCalc'), 100)]"
        data['variables']['scaleInNetworkBits'] = "[div(variables('scaleInCalc'), 100)]"
        data['variables']['scaleOutNetworkBytes'] = "[div(variables('scaleOutNetworkBits'), 8)]"
        data['variables']['scaleInNetworkBytes'] = "[div(variables('scaleInNetworkBits'), 8)]"
        data['variables']['timeWindow'] = "[concat('PT', parameters('scaleTimeWindow'), 'M')]"
        data['variables']['customEmailBaseArray'] = [""]
        data['variables']['customEmail'] = "[skip(union(variables('customEmailBaseArray'), split(replace(parameters('notificationEmail'), 'OPTIONAL', ''), ';')), 1)]"
        if license_type == 'BIGIQ_PAYG':
            data['variables']['staticVmssName'] = "[concat(parameters('dnsLabel'),'-vmss', '-static')]"
            data['variables']['staticVmssId'] = "[resourceId('Microsoft.Compute/virtualMachineScaleSets', variables('staticVmssName'))]"
            data['variables']['staticSkuToUse'] = byol_sku_to_use
            data['variables']['staticOfferToUse'] = byol_offer_to_use
            data['variables']['staticVmssTagValues'] = {"f5ClusterTag": "[variables('dnsLabel')]"}
    if template_name in ('autoscale_waf_via-lb', 'autoscale_waf_via-dns') or license_type == 'BIGIQ_PAYG':
        data['variables']['lbTcpProbeNameHttp'] = "tcp_probe_http"
        data['variables']['lbTcpProbeIdHttp'] = "[concat(variables('extLbId'),'/probes/',variables('lbTcpProbeNameHttp'))]"
        data['variables']['lbTcpProbeNameHttps'] = "tcp_probe_https"
        data['variables']['lbTcpProbeIdHttps'] = "[concat(variables('extLbId'),'/probes/',variables('lbTcpProbeNameHttps'))]"
        data['variables']['httpBackendPort'] = 880
        data['variables']['httpsBackendPort'] = 8445
        if template_name in ('autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
            data['variables']['f5NetworksSolutionScripts'] = "[concat('https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/', variables('f5NetworksTag'), '/" + solution_location + "/solutions/autoscale/waf/deploy_scripts/')]"
            data['variables']['commandArgs'] = "[concat('-m ', parameters('applicationProtocols'), ' -d ', parameters('solutionDeploymentName'), ' -n ', parameters('applicationAddress'), ' -j 880 -k 8445 -h ', parameters('applicationPort'), ' -s ', parameters('applicationSecurePort'), ' -t ', toLower(parameters('applicationType')), ' -l ', toLower(parameters('blockingLevel')), ' -a ', parameters('customPolicy'), ' -c ', parameters('sslCert'), ' -r ', parameters('sslPswd'), ' -o ', parameters('applicationServiceFqdn'), ' -u ', parameters('adminUsername'))]"

# Add learning stack variables
if learning_stack:
    data['variables']['webVmName'] = "[concat(variables('dnsLabel'), '-web01')]"
    data['variables']['webVmSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.3.10')]"
    data['variables']['webVmVsAddr'] = "[concat(variables('extSubnetPrivateAddressPrefix'), '10')]"
    data['variables']['webVmVsPort'] = "80"
    # Modify Custom Config
    data['variables']['customConfig'] = "[concat('### START (INPUT) CUSTOM CONFIGURATION HERE\nbranch=\"', variables('f5NetworksTag'), '\"\nhttp_iapp=\"f5.http.v1.2.0rc7.tmpl\"\ncurl https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/$branch/experimental/reference/learning-stack/iapps/$http_iapp > $http_iapp\ntmsh load sys application template $http_iapp\ntmsh create sys application service exampleApp template ${http_iapp//.tmpl} traffic-group none tables replace-all-with { pool__hosts { column-names { name } rows {{ row { exampleapp.f5.com }}}} pool__members { column-names { addr port connection_limit } rows {{ row { ', variables('webVmSubnetPrivateAddress'), ' ', variables('webVmVsPort'), ' 0 }}}} } variables replace-all-with { pool__addr { value ', variables('webVmVsAddr'), '} pool__mask { value 255.255.255.255 } pool__port { value ', variables('webVmVsPort'), ' } }')]"
        
# Remove unecessary variables and do a check for missing mandatory variables
master_helper.template_check(data, 'variables')
# Sort azuredeploy.json variable value (if exists) alphabetically
for variables in data['variables']:
    sorted_variable = json.dumps(data['variables'][variables], sort_keys=True, ensure_ascii=False)
    data['variables'][variables] = json.loads(sorted_variable, object_pairs_hook=OrderedDict)

######################################## ARM Resources ########################################
resources_list = []
###### Public IP Resource(s) ######
# Don't create public IP's for production stack
if stack_type in ('new_stack', 'existing_stack'):
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_1nic', 'autoscale_ltm_via-lb', 'autoscale_waf_via-lb'):
        pub_ip_def = { "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[variables('mgmtPublicIPAddressName')]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[variables('dnsLabel')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }
        if template_name in ('autoscale_ltm_via-lb', 'autoscale_waf_via-lb') and license_type == 'BIGIQ_PAYG':
            pub_ip_def['sku'] = { "name": "Standard" }
        resources_list += [pub_ip_def]
    if template_name in ('failover-api', 'failover-lb_3nic'):
        resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('mgmtPublicIPAddressName'), 0)]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabel'), '-0')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } },{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('mgmtPublicIPAddressName'), 1)]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabel'), '-1')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
    if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
        # Add Self Public IP - for external NIC
        resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('extSelfPublicIpAddressNamePrefix'), '0')]", "tags": tags, "properties": { "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
        if template_name in ('failover-api', 'failover-lb_3nic'):
            resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('extSelfPublicIpAddressNamePrefix'), '1')]", "tags": tags, "properties": { "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
        # Add Traffic Public IP's - for external NIC
        resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "condition": "[not(equals(variables('numberOfExternalIps'),0))]", "location": location, "name": "[concat(variables('extPublicIPAddressNamePrefix'), copyIndex())]", "copy": { "count": "[if(not(equals(variables('numberOfExternalIps'), 0)), variables('numberOfExternalIps'), 1)]", "name": "extpipcopy"}, "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabel'), copyIndex(0))]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]

###### Virtual Network Resources(s) ######
if template_name in ('standalone_1nic', 'failover-lb_1nic'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }]
if template_name in ('standalone_2nic'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }]
if template_name in ('standalone_3nic', 'failover-lb_3nic', 'failover-api'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }, { "name": "[variables('intSubnetName')]", "properties": { "addressPrefix": "[variables('intSubnetPrefix')]" } }]
if template_name in ('standalone_n-nic'):
    subnets = "[concat(take(variables('subnetArray'), 3), take(variables('addtlSubnetArray'), parameters('numberOfAdditionalNics')))]"
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_1nic', 'failover-lb_3nic', 'failover-api'):
    if stack_type == 'new_stack':
        resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }]
    scale_depends_on = []
    if stack_type == 'new_stack':
        scale_depends_on += ["[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]"]
        resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "dependsOn": [ "[variables('mgmtNsgID')]" ], "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

###### Network Interface Resource(s) ######
depends_on = ["[variables('vnetId')]", "[variables('mgmtPublicIPAddressId')]", "[variables('mgmtNsgID')]"]
depends_on_ext = ["[variables('vnetId')]", "[variables('extNsgID')]", "extpipcopy"]
depends_on_ext_pub0 = ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '0')]"]
depends_on_ext_pub1 = ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '1')]"]
# Remove incorrect depends_on items based on stack and solution type
if stack_type == 'existing_stack':
    depends_on.remove("[variables('vnetId')]")
    depends_on_ext.remove("[variables('vnetId')]")
elif stack_type == 'prod_stack':
    depends_on.remove("[variables('vnetId')]")
    depends_on.remove("[variables('mgmtPublicIPAddressId')]")
    depends_on_ext.remove("[variables('vnetId')]")
    depends_on_ext.remove("extpipcopy")
    depends_on_ext_pub0 = []
    depends_on_ext_pub1 = []
if template_name in ('failover-api', 'failover-lb_3nic'):
    depends_on.remove("[variables('mgmtPublicIPAddressId')]")

if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic',):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on, "location": location, "name": "[variables('mgmtNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[variables('mgmtNsgID')]" }, "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('mgmtSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": { "Id": "[variables('mgmtPublicIPAddressId')]" }, "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ] } }]
if template_name in ('standalone_2nic'):
    if stack_type in ('new_stack'):
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations', 1), 2)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations', 1), 2)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations', 1), 1), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations', 1), 1), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), 1, sub(copyIndex('ipConfigurations', 1), 2)))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ] } } ]
    if stack_type in ('existing_stack', 'prod_stack'):
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations', 1), 2)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations', 1), 2)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations', 1), 1), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations', 1), 1), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), sub(copyIndex('ipConfigurations', 1), 1))))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ] } } ]
if template_name in ('standalone_3nic', 'standalone_n-nic'):
    if stack_type in ('new_stack'):
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations', 1), 2)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations', 1), 2)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations', 1), 1), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations', 1), 1), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), 1, sub(copyIndex('ipConfigurations', 1), 2)))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ] } }, { "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_ext, "location": location, "name": "[variables('intNicName')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] } } ]
    if stack_type in ('existing_stack', 'prod_stack'):
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations', 1), 2)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations', 1), 2)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations', 1), 1), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations', 1), 1), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), sub(copyIndex('ipConfigurations', 1), 1))))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ] } }, { "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_ext, "location": location, "name": "[variables('intNicName')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] } } ]
if template_name in ('standalone_n-nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "condition": "[greaterOrEquals(parameters('numberOfAdditionalNics'), 1)]", "copy": { "count": "[parameters('numberOfAdditionalNics')]", "name": "addtlniccopy" }, "dependsOn": depends_on + ["[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]"], "location": location, "name": "[concat(variables('instanceName'), '-addtlNic', copyIndex(1))]", "properties": { "ipConfigurations": [ { "name": "ipconfig", "properties": { "privateIPAllocationMethod": "Dynamic", "subnet": { "id": "[concat(variables('vnetId'), '/subnets/', variables('addtlNicRefSplit')[copyIndex()])]" } } } ] }, "tags": tags }]
if template_name in ('failover-lb_1nic'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkInterfaces", "name": "[concat(variables('mgmtNicName'),copyindex())]", "location": location, "tags": tags, "dependsOn": depends_on + ["[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'),'/inboundNatRules/guimgt',copyindex())]", "[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'),'/inboundNatRules/sshmgt',copyindex())]"], "copy": { "count": "[parameters('numberOfInstances')]", "name": "niccopy" }, "properties": { "networkSecurityGroup": { "id": "[variables('mgmtNsgID')]" }, "ipConfigurations": [ { "name": "ipconfig1", "properties": { "privateIPAllocationMethod": "Static", "privateIPAddress": "[concat(variables('mgmtSubnetPrivateAddress'),add(variables('mgmtSubnetPrivateAddressSuffix'), copyindex()))]", "subnet": { "id": "[variables('mgmtSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('extLbId'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ], "loadBalancerInboundNatRules": [ { "id": "[concat(variables('extLbId'), '/inboundNatRules/', 'guimgt',copyIndex())]" }, { "id": "[concat(variables('extLbId'), '/inboundNatRules/', 'sshmgt',copyIndex())]" } ] } } ] } }]

# Can we shrink this down with a copy?
if template_name in ('failover-api', 'failover-lb_3nic'):
    resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on + ["[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'), '0')]"], "location": location, "name": "[concat(variables('mgmtNicName'), '0')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-mgmt-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(variables('mgmtPublicIPAddressName'), '0'))]" }, "privateIPAddress": "[variables('mgmtSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[variables('mgmtNsgId')]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on + ["[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'), '1')]"], "location": location, "name": "[concat(variables('mgmtNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-mgmt-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(variables('mgmtPublicIPAddressName'), '1'))]" }, "privateIPAddress": "[variables('mgmtSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[variables('mgmtNsgId')]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    if template_name in ('failover-api'):
        if stack_type in ('new_stack'):
            resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations'), 0), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations'), 1)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations'), 0), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations'), 1)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations'), 0), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations'), 0), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), sub(copyIndex('ipConfigurations'), 1))))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        if stack_type in ('existing_stack', 'prod_stack'):
            resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations'), 0), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations'), 1)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations'), 0), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations'), 1)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations'), 0), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations'), 0), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), sub(copyIndex('ipConfigurations'), 1))))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub1, "location": location, "name": "[concat(variables('extNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    if template_name in ('failover-lb_3nic'):
        if stack_type in ('new_stack'):
            resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0 + ["[variables('extLbId')]"], "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '0')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig0')]", "properties": { "primary": False, "loadBalancerBackendAddressPools": "[if(equals(variables('numberOfExternalIps'), 0), take(variables('backEndAddressPoolArray'), 0), take(variables('backEndAddressPoolArray'), 1))]", "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 10)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
            resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub1 + ["[variables('extLbId')]"], "location": location, "name": "[concat(variables('extNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig1')]", "properties": { "primary": False, "loadBalancerBackendAddressPools": "[if(equals(variables('numberOfExternalIps'), 0), take(variables('backEndAddressPoolArray'), 0), take(variables('backEndAddressPoolArray'), 1))]", "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 11)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        if stack_type in ('existing_stack', 'prod_stack'):
            resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0 + ["[variables('extLbId')]"], "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '0')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig0')]", "properties": { "primary": False, "loadBalancerBackendAddressPools": "[if(equals(variables('numberOfExternalIps'), 0), take(variables('backEndAddressPoolArray'), 0), take(variables('backEndAddressPoolArray'), 1))]", "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix0'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
            resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub1 + ["[variables('extLbId')]"], "location": location, "name": "[concat(variables('extNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig1')]", "properties": { "primary": False, "loadBalancerBackendAddressPools": "[if(equals(variables('numberOfExternalIps'), 0), take(variables('backEndAddressPoolArray'), 0), take(variables('backEndAddressPoolArray'), 1))]", "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix1'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    if template_name in ('failover-lb_3nic'):
        resources_list += [{"apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0 + ["[variables('intLbId')]"], "location": location, "name": "[concat(variables('intNicName'), '0')]", "properties": { "primary": True, "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "primary": True, "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } }, { "name": "[concat(variables('dnsLabel'), '-int-ipconfig-secondary')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress2')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" }, "loadBalancerBackendAddressPools": "[if(equals(parameters('internalLoadBalancerType'), 'DO_NOT_USE'), take(variables('backEndAddressPoolArray'), 0), skip(variables('backEndAddressPoolArray'), 1))]" } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces"}]
        resources_list += [{"apiVersion": api_version, "dependsOn": depends_on_ext + depends_on_ext_pub1 + ["[variables('intLbId')]"], "location": location, "name": "[concat(variables('intNicName'), '1')]", "properties": { "primary": True, "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "primary": True, "privateIPAddress": "[variables('intSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } }, { "name": "[concat(variables('dnsLabel'), '-int-ipconfig-secondary')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress3')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" }, "loadBalancerBackendAddressPools": "[if(equals(parameters('internalLoadBalancerType'), 'DO_NOT_USE'), take(variables('backEndAddressPoolArray'), 0), skip(variables('backEndAddressPoolArray'), 1))]" } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces"}]
    else:
        resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext, "location": location, "name": "[concat(variables('intNicName'), '0')]", "properties": { "primary": True, "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext, "location": location, "name": "[concat(variables('intNicName'), '1')]", "properties": { "primary": True, "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]

# Add learning stack NIC(s)
if learning_stack:
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on, "location": location, "name": "[concat(variables('webVmName'), '-nic')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('webVmName'), '-nic', '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('webVmSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": None, "subnet": { "id": "[variables('intSubnetId')]" } } } ] } }]

###### Network Security Group Resource(s) ######
mgmt_nsg_security_rules = [{ "name": "mgmt_allow_https", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('bigIpMgmtPort')]", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }, { "name": "ssh_allow_22", "properties": { "description": "", "priority": 102, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }]
ext_nsg_security_rules = []
# Add learning stack NSG rules
if learning_stack:
    ext_nsg_security_rules += [{ "name": "allow_example_app", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('webVmVsPort')]", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }]

if template_name in ('autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    mgmt_nsg_security_rules += [{ "name": "app_allow_http", "properties": { "description": "", "priority": 110, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpBackendPort')]", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }, { "name": "app_allow_https", "properties": { "description": "", "priority": 111, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpsBackendPort')]", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }]

if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_1nic', 'failover-lb_3nic', 'autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-mgmt-nsg')]", "tags": tags, "properties": { "securityRules": mgmt_nsg_security_rules } }]
if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-ext-nsg')]", "tags": tags, "properties": { "securityRules": ext_nsg_security_rules } }]

###### Load Balancer Resource(s) ######
probes_to_use = ""
lb_rules_to_use = ""
if template_name in ('autoscale_waf_via-lb', 'autoscale_waf_via-dns') or license_type == 'BIGIQ_PAYG':
    frontend_port = "[parameters('applicationPort')]"
    frontend_port_https = "[parameters('applicationSecurePort')]"
    if license_type == 'BIGIQ_PAYG' and template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns'):
        frontend_port = 80
        frontend_port_https = 443
    probes_to_use = [ { "name": "[variables('lbTcpProbeNameHttp')]", "properties": { "protocol": "Tcp", "port": "[variables('httpBackendPort')]", "intervalInSeconds": 15, "numberOfProbes": 3 } }, { "name": "[variables('lbTcpProbeNameHttps')]", "properties": { "protocol": "Tcp", "port": "[variables('httpsBackendPort')]", "intervalInSeconds": 15, "numberOfProbes": 3 } } ]
    lb_rules_to_use = [{ "Name": "app-http", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('externalLoadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('externalLoadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttp')]" }, "protocol": "Tcp", "frontendPort": frontend_port, "backendPort": "[variables('httpBackendPort')]", "idleTimeoutInMinutes": 15 } }, { "Name": "app-https", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('externalLoadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('externalLoadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttps')]" }, "protocol": "Tcp", "frontendPort": frontend_port_https, "backendPort": "[variables('httpsBackendPort')]", "idleTimeoutInMinutes": 15 } }]

if template_name == 'failover-lb_1nic':
    lb_fe_properties = { "publicIPAddress": { "id": "[variables('mgmtPublicIPAddressId')]" } }
    depends_on_pip = ["[variables('mgmtPublicIPAddressId')]"]
    if stack_type in ('prod_stack'):
        lb_fe_properties = { "privateIPAddress":  "[variables('externalLoadBalancerAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } }
        depends_on_pip.remove("[variables('mgmtPublicIPAddressId')]")
    resources_list += [{ "apiVersion": network_api_version, "dependsOn": [] + depends_on_pip, "location": location, "tags": tags, "name": "[variables('externalLoadBalancerName')]", "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": lb_fe_properties } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ] }, "type": "Microsoft.Network/loadBalancers" }]
if template_name == 'failover-lb_3nic':
    resources_list += [{ "apiVersion": network_api_version, "condition": "[not(equals(variables('numberOfExternalIps'),0))]", "dependsOn": [ "extpipcopy" ], "location": location, "tags": tags, "name": "[variables('externalLoadBalancerName')]", "properties": { "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ], "copy": [ { "name": "frontendIPConfigurations", "count": "[if(not(equals(variables('numberOfExternalIps'), 0)), variables('numberOfExternalIps'), 1)]", "input": { "name": "[concat('loadBalancerFrontEnd', copyIndex('frontendIPConfigurations', 1))]", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('frontendIPConfigurations', 1), 1))]" } } } } ] }, "type": "Microsoft.Network/loadBalancers" }]
    probes_to_use = [{"name": "[concat('tcp-probe-', parameters('internalLoadBalancerProbePort'))]", "properties": { "protocol": "Tcp", "port": "[parameters('internalLoadBalancerProbePort')]", "intervalInSeconds": 5, "numberOfProbes": 2 }}]
    lb_rules_to_use = [{"name": "[if(equals(parameters('internalLoadBalancerType'),'Per-protocol'), concat('lbRule-', parameters('internalLoadBalancerProbePort')), 'allProtocolLbRule')]", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('internalLoadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('internalLoadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('internalLoadBalancerName')), '/probes/tcp-probe-', parameters('internalLoadBalancerProbePort'))]" }, "frontendPort": "[if(equals(parameters('internalLoadBalancerType'),'Per-protocol'), parameters('internalLoadBalancerProbePort'), 0)]", "backendPort": "[if(equals(parameters('internalLoadBalancerType'),'Per-protocol'), parameters('internalLoadBalancerProbePort'), 0)]", "enableFloatingIP": False, "idleTimeoutInMinutes": 15, "protocol": "[if(equals(parameters('internalLoadBalancerType'),'Per-protocol'), 'Tcp', 'All')]", "loadDistribution": "Default" }}]
    resources_list += [{ "apiVersion": network_api_version, "name": "[variables('internalLoadBalancerName')]", "condition": "[not(equals(parameters('internalLoadBalancerType'),'DO_NOT_USE'))]", "type": "Microsoft.Network/loadBalancers", "location": location, "tags": tags, "dependsOn": depends_on_ext, "properties": { "frontendIPConfigurations": [ { "name": "LoadBalancerFrontEnd", "properties": { "privateIPAddress":  "[variables('internalLoadBalancerAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ], "backendAddressPools": [ { "name": "LoadBalancerBackEnd" } ], "loadBalancingRules": lb_rules_to_use, "probes": probes_to_use } }]
if template_name in ('autoscale_ltm_via-lb', 'autoscale_waf_via-lb'):
    scale_ports = { 'ssh_start': 50001, 'ssh_end': 50100, 'https_start': 50101, 'https_end': 50200 }
    inbound_nat_pools_static = []
    if license_type == 'BIGIQ_PAYG':
        # Update ports if static VMSS is using start range
        scale_ports_static = { 'ssh_start': 50001, 'ssh_end': 50009, 'https_start': 50101, 'https_end': 50109 }
        scale_ports = { 'ssh_start': 50010, 'ssh_end': 50100, 'https_start': 50110, 'https_end': 50200 }
        inbound_nat_pools_static = [ { "name": "sshnatpool-static", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPortRangeStart": scale_ports_static['ssh_start'], "frontendPortRangeEnd": scale_ports_static['ssh_end'], "backendPort": 22 } }, { "name": "mgmtnatpool-static", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPortRangeStart": scale_ports_static['https_start'], "frontendPortRangeEnd": scale_ports_static['https_end'], "backendPort": "[variables('bigIpMgmtPort')]" } } ]
    inbound_nat_pools = [ { "name": "sshnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPortRangeStart": scale_ports['ssh_start'], "frontendPortRangeEnd": scale_ports['ssh_end'], "backendPort": 22 } }, { "name": "mgmtnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPortRangeStart":  scale_ports['https_start'], "frontendPortRangeEnd": scale_ports['https_end'], "backendPort": "[variables('bigIpMgmtPort')]" } } ]
    inbound_nat_pools = inbound_nat_pools + inbound_nat_pools_static
    lb_def = { "apiVersion": network_api_version, "name": "[variables('externalLoadBalancerName')]", "type": "Microsoft.Network/loadBalancers", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'))]" ], "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('mgmtPublicIPAddressId')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ], "inboundNatPools": inbound_nat_pools, "loadBalancingRules": lb_rules_to_use, "probes": probes_to_use } }
    if license_type == 'BIGIQ_PAYG':
        lb_def['sku'] = { "name": "Standard" }
    resources_list += [lb_def]

###### Load Balancer Inbound NAT Rule(s) ######
if template_name == 'failover-lb_1nic':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('externalLoadBalancerName'),'/guimgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPort": "[copyIndex(8443)]", "backendPort": "[variables('bigIpMgmtPort')]", "enableFloatingIP": False } }]
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('externalLoadBalancerName'),'/sshmgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPort": "[copyIndex(8022)]", "backendPort": 22, "enableFloatingIP": False } }]

######## Availability Set Resource(s) ######
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_1nic', 'failover-lb_3nic'):
    avset = { "apiVersion": api_version, "location": location, "name": "[variables('availabilitySetName')]", "tags": tags, "type": "Microsoft.Compute/availabilitySets" }
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
        if stack_type in ('existing_stack', 'prod_stack'):
            avset['condition'] = "[equals(toUpper(parameters('avSetChoice')), 'CREATE_NEW')]"
    resources_list += [avset]

###### Storage Account Resource(s) ######
resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "kind": "Storage", "location": location, "name": "[variables('newStorageAccountName0')]", "tags": tags, "sku": { "name": "[variables('storageAccountType')]", "tier": "[variables('storageAccountTier')]" } }]
resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "kind": "Storage", "location": location, "name": "[variables('newDataStorageAccountName')]", "tags": tags, "sku": { "name": "[variables('dataStorageAccountType')]", "tier": "Standard" } }]
if template_name in ('failover-api', 'failover-lb_1nic', 'failover-lb_3nic'):
    resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "kind": "Storage", "location": location, "name": "[variables('newStorageAccountName1')]", "tags": tags, "sku": { "name": "[variables('storageAccountType')]", "tier": "[variables('storageAccountTier')]" } }]

###### Compute/VM Resource(s) ######
depends_on = "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]"
depends_on = list(depends_on)
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'))]")
if template_name == 'standalone_1nic':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }]
if template_name in ('standalone_2nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]")
if template_name in ('standalone_3nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('intNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]"); depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]")
if template_name in ('standalone_n-nic'):
    nic_reference = "[concat(take(variables('selfNicConfigArray'), 3), take(variables('addtlNicConfigArray').values, parameters('numberOfAdditionalNics')))]"
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]"); depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]"); depends_on.append("addtlniccopy")
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
    resources_list += [{"apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "dependsOn": depends_on, "location": location, "name": "[variables('instanceName')]", "tags": tags, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[reference(concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  nic_reference }, "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "osProfile": { "computerName": "[variables('instanceName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vhds/', variables('instanceName'),'.vhd')]" } } } } }]
if template_name == 'failover-lb_1nic':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "name": "[concat(variables('deviceNamePrefix'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), copyindex())]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName1'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "devicecopy" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "osProfile": { "computerName": "[concat(variables('deviceNamePrefix'),copyindex())]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "name": "[concat('osdisk',copyindex())]", "vhd": { "uri": "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables(concat('newStorageAccountName', copyIndex()))), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vhds/', copyindex(),'.vhd')]" }, "caching": "ReadWrite", "createOption": "FromImage" } }, "networkProfile": { "networkInterfaces": [ { "id": "[concat(resourceId('Microsoft.Network/networkInterfaces',variables('mgmtNicName')),copyindex())]" } ] }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[reference(concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob]" } } } }]
if template_name in ('failover-api', 'failover-lb_3nic'):
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), '0')]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'), '0')]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'), '0')]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '0')]", "plan": { "name": "[variables('skuToUse')]", "product": "[variables('offerToUse')]", "publisher": "f5-networks" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('availabilitySetName'))]" }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[reference(concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces": [ { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('mgmtNicName'), '0'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('extNicName'), '0'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('intNicName'), '0'))]", "properties": { "primary": False } } ] }, "osProfile": { "adminPassword": "[parameters('adminPassword')]", "adminUsername": "[parameters('adminUsername')]", "computerName": "[variables('instanceName')]" }, "storageProfile": { "imageReference": { "offer": "[variables('offerToUse')]", "publisher": "f5-networks", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vhds/', variables('instanceName'),'0.vhd')]" } } } }, "tags": tags, "type": "Microsoft.Compute/virtualMachines" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), '1')]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'), '1')]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'), '1')]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName1'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '1')]", "plan": { "name": "[variables('skuToUse')]", "product": "[variables('offerToUse')]", "publisher": "f5-networks" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('availabilitySetName'))]" }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[reference(concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces": [ { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('mgmtNicName'), '1'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('extNicName'), '1'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('intNicName'), '1'))]", "properties": { "primary": False } } ] }, "osProfile": { "adminPassword": "[parameters('adminPassword')]", "adminUsername": "[parameters('adminUsername')]", "computerName": "[variables('instanceName')]" }, "storageProfile": { "imageReference": { "offer": "[variables('offerToUse')]", "publisher": "f5-networks", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName1')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vhds/', variables('instanceName'),'1.vhd')]" } } } }, "tags": tags, "type": "Microsoft.Compute/virtualMachines" }]

# Add learning stack VM(s)
if learning_stack:
   resources_list += [{"apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "dependsOn": ["[concat('Microsoft.Network/networkInterfaces/', variables('webVmName'), '-nic')]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]"], "location": location, "name": "[variables('webVmName')]", "tags": tags, "properties": { "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('webVmName'), '-nic'))]" }] }, "osProfile": { "computerName": "[variables('webVmName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "Canonical", "offer": "UbuntuServer", "sku": "16.04.0-LTS", "version": "latest" }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "[concat(variables('dnsLabel'), '-web01', '-osdisk')]", "vhd": { "uri": "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vhds/', variables('webVmName'), '.vhd')]" } } } } }] 
###### Compute/VM Extension Resource(s) ######
command_to_execute = ''; command_to_execute2 = ''; route_add_cmd = ''; default_gw_cmd = "variables('tmmRouteGw')"

if template_name in ('standalone_1nic'):
    command_to_execute = "[concat(<MTU_CMD><BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module afm:none; <MTU_POST_CMD><POST_CMD_TO_EXECUTE>)]"
if template_name in ('standalone_2nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --log-level debug'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('standalone_3nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal --log-level debug'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('standalone_n-nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal ', variables('netCmd'), ' --log-level debug'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('failover-lb_1nic'):
    # Two Extensions for failover-lb_1nic
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/cluster.js --output /var/log/cloud/azure/cluster.log --log-level debug --host ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), ' --auto-sync --save-on-auto-sync'<POST_CMD_TO_EXECUTE>)]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix1')), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('deviceNamePrefix'), copyindex(1), '.azuresecurity.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/cluster.js --output /var/log/cloud/azure/cluster.log --log-level debug --host ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix1')), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix1')), ' --join-group --device-group Sync --sync --remote-host ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --remote-user svc_user --remote-password-url file:///config/cloud/.passwd'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('failover-api'):
    # Two Extensions for failover-api
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal --log-level debug; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/tgactive; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/tgrefresh; tmsh modify cm device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress'), '; ', variables('failoverCmdArray')[parameters('bigIpVersion')], '; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/cluster.js --output /var/log/cloud/azure/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', variables('intSubnetPrivateAddress'), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' --network-failover --auto-sync --save-on-auto-sync'<POST_CMD_TO_EXECUTE>)]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress1'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress1'), <INT_MASK_CMD> ',vlan:internal --log-level debug; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/tgactive; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/tgrefresh; tmsh modify cm device ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress1'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress1'), '; ', variables('failoverCmdArray')[parameters('bigIpVersion')], '; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/cluster.js --output /var/log/cloud/azure/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', variables('intSubnetPrivateAddress1'), ' --join-group --device-group Sync --sync --remote-host ', variables('mgmtSubnetPrivateAddress'), ' --remote-user svc_user --remote-password-url file:///config/cloud/.passwd'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('failover-lb_3nic'):
    # Two Extensions for failover-lb_3nic
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal --log-level debug; ', variables('failoverCmdArray')[parameters('enableNetworkFailover')].first, '; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/cluster.js --output /var/log/cloud/azure/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', variables('intSubnetPrivateAddress'), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' --network-failover --auto-sync --save-on-auto-sync'<POST_CMD_TO_EXECUTE>)]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress1'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress1'), <INT_MASK_CMD> ',vlan:internal --log-level debug; ', variables('failoverCmdArray')[parameters('enableNetworkFailover')].second, '; /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/cluster.js --output /var/log/cloud/azure/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', variables('intSubnetPrivateAddress1'), ' --join-group --device-group Sync --sync --remote-host ', variables('mgmtSubnetPrivateAddress'), ' --remote-user svc_user --remote-password-url file:///config/cloud/.passwd'<POST_CMD_TO_EXECUTE>)]"

## Base Start/Post Command to Execute
base_cmd_to_execute = "'mkdir -p /config/cloud/azure/node_modules/@f5devcentral && cp f5-cloud-libs.tar.gz* /config/cloud; mkdir -p /var/log/cloud/azure; function cp_logs() { cd /var/lib/waagent/custom-script/download && cp `ls -r | head -1`/std* /var/log/cloud/azure; }; TMP_DIR=/mnt/creds; TMP_CREDENTIALS_FILE=$TMP_DIR/.passwd; BIG_IP_CREDENTIALS_FILE=/config/cloud/.passwd; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null $BIG_IP_CREDENTIALS_FILE; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh;<BIGIQ_PWD_CMD> unset IFS; bash /config/installCloudLibs.sh; . /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/util.sh; create_temp_dir $TMP_DIR; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), '|sha512sum|cut -d \" \" -f 1|tr -d \"\n\" > $TMP_CREDENTIALS_FILE; bash /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/createUser.sh --user svc_user --password-file $TMP_CREDENTIALS_FILE; f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/encryptDataToFile.js --data-file $TMP_CREDENTIALS_FILE --out-file $BIG_IP_CREDENTIALS_FILE; wipe_temp_dir $TMP_DIR;<ANALYTICS_HASH> /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/onboard.js --output /var/log/cloud/azure/onboard.log --log-level debug --host '"
waagent_restart_cmd = ", '; if grep -i \"PUT failed\" /var/log/waagent.log -q; then echo \"Killing waagent exthandler, daemon should restart it\"; pkill -f \"python -u /usr/sbin/waagent -run-exthandlers\"; fi'"
post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl;<ROUTE_ADD_CMD><BIGIQ_PWD_DELETE> bash /config/customConfig.sh; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd

if template_name in 'failover-api':
    base_cmd_to_execute = "'mkdir -p /config/cloud/azure/node_modules/@f5devcentral && cp f5-cloud-libs*.tar.gz* /config/cloud; mkdir -p /var/log/cloud/azure; function cp_logs() { cd /var/lib/waagent/custom-script/download && cp `ls -r | head -1`/std* /var/log/cloud/azure; }; TMP_DIR=/mnt/creds; TMP_CREDENTIALS_FILE=$TMP_DIR/.passwd; BIG_IP_CREDENTIALS_FILE=/config/cloud/.passwd; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null $BIG_IP_CREDENTIALS_FILE; /usr/bin/install -b -m 400 /dev/null /config/cloud/.azCredentials; /usr/bin/install -b -m 755 /dev/null /config/cloud/managedRoutes; /usr/bin/install -b -m 755 /dev/null /config/cloud/routeTableTag;<BIGIQ_PWD_CMD> IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' > /config/verifyHash; echo -e ', variables('installCloudLibs'), ' > /config/installCloudLibs.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh; echo ', variables('singleQuote'), '{\"clientId\": \"', parameters('clientId'), '\", \"tenantId\": \"', parameters('tenantId'), '\", \"secret\": \"', parameters('servicePrincipalSecret'), '\", \"subscriptionId\": \"', variables('subscriptionID'), '\", \"storageAccount\": \"', variables('newDataStorageAccountName'), '\", \"storageKey\": \"', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('newDataStorageAccountName')), variables('storageApiVersion')).keys[0].value, '\", \"resourceGroupName\": \"', variables('resourceGroupName'), '\", \"uniqueLabel\": \"', variables('dnsLabel'), '\"}', variables('singleQuote'), ' > /config/cloud/.azCredentials; echo -e ', parameters('managedRoutes'), ' > /config/cloud/managedRoutes; echo -e ', parameters('routeTableTag'), ' > /config/cloud/routeTableTag; unset IFS; bash /config/installCloudLibs.sh; . /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/util.sh; create_temp_dir $TMP_DIR; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), '|sha512sum|cut -d \" \" -f 1|tr -d \"\n\" > $TMP_CREDENTIALS_FILE; bash /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/createUser.sh --user svc_user --password-file $TMP_CREDENTIALS_FILE; f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/encryptDataToFile.js --data-file $TMP_CREDENTIALS_FILE --out-file $BIG_IP_CREDENTIALS_FILE; wipe_temp_dir $TMP_DIR;<ANALYTICS_HASH> /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/onboard.js --output /var/log/cloud/azure/onboard.log --log-level debug --host '"
    post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl; base=', variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffixInt'), '; f3=$(echo $base | cut -d. -f1-3); last=$(echo $base | cut -d. -f4); for i in $(seq 1 ', variables('numberOfExternalIps'), '); do addr=${f3}.${last}; last=$((last+1)); tmsh create ltm virtual-address $addr address $addr; done;<ROUTE_ADD_CMD><BIGIQ_PWD_DELETE> bash /config/customConfig.sh; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd

# Link-local route command, for 2+ nic templates
if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
    route_add_cmd = " ', variables('routeCmdArray')[parameters('bigIpVersion')], ';"
# Default GW command is different for existing_stack
if stack_type in ('existing_stack', 'prod_stack'):
    default_gw_cmd = "concat(take(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, add(lastIndexOf(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, '.'), 1)), add(int(take(split(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, '.')[3], indexOf(split(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, '.')[3], '/'))), 1))"

## Map in some commandToExecute Elements
post_cmd_to_execute = post_cmd_to_execute.replace('<BIGIQ_PWD_DELETE>', bigiq_pwd_delete)
post_cmd_to_execute = post_cmd_to_execute.replace('<ROUTE_ADD_CMD>', route_add_cmd)
command_to_execute = command_to_execute.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute).replace('<POST_CMD_TO_EXECUTE>', post_cmd_to_execute)
command_to_execute2 = command_to_execute2.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute).replace('<POST_CMD_TO_EXECUTE>', post_cmd_to_execute)
command_to_execute = command_to_execute.replace('<EXT_MASK_CMD>', ext_mask_cmd).replace('<INT_MASK_CMD>', int_mask_cmd).replace('<DFL_GW_CMD>', default_gw_cmd)
command_to_execute2 = command_to_execute2.replace('<EXT_MASK_CMD>', ext_mask_cmd).replace('<INT_MASK_CMD>', int_mask_cmd).replace('<DFL_GW_CMD>', default_gw_cmd)
command_to_execute = command_to_execute.replace('<LICENSE1_COMMAND>', license1_command)
command_to_execute2 = command_to_execute2.replace('<LICENSE2_COMMAND>', license2_command)
command_to_execute = command_to_execute.replace('<BIGIQ_PWD_CMD>', big_iq_pwd_cmd)
command_to_execute2 = command_to_execute2.replace('<BIGIQ_PWD_CMD>', big_iq_pwd_cmd)

# Change MTU to 1400 for 1 NIC
mtu_cmd = "variables('networkMtuArray')[parameters('bigIpVersion')], '; ',"
if stack_type in ('existing_stack', 'prod_stack'):
    mtu_post_cmd = "if [[ $RUN_NETWORK == 1 ]]; then /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', concat(take(reference(variables('mgmtSubnetRef'), variables('networkApiVersion')).addressPrefix, add(lastIndexOf(reference(variables('mgmtSubnetRef'), variables('networkApiVersion')).addressPrefix, '.'), 1)), add(int(take(split(reference(variables('mgmtSubnetRef'), variables('networkApiVersion')).addressPrefix, '.')[3], indexOf(split(reference(variables('mgmtSubnetRef'), variables('networkApiVersion')).addressPrefix, '.')[3], '/'))), 1)), ' --self-ip name:self_1nic,address:', variables('mgmtSubnetPrivateAddress'), skip(reference(variables('mgmtSubnetRef'), variables('networkApiVersion')).addressPrefix, indexOf(reference(variables('mgmtSubnetRef'), variables('networkApiVersion')).addressPrefix, '/')), ',vlan:internal $EXT_ROUTE --log-level debug; fi'"
else:
    mtu_post_cmd = "if [[ $RUN_NETWORK == 1 ]]; then /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', variables('mgmtRouteGw'), ' --self-ip name:self_1nic,address:', variables('mgmtSubnetPrivateAddress'),  ',vlan:internal $EXT_ROUTE --log-level debug; fi'"
command_to_execute = command_to_execute.replace('<MTU_CMD>', mtu_cmd).replace('<MTU_POST_CMD>', mtu_post_cmd)
command_to_execute2 = command_to_execute2.replace('<MTU_CMD>', mtu_cmd).replace('<MTU_POST_CMD>', mtu_post_cmd)

# Add Usage Analytics Hash and Metrics Command
metrics_hash_to_exec = "', variables('allowUsageAnalytics')[parameters('allowUsageAnalytics')].hashCmd, ';"
metrics_cmd_to_exec = "', variables('allowUsageAnalytics')[parameters('allowUsageAnalytics')].metricsCmd, '"
command_to_execute = command_to_execute.replace('<ANALYTICS_HASH>', metrics_hash_to_exec).replace('<ANALYTICS_CMD>', metrics_cmd_to_exec)
command_to_execute2 = command_to_execute2.replace('<ANALYTICS_HASH>', metrics_hash_to_exec).replace('<ANALYTICS_CMD>', metrics_cmd_to_exec)


## Define base file(s) to download
file_uris = [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-iapps/', variables('f5CloudIappsTag'), '/f5-service-discovery/f5.service_discovery.tmpl')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-iapps/', variables('f5CloudIappsTag'), '/f5-cloud-logger/f5.cloud_logger.v1.0.0.tmpl')]" ]

## Define command to execute(s)
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
    resources_list += [{"apiVersion": "[variables('computeApiVersion')]", "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('instanceName'),'/start')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('instanceName'))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": file_uris }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
if template_name == 'failover-lb_1nic':
    # Two Extensions for failover-lb_1nic
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('deviceNamePrefix'),0,'/start')]", "apiVersion": "[variables('computeApiVersion')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),0)]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": file_uris }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "copy": { "name": "extensionLoop", "count": "[sub(parameters('numberOfInstances'), 1)]" }, "name": "[concat(variables('deviceNamePrefix'),add(copyindex(),1),'/start')]", "apiVersion": "[variables('computeApiVersion')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),add(copyindex(),1))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": file_uris }, "protectedSettings": { "commandToExecute": command_to_execute2 } } }]
if template_name in ('failover-api', 'failover-lb_3nic'):
    if template_name in ('failover-api'):
        file_uris += ["[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/dist/f5-cloud-libs-azure.tar.gz')]"]
    # Two Extensions for failover-api and failover-lb_3nic
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('dnsLabel'), '-', variables('instanceName'), '0')]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '0/start')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": file_uris }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('dnsLabel'), '-', variables('instanceName'), '1')]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '1/start')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute2 }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": file_uris }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]

# Add learning stack Custom Script Extension(s)
if learning_stack:
    file_uris = ["[concat('https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/', variables('f5NetworksTag'), '/experimental/reference/learning-stack/scripts/init_web.sh')]"]
    command_to_execute = "[concat('./init_web.sh ', variables('f5NetworksTag'))]"
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('webVmName'))]" ], "location": location, "name": "[concat(variables('webVmName'), '/webstart')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": file_uris }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]

###### Compute VM Scale Set(s) ######
autoscale_file_uris = ["[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-iapps/', variables('f5CloudIappsTag'), '/f5-service-discovery/f5.service_discovery.tmpl')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-iapps/', variables('f5CloudIappsTag'), '/f5-cloud-logger/f5.cloud_logger.v1.0.0.tmpl')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/dist/f5-cloud-libs-azure.tar.gz')]"]
addtl_setup = ""
addtl_encrypt_calls = ""
addtl_script_args = ""
if template_name in ('autoscale_ltm_via-dns', 'autoscale_waf_via-dns'):
    addtl_encrypt_calls = " echo ', variables('singleQuote'), parameters('dnsProviderPassword'), variables('singleQuote'), ' | tr -d \"\n\" > $TMP_CREDENTIALS_FILE; f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/encryptDataToFile.js --data-file $TMP_CREDENTIALS_FILE --out-file /config/cloud/.dnsPasswd;"
    addtl_script_args += ", ' --dnsOptions \\\"--dns gtm --dns-ip-type ', parameters('dnsMemberIpType'), ' --dns-app-port ', parameters('dnsMemberPort'), ' --dns-provider-options host:', parameters('dnsProviderHost'), ',port:', parameters('dnsProviderPort'), ',user:', parameters('dnsProviderUser'), ',passwordUrl:file:///config/cloud/.dnsPasswd,passwordEncrypted:true,serverName:', variables('vmssName'), ',poolName:', parameters('dnsProviderPool'), ',datacenter:', parameters('dnsProviderDataCenter'), '\\\"'"
if template_name in ('autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    addtl_setup += "cp asm-policy.tar.gz deploy_waf.sh *.tmpl /config/cloud;"
    addtl_script_args += ", ' --wafScriptArgs \\\"', variables('commandArgs'), '\\\"'"
    autoscale_file_uris += ["[concat(variables('f5NetworksSolutionScripts'), 'deploy_waf.sh')]", "[concat(variables('f5NetworksSolutionScripts'), 'f5.http.v1.2.0rc7.tmpl')]", "[concat(variables('f5NetworksSolutionScripts'), 'f5.policy_creator.tmpl')]", "[concat(variables('f5NetworksSolutionScripts'), 'asm-policy.tar.gz')]"]

if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    # Add TMM CPU metric option into autoscale templates - pass key into autoscale.sh
    addtl_script_args += ", ' --appInsightsKey ', reference(resourceId(variables('appInsightsNameArray')[1], 'Microsoft.Insights/components', variables('appInsightsNameArray')[0]), variables('appInsightsComponentsApiVersion')).InstrumentationKey"
    if template_name in ('autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
        post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh modify cm device-group Sync asm-sync enabled; tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl;<BIGIQ_PWD_DELETE> bash /config/customConfig.sh; reboot_signal=\"/tmp/f5-cloud-libs-signals/REBOOT_REQUIRED\"; if [ -f $reboot_signal ]; then echo \"Reboot signaled by cloud libs, rebooting\"; rm -f $reboot_signal; reboot; else echo \"Cloud libs did not signal a reboot\"; fi; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd
    else:
        post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl;<BIGIQ_PWD_DELETE> bash /config/customConfig.sh; reboot_signal=\"/tmp/f5-cloud-libs-signals/REBOOT_REQUIRED\"; if [ -f $reboot_signal ]; then echo \"Reboot signaled by cloud libs, rebooting\"; rm -f $reboot_signal; reboot; else echo \"Cloud libs did not signal a reboot\"; fi; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd
    autoscale_command_to_execute = "[concat('mkdir -p /config/cloud/azure/node_modules/@f5devcentral; mkdir -p /var/log/cloud/azure; function cp_logs() { cd /var/lib/waagent/custom-script/download && cp `ls -r | head -1`/std* /var/log/cloud/azure; }; <ADDTL_SETUP>AZURE_CREDENTIALS_FILE=/config/cloud/.azCredentials; TMP_DIR=/mnt/creds; TMP_CREDENTIALS_FILE=$TMP_DIR/.passwd; BIG_IP_CREDENTIALS_FILE=/config/cloud/.passwd; /usr/bin/install -m 400 /dev/null $AZURE_CREDENTIALS_FILE; /usr/bin/install -m 400 /dev/null $BIG_IP_CREDENTIALS_FILE; echo ', variables('singleQuote'), '{\"clientId\": \"', parameters('clientId'), '\", \"tenantId\": \"', parameters('tenantId'), '\", \"secret\": \"', parameters('servicePrincipalSecret'), '\", \"subscriptionId\": \"', variables('subscriptionID'), '\", \"storageAccount\": \"', variables('newDataStorageAccountName'), '\", \"storageKey\": \"', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('newDataStorageAccountName')), variables('storageApiVersion')).keys[0].value, '\", \"resourceGroupName\": \"', variables('resourceGroupName'), '\", \"loadBalancerName\": \"', variables('externalLoadBalancerName'), '\", \"appInsightsName\": \"', variables('appInsightsName'), '\", \"appInsightsId\": \"', reference(resourceId(variables('appInsightsNameArray')[1], 'Microsoft.Insights/components', variables('appInsightsNameArray')[0]), variables('appInsightsComponentsApiVersion')).AppId, '\"}', variables('singleQuote'), ' > $AZURE_CREDENTIALS_FILE;<BIGIQ_PWD_CMD> cp f5-cloud-libs*.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh; bash /config/installCloudLibs.sh; . /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/util.sh; create_temp_dir $TMP_DIR; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), '|sha512sum|cut -d \" \" -f 1|tr -d \"\n\" > $TMP_CREDENTIALS_FILE; bash /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/createUser.sh --user svc_user --password-file $TMP_CREDENTIALS_FILE; f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/encryptDataToFile.js --data-file $TMP_CREDENTIALS_FILE --out-file $BIG_IP_CREDENTIALS_FILE;<ADDTL_ENCRYPT_CALLS> wipe_temp_dir $TMP_DIR;', variables('allowUsageAnalytics')[parameters('allowUsageAnalytics')].hashCmd, '; <SCALE_SCRIPT_CALL><POST_CMD_TO_EXECUTE>)]"
    scale_script_call = " /usr/bin/f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js --output /var/log/cloud/azure/autoScaleScript.log --log-level debug --file /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs-azure/scripts/autoscale.sh --shell /bin/bash --cl-args \"--logLevel info --backupUcs 7 --resourceGroup ', resourceGroup().name, ' --vmssName ', variables('vmssName'), ' --userName svc_user --password /config/cloud/.passwd --azureSecretFile /config/cloud/.azCredentials --managementPort ', variables('bigIpMgmtPort'), ' --ntpServer ', parameters('ntpServer'), ' --timeZone ', parameters('timeZone'), variables('allowUsageAnalytics')[parameters('allowUsageAnalytics')].metricsCmd<ADDTL_SCRIPT_ARGS>"
    scale_script_call = scale_script_call.replace('<ADDTL_SCRIPT_ARGS>', addtl_script_args)
    # Add licensing (BIG-IQ)
    if license_type == 'BIGIQ_PAYG':
        static_scale_script_call = scale_script_call + static_license1_command + ", '\" --signal AUTOSCALE_SCRIPT_DONE'"
    scale_script_call = scale_script_call + license1_command + ", '\" --signal AUTOSCALE_SCRIPT_DONE'"

    # Map in dynamic items
    post_cmd_to_execute = post_cmd_to_execute.replace('<BIGIQ_PWD_DELETE>', bigiq_pwd_delete)
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<ADDTL_SETUP>', addtl_setup).replace('<BIGIQ_PWD_CMD>', big_iq_pwd_cmd)
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<POST_CMD_TO_EXECUTE>', post_cmd_to_execute)
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<ADDTL_ENCRYPT_CALLS>', addtl_encrypt_calls)
    # Modified command to execute for static VMSS
    if license_type == 'BIGIQ_PAYG':
        static_autoscale_command_to_execute = autoscale_command_to_execute.replace('<SCALE_SCRIPT_CALL>', static_scale_script_call)
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<SCALE_SCRIPT_CALL>', scale_script_call)

if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):   
    lb_inbound_nat_pools = [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/inboundNatPools/sshnatpool')]" }, { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/inboundNatPools/mgmtnatpool')]" } ]
    ipConfigProperties = { "subnet": { "id": "[variables('mgmtSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/backendAddressPools/loadBalancerBackEnd')]" } ], "loadBalancerInboundNatPools": lb_inbound_nat_pools }
    if template_name in ('autoscale_ltm_via-dns', 'autoscale_waf_via-dns'):
        ipConfigProperties = { "subnet": { "id": "[variables('mgmtSubnetId')]" }, "publicIpAddressConfiguration": { "name": "publicIp01", "properties": { "idleTimeoutInMinutes": 15 } } }
    resources_list += [{ "type": "Microsoft.Compute/virtualMachineScaleSets", "apiVersion": compute_api_version, "name": "[variables('vmssName')]", "location": location, "tags": tags, "dependsOn": scale_depends_on + ["[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0'))]"], "sku": { "name": "[parameters('instanceType')]", "tier": "Standard", "capacity": "[parameters('vmScaleSetMinCount')]" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "upgradePolicy": { "mode": "Manual" }, "virtualMachineProfile": { "storageProfile": { "osDisk": { "vhdContainers": [ "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vmss1/')]" ], "name": "vmssosdisk", "caching": "ReadOnly", "createOption": "FromImage" }, "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use } }, "osProfile": { "computerNamePrefix": "[variables('vmssName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "networkProfile": { "networkInterfaceConfigurations": [ { "name": "nic1", "properties": { "primary": True, "networkSecurityGroup": {"id": "[variables('mgmtNsgID')]"}, "ipConfigurations": [ { "name": "ipconfig1", "properties": ipConfigProperties } ] } } ] }, "extensionProfile": { "extensions": [ { "name":"main", "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": autoscale_file_uris }, "protectedSettings": { "commandToExecute": autoscale_command_to_execute } } } ] } }, "overprovision": False } }]
    if license_type == 'BIGIQ_PAYG':
        # Static VMSS
        lb_inbound_nat_pools = [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/inboundNatPools/sshnatpool-static')]" }, { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/inboundNatPools/mgmtnatpool-static')]" } ]
        ipConfigProperties = { "subnet": { "id": "[variables('mgmtSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/backendAddressPools/loadBalancerBackEnd')]" } ], "loadBalancerInboundNatPools": lb_inbound_nat_pools }
        resources_list += [{ "type": "Microsoft.Compute/virtualMachineScaleSets", "apiVersion": compute_api_version, "name": "[variables('staticVmssName')]", "location": location, "tags": static_vmss_tags, "dependsOn": scale_depends_on + ["[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0'))]"], "sku": { "name": "[parameters('instanceType')]", "tier": "Standard", "capacity": "[parameters('numberOfStaticInstances')]" }, "plan": { "name": "[variables('staticSkuToUse')]", "publisher": "f5-networks", "product": "[variables('staticOfferToUse')]" }, "properties": { "upgradePolicy": { "mode": "Manual" }, "virtualMachineProfile": { "storageProfile": { "osDisk": { "vhdContainers": [ "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName0')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'static-vmss/')]" ], "name": "vmssosdisk", "caching": "ReadOnly", "createOption": "FromImage" }, "imageReference": { "publisher": "f5-networks", "offer": "[variables('staticOfferToUse')]", "sku": "[variables('staticSkuToUse')]", "version": image_to_use } }, "osProfile": { "computerNamePrefix": "[variables('vmssName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "networkProfile": { "networkInterfaceConfigurations": [ { "name": "nic1", "properties": { "primary": True, "networkSecurityGroup": {"id": "[variables('mgmtNsgID')]"}, "ipConfigurations": [ { "name": "ipconfig1", "properties": ipConfigProperties } ] } } ] }, "extensionProfile": { "extensions": [ { "name":"main", "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": autoscale_file_uris }, "protectedSettings": { "commandToExecute": static_autoscale_command_to_execute } } } ] } }, "overprovision": False } }]

###### Compute VM Scale Set(s) AutoScale Settings ######
if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    depends_on = ["[variables('vmssId')]"]
    if license_type == 'BIGIQ_PAYG':
        depends_on.append("[variables('staticVmssId')]")
    resources_list += [{ "type": "Microsoft.Insights/autoscaleSettings", "apiVersion": "[variables('appInsightsApiVersion')]", "name": "autoscaleconfig", "location": location, "dependsOn": depends_on, "properties": { "name": "autoscaleconfig", "targetResourceUri": "[variables('vmssId')]", "enabled": True, "profiles": [ { "name": "Profile1", "capacity": { "minimum": "[parameters('vmScaleSetMinCount')]", "maximum": "[parameters('vmScaleSetMaxCount')]", "default": "[parameters('vmScaleSetMinCount')]" }, "rules": [ { "metricTrigger": { "metricName": "[variables('scaleMetricMap')[variables('autoScaleMetric')].metricName]", "metricNamespace": "", "metricResourceUri": "[variables('scaleMetricMap')[variables('autoScaleMetric')].metricResourceUri]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('timeWindow')]", "timeAggregation": "Average", "operator": "GreaterThan", "threshold": "[variables('scaleMetricMap')[variables('autoScaleMetric')].thresholdOut]" }, "scaleAction": { "direction": "Increase", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } }, { "metricTrigger": { "metricName": "[variables('scaleMetricMap')[variables('autoScaleMetric')].metricName]", "metricNamespace": "", "metricResourceUri": "[variables('scaleMetricMap')[variables('autoScaleMetric')].metricResourceUri]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('timeWindow')]", "timeAggregation": "Average", "operator": "LessThan", "threshold": "[variables('scaleMetricMap')[variables('autoScaleMetric')].thresholdIn]" }, "scaleAction": { "direction": "Decrease", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } } ] } ], "notifications": [ { "operation": "Scale", "email": { "sendToSubscriptionAdministrator": False, "sendToSubscriptionCoAdministrators": False, "customEmails": "[variables('customEmail')]" }, "webhooks": [] } ] } }]


###### Appliction Insight Workspace(s) ######
# Add TMM CPU metric option into autoscale templates
if template_name in ('autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns'):
    resources_list += [{ "type": "Microsoft.Insights/components", "condition": "[contains(toUpper(parameters('appInsights')), 'CREATE_NEW')]", "kind": "other", "name": "[variables('appInsightsName')]", "apiVersion": "[variables('appInsightsComponentsApiVersion')]", "location": "[variables('appInsightsLocation')]", "tags": tags, "properties": { "ApplicationId": "[variables('appInsightsName')]", "Application_Type": "other" }, "dependsOn": [] }]

## Sort resources section - Expand to choose order of resources instead of just alphabetical?
resources_sorted = json.dumps(resources_list, sort_keys=True, indent=4, ensure_ascii=False)
data['resources'] = json.loads(resources_sorted, object_pairs_hook=OrderedDict)

# Prod Stack Strip Public IP Address Function
if stack_type == 'prod_stack':
    master_helper.pub_ip_strip(data['variables'], 'PublicIpAddress', 'variables')
    master_helper.pub_ip_strip(data['resources'], 'PublicIpAddress', 'resources')

######################################## ARM Outputs ########################################
## Note: Change outputs if prod_stack as public IP's are not attached to the BIG-IP's
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
    if stack_type == 'prod_stack':
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://', reference(variables('mgmtNicId')).ipConfigurations[0].properties.privateIPAddress, ':', variables('bigIpMgmtPort'))]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtNicId')).ipConfigurations[0].properties.privateIPAddress, ' ',22)]" }
    else:
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://', reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ':', variables('bigIpMgmtPort'))]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ' ',22)]" }
    # Add learning stack output(s)
    if learning_stack:
        data['outputs']['EXAMPLE-APP-URL'] = { "type": "string", "value": "[concat('http://', reference(concat(variables('extPublicIPAddressIdPrefix'), '0')).dnsSettings.fqdn, ':', variables('webVmVsPort'))]" }
if template_name == 'failover-lb_1nic':
    if stack_type == 'prod_stack':
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(concat(variables('mgmtNicId'), 0)).ipConfigurations[0].properties.privateIPAddress,':8443')]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(concat(variables('mgmtNicId'), 0)).ipConfigurations[0].properties.privateIPAddress,' ',8022)]" }
    else:
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':8443')]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',8022)]" }
if template_name in ('failover-api', 'failover-lb_3nic'):
    if stack_type == 'prod_stack':
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(concat(variables('mgmtNicId'), '0')).ipConfigurations[0].properties.privateIPAddress, ':', variables('bigIpMgmtPort'))]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(concat(variables('mgmtNicId'), '0')).ipConfigurations[0].properties.privateIPAddress,' ',22)]" }
    else:
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(concat(variables('mgmtPublicIPAddressId'), '0')).dnsSettings.fqdn, ':', variables('bigIpMgmtPort'))]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(concat(variables('mgmtPublicIPAddressId'), '0')).dnsSettings.fqdn,' ',22)]" }
    # Add learning stack output(s)
    if learning_stack:
        data['outputs']['EXAMPLE-APP-URL'] = { "type": "string", "value": "[concat('http://', reference(concat(variables('extPublicIPAddressIdPrefix'), '0')).dnsSettings.fqdn, ':', variables('webVmVsPort'))]" }
if template_name in ('autoscale_ltm_via-lb', 'autoscale_waf_via-lb'):
    if license_type == 'BIGIQ_PAYG':
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':50101', ' - 50109')]" }
        data['outputs']['GUI-URL-DYNAMIC'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':50110', ' - 50200')]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',50001, ' - 50009')]" }
        data['outputs']['SSH-URL-DYAMIC'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',50010, ' - 50100')]" }
    else:
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':50101', ' - 50200')]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',50001, ' - 50100')]" }
if template_name in ('autoscale_ltm_via-dns', 'autoscale_waf_via-dns'):
    # Do nothing currently
    data['outputs']['GUI-URL'] = { "type": "string", "value": "N/A" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "N/A" }
######################################## End Create/Modify ARM Template Objects ########################################

## Write modified template(s) to appropriate location
with open(created_file, 'w') as finished:
    json.dump(data, finished, indent=4, sort_keys=False, ensure_ascii=False)
with open(created_file_params, 'w') as finished_params:
    json.dump(data_params, finished_params, indent=4, sort_keys=False, ensure_ascii=False)


###### Prepare some information prior to creating Scripts/Readme's ######
if stack_type in ('prod_stack'):
    all_lic = ['BYOL', 'PAYG']
else:
    all_lic = ['BYOL', 'PAYG', 'BIG-IQ']
lic_support = {'standalone_1nic': all_lic, 'standalone_2nic': all_lic, 'standalone_3nic': all_lic, 'standalone_n-nic': all_lic, 'failover-lb_1nic': all_lic, 'failover-lb_3nic': all_lic, 'failover-api': all_lic, 'autoscale_ltm_via-lb': ['PAYG', 'BIG-IQ'], 'autoscale_ltm_via-dns': ['PAYG', 'BIG-IQ'], 'autoscale_waf_via-lb': ['PAYG', 'BIG-IQ'], 'autoscale_waf_via-dns': ['PAYG', 'BIG-IQ']}
# Experimental autoscale templates have new licensing options
if support_type == 'experimental':
    lic_support['autoscale_ltm_via-lb'] = ['PAYG', 'BIG-IQ', 'BIG-IQ+PAYG']
    lic_support['autoscale_waf_via-lb'] = ['PAYG', 'BIG-IQ', 'BIG-IQ+PAYG']
lic_key_count = {'standalone_1nic': 1, 'standalone_2nic': 1, 'standalone_3nic': 1, 'standalone_n-nic': 1, 'failover-lb_1nic': 2, 'failover-lb_3nic': 2, 'failover-api': 2, 'autoscale_ltm_via-lb': 0, 'autoscale_ltm_via-dns': 0, 'autoscale_waf_via-lb': 0, 'autoscale_waf_via-dns': 0}
api_access_required = {'standalone_1nic': None, 'standalone_2nic': None, 'standalone_3nic': None, 'standalone_n-nic': None, 'failover-lb_1nic': None, 'failover-lb_3nic': None, 'failover-api': 'required', 'autoscale_ltm_via-lb': 'required', 'autoscale_ltm_via-dns': 'required', 'autoscale_waf_via-lb': 'required', 'autoscale_waf_via-dns': 'required'}
template_info = {'template_name': template_name, 'location': script_location, 'lic_support': lic_support, 'lic_key_count': lic_key_count, 'api_access_required': api_access_required}

## Abstract license key parameters for readme_generator/script_generator ##
license_params = OrderedDict([('numberOfStaticInstances',['BIG-IQ+PAYG']), ('licenseKey1',['BYOL']), ('licenseKey2',['BYOL']), ('licensedBandwidth',['PAYG',]), ('bigIqLicenseHost',['BIG-IQ']), ('bigIqLicenseUsername',['BIG-IQ']), ('bigIqLicensePassword',['BIG-IQ']), ('bigIqLicensePool',['BIG-IQ'])])
# licenseKey2 is only used by cluster templates
if template_name not in ('failover-lb_1nic', 'failover-lb_3nic', 'failover-api'):
    license_params.pop('licenseKey2')
# BIGIQ+PAYG is only in experimental autoscale
if template_name in ('autoscale_ltm_via-lb', 'autoscale_waf_via-lb') and 'experimental' in support_type:
    bigiq_payg_list = ['licensedBandwidth', 'bigIqLicenseHost', 'bigIqLicenseUsername', 'bigIqLicensePassword', 'bigIqLicensePool']
    [license_params[k].append('BIG-IQ+PAYG') for k in bigiq_payg_list]
else:
    license_params.pop('numberOfStaticInstances')
# BIG-IQ does not exist for prod_stack currently
if stack_type in ('prod_stack'):
    [license_params.pop(k) for k in ['bigIqLicenseHost', 'bigIqLicenseUsername', 'bigIqLicensePassword', 'bigIqLicensePool']]

######################################## Create/Modify Scripts ###########################################
# Manually adding templates to create scripts proc for now as a 'check'...
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_1nic', 'failover-lb_3nic', 'failover-api', 'autoscale_ltm_via-lb', 'autoscale_ltm_via-dns', 'autoscale_waf_via-lb', 'autoscale_waf_via-dns') and script_location:
    s_data = {'template_info': template_info, 'license_params': license_params, 'default_payg_bw': default_payg_bw}
    bash_script = script_generator.script_creation(data, s_data, 'bash')
    ps_script = script_generator.script_creation(data, s_data, 'powershell')
######################################## END Create/Modify Scripts ########################################

######################################## Create/Modify README's ########################################
    readme_text = {'deploy_links': {}, 'ps_script': {}, 'bash_script': {}}
    ## Deploy Buttons ##
    readme_text['deploy_links']['version_tag'] = f5_networks_tag
    readme_text['deploy_links']['lic_support'] = template_info['lic_support']
    ## Example Scripts - These are set above, just adding to README ##
    readme_text['bash_script'] = bash_script
    readme_text['ps_script'] = ps_script

    #### Call function to create/update README ####
    i_data = {'template_info': template_info, 'license_params': license_params, 'readme_text': readme_text, 'template_location': created_file, 'files': {}}
    folder_loc = 'files/readme_files/'
    i_data['files']['doc_text_file'] = folder_loc + 'template_text.yaml'
    i_data['files']['misc_readme_file'] = folder_loc + 'misc.README.txt'
    i_data['files']['base_readme'] = folder_loc + 'base.README.md'
    rG = readme_generator.ReadmeGen()
    rG.create(data, i_data)
######################################## END Create/Modify README's ########################################