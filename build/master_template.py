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
parser.add_option("-n", "--template-name", action="store", type="string", dest="template_name", help="Template Name: standalone_1nic, standalone_2nic, cluster_1nic, etc.")
parser.add_option("-l", "--license-type", action="store", type="string", dest="license_type", help="License Type: BYOL or PAYG")
parser.add_option("-m", "--stack-type", action="store", type="string", dest="stack_type", default="new_stack", help="Networking Stack Type: new_stack or existing_stack")
parser.add_option("-t", "--template-location", action="store", type="string", dest="template_location", help="Template Location: such as ../experimental/standalone/1nic/PAYG/")
parser.add_option("-s", "--script-location", action="store", type="string", dest="script_location", help="Script Location: such as ../experimental/standalone/1nic/")
parser.add_option("-v", "--solution-location", action="store", type="string", dest="solution_location", default="experimental", help="Solution location: experimental or supported")

(options, args) = parser.parse_args()
template_name = options.template_name
license_type = options.license_type
stack_type = options.stack_type
template_location = options.template_location
script_location = options.script_location
solution_location = options.solution_location

## Specify meta file and file to create(should be argument)
metafile = 'files/tmpl_files/base.azuredeploy.json'
metafile_params = 'files/tmpl_files/base.azuredeploy.parameters.json'
created_file = template_location + 'azuredeploy.json'
createdfile_params = template_location + 'azuredeploy.parameters.json'

## Static Variable Defaults
nic_reference = ""
command_to_execute = ""

## Static Variable Assignment ##
content_version = '3.2.1.0'
f5_networks_tag = 'v3.2.1.0'
f5_cloud_libs_tag = 'ese-1120'
f5_cloud_libs_azure_tag = 'v1.2.0'
f5_cloud_iapps_tag = 'v1.0.2'
f5_cloud_workers_tag = 'v1.0.0'
f5_tag = '82e08e16-fc62-4bf0-8916-e1c02dc871cd'
f5_template_tag = template_name
# Set BIG-IP versions to allow
default_big_ip_version = '13.0.021'
allowed_big_ip_versions = ["13.0.021", "12.1.24", "latest"]
version_port_map = {"latest": {"Port": 8443}, "13.0.021": {"Port": 8443}, "12.1.24": {"Port": 443}, "443": {"Port": 443}}

install_cloud_libs = """[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit 1\nfi\necho loaded verifyHash\nscript_loc="/var/lib/waagent/custom-script/download/0/"\nconfig_loc="/config/cloud/"\nhashed_file_list="<HASHED_FILE_LIST>"\nfor file in $hashed_file_list; do\necho "verifying $file"\n/usr/bin/tmsh run cli script verifyHash $file\nif [ $? != 0 ]; then\necho "$file is not valid"\nexit 1\nfi\necho "verified $file"\ndone\necho "expanding $hashed_file_list"\ntar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/node_modules\n<TAR_LIST>touch /config/cloud/cloudLibsReady', variables('singleQuote'))]"""
# Automate Verify Hash - the verify_hash function will go out and pull in the latest hash file
verify_hash = '''[concat(variables('singleQuote'), '<CLI_SCRIPT>', variables('singleQuote'))]'''
verify_hash_url = "https://gitswarm.f5net.com/cloudsolutions/f5-cloud-libs/raw/" + f5_cloud_libs_tag + "/dist/verifyHash"
verify_hash = verify_hash.replace('<CLI_SCRIPT>', master_helper.verify_hash(verify_hash_url))

hashed_file_list = "${config_loc}f5-cloud-libs.tar.gz ${script_loc}f5.service_discovery.tmpl"
additional_tar_list = ""
if template_name in ('ltm_autoscale', 'ha-avset'):
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz"
    additional_tar_list = "tar xvfz /config/cloud/f5-cloud-libs-azure.tar.gz -C /config/cloud/node_modules/f5-cloud-libs/node_modules\n"
elif template_name in 'waf_autoscale':
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz ${script_loc}deploy_waf.sh ${script_loc}f5.http.v1.2.0rc7.tmpl ${script_loc}f5.policy_creator.tmpl ${script_loc}asm-policy.tar.gz"
    additional_tar_list = "tar xvfz /config/cloud/f5-cloud-libs-azure.tar.gz -C /config/cloud/node_modules/f5-cloud-libs/node_modules\n"
#### Temp empty hashed file list when testing new cloud libs....
hashed_file_list = ""
install_cloud_libs = install_cloud_libs.replace('<HASHED_FILE_LIST>', hashed_file_list)
install_cloud_libs = install_cloud_libs.replace('<TAR_LIST>', additional_tar_list)
instance_type_list = ["Standard_A2", "Standard_A3", "Standard_A4", "Standard_A5", "Standard_A6", "Standard_A7", "Standard_D2", "Standard_D3", "Standard_D4", "Standard_D11", "Standard_D12", "Standard_D13", "Standard_D14", "Standard_DS2", "Standard_DS3", "Standard_DS4", "Standard_DS11", "Standard_DS12", "Standard_DS13", "Standard_DS14", "Standard_D2_v2", "Standard_D3_v2", "Standard_D4_v2", "Standard_D5_v2", "Standard_D11_v2", "Standard_D12_v2", "Standard_D13_v2", "Standard_D14_v2", "Standard_D15_v2", "Standard_DS2_v2", "Standard_DS3_v2", "Standard_DS4_v2", "Standard_DS5_v2", "Standard_DS11_v2", "Standard_DS12_v2", "Standard_DS13_v2", "Standard_DS14_v2", "Standard_DS15_v2", "Standard_F2", "Standard_F4", "Standard_F8", "Standard_F2S", "Standard_F4S", "Standard_F8S", "Standard_F16S", "Standard_G2", "Standard_G3", "Standard_G4", "Standard_G5", "Standard_GS2", "Standard_GS3", "Standard_GS4", "Standard_GS5"]
tags = {"application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]", "f5": "[variables('f5Tag')]", "f5Template":"[variables('f5TemplateTag')]"}
tag_values = {"application":"APP", "environment":"ENV", "group":"GROUP", "owner":"OWNER", "cost":"COST"}
api_version = "[variables('apiVersion')]"
compute_api_version = "[variables('computeApiVersion')]"
network_api_version = "[variables('networkApiVersion')]"
storage_api_version = "[variables('storageApiVersion')]"
insights_api_version = "[variables('insightsApiVersion')]"
location = "[variables('location')]"
default_payg_bw = '200m'
nic_port_map = "[variables('bigIpNicPortMap')['1'].Port]"
default_instance = "Standard_DS2_v2"

## Update port map variable if deploying multi_nic template
if template_name in 'standalone_2nic':
    nic_port_map = "[variables('bigIpNicPortMap')['2'].Port]"
if template_name in ('standalone_3nic', 'standalone_multi-nic', 'ha-avset', 'cluster_3nic'):
    nic_port_map = "[variables('bigIpNicPortMap')['3'].Port]"

## Update allowed instances available based on solution
disallowed_instance_list = []
if template_name in 'waf_autoscale':
    disallowed_instance_list = ["Standard_A2", "Standard_F2"]
if template_name in ('standalone_3nic', 'standalone_multi-nic', 'ha-avset', 'cluster_3nic'):
    default_instance = "Standard_DS3_v2"
    disallowed_instance_list = ["Standard_A2", "Standard_D2", "Standard_DS2", "Standard_D2_v2", "Standard_DS2_v2", "Standard_F2", "Standard_F2S", "Standard_G2", "Standard_GS2"]
for instance in disallowed_instance_list:
    instance_type_list.remove(instance)

## Set stack mask commands ##
ext_mask_cmd = ''
int_mask_cmd = ''
if stack_type == 'existing_stack':
    if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'ha-avset', 'cluster_3nic'):
        ext_mask_cmd = "skip(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, indexOf(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, '/')),"
    if template_name in ('standalone_3nic', 'standalone_multi-nic', 'ha-avset', 'cluster_3nic'):
        int_mask_cmd = "skip(reference(variables('intSubnetRef'), variables('networkApiVersion')).addressPrefix, indexOf(reference(variables('intSubnetRef'), variables('networkApiVersion')).addressPrefix, '/')),"

## Determine PAYG/BYOL/BIGIQ variables
image_to_use = "[parameters('bigIpVersion')]"
sku_to_use = "[concat('f5-bigip-virtual-edition-', variables('imageNameToLower'),'-byol')]"
offer_to_use = "f5-big-ip"
license1_command = ''
license2_command = ''
big_iq_pwd_cmd = ''
bigiq_pwd_delete = ''
if license_type == 'BYOL':
    license1_command = "' --license ', parameters('licenseKey1'),"
    license2_command = "' --license ', parameters('licenseKey2'),"
elif license_type == 'PAYG':
    sku_to_use = "[concat('f5-bigip-virtual-edition-', parameters('licensedBandwidth'), '-', variables('imageNameToLower'),'-hourly')]"
    offer_to_use = "f5-big-ip-hourly"
elif license_type == 'BIGIQ':
    big_iq_mgmt_ip_ref = ''
    big_iq_mgmt_ip_ref2 = ''
    big_iq_pwd_cmd = " echo ', variables('singleQuote'), parameters('bigIqLicensePassword'), variables('singleQuote'), ' >> /config/cloud/bigIqPasswd; "
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic'):
        big_iq_mgmt_ip_ref =  "reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,"
    if template_name in ('cluster_1nic'):
        big_iq_mgmt_ip_ref =  "reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ' --big-ip-mgmt-port 8443',"
        big_iq_mgmt_ip_ref2 =  "reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ' --big-ip-mgmt-port 8444',"
    if template_name in ('ha-avset', 'cluster_3nic'):
        big_iq_mgmt_ip_ref =  "reference(concat(variables('mgmtPublicIPAddressId'), '0')).dnsSettings.fqdn,"
        big_iq_mgmt_ip_ref2 =  "reference(concat(variables('mgmtPublicIPAddressId'), '1')).dnsSettings.fqdn,"
    license1_command = "' --license-pool --big-iq-host ', parameters('bigIqLicenseHost'), ' --big-iq-user ', parameters('bigIqLicenseUsername'), ' --big-iq-password-uri file:///config/cloud/bigIqPasswd --license-pool-name ', parameters('bigIqLicensePool'), ' --big-ip-mgmt-address ', " + big_iq_mgmt_ip_ref
    license2_command = "' --license-pool --big-iq-host ', parameters('bigIqLicenseHost'), ' --big-iq-user ', parameters('bigIqLicenseUsername'), ' --big-iq-password-uri file:///config/cloud/bigIqPasswd --license-pool-name ', parameters('bigIqLicensePool'), ' --big-ip-mgmt-address ', " + big_iq_mgmt_ip_ref2
    bigiq_pwd_delete = ' rm -f /config/cloud/bigIqPasswd;'
## Abstract license key text for readme_generator
license_text = OrderedDict()
license_text['licenseKey1'] = 'The license token for the F5 BIG-IP VE (BYOL).'
license_text['licenseKey2'] = 'The license token for the F5 BIG-IP VE (BYOL). This field is required when deploying two or more devices.'
license_text['licensedBandwidth'] = 'The amount of licensed bandwidth (Mbps) you want the PAYG image to use.'
license_text['bigIqLicenseHost'] = 'The IP address (or hostname) for the BIG-IQ to be used when licensing the BIG-IP.'
license_text['bigIqLicenseUsername'] = 'The BIG-IQ username to use during licensing.'
license_text['bigIqLicensePassword'] = 'The BIG-IQ password to use during licensing.'
license_text['bigIqLicensePool'] = 'The BIG-IQ license pool to use during licensing.'
if template_name not in ('cluster_1nic', 'cluster_3nic', 'ha-avset'):
    license_text.pop('licenseKey2')

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
data['parameters']['adminUsername'] = {"type": "string", "defaultValue": "azureuser", "metadata": {"description": "User name for the Virtual Machine."}}
data['parameters']['adminPassword'] = {"type": "securestring", "metadata": {"description": "Password to login to the Virtual Machine."}}
data['parameters']['dnsLabel'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": {"description": "Unique DNS Name for the Public IP address used to access the Virtual Machine"}}
data['parameters']['instanceType'] = {"type": "string", "defaultValue": default_instance, "allowedValues": instance_type_list, "metadata": {"description": "Azure instance size of the Virtual Machine."}}
data['parameters']['imageName'] = {"type": "string", "defaultValue": "Good", "allowedValues": ["Good", "Better", "Best"], "metadata": {"description": "F5 SKU (IMAGE) to you want to deploy."}}
data['parameters']['bigIpVersion'] = {"type": "string", "defaultValue": default_big_ip_version, "allowedValues": allowed_big_ip_versions, "metadata": {"description": "F5 BIG-IP version you want to use."}}
if license_type == 'BYOL':
    data['parameters']['licenseKey1'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": {"description": license_text['licenseKey1']}}
    if template_name in ('cluster_1nic', 'cluster_3nic', 'ha-avset'):
        for license_key in ['licenseKey2']:
            data['parameters'][license_key] = {"type": "string", "defaultValue": "REQUIRED", "metadata": {"description": license_text[license_key]}}
elif license_type == 'PAYG':
    data['parameters']['licensedBandwidth'] = {"type": "string", "defaultValue": default_payg_bw, "allowedValues": ["25m", "200m", "1g"], "metadata": {"description": license_text['licensedBandwidth']}}
elif license_type == 'BIGIQ':
    data['parameters']['bigIqLicenseHost'] = {"type": "string", "metadata": {"description": license_text['bigIqLicenseHost']}}
    data['parameters']['bigIqLicenseUsername'] = {"type": "string", "metadata": {"description": license_text['bigIqLicenseUsername']}}
    data['parameters']['bigIqLicensePassword'] = {"type": "securestring", "metadata": {"description": license_text['bigIqLicensePassword']}}
    data['parameters']['bigIqLicensePool'] = {"type": "string", "metadata": {"description": license_text['bigIqLicensePool']}}
data['parameters']['ntpServer'] = {"type": "string", "defaultValue": "0.pool.ntp.org", "metadata": {"description": "If you would like to change the NTP server the BIG-IP uses then replace the default ntp server with your choice."}}
data['parameters']['timeZone'] = {"type": "string", "defaultValue": "UTC", "metadata": {"description": "If you would like to change the time zone the BIG-IP uses then enter your choice. This is in the format of the Olson timezone string from /usr/share/zoneinfo, such as UTC, US/Central or Europe/London."}}
data['parameters']['restrictedSrcAddress'] = {"type": "string", "defaultValue": "*", "metadata": {"description": "This field restricts management access to a specific network or address. Enter an IP address or address range in CIDR notation, or asterisk for all sources"}}
data['parameters']['tagValues'] = {"type": "object", "defaultValue": tag_values, "metadata": {"description": "Default key/value resource tags will be added to the resources in this deployment, if you would like the values to be unique adjust them as needed for each key."}}

# Set new_stack/existing_stack parameters for templates that support that
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset', 'cluster_1nic', 'ltm_autoscale', 'waf_autoscale'):
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
        data['parameters']['instanceName'] = {"type": "string", "defaultValue": "f5vm01", "metadata": {"description": "Name of the Virtual Machine."}}
    if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
        data['parameters']['numberOfExternalIps'] = {"type": "int", "defaultValue": 1, "allowedValues": [1, 2, 3, 4, 5, 6, 7, 8], "metadata": {"description": "The number of public/private IP addresses you want to deploy for the application traffic (external) NIC on the BIG-IP VE to be used for virtual servers."}}
    if stack_type == 'new_stack':
        data['parameters']['vnetAddressPrefix'] = {"type": "string", "defaultValue": "10.0", "metadata": {"description": "The start of the CIDR block the BIG-IP VEs use when creating the Vnet and subnets.  You MUST type just the first two octets of the /16 virtual network that will be created, for example '10.0', '10.100', 192.168'."}}
    elif stack_type == 'existing_stack':
        data['parameters']['vnetName'] = {"type": "string", "metadata": {"description": "The name of the existing virtual network to which you want to connect the BIG-IP VEs."}}
        data['parameters']['vnetResourceGroupName'] = {"type": "string", "metadata": {"description": "The name of the resource group that contains the Virtual Network where the BIG-IP VE will be placed."}}
        data['parameters']['mgmtSubnetName'] = {"type": "string", "metadata": {"description": "Name of the existing MGMT subnet - with external access to the Internet."}}
        if template_name in ('ha-avset', 'cluster_1nic', 'cluster_3nic'):
            data['parameters']['mgmtIpAddressRangeStart'] = {"metadata": {"description": "The static private IP address you would like to assign to the management self IP of the first BIG-IP. The next contiguous address will be used for the second BIG-IP device."}, "type": "string"}
        elif template_name in ('ltm_autoscale', 'waf_autoscale'):
            # Auto Scale(VM Scale Set) solutions get the IP address dynamically
            pass
        else:
            data['parameters']['mgmtIpAddress'] = {"type": "string", "metadata": {"description": "MGMT subnet IP Address to use for the BIG-IP management IP address."}}
        if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
            data['parameters']['externalSubnetName'] = {"type": "string", "metadata": {"description": "Name of the existing external subnet - with external access to Internet."}}
            if template_name in ('ha-avset', 'cluster_3nic'):
                data['parameters']['externalIpSelfAddressRangeStart'] = {"metadata": {"description": "The static private IP address you would like to assign to the external self IP (primary) of the first BIG-IP. The next contiguous address will be used for the second BIG-IP device."}, "type": "string"}
                data['parameters']['externalIpAddressRangeStart'] = {"metadata": {"description": "The static private IP address (secondary) you would like to assign to the first shared Azure public IP. An additional private IP address will be assigned for each public IP address you specified in numberOfExternalIps.  For example, inputting 10.100.1.50 here and choosing 2 in numberOfExternalIps would result in 10.100.1.50 and 10.100.1.51 being configured as static private IP addresses for external virtual servers."}, "type": "string"}
            else:
                data['parameters']['externalIpAddressRangeStart'] = {"type": "string", "metadata": {"description": "The static private IP address  you would like to assign to the first external Azure public IP(for self IP). An additional private IP address will be assigned for each public IP address you specified in numberOfExternalIps.  For example, inputting 10.100.1.50 here and choosing 2 in numberOfExternalIps would result in 10.100.1.50(self IP), 10.100.1.51 and 10.100.1.52 being configured as static private IP addresses for external virtual servers."}}
        if template_name in ('standalone_3nic', 'standalone_multi-nic', 'ha-avset', 'cluster_3nic'):
            data['parameters']['internalSubnetName'] = {"type": "string", "metadata": {"description": "Name of the existing internal subnet."}}
            if template_name in ('ha-avset', 'cluster_3nic'):
                data['parameters']['internalIpAddressRangeStart'] = {"type": "string", "metadata": {"description": "The static private IP address you would like to assign to the internal self IP of the first BIG-IP. The next contiguous address will be used for the second BIG-IP device."}}
            else:
                data['parameters']['internalIpAddress'] = {"type": "string", "metadata": {"description": "Internal subnet IP address you want to use for the BIG-IP internal self IP address."}}

# Set unique solution parameters
if template_name in ('standalone_multi-nic'):
    data['parameters']['numberOfAdditionalNics'] = {"type": "int", "defaultValue": 1, "allowedValues": [1, 2, 3, 4, 5], "metadata": {"description": "By default this solution deploys the BIG-IP in a 3 NIC configuration, however it will also add a select number of additional NICs to the BIG-IP using this parameter."}}
    data['parameters']['additionalNicLocation'] = {"type": "string", "metadata": {"description": "This parameter specifies where the additional NIC's should go.  This should be a semi-colon delimited string of subnets equal to the number of additional NIC's being deployed.  Example (if 2 additional NIC's was selected): 'subnet01;subnet02' NOTE: Please ensure that there is no spaces and that the correct number of subnets are provided based on the value chosen in 'numberOfAdditionalNics'."}}
if template_name in ('cluster_1nic'):
    data['parameters']['numberOfInstances'] = {"type": "int", "defaultValue": 2, "allowedValues": [2], "metadata": {"description": "The number of BIG-IP VEs that will be deployed in front of your application(s)."}}
if template_name in ('ha-avset'):
    data['parameters']['managedRoutes'] = {"defaultValue": "NOT_SPECIFIED", "metadata": {"description": "A comma-delimited list of route destinations to be managed by this cluster.  For example: 0.0.0.0/0,192.168.1.0/24."}, "type": "string"}
    data['parameters']['routeTableTag'] = {"defaultValue": "NOT_SPECIFIED", "metadata": {"description": "Azure tag value to identify the route tables to be managed by this cluster. For example tag value: myRoute.  Example Azure tag: f5_ha:myRoute."}, "type": "string"}
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    data['parameters']['vmScaleSetMinCount'] = {"type": "int", "defaultValue": 2, "allowedValues": [1, 2, 3, 4, 5, 6], "metadata": {"description": "The minimum (and default) number of BIG-IP VEs that will be deployed into the VM Scale Set."}}
    data['parameters']['vmScaleSetMaxCount'] = {"type": "int", "defaultValue": 4, "allowedValues": [2, 3, 4, 5, 6, 7, 8], "metadata": {"description": "The maximum number of BIG-IP VEs that can be deployed into the VM Scale Set."}}
    data['parameters']['scaleOutThroughput'] = {"type": "int", "defaultValue": 90, "allowedValues": [50, 55, 60, 65, 70, 75, 80, 85, 90, 95], "metadata": {"description": "The percentage of 'Network Out' throughput that triggers a Scale Out event.  This is factored as a percentage of the F5 PAYG image bandwidth (Mbps) size you choose."}}
    data['parameters']['scaleInThroughput'] = {"type": "int", "defaultValue": 10, "allowedValues": [5, 10, 15, 20, 25, 30, 35, 40, 45], "metadata": {"description": "The percentage of 'Network Out' throughput that triggers a Scale In event.  This is factored as a percentage of the F5 PAYG image bandwidth (Mbps) size you choose."}}
    data['parameters']['scaleTimeWindow'] = {"type": "int", "defaultValue": 10, "allowedValues": [5, 10, 15, 30], "metadata": {"description": "The time window required to trigger a scale event (in and out). This is used to determine the amount of time needed for a threshold to be breached, as well as to prevent excessive scaling events (flapping)."}}
    data['parameters']['notificationEmail'] = {"defaultValue": "OPTIONAL", "metadata": {"description": "If you would like email notifications on scale events please specify an email address, otherwise leave the parameter as 'OPTIONAL'."}, "type": "string"}
if template_name in ('waf_autoscale'):
    # WAF-like templates need the 'Best' Image, still prompt as a parameter so they are aware of what they are paying for with PAYG
    data['parameters']['imageName'] = {"type": "string", "defaultValue": "Best", "allowedValues": ["Best"], "metadata": {"description": "F5 SKU (IMAGE) you want to deploy. 'Best' is the only option because ASM is required."}}
    data['parameters']['solutionDeploymentName'] = {"type": "string", "metadata": {"description": "A unique name for this deployment."}}
    data['parameters']['applicationProtocols'] = {"type": "string", "defaultValue": "http-https", "metadata": {"description": "The protocol(s) used by your application."}, "allowedValues" : ["http", "https", "http-https", "https-offload"]}
    data['parameters']['applicationAddress'] = {"type": "string", "metadata": { "description": "The public IP address or DNS FQDN of the application that this WAF will protect."}}
    data['parameters']['applicationServiceFqdn'] = {"type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": "If you are deploying in front of an Azure App Service, the FQDN of the public application."}}
    data['parameters']['applicationPort'] = {"type": "string", "defaultValue": "80", "metadata": {"description": "If you are deploying an HTTP application, the port on which your service listens for unencrypted traffic. This field is not required when deploying HTTPS only."}}
    data['parameters']['applicationSecurePort'] = {"type": "string", "defaultValue": "443", "metadata": {"description": "If you are deploying an HTTPS application, the port on which your service listens for encrypted traffic. This field is not required when deploying HTTP only."}}
    data['parameters']['sslCert'] = {"type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": "The SSL certificate .pfx file corresponding to public facing virtual server."}}
    data['parameters']['sslPswd'] = {"type": "securestring", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": "The SSL certificate .pfx password corresponding to the certificate you entered."}}
    data['parameters']['applicationType'] = {"type": "string", "defaultValue": "Linux", "metadata": {"description": "Is your application running on a Linux OS or a Windows OS?"}, "allowedValues": ["Windows", "Linux"]}
    data['parameters']['blockingLevel'] = {"type": "string", "defaultValue": "medium", "metadata": {"description": "Select how aggressive you want the blocking level of this WAF.  Remember that the more aggressive the blocking level, the more potential there is for false-positives that the WAF might detect. Select Custom to specify your own security policy."}, "allowedValues": ["low", "medium", "high", "off", "custom"]}
    data['parameters']['customPolicy'] = {"type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": "Specify the publicly available URL of a custom ASM security policy in XML format. This policy will be applied in place of the standard High/Medium/Low policy."}}
# Add service principal parameters to necessary solutions
if template_name in ('ltm_autoscale', 'waf_autoscale', 'ha-avset'):
    data['parameters']['tenantId'] = {"type": "string", "metadata": {"description": "Your Azure service principal application tenant ID."}}
    data['parameters']['clientId'] = {"type": "string", "metadata": {"description": "Your Azure service principal application client ID."}}
    data['parameters']['servicePrincipalSecret'] = {"type": "securestring", "metadata": {"description": "Your Azure service principal application secret."}}

## Remove unecessary parameters and do a check for missing mandatory variables
master_helper.template_check(data, 'parameters')
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
data['variables']['f5Tag'] = f5_tag
data['variables']['f5TemplateTag'] = f5_template_tag
data['variables']['f5CloudIappsTag'] = f5_cloud_iapps_tag
data['variables']['verifyHash'] = verify_hash
data['variables']['installCloudLibs'] = install_cloud_libs
data['variables']['skuToUse'] = sku_to_use
data['variables']['offerToUse'] = offer_to_use
data['variables']['bigIpNicPortValue'] = nic_port_map
## Handle new_stack/existing_stack variable differences
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'ha-avset', 'cluster_1nic', 'cluster_3nic', 'ltm_autoscale', 'waf_autoscale'):
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
        data['variables']['instanceName'] = "[toLower(parameters('instanceName'))]"
    if stack_type == 'new_stack':
        data['variables']['vnetId'] = "[resourceId('Microsoft.Network/virtualNetworks', variables('virtualNetworkName'))]"
        data['variables']['vnetAddressPrefix'] = "[concat(parameters('vnetAddressPrefix'),'.0.0/16')]"
        data['variables']['mgmtSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.1.0/24')]"
        data['variables']['mgmtSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.1.4')]"
        if template_name in ('cluster_1nic'):
            data['variables']['mgmtSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.1.')]"
            data['variables']['mgmtSubnetPrivateAddressSuffix'] = 4
            data['variables']['mgmtSubnetPrivateAddressSuffix1'] = "[add(variables('mgmtSubnetPrivateAddressSuffix'), 1)]"
        if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
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
            if template_name in ('standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
                data['variables']['intNicName'] = "[concat(variables('dnsLabel'), '-int')]"
                data['variables']['intSubnetName'] = "internal"
                data['variables']['intSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('intsubnetName'))]"
                data['variables']['intSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.3.0/24')]"
                data['variables']['intSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.3.4')]"
            self_ip_config_array = [{"name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": {"PublicIpAddress": {"Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '0')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]"}}}]
            if template_name in ('ha-avset', 'cluster_3nic'):
                data['variables']['mgmtSubnetPrivateAddress1'] = "[concat(parameters('vnetAddressPrefix'), '.1.5')]"
                data['variables']['extSubnetPrivateAddress1'] = "[concat(parameters('vnetAddressPrefix'), '.2.5')]"
                data['variables']['intSubnetPrivateAddress1'] = "[concat(parameters('vnetAddressPrefix'), '.3.5')]"
                self_ip_config_array += [{"name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": {"PublicIpAddress": {"Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]"}}}]
            if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'ha-avset'):
                ext_ip_config_array = [{"name": "[concat(variables('resourceGroupName'), '-ext-ipconfig0')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 0)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 10)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig1')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 1)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 11)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig2')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 2)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 12)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig3')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 3)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 13)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig4')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 4)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 14)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig5')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 5)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 15)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig6')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 6)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 16)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig7')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 7)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 17)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]"}}}]
            if template_name in ('cluster_3nic'):
                ext_ip_config_array = [ { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig0')]", "properties": { "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 10)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('lbID'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ] } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig1')]", "properties": { "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 11)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('lbID'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ] } } ]
                lb_front_end_array = [ { "name": "loadBalancerFrontEnd0", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), 0)]" } } }, { "name": "loadBalancerFrontEnd1", "properties": { "publicIPAddress": { "id":"[concat(variables('extPublicIPAddressIdPrefix'), 1)]" } } }, { "name": "loadBalancerFrontEnd2", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), 2)]" } } }, { "name": "loadBalancerFrontEnd3", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), 3)]" } } }, { "name": "loadBalancerFrontEnd4", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), 4)]" } } } ]
    if stack_type == 'existing_stack':
        data['variables']['virtualNetworkName'] = "[parameters('vnetName')]"
        data['variables']['vnetId'] = "[resourceId(parameters('vnetResourceGroupName'),'Microsoft.Network/virtualNetworks',variables('virtualNetworkName'))]"
        data['variables']['mgmtSubnetName'] = "[parameters('mgmtSubnetName')]"
        data['variables']['mgmtSubnetPrivateAddress'] = "[parameters('mgmtIpAddress')]"
        if template_name in ('cluster_1nic'):
                data['variables']['mgmtSubnetPrivateAddressPrefixArray'] = "[split(parameters('mgmtIpAddressRangeStart'), '.')]"
                data['variables']['mgmtSubnetPrivateAddressPrefix'] = "[concat(variables('mgmtSubnetPrivateAddressPrefixArray')[0], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[1], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[2], '.')]"
                data['variables']['mgmtSubnetPrivateAddressSuffix'] = "[int(variables('mgmtSubnetPrivateAddressPrefixArray')[3])]"
                data['variables']['mgmtSubnetPrivateAddressSuffix1'] = "[add(variables('mgmtSubnetPrivateAddressSuffix'), 1)]"
                data['variables']['mgmtSubnetPrivateAddress'] = "[variables('mgmtSubnetPrivateAddressPrefix')]"
        if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
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
            data['variables']['extSubnetPrivateAddressSuffixInt'] = "[int(variables('extSubnetPrivateAddressPrefixArray')[3])]"
            data['variables']['extSubnetPrivateAddressSuffix0'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 1)]"
            data['variables']['extSubnetPrivateAddressSuffix1'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 2)]"
            if template_name in ('standalone_2nic', 'standalone_3nic', 'ha-avset'):
                data['variables']['extSubnetPrivateAddressSuffix2'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 3)]"
                data['variables']['extSubnetPrivateAddressSuffix3'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 4)]"
                data['variables']['extSubnetPrivateAddressSuffix4'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 5)]"
                data['variables']['extSubnetPrivateAddressSuffix5'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 6)]"
                data['variables']['extSubnetPrivateAddressSuffix6'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 7)]"
                data['variables']['extSubnetPrivateAddressSuffix7'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 8)]"
            data['variables']['extSubnetRef'] = "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/', parameters('vnetResourceGroupName'), '/providers/Microsoft.Network/virtualNetworks/', parameters('vnetName'), '/subnets/', parameters('externalSubnetName'))]"
            if template_name in ('standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
                data['variables']['intNicName'] = "[concat(variables('dnsLabel'), '-int')]"
                data['variables']['intSubnetName'] = "[parameters('internalSubnetName')]"
                data['variables']['intSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('intsubnetName'))]"
                data['variables']['intSubnetPrivateAddress'] = "[parameters('internalIpAddress')]"
                data['variables']['intSubnetRef'] = "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/', parameters('vnetResourceGroupName'), '/providers/Microsoft.Network/virtualNetworks/', parameters('vnetName'), '/subnets/', parameters('internalSubnetName'))]"
            self_ip_config_array = [{ "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": {"PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '0')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
            if template_name in ('ha-avset', 'cluster_3nic'):
                data['variables']['mgmtSubnetPrivateAddressPrefixArray'] = "[split(parameters('mgmtIpAddressRangeStart'), '.')]"
                data['variables']['mgmtSubnetPrivateAddressPrefix'] = "[concat(variables('mgmtSubnetPrivateAddressPrefixArray')[0], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[1], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[2], '.')]"
                data['variables']['mgmtSubnetPrivateAddressSuffixInt'] = "[int(variables('mgmtSubnetPrivateAddressPrefixArray')[3])]"
                data['variables']['mgmtSubnetPrivateAddressSuffix'] = "[add(variables('mgmtSubnetPrivateAddressSuffixInt'), 1)]"
                data['variables']['mgmtSubnetPrivateAddress'] = "[parameters('mgmtIpAddressRangeStart')]"
                data['variables']['mgmtSubnetPrivateAddress1'] = "[concat(variables('mgmtSubnetPrivateAddressPrefix'), variables('mgmtSubnetPrivateAddressSuffix'))]"
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
                self_ip_config_array += [{ "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": {"PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
            if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'ha-avset'):
                ext_ip_config_array = [{ "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig0')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 0)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix0'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig1')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 1)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix1'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig2')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 2)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix2'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig3')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 3)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix3'))]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig4')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 4)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix4'))]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig5')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 5)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix5'))]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig6')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 6)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix6'))]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig7')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 7)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix7'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
            if template_name in ('cluster_3nic'):
                ext_ip_config_array = [ { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig0')]", "properties": { "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix0'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('lbID'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ] } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig1')]", "properties": { "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix1'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('lbID'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ] } } ]
                lb_front_end_array = [ { "name": "loadBalancerFrontEnd0", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), 0)]" } } }, { "name": "loadBalancerFrontEnd1", "properties": { "publicIPAddress": { "id":"[concat(variables('extPublicIPAddressIdPrefix'), 1)]" } } }, { "name": "loadBalancerFrontEnd2", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), 2)]" } } }, { "name": "loadBalancerFrontEnd3", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), 3)]" } } }, { "name": "loadBalancerFrontEnd4", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), 4)]" } } } ]

    # After adding variables for new_stack/existing_stack we need to add the ip config array
    if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
        data['variables']['numberOfExternalIps'] = "[parameters('numberOfExternalIps')]"
        data['variables']['selfIpconfigArray'] = self_ip_config_array
        data['variables']['extIpconfigArray'] = ext_ip_config_array
        if template_name in ('cluster_3nic'):
            data['variables']['lbFrontEndArray'] = lb_front_end_array

if template_name in ('standalone_multi-nic'):
    data['variables']['addtlNicFillerArray'] = ["filler01", "filler02", "filler03", "filler04", "filler05"]
    data['variables']['addtlNicRefSplit'] = "[concat(split(parameters('additionalNicLocation'), ';'), variables('addtlNicFillerArray'))]"
    data['variables']['netCmd01'] = "[concat(' --vlan name:', variables('addtlNicRefSplit')[0], ',nic:1.3')]"
    data['variables']['netCmd02'] = "[concat(variables('netCmd01'), ' --vlan name:', variables('addtlNicRefSplit')[1], ',nic:1.4')]"
    data['variables']['netCmd03'] = "[concat(variables('netCmd02'), ' --vlan name:', variables('addtlNicRefSplit')[2], ',nic:1.5')]"
    data['variables']['netCmd04'] = "[concat(variables('netCmd03'), ' --vlan name:', variables('addtlNicRefSplit')[3], ',nic:1.6')]"
    data['variables']['netCmd05'] = "[concat(variables('netCmd04'), ' --vlan name:', variables('addtlNicRefSplit')[4], ',nic:1.7')]"
    data['variables']['netCmd'] = "[variables(concat('netCmd0', parameters ('numberOfAdditionalNics')))]"
    data['variables']['selfNicConfigArray'] = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('intNicName'))]", "properties": { "primary": False } }]
    data['variables']['addtlNicConfigArray'] = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('instanceName'), '-addtlNic1'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('instanceName'), '-addtlNic2'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('instanceName'), '-addtlNic3'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('instanceName'), '-addtlNic4'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('instanceName'), '-addtlNic5'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('instanceName'), '-addtlNic6'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('instanceName'), '-addtlNic7'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('instanceName'), '-addtlNic8'))]", "properties": { "primary": False } }]
if template_name in ('cluster_1nic', 'cluster_3nic', 'ltm_autoscale', 'waf_autoscale'):
    data['variables']['loadBalancerName'] = "[concat(variables('dnsLabel'),'-alb')]"
    data['variables']['lbID'] = "[resourceId('Microsoft.Network/loadBalancers',variables('loadBalancerName'))]"
    if template_name in ('cluster_1nic', 'ltm_autoscale', 'waf_autoscale'):
        data['variables']['deviceNamePrefix'] = "[concat(variables('dnsLabel'),'-device')]"
        data['variables']['frontEndIPConfigID'] = "[concat(variables('lbID'),'/frontendIPConfigurations/loadBalancerFrontEnd')]"
    if template_name in ('ltm_autoscale', 'waf_autoscale'):
        data['variables']['mgmtSubnetPrivateAddress'] = "OPTIONAL"
        data['variables']['computeApiVersion'] = "2016-04-30-preview"
        data['variables']['networkApiVersion'] = "2016-06-01"
        data['variables']['bigIpMgmtPort'] = 8443
        data['variables']['vmssName'] = "[concat(parameters('dnsLabel'),'-vmss')]"
        data['variables']['newDataStorageAccountName'] = "[concat(uniqueString(resourceGroup().id, deployment().name), 'data000')]"
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
        data['variables']['customEmailToUse'] = ["[parameters('notificationEmail')]"]
        data['variables']['customEmail'] = "[take(variables('customEmailToUse'), length(replace(parameters('notificationEmail'), 'OPTIONAL', '')))]"
    if template_name in ('waf_autoscale'):
        data['variables']['f5NetworksSolutionScripts'] = "[concat('https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/', variables('f5NetworksTag'), '/" + solution_location + "/solutions/autoscale/waf/deploy_scripts/')]"
        data['variables']['lbTcpProbeNameHttp'] = "tcp_probe_http"
        data['variables']['lbTcpProbeIdHttp'] = "[concat(variables('lbID'),'/probes/',variables('lbTcpProbeNameHttp'))]"
        data['variables']['lbTcpProbeNameHttps'] = "tcp_probe_https"
        data['variables']['lbTcpProbeIdHttps'] = "[concat(variables('lbID'),'/probes/',variables('lbTcpProbeNameHttps'))]"
        data['variables']['httpBackendPort'] = 880
        data['variables']['httpsBackendPort'] = 8445
        data['variables']['commandArgs'] = "[concat('-m ', parameters('applicationProtocols'), ' -d ', parameters('solutionDeploymentName'), ' -n ', parameters('applicationAddress'), ' -j 880 -k 8445 -h ', parameters('applicationPort'), ' -s ', parameters('applicationSecurePort'), ' -t ', toLower(parameters('applicationType')), ' -l ', toLower(parameters('blockingLevel')), ' -a ', parameters('customPolicy'), ' -c ', parameters('sslCert'), ' -r ', parameters('sslPswd'), ' -o ', parameters('applicationServiceFqdn'), ' -u ', parameters('adminUsername'))]"

# Remove unecessary variables and do a check for missing mandatory variables
master_helper.template_check(data, 'variables')
# Sort azuredeploy.json variable value (if exists) alphabetically
for variables in data['variables']:
    sorted_variable = json.dumps(data['variables'][variables], sort_keys=True, ensure_ascii=False)
    data['variables'][variables] = json.loads(sorted_variable, object_pairs_hook=OrderedDict)

######################################## ARM Resources ########################################
resources_list = []
###### Public IP Resource(s) ######
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_1nic', 'ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[variables('mgmtPublicIPAddressName')]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[variables('dnsLabel')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
if template_name in ('ha-avset', 'cluster_3nic'):
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('mgmtPublicIPAddressName'), 0)]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabel'), '-0')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } },{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('mgmtPublicIPAddressName'), 1)]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabel'), '-1')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
    # Add Self Public IP - for external NIC
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('extSelfPublicIpAddressNamePrefix'), '0')]", "tags": tags, "properties": { "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
    if template_name in ('ha-avset', 'cluster_3nic'):
        resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('extSelfPublicIpAddressNamePrefix'), '1')]", "tags": tags, "properties": { "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
    # Add Traffic Public IP's - for external NIC
    pip_tags = tags.copy()
    if template_name in ('ha-avset'):
        if stack_type == 'new_stack':
            private_ip_value = "[concat(variables('extSubnetPrivateAddressPrefix'), 1, copyIndex())]"
        elif stack_type == 'existing_stack':
            private_ip_value = "[concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), copyIndex()))]"
        pip_tags['f5_privateIp'] = private_ip_value
        pip_tags['f5_extSubnetId'] = "[variables('extSubnetId')]"
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('extPublicIPAddressNamePrefix'), copyIndex())]", "copy": { "count": "[variables('numberOfExternalIps')]", "name": "extpipcopy"}, "tags": pip_tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabel'), copyIndex(0))]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]

###### Virtual Network Resources(s) ######
if template_name in ('standalone_1nic', 'cluster_1nic'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }]
if template_name in ('standalone_2nic'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }]
if template_name in ('standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }, { "name": "[variables('intSubnetName')]", "properties": { "addressPrefix": "[variables('intSubnetPrefix')]" } }]
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_1nic', 'cluster_3nic', 'ha-avset'):
    if stack_type == 'new_stack':
        resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

if template_name in ('ltm_autoscale', 'waf_autoscale'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]", "networkSecurityGroup": {"id": "[variables('mgmtNsgID')]"} } }]
    scale_depends_on = []
    if stack_type == 'new_stack':
        scale_depends_on += ["[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]"]
        resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "dependsOn": [ "[variables('mgmtNsgID')]" ], "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

###### Network Interface Resource(s) ######
if stack_type == 'new_stack':
    depends_on = ["[variables('vnetId')]", "[variables('mgmtPublicIPAddressId')]", "[variables('mgmtNsgID')]"]
    depends_on_ext = ["[variables('vnetId')]", "[variables('extNsgID')]", "extpipcopy"]
    if template_name in ('ha-avset', 'cluster_3nic'):
        depends_on = ["[variables('vnetId')]", "[variables('mgmtNsgID')]"]
elif stack_type == 'existing_stack':
    depends_on = ["[variables('mgmtPublicIPAddressId')]", "[variables('mgmtNsgID')]"]
    depends_on_ext = ["[variables('extNsgID')]", "extpipcopy"]
    if template_name in ('ha-avset', 'cluster_3nic'):
        depends_on = ["[variables('mgmtNsgID')]"]
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic',):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on, "location": location, "name": "[variables('mgmtNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[variables('mgmtNsgID')]" }, "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('mgmtSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": { "Id": "[variables('mgmtPublicIPAddressId')]" }, "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ] } }]
if template_name in ('standalone_2nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_ext + ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '0')]"], "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "ipConfigurations": "[concat(take(variables('selfIpConfigArray'), 1), take(variables('extIpconfigArray'),variables('numberofExternalIps')))]" } } ]
if template_name in ('standalone_3nic', 'standalone_multi-nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_ext + ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '0')]"], "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "ipConfigurations": "[concat(take(variables('selfIpConfigArray'), 1), take(variables('extIpconfigArray'),variables('numberofExternalIps')))]" } }, { "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_ext, "location": location, "name": "[variables('intNicName')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] } } ]
if template_name in ('standalone_multi-nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "condition": "[greaterOrEquals(parameters('numberOfAdditionalNics'), 1)]", "copy": { "count": "[parameters('numberOfAdditionalNics')]", "name": "addtlniccopy" }, "dependsOn": depends_on + ["[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]"], "location": location, "name": "[concat(variables('instanceName'), '-addtlNic', copyIndex(1))]", "properties": { "ipConfigurations": [ { "name": "ipconfig", "properties": { "privateIPAllocationMethod": "Dynamic", "subnet": { "id": "[concat(variables('vnetId'), '/subnets/', variables('addtlNicRefSplit')[copyIndex()])]" } } } ] }, "tags": tags }]
if template_name in ('cluster_1nic'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkInterfaces", "name": "[concat(variables('mgmtNicName'),copyindex())]", "location": location, "tags": tags, "dependsOn": depends_on + ["[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/guimgt',copyindex())]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/sshmgt',copyindex())]"], "copy": { "count": "[parameters('numberOfInstances')]", "name": "niccopy" }, "properties": { "networkSecurityGroup": { "id": "[variables('mgmtNsgID')]" }, "ipConfigurations": [ { "name": "ipconfig1", "properties": { "privateIPAllocationMethod": "Static", "privateIPAddress": "[concat(variables('mgmtSubnetPrivateAddress'),add(variables('mgmtSubnetPrivateAddressSuffix'), copyindex()))]", "subnet": { "id": "[variables('mgmtSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('lbID'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ], "loadBalancerInboundNatRules": [ { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'guimgt',copyIndex())]" }, { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'sshmgt',copyIndex())]" } ] } } ] } }]
# Can we shrink this down with a copy?
if template_name in ('ha-avset', 'cluster_3nic'):
    resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on + ["[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'), '0')]"], "location": location, "name": "[concat(variables('mgmtNicName'), '0')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-mgmt-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(variables('mgmtPublicIPAddressName'), '0'))]" }, "privateIPAddress": "[variables('mgmtSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[variables('mgmtNsgId')]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on + ["[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'), '1')]"], "location": location, "name": "[concat(variables('mgmtNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-mgmt-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(variables('mgmtPublicIPAddressName'), '1'))]" }, "privateIPAddress": "[variables('mgmtSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[variables('mgmtNsgId')]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    if template_name in ('ha-avset'):
        resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '0')]"], "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "ipConfigurations": "[concat(take(variables('selfIpConfigArray'), 1), take(variables('extIpConfigArray'), parameters('numberOfExternalIps')))]", "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '1')]"], "location": location, "name": "[concat(variables('extNicName'), '1')]", "properties": { "ipConfigurations": "[skip(variables('selfIpConfigArray'), 1)]", "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    if template_name in ('cluster_3nic'):
        resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '0')]"], "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "ipConfigurations": "[concat(take(variables('selfIpConfigArray'), 1), take(variables('extIpconfigArray'), 1))]", "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext + ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '1')]"], "location": location, "name": "[concat(variables('extNicName'), '1')]", "properties": { "ipConfigurations": "[concat(skip(variables('selfIpConfigArray'), 1), skip(variables('extIpconfigArray'), 1))]", "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext, "location": location, "name": "[concat(variables('intNicName'), '0')]", "properties": { "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_ext, "location": location, "name": "[concat(variables('intNicName'), '1')]", "properties": { "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]

###### Network Security Group Resource(s) ######
nsg_security_rules = [{ "name": "mgmt_allow_https", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('bigIpMgmtPort')]", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "ssh_allow_22", "properties": { "description": "", "priority": 102, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }]
if template_name in ('waf_autoscale'):
    nsg_security_rules += [{ "name": "app_allow_http", "properties": { "description": "", "priority": 110, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpBackendPort')]", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "app_allow_https", "properties": { "description": "", "priority": 111, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpsBackendPort')]", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }]

if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'ha-avset', 'cluster_1nic', 'cluster_3nic', 'ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-mgmt-nsg')]", "tags": tags, "properties": { "securityRules": nsg_security_rules } }]
if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_3nic', 'ha-avset'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-ext-nsg')]", "tags": tags, "properties": { "securityRules": "" } }]

###### Load Balancer Resource(s) ######
probes_to_use = ""; lb_rules_to_use = ""
if template_name in ('waf_autoscale'):
    probes_to_use = [ { "name": "[variables('lbTcpProbeNameHttp')]", "properties": { "protocol": "Tcp", "port": "[variables('httpBackendPort')]", "intervalInSeconds": 15, "numberOfProbes": 3 } }, { "name": "[variables('lbTcpProbeNameHttps')]", "properties": { "protocol": "Tcp", "port": "[variables('httpsBackendPort')]", "intervalInSeconds": 15, "numberOfProbes": 3 } } ]
    lb_rules_to_use = [{ "Name": "app-http", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttp')]" }, "protocol": "Tcp", "frontendPort": "[parameters('applicationPort')]", "backendPort": "[variables('httpBackendPort')]", "idleTimeoutInMinutes": 15 } }, { "Name": "app-https", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttps')]" }, "protocol": "Tcp", "frontendPort": "[parameters('applicationSecurePort')]", "backendPort": "[variables('httpsBackendPort')]", "idleTimeoutInMinutes": 15 } }]

if template_name == 'cluster_1nic':
    resources_list += [{ "apiVersion": network_api_version, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'))]" ], "location": location, "tags": tags, "name": "[variables('loadBalancerName')]", "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('mgmtPublicIPAddressId')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ] }, "type": "Microsoft.Network/loadBalancers" }]
if template_name == 'cluster_3nic':
    resources_list += [{ "apiVersion": network_api_version, "dependsOn": [ "extpipcopy" ], "location": location, "tags": tags, "name": "[variables('loadBalancerName')]", "properties": { "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ],
    "frontendIPConfigurations": "[take(variables('lbFrontEndArray'), variables('numberOfExternalIps'))]" }, "type": "Microsoft.Network/loadBalancers" }]
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "apiVersion": network_api_version, "name": "[variables('loadBalancerName')]", "type": "Microsoft.Network/loadBalancers", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'))]" ], "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('mgmtPublicIPAddressId')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ], "inboundNatPools": [ { "name": "sshnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPortRangeStart": 50001, "frontendPortRangeEnd": 50100, "backendPort": 22 } }, { "name": "mgmtnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPortRangeStart": 50101, "frontendPortRangeEnd": 50200, "backendPort": "[variables('bigIpMgmtPort')]" } } ], "loadBalancingRules": lb_rules_to_use, "probes": probes_to_use } }]

###### Load Balancer Inbound NAT Rule(s) ######
if template_name == 'cluster_1nic':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('loadBalancerName'),'/guimgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPort": "[copyIndex(8443)]", "backendPort": "[variables('bigIpMgmtPort')]", "enableFloatingIP": False } }]
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('loadBalancerName'),'/sshmgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPort": "[copyIndex(8022)]", "backendPort": 22, "enableFloatingIP": False } }]

######## Availability Set Resource(s) ######
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'ha-avset', 'cluster_1nic', 'cluster_3nic'):
    resources_list += [{ "apiVersion": api_version, "location": location, "name": "[variables('availabilitySetName')]", "tags": tags, "type": "Microsoft.Compute/availabilitySets" }]

###### Storage Account Resource(s) ######
resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "location": location, "name": "[variables('newStorageAccountName')]", "tags": tags, "properties": { "accountType": "[variables('storageAccountType')]" } }]
resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "location": location, "name": "[variables('newDataStorageAccountName')]", "tags": tags, "properties": { "accountType": "[variables('dataStorageAccountType')]" } }]

###### Compute/VM Resource(s) ######
depends_on = "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'))]"
depends_on = list(depends_on)
if template_name == 'standalone_1nic':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }]
if template_name in ('standalone_2nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]")
if template_name in ('standalone_3nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('intNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]"); depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]")
if template_name in ('standalone_multi-nic'):
    nic_reference = "[concat(take(variables('selfNicConfigArray'), 3), take(variables('addtlNicConfigArray'), parameters('numberOfAdditionalNics')))]"
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]"); depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]"); depends_on.append("addtlniccopy")
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic'):
    resources_list += [{"apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "dependsOn": depends_on, "location": location, "name": "[variables('instanceName')]", "tags": tags, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newDataStorageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  nic_reference }, "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "osProfile": { "computerName": "[variables('instanceName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vhds/', variables('instanceName'),'.vhd')]" } } } } }]
if template_name == 'cluster_1nic':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "name": "[concat(variables('deviceNamePrefix'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), copyindex())]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "devicecopy" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "osProfile": { "computerName": "[concat(variables('deviceNamePrefix'),copyindex())]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "name": "[concat('osdisk',copyindex())]", "vhd": { "uri": "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vhds/', copyindex(),'.vhd')]" }, "caching": "ReadWrite", "createOption": "FromImage" } }, "networkProfile": { "networkInterfaces": [ { "id": "[concat(resourceId('Microsoft.Network/networkInterfaces',variables('mgmtNicName')),copyindex())]" } ] }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newDataStorageAccountName'),'.blob.core.windows.net')]" } } } }]
if template_name in ('ha-avset', 'cluster_3nic'):
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), '0')]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'), '0')]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'), '0')]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '0')]", "plan": { "name": "[variables('skuToUse')]", "product": "[variables('offerToUse')]", "publisher": "f5-networks" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('availabilitySetName'))]" }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newDataStorageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces": [ { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('mgmtNicName'), '0'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('extNicName'), '0'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('intNicName'), '0'))]", "properties": { "primary": False } } ] }, "osProfile": { "adminPassword": "[parameters('adminPassword')]", "adminUsername": "[parameters('adminUsername')]", "computerName": "[variables('instanceName')]" }, "storageProfile": { "imageReference": { "offer": "[variables('offerToUse')]", "publisher": "f5-networks", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vhds/', variables('instanceName'),'.0vhd')]" } } } }, "tags": tags, "type": "Microsoft.Compute/virtualMachines" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), '1')]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'), '1')]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'), '1')]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '1')]", "plan": { "name": "[variables('skuToUse')]", "product": "[variables('offerToUse')]", "publisher": "f5-networks" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('availabilitySetName'))]" }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newDataStorageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces": [ { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('mgmtNicName'), '1'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('extNicName'), '1'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('intNicName'), '1'))]", "properties": { "primary": False } } ] }, "osProfile": { "adminPassword": "[parameters('adminPassword')]", "adminUsername": "[parameters('adminUsername')]", "computerName": "[variables('instanceName')]" }, "storageProfile": { "imageReference": { "offer": "[variables('offerToUse')]", "publisher": "f5-networks", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vhds/', variables('instanceName'),'.1vhd')]" } } } }, "tags": tags, "type": "Microsoft.Compute/virtualMachines" }]

###### Compute/VM Extension Resource(s) ######
command_to_execute = ''; command_to_execute2 = ''
if template_name in ('standalone_1nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('standalone_2nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --log-level debug'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('standalone_3nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal --log-level debug'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('standalone_multi-nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal ', variables('netCmd'), ' --log-level debug'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('cluster_1nic'):
    # Two Extensions for cluster_1nic
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), ' --auto-sync --save-on-auto-sync'<POST_CMD_TO_EXECUTE>)]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix1')), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), copyindex(1), '.azuresecurity.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix1')), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix1')), ' --join-group --device-group Sync --sync --remote-host ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --remote-user admin --remote-password-url file:///config/cloud/passwd'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('ha-avset'):
    # Two Extensions for HA-Avset
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal --log-level debug; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node --use-strict /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/active; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node --use-strict /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/tgrefresh; tmsh modify cm device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress'), '; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', variables('intSubnetPrivateAddress'), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' --network-failover --auto-sync --save-on-auto-sync'<POST_CMD_TO_EXECUTE>)]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress1'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress1'), <INT_MASK_CMD> ',vlan:internal --log-level debug; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node --use-strict /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/active; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node --use-strict /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/tgrefresh; tmsh modify cm device ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress1'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress1'), '; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', variables('intSubnetPrivateAddress1'), ' --join-group --device-group Sync --sync --remote-host ', variables('mgmtSubnetPrivateAddress'), ' --remote-user admin --remote-password-url file:///config/cloud/passwd'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('cluster_3nic'):
    # Two Extensions for cluster_3nic
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal --log-level debug; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', variables('intSubnetPrivateAddress'), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' --network-failover --auto-sync --save-on-auto-sync'<POST_CMD_TO_EXECUTE>)]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress1'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress1'), <INT_MASK_CMD> ',vlan:internal --log-level debug; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', variables('intSubnetPrivateAddress1'), ' --join-group --device-group Sync --sync --remote-host ', variables('mgmtSubnetPrivateAddress'), ' --remote-user admin --remote-password-url file:///config/cloud/passwd'<POST_CMD_TO_EXECUTE>)]"

## Base Start/Post Command to Execute
base_cmd_to_execute = "'mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; mkdir -p /config/cloud/node_modules; BIG_IP_CREDENTIALS_FILE=/config/cloud/passwd; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null $BIG_IP_CREDENTIALS_FILE; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), ' >> $BIG_IP_CREDENTIALS_FILE;<BIGIQ_PWD_CMD> unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host '"
post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; rm -f /config/cloud/passwd;<BIGIQ_PWD_DELETE> bash /config/customConfig.sh; else exit 1; fi'"

if template_name in 'ha-avset':
    base_cmd_to_execute = "'mkdir -p /config/cloud/node_modules && cp f5-cloud-libs*.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null /config/cloud/passwd; /usr/bin/install -b -m 400 /dev/null /config/cloud/azCredentials; /usr/bin/install -b -m 755 /dev/null /config/cloud/managedRoutes; /usr/bin/install -b -m 755 /dev/null /config/cloud/routeTableTag;<BIGIQ_PWD_CMD> IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' > /config/verifyHash; echo -e ', variables('installCloudLibs'), ' > /config/installCloudLibs.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), ' > /config/cloud/passwd; echo ', variables('singleQuote'), '{\"clientId\": \"', parameters('clientId'), '\", \"tenantId\": \"', parameters('tenantId'), '\", \"secret\": \"', parameters('servicePrincipalSecret'), '\", \"subscriptionId\": \"', variables('subscriptionID'), '\", \"resourceGroup\": \"', variables('resourceGroupName'), '\"}', variables('singleQuote'), ' > /config/cloud/azCredentials; echo -e ', parameters('managedRoutes'), ' > /config/cloud/managedRoutes; echo -e ', parameters('routeTableTag'), ' > /config/cloud/routeTableTag; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host '"
    post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl;<BIGIQ_PWD_DELETE> bash /config/customConfig.sh; else exit 1; fi'"

## Map in some commandToExecute Elements
post_cmd_to_execute = post_cmd_to_execute.replace('<BIGIQ_PWD_DELETE>', bigiq_pwd_delete)
command_to_execute = command_to_execute.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute).replace('<POST_CMD_TO_EXECUTE>', post_cmd_to_execute)
command_to_execute2 = command_to_execute2.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute).replace('<POST_CMD_TO_EXECUTE>', post_cmd_to_execute)
command_to_execute = command_to_execute.replace('<EXT_MASK_CMD>', ext_mask_cmd).replace('<INT_MASK_CMD>', int_mask_cmd)
command_to_execute2 = command_to_execute2.replace('<EXT_MASK_CMD>', ext_mask_cmd).replace('<INT_MASK_CMD>', int_mask_cmd)
command_to_execute = command_to_execute.replace('<LICENSE1_COMMAND>', license1_command)
command_to_execute2 = command_to_execute2.replace('<LICENSE2_COMMAND>', license2_command)
command_to_execute = command_to_execute.replace('<BIGIQ_PWD_CMD>', big_iq_pwd_cmd)
command_to_execute2 = command_to_execute2.replace('<BIGIQ_PWD_CMD>', big_iq_pwd_cmd)

## Define base file(s) to download
file_uris = [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-iapps/', variables('f5CloudIappsTag'), '/f5-service-discovery/f5.service_discovery.tmpl')]" ]

## Define command to execute(s)
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic'):
    resources_list += [{"apiVersion": "2016-03-30", "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('instanceName'),'/start')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('instanceName'))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": file_uris }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
if template_name == 'cluster_1nic':
    # Two Extensions for cluster_1nic
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('deviceNamePrefix'),0,'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),0)]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": file_uris }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "copy": { "name": "extensionLoop", "count": "[sub(parameters('numberOfInstances'), 1)]" }, "name": "[concat(variables('deviceNamePrefix'),add(copyindex(),1),'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),add(copyindex(),1))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": file_uris }, "protectedSettings": { "commandToExecute": command_to_execute2 } } }]
if template_name in ('ha-avset', 'cluster_3nic'):
    if template_name in ('ha-avset'):
        file_uris += ["[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/dist/f5-cloud-libs-azure.tar.gz')]"]
    # Two Extensions for ha-avset and cluster_3nic
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('dnsLabel'), '-', variables('instanceName'), '0')]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '0/start')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": file_uris }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('dnsLabel'), '-', variables('instanceName'), '1')]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '1/start')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute2 }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": file_uris }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]


###### Compute VM Scale Set(s) ######
autoscale_file_uris = ["[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-iapps/', variables('f5CloudIappsTag'), '/f5-service-discovery/f5.service_discovery.tmpl')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/dist/f5-cloud-libs-azure.tar.gz')]"]
if template_name in ('ltm_autoscale'):
    scale_script_call = "bash /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/autoscale.sh --resourceGroup ', resourceGroup().name, ' --vmssName ', variables('vmssName'), ' --userName ', parameters('adminUsername'), ' --password $BIG_IP_CREDENTIALS_FILE --azureSecretFile $AZURE_CREDENTIALS_FILE --managementPort ', variables('bigIpMgmtPort'), ' --ntpServer ', parameters('ntpServer'), ' --timeZone ', parameters('timeZone')"
if template_name in ('waf_autoscale'):
    scale_script_call = "bash /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/autoscalewaf.sh --resourceGroup ', resourceGroup().name, ' --vmssName ', variables('vmssName'), ' --userName ', parameters('adminUsername'), ' --password $BIG_IP_CREDENTIALS_FILE --azureSecretFile $AZURE_CREDENTIALS_FILE --managementPort ', variables('bigIpMgmtPort'), ' --ntpServer ', parameters('ntpServer'), ' --timeZone ', parameters('timeZone'), ' --wafScriptArgs ', variables('singleQuote'), variables('commandArgs'), variables('singleQuote')"
    autoscale_file_uris += ["[concat(variables('f5NetworksSolutionScripts'), 'deploy_waf.sh')]", "[concat(variables('f5NetworksSolutionScripts'), 'f5.http.v1.2.0rc7.tmpl')]", "[concat(variables('f5NetworksSolutionScripts'), 'f5.policy_creator.tmpl')]", "[concat(variables('f5NetworksSolutionScripts'), 'asm-policy.tar.gz')]"]

if template_name in ('ltm_autoscale', 'waf_autoscale'):
    post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; bash /config/customConfig.sh; else exit 1; fi'"
    autoscale_command_to_execute = "[concat('mkdir -p /config/cloud/node_modules; AZURE_CREDENTIALS_FILE=/config/cloud/azCredentials; BIG_IP_CREDENTIALS_FILE=/config/cloud/passwd; /usr/bin/install -m 400 /dev/null $AZURE_CREDENTIALS_FILE; /usr/bin/install -m 400 /dev/null $BIG_IP_CREDENTIALS_FILE; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), ' > $BIG_IP_CREDENTIALS_FILE; echo ', variables('singleQuote'), '{\"clientId\": \"', parameters('clientId'), '\", \"tenantId\": \"', parameters('tenantId'), '\", \"secret\": \"', parameters('servicePrincipalSecret'), '\", \"subscriptionId\": \"', variables('subscriptionID'), '\", \"storageAccount\": \"', variables('newDataStorageAccountName'), '\", \"storageKey\": \"', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('newDataStorageAccountName')), variables('storageApiVersion')).key1, '\"}', variables('singleQuote'), ' > $AZURE_CREDENTIALS_FILE; cp f5-cloud-libs*.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh; bash /config/installCloudLibs.sh; <SCALE_SCRIPT_CALL><POST_CMD_TO_EXECUTE>)]"
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<SCALE_SCRIPT_CALL>', scale_script_call).replace('<POST_CMD_TO_EXECUTE>', post_cmd_to_execute)

if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Compute/virtualMachineScaleSets", "apiVersion": compute_api_version, "name": "[variables('vmssName')]", "location": location, "tags": tags, "dependsOn": scale_depends_on + ["[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]"], "sku": { "name": "[parameters('instanceType')]", "tier": "Standard", "capacity": "[parameters('vmScaleSetMinCount')]" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "upgradePolicy": { "mode": "Manual" }, "virtualMachineProfile": { "storageProfile": { "osDisk": { "vhdContainers": [ "[concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'vmss1/')]" ], "name": "vmssosdisk", "caching": "ReadOnly", "createOption": "FromImage" }, "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use } }, "osProfile": { "computerNamePrefix": "[variables('vmssName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "networkProfile": { "networkInterfaceConfigurations": [ { "name": "nic1", "properties": { "primary": "true", "ipConfigurations": [ { "name": "ipconfig1", "properties": { "subnet": { "id": "[variables('mgmtSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/backendAddressPools/loadBalancerBackEnd')]" } ], "loadBalancerInboundNatPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/sshnatpool')]" }, { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/mgmtnatpool')]" } ] } } ] } } ] }, "extensionProfile": { "extensions": [ { "name":"main", "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": autoscale_file_uris }, "protectedSettings": { "commandToExecute": autoscale_command_to_execute } } } ] } }, "overprovision": "false" } }]

###### Compute VM Scale Set(s) AutoScale Settings ######
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Insights/autoscaleSettings", "apiVersion": "[variables('insightsApiVersion')]", "name": "autoscaleconfig", "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]" ], "properties": { "name": "autoscaleconfig", "targetResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "enabled": True, "profiles": [ { "name": "Profile1", "capacity": { "minimum": "[parameters('vmScaleSetMinCount')]", "maximum": "[parameters('vmScaleSetMaxCount')]", "default": "[parameters('vmScaleSetMinCount')]" }, "rules": [ { "metricTrigger": { "metricName": "Network Out", "metricNamespace": "", "metricResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('timeWindow')]", "timeAggregation": "Average", "operator": "GreaterThan", "threshold": "[variables('scaleOutNetworkBytes')]" }, "scaleAction": { "direction": "Increase", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } }, { "metricTrigger": { "metricName": "Network Out", "metricNamespace": "", "metricResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('timeWindow')]", "timeAggregation": "Average", "operator": "LessThan", "threshold": "[variables('scaleInNetworkBytes')]" }, "scaleAction": { "direction": "Decrease", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } } ] } ], "notifications": [ { "operation": "Scale", "email": { "sendToSubscriptionAdministrator": False, "sendToSubscriptionCoAdministrators": False, "customEmails": "[variables('customEmail')]" }, "webhooks": [] } ] } }]

## Sort resources section - Expand to choose order of resources instead of just alphabetical?
resources_sorted = json.dumps(resources_list, sort_keys=True, indent=4, ensure_ascii=False)
data['resources'] = json.loads(resources_sorted, object_pairs_hook=OrderedDict)

######################################## ARM Outputs ########################################
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic'):
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://', reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ':', variables('bigIpMgmtPort'))]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ' ',22)]" }
if template_name == 'cluster_1nic':
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':8443')]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',8022)]" }
if template_name in ('ha-avset', 'cluster_3nic'):
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(concat(variables('mgmtPublicIPAddressId'), '0')).dnsSettings.fqdn, ':', variables('bigIpMgmtPort'))]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(concat(variables('mgmtPublicIPAddressId'), '0')).dnsSettings.fqdn,' ',22)]" }
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':50101', ' - 50200')]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',50001, ' - 50100')]" }

######################################## End Create/Modify ARM Template Objects ########################################

## Write modified template(s) to appropriate location
with open(created_file, 'w') as finished:
    json.dump(data, finished, indent=4, sort_keys=False, ensure_ascii=False)
with open(createdfile_params, 'w') as finished_params:
    json.dump(data_params, finished_params, indent=4, sort_keys=False, ensure_ascii=False)


###### Prepare some information prior to creating Scripts/Readme's ######
lic_support = {'standalone_1nic': 'All', 'standalone_2nic': 'All', 'standalone_3nic': 'All', 'standalone_multi-nic': 'All', 'cluster_1nic': 'All', 'cluster_3nic': 'All', 'ha-avset': 'All', 'ltm_autoscale': 'PAYG', 'waf_autoscale': 'PAYG'}
lic_key_count = {'standalone_1nic': 1, 'standalone_2nic': 1, 'standalone_3nic': 1, 'standalone_multi-nic': 1, 'cluster_1nic': 2, 'cluster_3nic': 2, 'ha-avset': 2, 'ltm_autoscale': 0, 'waf_autoscale': 0}
api_access_needed = {'standalone_1nic': None, 'standalone_2nic': None, 'standalone_3nic': None, 'standalone_multi-nic': None, 'cluster_1nic': None, 'cluster_3nic': None, 'ha-avset': 'read_write', 'ltm_autoscale': 'read', 'waf_autoscale': 'read'}
template_info = {'template_name': template_name, 'location': script_location, 'lic_support': lic_support, 'lic_key_count': lic_key_count, 'api_access_needed': api_access_needed}
######################################## Create/Modify Scripts ########################################
# Manually adding templates to create scripts proc for now as a 'check'...
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_multi-nic', 'cluster_1nic', 'cluster_3nic', 'ha-avset', 'ltm_autoscale', 'waf_autoscale') and script_location:
    bash_script = script_generator.script_creation(template_info, data, default_payg_bw, 'bash')
    ps_script = script_generator.script_creation(template_info, data, default_payg_bw, 'powershell')
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
    readme_generator.readme_creation(template_info, data, license_text, readme_text, created_file)
######################################## END Create/Modify README's ########################################
