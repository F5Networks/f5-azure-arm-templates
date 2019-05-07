#/usr/bin/python env
import sys
import os
import json
import yaml
from collections import OrderedDict
from optparse import OptionParser
import master_helper
import script_generator
import readme_generator

from github import Github
import getpass

F5_CLOUD_LIBRARY_VERSION_FILE = 'files/f5_cloud_library_versions.json'

# Dictionary contains F5 cloud libraries and paths
# Note: F5 cloud iapps logger is currently set to v1.0.0 and not being changed very often so no need
# to populate its latest version dynamically
F5_CLOUD_LIBRARIES = {
    "f5_cloud_libs_tag": {
        "name": "F5Networks/f5-cloud-libs",
        "version": ""
    },
    "f5_cloud_libs_azure_tag": {
        "name": "F5Networks/f5-cloud-libs-azure",
        "version": ""
    },
    "f5_cloud_iapps_sd_tag": {
        "name": "F5Networks/f5-cloud-iapps",
        "version": "v2.3.2"
    },
    "f5_cloud_iapps_logger_tag": {
        "name": "F5Networks/f5-cloud-iapps",
        "version": "v1.0.0"
    },
    "f5_cloud_workers_tag": {
        "name": "F5Networks/f5-cloud-workers",
        "version": ""
    },
    "f5_as3_tag": {
        "name": "F5Networks/f5-appsvcs-extension",
        "version": "v3.6.0"
    },
    "f5_as3_build": {
        "name": "F5Networks/f5-appsvcs-extension",
        "version": ""
    }
}


#######################################################################################################################
# Helper function to retrieve latest versions of F5 cloud libraries
#######################################################################################################################
def get_latest_f5_cloud_library_versions():
    version_data = {}
    if os.path.isfile(F5_CLOUD_LIBRARY_VERSION_FILE):
        with open(F5_CLOUD_LIBRARY_VERSION_FILE, 'r+') as version_file:
            version_data = json.load(version_file)
    else:
        username = raw_input('Enter your GitHUb username: ')
        password = getpass.getpass('Enter your GitHub password: ')
        github_handler = Github(username, password)
        for repo_name in F5_CLOUD_LIBRARIES:
            print("Repo: {}".format(repo_name))
            repo = github_handler.get_repo(F5_CLOUD_LIBRARIES[repo_name]["name"])
            tags = repo.get_tags()
            # Get the latest tag version
            if F5_CLOUD_LIBRARIES[repo_name]["version"] == "":
                # AS3 build is handled with care
                if repo_name == "f5_as3_build":
                    version_data[repo_name] = repo.get_dir_contents("dist/lts")[0].path.split("/")[-1]
                else:
                    version_data[repo_name] = tags[0].name
            else:
                version_data[repo_name] = F5_CLOUD_LIBRARIES[repo_name]["version"]
        # Store cloud library versions for further processing
        with open(F5_CLOUD_LIBRARY_VERSION_FILE, 'w') as version_file:
            json.dump(version_data, version_file)
    return version_data

# Process Script Parameters ##
parser = OptionParser()
parser.add_option("-n", "--template-name", action="store", type="string", dest="template_name", help="Template Name: standalone_1nic, standalone_2nic, failover-lb_1nic, etc.")
parser.add_option("-l", "--license-type", action="store", type="string", dest="license_type", help="License Type: byol, payg, bigiq or bigiq-payg")
parser.add_option("-m", "--stack-type", action="store", type="string", dest="stack_type", default="new-stack", help="Networking Stack Type: new-stack, existing-stack, production-stack or learning-stack")
parser.add_option("-t", "--template-location", action="store", type="string", dest="template_location", help="Template Location: such as ../experimental/standalone/1nic/payg/")
parser.add_option("-a", "--artifact-location", action="store", type="string", dest="artifact_location", help="Artifacts Location: such as ../experimental/standalone/1nic/")
parser.add_option("-v", "--solution-location", action="store", type="string", dest="solution_location", default="experimental", help="Solution location: experimental or supported")
parser.add_option("-e", "--environment", action="store", type="string", dest="environment", default="azure", help="Environment: azure or azurestack")
parser.add_option("-r", "--release-prep", action="store_true", dest="release_prep", default=False, help="Release Prep Flag: If passed will equal True.")

(options, args) = parser.parse_args()
template_name = options.template_name
license_type = options.license_type
stack_type = options.stack_type
template_location = options.template_location
artifact_location = options.artifact_location
solution_location = options.solution_location
environment = options.environment
release_prep = options.release_prep

# Artifact location is same as template_location
artifact_location = template_location

## Specify meta file and file to create ##
metafile = 'files/tmpl_files/base.azuredeploy.json'
metafile_params = 'files/tmpl_files/base.azuredeploy.parameters.json'
created_file = template_location + 'azuredeploy.json'
created_file_params = template_location + 'azuredeploy.parameters.json'

## Static Variable Defaults ##
nic_reference = ""
command_to_execute = ""
route_add_cmd = ""

# Static Variable Assignment ##
# Update the template version value for every new release
template_version = "6.1.0.0"

cloud_library_versions = get_latest_f5_cloud_library_versions()
if environment == 'azurestack':
    content_version = '1.2.0.0'
    f5_networks_tag = 'v1.2.0.0'
else:
    content_version = template_version
    f5_networks_tag = "v" + template_version
f5_cloud_libs_tag = cloud_library_versions['f5_cloud_libs_tag']
f5_cloud_libs_azure_tag = cloud_library_versions['f5_cloud_libs_azure_tag']
f5_cloud_iapps_sd_tag = cloud_library_versions['f5_cloud_iapps_sd_tag']
f5_cloud_iapps_logger_tag = cloud_library_versions['f5_cloud_iapps_logger_tag']
f5_cloud_workers_tag = cloud_library_versions['f5_cloud_workers_tag']
f5_as3_tag = cloud_library_versions['f5_as3_tag']
f5_as3_build = cloud_library_versions['f5_as3_build']

# Set BIG-IP versions to allow
default_big_ip_version = '14.1.003000'
allowed_big_ip_versions = ["14.1.003000", "13.1.100000", "latest"]
version_port_map = {"latest": {"Port": 8443}, "13.1.100000": {"Port": 8443}, "14.1.003000": {"Port": 8443}, "443": {"Port": 443}}
route_cmd_array = {"latest": "route", "14.1.003000": "route", "13.1.100000": "route"}

install_cloud_libs = """[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit 1\nfi\necho loaded verifyHash\n\nconfig_loc="/config/cloud/"\nhashed_file_list="<HASHED_FILE_LIST>"\nfor file in $hashed_file_list; do\necho "verifying $file"\n/usr/bin/tmsh run cli script verifyHash $file\nif [ $? != 0 ]; then\necho "$file is not valid"\nexit 1\nfi\necho "verified $file"\ndone\necho "expanding $hashed_file_list"\ntar xfz /config/cloud/f5-cloud-libs.tar.gz --warning=no-unknown-keyword -C /config/cloud/azure/node_modules/@f5devcentral\n<TAR_LIST>touch /config/cloud/cloudLibsReady', variables('singleQuote'))]"""

# Automate Verify Hash - the verify_hash function will go out and pull in the latest hash file
# if release-prep flag is included.  Otherwise it will pull from local verifyHash file
verify_hash = '''[concat(variables('singleQuote'), '<CLI_SCRIPT>', variables('singleQuote'))]'''
verify_hash_url = "https://gitswarm.f5net.com/cloudsolutions/f5-cloud-libs/raw/" + f5_cloud_libs_tag + "/dist/verifyHash"
verify_hash = verify_hash.replace('<CLI_SCRIPT>', master_helper.verify_hash(verify_hash_url, release_prep))

hashed_file_list = "${config_loc}f5-cloud-libs.tar.gz f5-appsvcs-3.5.1-5.noarch.rpm f5.service_discovery.tmpl f5.cloud_logger.v1.0.0.tmpl"
additional_tar_list = ""
if template_name in ('as_ltm_lb', 'as_ltm_dns', 'failover-api'):
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz"
    additional_tar_list = "tar xfz /config/cloud/f5-cloud-libs-azure.tar.gz --warning=no-unknown-keyword -C /config/cloud/azure/node_modules/@f5devcentral\n"
elif template_name in ('as_waf_lb', 'as_waf_dns'):
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz asm-policy.tar.gz"
    additional_tar_list = "tar xfz /config/cloud/f5-cloud-libs-azure.tar.gz --warning=no-unknown-keyword -C /config/cloud/azure/node_modules/@f5devcentral\n"

#### Empty hashed file list when testing new code ####
# hashed_file_list = ""
######################################################
install_cloud_libs = install_cloud_libs.replace('<HASHED_FILE_LIST>', hashed_file_list)
install_cloud_libs = install_cloud_libs.replace('<TAR_LIST>', additional_tar_list)
instance_type_list = ["Standard_A2", "Standard_A3", "Standard_A4", "Standard_A5", "Standard_A6", "Standard_A7", "Standard_D2", "Standard_D3", "Standard_D4", "Standard_D11", "Standard_D12", "Standard_D13", "Standard_D14", "Standard_DS2", "Standard_DS3", "Standard_DS4", "Standard_DS11", "Standard_DS12", "Standard_DS13", "Standard_DS14", "Standard_D2_v2", "Standard_D3_v2", "Standard_D4_v2", "Standard_D5_v2", "Standard_D11_v2", "Standard_D12_v2", "Standard_D13_v2", "Standard_D14_v2", "Standard_D15_v2", "Standard_DS2_v2", "Standard_DS3_v2", "Standard_DS4_v2", "Standard_DS5_v2", "Standard_DS11_v2", "Standard_DS12_v2", "Standard_DS13_v2", "Standard_DS14_v2", "Standard_DS15_v2", "Standard_F2", "Standard_F4", "Standard_F8", "Standard_F2S", "Standard_F4S", "Standard_F8S", "Standard_F16S", "Standard_G2", "Standard_G3", "Standard_G4", "Standard_G5", "Standard_GS2", "Standard_GS3", "Standard_GS4", "Standard_GS5"]
premium_instance_type_list = ["Standard_DS2", "Standard_DS3", "Standard_DS4", "Standard_DS11", "Standard_DS12", "Standard_DS13", "Standard_DS14", "Standard_DS2_v2", "Standard_DS3_v2", "Standard_DS4_v2", "Standard_DS5_v2", "Standard_DS11_v2", "Standard_DS12_v2", "Standard_DS13_v2", "Standard_DS14_v2", "Standard_DS15_v2", "Standard_F2S", "Standard_F4S", "Standard_F8S", "Standard_F16S", "Standard_GS2", "Standard_GS3", "Standard_GS4", "Standard_GS5"]
tags = "[if(empty(variables('tagValues')), json('null'), variables('tagValues'))]"
static_vmss_tags = "[if(empty(variables('tagValues')), union(json('{}'), variables('staticVmssTagValues')), union(variables('tagValues'), variables('staticVmssTagValues')))]"
tag_values = {"application":"APP", "environment":"ENV", "group":"GROUP", "owner":"OWNER", "cost":"COST"}
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
if template_name in ('as_waf_lb', 'as_waf_dns'):
    disallowed_instance_list = ["Standard_A2", "Standard_F2"]
if template_name in ('standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_3nic'):
    default_instance = "Standard_DS3_v2"
    disallowed_instance_list = ["Standard_A2", "Standard_D2", "Standard_DS2", "Standard_D2_v2", "Standard_DS2_v2", "Standard_F2", "Standard_F2S", "Standard_G2", "Standard_GS2"]
for instance in disallowed_instance_list:
    instance_type_list.remove(instance)

## Determine if learning stack and set flags ##
learningStack = False
if stack_type in ('learning-stack'):
    learningStack = True
    stack_type = 'new-stack'

## Set stack mask commands ##
ext_mask_cmd = ''
int_mask_cmd = ''
if stack_type in ('existing-stack', 'production-stack'):
    if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_3nic'):
        ext_mask_cmd = "skip(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, indexOf(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, '/')),"
    if template_name in ('standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_3nic'):
        int_mask_cmd = "skip(reference(variables('intSubnetRef'), variables('networkApiVersion')).addressPrefix, indexOf(reference(variables('intSubnetRef'), variables('networkApiVersion')).addressPrefix, '/')),"

## Determine payg/byol/bigiq variables
image_to_use = "[parameters('bigIpVersion')]"
byol_array = {
    "13.1.100000": {
        "AllOneBootLocation": "big-all-1slot",
        "LTMOneBootLocation": "big-ltm-1slot",
        "AllTwoBootLocations": "big-all-2slot",
        "LTMTwoBootLocations": "big-ltm-2slot"
    },
    "14.1.003000": {
        "AllTwoBootLocations": "big-all-2slot",
        "LTMTwoBootLocations": "big-ltm-2slot",
        "AllOneBootLocation": "big-all-1slot",
        "LTMOneBootLocation": "big-ltm-1slot"
    },
    "latest": {
        "AllTwoBootLocations": "big-all-2slot",
        "LTMTwoBootLocations": "big-ltm-2slot",
        "AllOneBootLocation": "big-all-2slot",
        "LTMOneBootLocation": "big-ltm-2slot"
    },
    "offerPostfix": {
        "bigip-virtual-edition-best": "best",
        "bigip-virtual-edition-good": "good",
        "big-all-1slot": "byol",
        "big-all-2slot": "byol",
        "big-ltm-1slot": "byol",
        "big-ltm-2slot": "byol"
    }
}
payg_offer_map = {
    "big-all-1slot": "best",
    "big-all-2slot": "best",
    "big-ltm-1slot": "good",
    "big-ltm-2slot": "good",
    "bigip-virtual-edition-best": "best",
    "bigip-virtual-edition-good": "good"
}

payg_image_map = {
    "good25mbps": {
        "offer": "f5-big-ip-good",
        "sku": "f5-bigip-virtual-edition-25m-good-hourly"
    },
    "good200mbps": {
        "offer": "f5-big-ip-good",
        "sku": "f5-bigip-virtual-edition-200m-good-hourly"
    },
    "good1gbps": {
        "offer": "f5-big-ip-good",
        "sku": "f5-bigip-virtual-edition-1g-good-hourly"
    },
    "better25mbps": {
        "offer": "f5-big-ip-better",
        "sku": "f5-bigip-virtual-edition-25m-better-hourly"
    },
    "better200mbps": {
        "offer": "f5-big-ip-better",
        "sku": "f5-bigip-virtual-edition-200m-better-hourly"
    },
    "better1gbps": {
        "offer": "f5-big-ip-better",
        "sku": "f5-bigip-virtual-edition-1g-better-hourly"
    },
    "best25mbps": {
        "offer": "f5-big-ip-best",
        "sku": "f5-bigip-virtual-edition-25m-best-hourly"
    },
    "best200mbps": {
        "offer": "f5-big-ip-best",
        "sku": "f5-bigip-virtual-edition-200m-best-hourly"
    },
    "best1gbps": {
        "offer": "f5-big-ip-best",
        "sku": "f5-bigip-virtual-edition-1g-best-hourly"
    },
    "advancedwaf25mbps": {
        "offer": "f5-big-ip-advanced-waf",
        "sku": "f5-bigip-virtual-edition-25m-waf-hourly"
    },
    "advancedwaf200mbps": {
        "offer": "f5-big-ip-advanced-waf",
        "sku": "f5-bigip-virtual-edition-200m-waf-hourly"
    },
    "advancedwaf1gbps": {
        "offer": "f5-big-ip-advanced-waf",
        "sku": "f5-bigip-virtual-edition-1g-waf-hourly"
    },
    "perappveltm25mbps": {
        "offer": "f5-big-ip-per-app-ve",
        "sku": "f5-big-ip-per-app-ve-ltm-25m-hourly"
    },
    "perappveltm200mbps": {
        "offer": "f5-big-ip-per-app-ve",
        "sku": "f5-big-ip-per-app-ve-ltm-200m-hourly"
    },
    "perappveadvancedwaf25mbps": {
        "offer": "f5-big-ip-per-app-ve",
        "sku": "f5-big-ip-per-app-ve-awf-25m-hourly"
    },
    "perappveadvancedwaf200mbps": {
        "offer": "f5-big-ip-per-app-ve",
        "sku": "f5-big-ip-per-app-ve-awf-200m-hourly"
    }
}

byol_sku_to_use = "[concat('f5-', variables('imageNameSub'),'-byol')]"
byol_offer_to_use = "[concat('f5-big-ip-', variables('imageNameArray').offerPostfix[variables('imageNameSub')])]"
byol_image_name_sub = "[variables('imageNameArray')[parameters('bigIpVersion')][parameters('imageName')]]"
byol_static_image_name_sub = "[variables('imageNameArray')[parameters('bigIpVersion')][parameters('staticImageName')]]"

payg_offer_to_use = "[variables('paygImageMap')[variables('imageNameToLower')]['offer']]"
payg_sku_to_use = "[variables('paygImageMap')[variables('imageNameToLower')]['sku']]"

payg_mapped_sku_to_use = "[concat('f5-bigip-virtual-edition-', parameters('licensedBandwidth'), '-', variables('paygOfferMap')[variables('imageNameSub')],'-hourly')]"
payg_mapped_offer_to_use = "[concat('f5-big-ip-', variables('paygOfferMap')[variables('imageNameSub')])]"

license1_command = ''
license2_command = ''
big_iq_pwd_cmd = ''
bigiq_pwd_delete = ''
if license_type == 'byol':
    byol_image_name_sub = byol_image_name_sub
    sku_to_use = byol_sku_to_use
    offer_to_use = byol_offer_to_use
    license1_command = "' --license ', parameters('licenseKey1'),"
    license2_command = "' --license ', parameters('licenseKey2'),"
elif license_type == 'payg':
    byol_array = ""
    sku_to_use = payg_sku_to_use
    offer_to_use = payg_offer_to_use
elif license_type == 'bigiq' or license_type == 'bigiq-payg':
    if license_type == 'bigiq':
        sku_to_use = byol_sku_to_use
        offer_to_use = byol_offer_to_use
    elif license_type == 'bigiq-payg':
        sku_to_use = payg_sku_to_use
        offer_to_use = payg_offer_to_use
    big_iq_mgmt_ip_ref = ''
    big_iq_mgmt_ip_ref2 = ''
    big_iq_pwd_cmd = " /usr/bin/install -m 400 /dev/null /config/cloud/.bigIqPasswd; encrypt_secret ', variables('singleQuote'), parameters('bigIqPassword'), variables('singleQuote'), ' \"/config/cloud/.bigIqPasswd\"; "
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
        big_iq_mgmt_ip_ref =  "reference(variables('mgmtPublicIPAddressId')).ipAddress,"
    if template_name in ('failover-lb_1nic'):
        big_iq_mgmt_ip_ref =  "reference(variables('mgmtPublicIPAddressId')).ipAddress, ' --big-ip-mgmt-port 8443',"
        big_iq_mgmt_ip_ref2 =  "reference(variables('mgmtPublicIPAddressId')).ipAddress, ' --big-ip-mgmt-port 8444',"
    if template_name in ('failover-api', 'failover-lb_3nic'):
        big_iq_mgmt_ip_ref =  "reference(concat(variables('mgmtPublicIPAddressId'), '0')).ipAddress,"
        big_iq_mgmt_ip_ref2 =  "reference(concat(variables('mgmtPublicIPAddressId'), '1')).ipAddress,"
    license1_command = "' --license-pool --big-iq-host ', parameters('bigIqAddress'), ' --big-iq-user ', parameters('bigIqUsername'), ' --big-iq-password-uri file:///config/cloud/.bigIqPasswd --big-iq-password-encrypted --license-pool-name ', parameters('bigIqLicensePoolName'), ' $(format_args sku-keyword-1:', parameters('bigIqLicenseSkuKeyWord1'), ',unit-of-measure:', parameters('bigIqLicenseUnitOfMeasure'), ') --big-ip-mgmt-address ', " + big_iq_mgmt_ip_ref
    license2_command = "' --license-pool --big-iq-host ', parameters('bigIqAddress'), ' --big-iq-user ', parameters('bigIqUsername'), ' --big-iq-password-uri file:///config/cloud/.bigIqPasswd --big-iq-password-encrypted --license-pool-name ', parameters('bigIqLicensePoolName'), ' $(format_args sku-keyword-1:', parameters('bigIqLicenseSkuKeyWord1'), ',unit-of-measure:', parameters('bigIqLicenseUnitOfMeasure'), ') --big-ip-mgmt-address ', " + big_iq_mgmt_ip_ref2
    bigiq_pwd_delete = ' rm -f /config/cloud/.bigIqPasswd;'
    if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
        big_ip_ext_params = "--bigIpExtMgmtAddress ', reference(variables('mgmtPublicIPAddressId')).ipAddress, ' --bigIpExtMgmtPort via-api'"
        if template_name in ('as_ltm_dns', 'as_waf_dns'):
            big_ip_ext_params = "--bigIpExtMgmtAddress via-api --bigIpExtMgmtPort ', variables('bigIpMgmtPort')"
        if license_type == 'bigiq-payg':
            # Dynamic VMSS (payg)
            license1_command =  ", ' --externalTag key:f5ClusterTag,value:', variables('dnsLabel')"
            # Static VMSS
            static_license1_command =  ", ' --bigIqAddress ', parameters('bigIqAddress'), ' --bigIqUsername ', parameters('bigIqUsername'), ' --bigIqPassword /config/cloud/.bigIqPasswd --bigIqLicensePoolName ', parameters('bigIqLicensePoolName'), ' --bigIqExtraLicenseOptions \\\"$(format_args sku-keyword-1:', parameters('bigIqLicenseSkuKeyWord1'), ',unit-of-measure:', parameters('bigIqLicenseUnitOfMeasure'), ')\\\" " + big_ip_ext_params + ", ' --static --natBase mgmtnatpool-static. --externalTag key:f5ClusterTag,value:', variables('dnsLabel')"
        else:
            license1_command =  ", ' --bigIqAddress ', parameters('bigIqAddress'), ' --bigIqUsername ', parameters('bigIqUsername'), ' --bigIqPassword /config/cloud/.bigIqPasswd --bigIqLicensePoolName ', parameters('bigIqLicensePoolName'), ' --bigIqExtraLicenseOptions \\\"$(format_args sku-keyword-1:', parameters('bigIqLicenseSkuKeyWord1'), ',unit-of-measure:', parameters('bigIqLicenseUnitOfMeasure'), ')\\\" " + big_ip_ext_params

        # Need to keep big-iq password around in autoscale case for license revocation
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

###### Prepare some metadata about the template artifact ######
api_access_required = {'standalone_1nic': None, 'standalone_2nic': None, 'standalone_3nic': None, 'standalone_n-nic': None, 'failover-lb_1nic': None, 'failover-lb_3nic': None, 'failover-api': 'required', 'as_ltm_lb': 'required', 'as_ltm_dns': 'required',
    'as_waf_dns': {
        'existing-stack': {
            'bigiq': 'required',
            'payg': 'required'
        },
        'new-stack': {
            'bigiq': 'required',
            'payg': 'required'
        }
    },
    'as_waf_lb': {
        'existing-stack': {
            'bigiq': 'required',
            'payg': 'required',
            'bigiq-payg': 'required'
        },
        'new-stack': {
            'bigiq': 'required',
            'payg': 'required',
            'bigiq-payg': 'required'
        }
    }
    }
template_info = {'template_name': template_name, 'location': artifact_location, 'api_access_required': api_access_required}
i_data = {'template_info': template_info, 'readme_text': {}, 'template_location': created_file, 'environment': environment, 'files': {}}

######################################## Create/Modify ARM Objects ########################################
data['contentVersion'] = content_version
data_params['contentVersion'] = content_version

######################################## ARM Parameters ########################################
## Pulling in a base set of variables and setting order with below call, it is a function of master_helper.py
master_helper.parameter_initialize(data)
## Set default parameters for all templates
data['parameters']['adminUsername'] = {"type": "string", "defaultValue": "azureuser", "metadata": {"description": ""}}
data['parameters']['authenticationType'] = {"type": "string", "defaultValue": "password", "allowedValues": [ "password", "sshPublicKey"], "metadata": {"description": ""}}
data['parameters']['adminPasswordOrKey'] = {"type": "securestring", "metadata": {"description": ""}}
if stack_type not in ('production-stack'):
    data['parameters']['dnsLabel'] = {"type": "string", "metadata": {"description": ""}}
data['parameters']['instanceType'] = {"type": "string", "defaultValue": default_instance, "allowedValues": instance_type_list, "metadata": {"description": ""}}
# Standalone PAYG image names
data['parameters']['imageName'] = {"type": "string", "defaultValue": "Best1Gbps", "allowedValues": ["Best25Mbps", "Best200Mbps", "Best1Gbps",
    "Better25Mbps", "Better200Mbps", "Better1Gbps", "Good25Mbps", "Good200Mbps", "Good1Gbps", "AdvancedWaf25Mbps", "AdvancedWaf200Mbps",
    "AdvancedWaf1Gbps", "PerAppVeLTM25Mbps", "PerAppVeLTM200Mbps", "PerAppVeAdvancedWaf25Mbps", "PerAppVeAdvancedWaf200Mbps"], "metadata": {"description": ""}}
if license_type == "payg" or license_type == 'bigiq-payg':
    if "failover" in template_name:
        data['parameters']['imageName'] = {"type": "string", "defaultValue": "Best1Gbps", "allowedValues": ["Best25Mbps", "Best200Mbps", "Best1Gbps",
            "Better25Mbps", "Better200Mbps", "Better1Gbps", "Good25Mbps", "Good200Mbps", "Good1Gbps", "AdvancedWaf25Mbps", "AdvancedWaf200Mbps",
            "AdvancedWaf1Gbps"], "metadata": {"description": ""}}
    elif "as_ltm" in template_name:
        data['parameters']['imageName'] = {"type": "string", "defaultValue": "Best1Gbps", "allowedValues": ["Best25Mbps", "Best200Mbps", "Best1Gbps",
            "Better25Mbps", "Better200Mbps", "Better1Gbps", "Good25Mbps", "Good200Mbps", "Good1Gbps", "PerAppVeLTM25Mbps", "PerAppVeLTM200Mbps"],
            "metadata": {"description": ""}}
    elif "as_waf" in template_name:
        data['parameters']['imageName'] = {"type": "string", "defaultValue": "Best1Gbps", "allowedValues": ["Best25Mbps", "Best200Mbps", "Best1Gbps",
            "AdvancedWaf25Mbps", "AdvancedWaf200Mbps", "AdvancedWaf1Gbps", "PerAppVeAdvancedWaf25Mbps", "PerAppVeAdvancedWaf200Mbps"], "metadata": {"description": ""}}
data['parameters']['bigIpVersion'] = {"type": "string", "defaultValue": default_big_ip_version, "allowedValues": allowed_big_ip_versions, "metadata": {"description": ""}}
if license_type == 'byol':
    if "failover" in template_name:
        data['parameters']['imageName'] = {"type": "string", "defaultValue": "AllTwoBootLocations", "allowedValues": ["LTMTwoBootLocations", "AllTwoBootLocations" ], "metadata": {"description": ""}}
    else:
        data['parameters']['imageName'] = {"type": "string", "defaultValue": "AllTwoBootLocations", "allowedValues": ["LTMOneBootLocation", "LTMTwoBootLocations", "AllOneBootLocation", "AllTwoBootLocations" ], "metadata": {"description": ""}}
    data['parameters']['licenseKey1'] = {"type": "string", "defaultValue": "", "metadata": {"description": ""}}
    if template_name in ('failover-lb_1nic', 'failover-lb_3nic', 'failover-api'):
        for license_key in ['licenseKey2']:
            data['parameters'][license_key] = {"type": "string", "defaultValue": "", "metadata": {"description": ""}}
if license_type == 'bigiq' or license_type == 'bigiq-payg':
    if "failover" in template_name:
        data['parameters']['imageName'] = {"type": "string", "defaultValue": "AllTwoBootLocations", "allowedValues": ["LTMTwoBootLocations", "AllTwoBootLocations" ], "metadata": {"description": ""}}
    elif license_type == 'bigiq-payg':
        if "as_ltm" in template_name:
            data['parameters']['staticImageName'] = {"type": "string", "defaultValue": "AllTwoBootLocations", "allowedValues": ["LTMOneBootLocation", "LTMTwoBootLocations", "AllOneBootLocation", "AllTwoBootLocations" ], "metadata": {"description": ""}}
        else:
            data['parameters']['staticImageName'] = {"type": "string", "defaultValue": "AllTwoBootLocations", "allowedValues": ["AllOneBootLocation", "AllTwoBootLocations" ], "metadata": {"description": ""}}
    else:
        data['parameters']['imageName'] = {"type": "string", "defaultValue": "AllTwoBootLocations", "allowedValues": ["LTMOneBootLocation", "LTMTwoBootLocations", "AllOneBootLocation", "AllTwoBootLocations" ], "metadata": {"description": ""}}
    data['parameters']['bigIqAddress'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['bigIqUsername'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['bigIqPassword'] = {"type": "securestring", "metadata": {"description": ""}}
    data['parameters']['bigIqLicensePoolName'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['bigIqLicenseSkuKeyword1'] = {"type": "string", "defaultValue": "OPTIONAL", "metadata": {"description": ""}}
    data['parameters']['bigIqLicenseUnitOfMeasure'] = {"type": "string", "defaultValue": "OPTIONAL", "metadata": {"description": ""}}
    if license_type == 'bigiq-payg':
        data['parameters']['numberOfStaticInstances'] = {"type": "int", "allowedValues": [1, 2, 3, 4], "metadata": {"description": ""}}
data['parameters']['ntpServer'] = {"type": "string", "defaultValue": "0.pool.ntp.org", "metadata": {"description": ""}}
data['parameters']['timeZone'] = {"type": "string", "defaultValue": "UTC", "metadata": {"description": ""}}
data['parameters']['customImage'] = {"type": "string", "defaultValue": "OPTIONAL", "metadata": {"description": ""}}
data['parameters']['restrictedSrcAddress'] = {"type": "string", "defaultValue": "*", "metadata": {"description": ""}}
data['parameters']['tagValues'] = {"type": "object", "defaultValue": tag_values, "metadata": {"description": ""}}
data['parameters']['allowUsageAnalytics'] = {"type": "string", "defaultValue": "Yes", "allowedValues": ["Yes", "No"], "metadata": {"description": ""}}

# Set new-stack/existing-stack/production-stack parameters for templates
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
    data['parameters']['instanceName'] = {"type": "string", "defaultValue": "f5vm01", "metadata": {"description": ""}}
if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
    data['parameters']['numberOfExternalIps'] = {"type": "int", "defaultValue": 1, "allowedValues": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "metadata": {"description": ""}}
if template_name in ('failover-lb_3nic'):
    data['parameters']['enableNetworkFailover'] = {"allowedValues": [ "No", "Yes" ], "defaultValue": "Yes", "metadata": { "description": "" }, "type": "string"}
    data['parameters']['internalLoadBalancerType'] = {"defaultValue": "Per-protocol", "allowedValues": ["Per-protocol", "All-protocol", "DO_NOT_USE"], "metadata": { "description": "" }, "type": "string"}
    data['parameters']['internalLoadBalancerProbePort'] = {"defaultValue": "3456", "metadata": { "description": "" }, "type": "string"}
if stack_type == 'new-stack':
    data['parameters']['vnetAddressPrefix'] = {"type": "string", "defaultValue": "10.0", "metadata": {"description": ""}}
elif stack_type in ('existing-stack', 'production-stack'):
    data['parameters']['vnetName'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['vnetResourceGroupName'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['mgmtSubnetName'] = {"type": "string", "metadata": {"description": ""}}
    if template_name in ('failover-api', 'failover-lb_1nic', 'failover-lb_3nic'):
        data['parameters']['mgmtIpAddressRangeStart'] = {"metadata": {"description": ""}, "type": "string"}
    elif template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
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
if stack_type in ('production-stack'):
    data['parameters']['uniqueLabel'] = {"type": "string", "defaultValue": "", "metadata": {"description": ""}}

# Set unique solution parameters
if template_name in ('standalone_n-nic'):
    data['parameters']['numberOfAdditionalNics'] = {"type": "int", "defaultValue": 1, "allowedValues": [1, 2, 3, 4, 5], "metadata": {"description": ""}}
    data['parameters']['additionalNicLocation'] = {"type": "string", "metadata": {"description": ""}}
if template_name in ('failover-lb_1nic'):
    data['parameters']['numberOfInstances'] = {"type": "int", "defaultValue": 2, "allowedValues": [2], "metadata": {"description": ""}}
if template_name in ('failover-api'):
    data['parameters']['numberOfAdditionalNics'] = {"type": "int", "defaultValue": 0, "allowedValues": [0, 1, 2, 3, 4, 5], "metadata": {"description": ""}}
    data['parameters']['additionalNicLocation'] = {"type": "string", "defaultValue": "OPTIONAL", "metadata": {"description": ""}}
    data['parameters']['managedRoutes'] = {"defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}, "type": "string"}
if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    if license_type == 'bigiq-payg':
        min_allowed_values = [0, 1, 2, 3, 4, 5, 6]
        max_allowed_values = [1, 2, 3, 4, 5, 6, 7, 8]
    else:
        min_allowed_values = [1, 2, 3, 4, 5, 6]
        max_allowed_values = [2, 3, 4, 5, 6, 7, 8]
    data['parameters']['vmScaleSetMinCount'] = {"type": "int", "defaultValue": 2, "allowedValues": min_allowed_values, "metadata": {"description": ""}}
    data['parameters']['vmScaleSetMaxCount'] = {"type": "int", "defaultValue": 4, "allowedValues": max_allowed_values, "metadata": {"description": ""}}
    data['parameters']['appInsights'] = {"type": "string", "defaultValue": "CREATE_NEW", "metadata": {"description": ""}}
    data['parameters']['scaleOutCpuThreshold'] = {"type": "int", "defaultValue": 80, "minValue": 1, "maxValue": 100, "metadata": {"description": ""}}
    data['parameters']['scaleInCpuThreshold'] = {"type": "int", "defaultValue": 20, "minValue": 1, "maxValue": 100, "metadata": {"description": ""}}
    data['parameters']['scaleOutThroughputThreshold'] = {"type": "int", "defaultValue": 20000000, "metadata": {"description": ""}}
    data['parameters']['scaleInThroughputThreshold'] = {"type": "int", "defaultValue": 10000000, "metadata": {"description": ""}}
    data['parameters']['scaleInTimeWindow'] = {"type": "int", "defaultValue": 10, "minValue": 1, "maxValue": 60, "metadata": {"description": ""}}
    data['parameters']['scaleOutTimeWindow'] = {"type": "int", "defaultValue": 10, "minValue": 1, "maxValue": 60, "metadata": {"description": ""}}
    data['parameters']['notificationEmail'] = {"defaultValue": "OPTIONAL", "metadata": {"description": ""}, "type": "string"}
    if template_name in ('as_ltm_lb', 'as_waf_lb'):
        data['parameters']['enableMgmtPublicIp'] = {"type": "string", "defaultValue": "No", "allowedValues": ["No", "Yes"], "metadata": {"description": ""}}
if template_name in ('as_waf_lb', 'as_waf_dns'):
    # WAF-like templates need the 'Best' Image, still prompt as a parameter so they are aware of what they are paying for with payg
    if license_type == 'bigiq':
        data['parameters']['imageName'] = {"type": "string", "defaultValue": "AllTwoBootLocations", "allowedValues": ["AllOneBootLocation", "AllTwoBootLocations" ], "metadata": {"description": ""}}
    data['parameters']['applicationProtocols'] = {"type": "string", "defaultValue": "http-https", "metadata": {"description": ""}, "allowedValues" : ["http", "https", "http-https", "https-offload"]}
    data['parameters']['applicationAddress'] = {"type": "string", "metadata": { "description": ""}}
    data['parameters']['applicationPort'] = {"type": "string", "defaultValue": "80", "metadata": {"description": ""}}
    data['parameters']['applicationSecurePort'] = {"type": "string", "defaultValue": "443", "metadata": {"description": ""}}
    data['parameters']['sslCert'] = {"type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}}
    data['parameters']['sslPswd'] = {"type": "securestring", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}}
    data['parameters']['applicationType'] = {"type": "string", "defaultValue": "Linux", "metadata": {"description": ""}, "allowedValues": ["Windows", "Linux"]}
    data['parameters']['blockingLevel'] = {"type": "string", "defaultValue": "medium", "metadata": {"description": ""}, "allowedValues": ["low", "medium", "high", "off", "custom"]}
    data['parameters']['customPolicy'] = {"type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}}
if template_name in ('as_ltm_dns', 'as_waf_dns'):
    data['parameters']['dnsMemberIpType'] = {"type": "string", "defaultValue": "private", "allowedValues": ["private", "public"], "metadata": {"description": ""}}
    data['parameters']['dnsMemberPort'] = {"type": "string", "defaultValue": "80", "metadata": {"description": ""}}
    data['parameters']['dnsProviderHost'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['dnsProviderPort'] = {"type": "string", "defaultValue": "443", "metadata": {"description": ""}}
    data['parameters']['dnsProviderUser'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['dnsProviderPassword'] = {"type": "securestring", "metadata": {"description": ""}}
    data['parameters']['dnsProviderPool'] = {"type": "string", "defaultValue": "autoscale_pool", "metadata": {"description": ""}}
    data['parameters']['dnsProviderDataCenter'] = {"type": "string", "defaultValue": "azure_datacenter", "metadata": {"description": ""}}
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns', 'failover-api', 'failover-lb_1nic', 'failover-lb_3nic'):
    data['parameters']['declarationUrl'] = {"type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": {"description": ""}}
# Add service principal parameters to necessary solutions
if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns', 'failover-api'):
    data['parameters']['tenantId'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['clientId'] = {"type": "string", "metadata": {"description": ""}}
    data['parameters']['servicePrincipalSecret'] = {"type": "securestring", "metadata": {"description": ""}}

## Remove unecessary parameters and do a check for missing mandatory variables
master_helper.template_check(data, 'parameters')
## Fill in descriptions from YAML doc file in files/readme_files
master_helper.param_descr_update(data['parameters'], i_data)
# Some modifications once parameters have been defined
for parameter in data['parameters']:
    # Sort azuredeploy.json parameter values alphabetically
    sorted_param = json.dumps(data['parameters'][parameter], sort_keys=True, ensure_ascii=False)
    data['parameters'][parameter] = json.loads(sorted_param, object_pairs_hook=OrderedDict)
    # Add parameters into parameters file as well
    try:
        data_params['parameters'][parameter] = {"value": data['parameters'][parameter]['defaultValue']}
    except:
        data_params['parameters'][parameter] = {"value": ''}

######################################## ARM Variables ########################################
## Pulling in a base set of variables and setting order with below call, it is a function of master_helper.py
master_helper.variable_initialize(data)
## Set certain default variables to unique, changing value
data['variables']['bigIpVersionPortMap'] = version_port_map
data['variables']['f5CloudLibsTag'] = f5_cloud_libs_tag
data['variables']['f5CloudLibsAzureTag'] = f5_cloud_libs_azure_tag
data['variables']['f5NetworksTag'] = f5_networks_tag
data['variables']['f5CloudIappsSdTag'] = f5_cloud_iapps_sd_tag
data['variables']['f5CloudIappsLoggerTag'] = f5_cloud_iapps_logger_tag
data['variables']['f5AS3Tag'] = f5_as3_tag
data['variables']['f5AS3Build'] = f5_as3_build
data['variables']['verifyHash'] = verify_hash
data['variables']['installCloudLibs'] = install_cloud_libs
data['variables']['skuToUse'] = sku_to_use
data['variables']['offerToUse'] = offer_to_use
data['variables']['bigIpNicPortValue'] = nic_port_map
if environment == 'azure':
    data['variables']['computeApiVersion'] = "2017-12-01"
    data['variables']['networkApiVersion'] = "2017-11-01"
    data['variables']['storageApiVersion'] = "2017-10-01"
    # Managed disk - custom image
    data['variables']['customImage'] = "[replace(parameters('customImage'), 'OPTIONAL', '')]"
    data['variables']['useCustomImage'] = "[not(empty(variables('customImage')))]"
    data['variables']['createNewCustomImage'] = "[contains(variables('customImage'), 'https://')]"
    data['variables']['newCustomImageName'] = "[concat(variables('dnsLabel'), 'image')]"
    data['variables']['storageProfileArray'] = {"platformImage": {"imageReference": "[variables('imageReference')]", "osDisk": {"createOption": "FromImage"}}, "customImage": {"imageReference": {"id": "[if(variables('createNewCustomImage'), resourceId('Microsoft.Compute/images', variables('newCustomImageName')), variables('customImage'))]"}}}
    data['variables']['premiumInstanceArray'] = premium_instance_type_list
elif environment == 'azurestack':
    data['variables']['computeApiVersion'] = "2015-06-15"
    data['variables']['networkApiVersion'] = "2015-06-15"
    data['variables']['storageApiVersion'] = "2015-06-15"
    # Non-managed disk - custom image
    data['variables']['customImage'] = "[replace(parameters('customImage'), 'OPTIONAL', '')]"
    data['variables']['useCustomImage'] = "[not(empty(variables('customImage')))]"
    data['variables']['customImageReference'] = {"uri": "[variables('customImage')]"}
## Add additional default variables
# CLI Tools *may* take \n and send up in deployment as \\n, which fails
data['variables']['adminPasswordOrKey'] = "[replace(parameters('adminPasswordOrKey'),'\\n', '\n')]"
data['variables']['linuxConfiguration'] = { "disablePasswordAuthentication": True, "ssh": { "publicKeys": [{"path": "[concat('/home/', parameters('adminUsername'), '/.ssh/authorized_keys')]", "keyData": "[variables('adminPasswordOrKey')]"}]}}

# Set apropriate osProfile for corresponding template type
data['variables']['osProfiles'] = {
    "password": {
        "adminPassword": "[variables('adminPasswordOrKey')]",
        "adminUsername": "[parameters('adminUsername')]",
        "linuxConfiguration": "[json('null')]"
    },
    "sshPublicKey": {
        "adminUsername": "[parameters('adminUsername')]",
        "linuxConfiguration": "[variables('linuxConfiguration')]"
    }
}
if template_name == 'failover-lb_1nic':
    data['variables']['osProfiles']['password']['computerName'] = "[variables('deviceNamePrefix')]"
    data['variables']['osProfiles']['sshPublicKey']['computerName'] = "[variables('deviceNamePrefix')]"
elif learningStack:
    data['variables']['osProfiles']['password']['computerName'] = "localhost"
    data['variables']['osProfiles']['sshPublicKey']['computerName'] = "localhost"
elif template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns') or license_type == 'bigiq-payg':
    data['variables']['osProfiles']['password']['computerNamePrefix'] = "[variables('vmssName')]"
    data['variables']['osProfiles']['sshPublicKey']['computerNamePrefix'] = "[variables('vmssName')]"
elif template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic','failover-api', 'failover-lb_3nic'):
    data['variables']['osProfiles']['password']['computerName'] = "[variables('instanceName')]"
    data['variables']['osProfiles']['sshPublicKey']['computerName'] = "[variables('instanceName')]"

## Configure usage analytics variables
data['variables']['deploymentId'] = "[concat(variables('subscriptionId'), resourceGroup().id, deployment().name, variables('dnsLabel'))]"
metrics_cmd = "[concat(' --metrics customerId:${custId},deploymentId:${deployId},templateName:<TMPL_NAME>,templateVersion:<TMPL_VER>,region:', variables('location'), ',bigIpVersion:', parameters('bigIpVersion') ,',licenseType:<LIC_TYPE>,cloudLibsVersion:', variables('f5CloudLibsTag'), ',cloudName:azure')]"
if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    # Pass down to autoscale.sh for autoscale templates
    metrics_cmd = "[concat(' --usageAnalytics \\\" --metrics customerId:${custId},deploymentId:${deployId},templateName:<TMPL_NAME>,templateVersion:<TMPL_VER>,region:', variables('location'), ',bigIpVersion:', parameters('bigIpVersion') ,',licenseType:<LIC_TYPE>,cloudLibsVersion:', variables('f5CloudLibsTag'), ',cloudName:azure\\\"')]"
if template_name in ('as_waf_lb', 'as_waf_dns'):
    metrics_cmd = metrics_cmd.replace('<TMPL_NAME>', template_name + '-' + stack_type + '-' + support_type + '-' + license_type).replace('<TMPL_VER>', content_version).replace('<LIC_TYPE>', license_type)
else:
    metrics_cmd = metrics_cmd.replace('<TMPL_NAME>', template_name + '-' + stack_type + '-' + support_type).replace('<TMPL_VER>', content_version).replace('<LIC_TYPE>', license_type)
hash_cmd = "[concat('custId=`echo \"', variables('subscriptionId'), '\"|sha512sum|cut -d \" \" -f 1`; deployId=`echo \"', variables('deploymentId'), '\"|sha512sum|cut -d \" \" -f 1`')]"
data['variables']['allowUsageAnalytics'] = { "Yes": { "hashCmd": hash_cmd, "metricsCmd": metrics_cmd}, "No": { "hashCmd": "echo AllowUsageAnalytics:No", "metricsCmd": ""} }
## Handle new-stack/existing-stack variable differences
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_1nic', 'failover-lb_3nic', 'as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
        data['variables']['instanceName'] = "[toLower(parameters('instanceName'))]"
    if template_name in ('failover-lb_3nic'):
        data['variables']['internalLoadBalancerName'] =  "[concat(variables('dnsLabel'),'-int-ilb')]"
        data['variables']["intLbId"] = "[resourceId('Microsoft.Network/loadBalancers',variables('internalLoadBalancerName'))]"
        data['variables']['failoverCmdArray'] = {"No": {"first": "[concat('tmsh modify cm device ', concat(variables('instanceName'), '0.', variables('location'), '.cloudapp.azure.com'), ' unicast-address none')]", "second": "[concat('tmsh modify cm device ', concat(variables('instanceName'), '1.', variables('location'), '.cloudapp.azure.com'), ' unicast-address none')]" }, "Yes": {"first": "[concat('tmsh modify cm device ', concat(variables('instanceName'), '0.', variables('location'), '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress'))]", "second": "[concat('tmsh modify cm device ', concat(variables('instanceName'), '1.', variables('location'), '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress1'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress1'))]"}}
    if template_name in ('failover-api'):
        data['variables']['failoverCmdArray'] = {
            "13.1.100000": "tmsh modify sys db failover.selinuxallowscripts value enable",
            "14.1.003000": "tmsh modify sys db failover.selinuxallowscripts value enable",
            "latest": "tmsh modify sys db failover.selinuxallowscripts value enable" }
    if stack_type == 'new-stack':
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
            if template_name in ('standalone_n-nic', 'failover-api'):
                data['variables']['subnetArray'] = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }, { "name": "[variables('intSubnetName')]", "properties": { "addressPrefix": "[variables('intSubnetPrefix')]" } }]
                data['variables']['addtlSubnetArray'] = [{ "name": "[variables('addtlNicRefSplit')[0]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.4.0/24')]" } }, { "name": "[variables('addtlNicRefSplit')[1]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.5.0/24')]" } }, { "name": "[variables('addtlNicRefSplit')[2]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.6.0/24')]" } }, { "name": "[variables('addtlNicRefSplit')[3]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.7.0/24')]" } }, { "name": "[variables('addtlNicRefSplit')[4]]", "properties": { "addressPrefix": "[concat(parameters('vnetAddressPrefix'), '.8.0/24')]" } }]
    if stack_type in ('existing-stack', 'production-stack'):
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
            if stack_type in ('production-stack'):
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
    if stack_type in ('production-stack'):
        data['variables']['dnsLabel'] = "[toLower(parameters('uniqueLabel'))]"

    # After adding variables for new-stack/existing-stack we need to add the ip config array
    if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
        data['variables']['numberOfExternalIps'] = "[parameters('numberOfExternalIps')]"
        if template_name in ('failover-lb_3nic'):
            data['variables']['backEndAddressPoolArray'] = lb_back_end_array

# Add license type variables
if license_type == 'byol' or license_type == 'bigiq':
    data['variables']['imageNameArray'] = byol_array
    data['variables']['imageNameSub'] = byol_image_name_sub
elif license_type == "payg" or license_type == 'bigiq-payg':
    data['variables']['paygImageMap'] = payg_image_map
    if license_type == "bigiq-payg":
        data['variables']['imageNameArray'] = byol_array
        data['variables']['imageNameSub'] = byol_static_image_name_sub
if template_name in ('standalone_n-nic', 'failover-api'):
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
        data['variables']['netCmd00'] = "[concat('')]"
        data['variables']['addtlNicName'] = "[concat(variables('dnsLabel'), '-addtlnic')]"
        data['variables']['selfNicConfigArray'] = { "0": [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('mgmtNicName'), '0'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('extNicName'), '0'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('intNicName'), '0'))]", "properties": { "primary": False } }], "1": [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('mgmtNicName'), '1'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('extNicName'), '1'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('intNicName'), '1'))]", "properties": { "primary": False } }] }
        data['variables']['addtlNicConfigArray'] = {"copy": [{"count": 5, "input": {"id": "[resourceId('Microsoft.Network/networkInterfaces', concat(toLower(parameters('dnsLabel')), '-addtlnic', copyIndex('values0', 1), '0'))]", "properties": {"primary": False}}, "name": "values0"},{"count": 5, "input": {"id": "[resourceId('Microsoft.Network/networkInterfaces', concat(toLower(parameters('dnsLabel')), '-addtlnic', copyIndex('values1', 1), '1'))]", "properties": {"primary": False}}, "name": "values1"}]}
if template_name in ('failover-api'):
    if stack_type == 'new-stack':
        private_ip_value = "[concat(parameters('vnetAddressPrefix'), '.2.', copyIndex('values', 10))]"
    elif stack_type in ('existing-stack', 'production-stack'):
        private_ip_value = "[concat(split(parameters('externalIpAddressRangeStart'), '.')[0], '.', split(parameters('externalIpAddressRangeStart'), '.')[1], '.', split(parameters('externalIpAddressRangeStart'), '.')[2], '.', add(int(split(parameters('externalIpAddressRangeStart'), '.')[3]), copyIndex('values')))]"
if template_name in ('failover-lb_1nic', 'failover-lb_3nic', 'as_ltm_lb', 'as_waf_lb', 'as_ltm_dns', 'as_waf_dns'):
    if template_name in ('as_ltm_dns', 'as_waf_dns'):
        data['variables']['externalLoadBalancerName'] = ""
    else:
        data['variables']['externalLoadBalancerName'] = "[concat(variables('dnsLabel'),'-ext-alb')]"
    data['variables']['extLbId'] = "[resourceId('Microsoft.Network/loadBalancers',variables('externalLoadBalancerName'))]"
if template_name in ('failover-lb_1nic', 'as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    data['variables']['deviceNamePrefix'] = "[concat(variables('dnsLabel'),'-device')]"
    data['variables']['frontEndIPConfigID'] = "[concat(variables('extLbId'),'/frontendIPConfigurations/loadBalancerFrontEnd')]"
if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    data['variables']['appInsightsApiVersion'] = "2015-04-01"
    data['variables']['appInsightsComponentsApiVersion'] = "2015-05-01"
    data['variables']['mgmtSubnetPrivateAddress'] = "OPTIONAL"
    data['variables']['bigIpMgmtPort'] = 8443
    data['variables']['vmssName'] = "[concat(parameters('dnsLabel'),'-vmss')]"
    data['variables']['vmssId'] = "[resourceId('Microsoft.Compute/virtualMachineScaleSets', variables('vmssName'))]"
    data['variables']['subscriptionID'] = "[subscription().subscriptionId]"
    data['variables']['defaultAppInsightsLocation'] = "eastus"
    data['variables']['appInsightsLocation'] = "[split(concat(parameters('appInsights'), ':', variables('defaultAppInsightsLocation')), ':')[1]]"
    data['variables']['appInsightsName'] = "[replace(split(parameters('appInsights'), ':')[0], 'CREATE_NEW', concat(deployment().name, '-appinsights'))]"
    data['variables']['appInsightsNameArray'] = "[split(concat(variables('appInsightsName'), ';', variables('resourceGroupName')) , ';')]"
    data['variables']['scaleOutTimeWindow'] = "[concat('PT', parameters('scaleOutTimeWindow'), 'M')]"
    data['variables']['scaleInTimeWindow'] = "[concat('PT', parameters('scaleInTimeWindow'), 'M')]"
    data['variables']['cpuMetricName'] = "F5_TMM_CPU"
    data['variables']['throughputMetricName'] = "F5_TMM_TRAFFIC"
    data['variables']['scaleMetricMap'] = { "F5_TMM_CPU": { "metricName": "customMetrics/F5_TMM_CPU", "metricResourceUri": "[resourceId(variables('appInsightsNameArray')[1], 'Microsoft.Insights/components', variables('appInsightsNameArray')[0])]", "thresholdOut": "[parameters('scaleOutCpuThreshold')]", "thresholdIn": "[parameters('scaleInCpuThreshold')]" }, "F5_TMM_Traffic": { "metricName": "customMetrics/F5_TMM_TRAFFIC", "metricResourceUri": "[resourceId(variables('appInsightsNameArray')[1], 'Microsoft.Insights/components', variables('appInsightsNameArray')[0])]", "thresholdOut": "[parameters('scaleOutThroughputThreshold')]", "thresholdIn": "[parameters('scaleInThroughputThreshold')]" } }
    data['variables']['customEmailBaseArray'] = [""]
    data['variables']['customEmail'] = "[skip(union(variables('customEmailBaseArray'), split(replace(parameters('notificationEmail'), 'OPTIONAL', ''), ';')), 1)]"
    data['variables']['publicIpAddressConfiguration'] = { "name": "publicIp01", "properties": { "idleTimeoutInMinutes": 15 } }
    if license_type == 'bigiq-payg':
        data['variables']['staticVmssName'] = "[concat(parameters('dnsLabel'),'-vmss', '-static')]"
        data['variables']['staticVmssId'] = "[resourceId('Microsoft.Compute/virtualMachineScaleSets', variables('staticVmssName'))]"
        data['variables']['staticSkuToUse'] = byol_sku_to_use
        data['variables']['staticOfferToUse'] = byol_offer_to_use
        data['variables']['staticImageReference'] = {"offer": "[variables('staticOfferToUse')]", "publisher": "f5-networks", "sku": "[variables('staticSkuToUse')]", "version": "[parameters('bigIpVersion')]"}
        data['variables']['staticStorageProfileArray'] = {"platformImage": {"imageReference": "[variables('staticImageReference')]", "osDisk": {"createOption": "FromImage"}}, "customImage": {"imageReference": {"id": "[if(variables('createNewCustomImage'), resourceId('Microsoft.Compute/images', variables('newCustomImageName')), variables('customImage'))]"}}}
        data['variables']['staticImagePlan'] = {"name": "[variables('staticSkuToUse')]", "product": "[variables('staticOfferToUse')]", "publisher": "f5-networks"}
        data['variables']['staticVmssTagValues'] = {"f5ClusterTag": "[variables('dnsLabel')]"}
# outside of above conditional because of bigiq-payg license type
if template_name in ('as_waf_lb', 'as_waf_dns') or license_type == 'bigiq-payg':
    data['variables']['lbTcpProbeNameHttp'] = "tcp_probe_http"
    data['variables']['lbTcpProbeIdHttp'] = "[concat(variables('extLbId'),'/probes/',variables('lbTcpProbeNameHttp'))]"
    data['variables']['lbTcpProbeNameHttps'] = "tcp_probe_https"
    data['variables']['lbTcpProbeIdHttps'] = "[concat(variables('extLbId'),'/probes/',variables('lbTcpProbeNameHttps'))]"
    if template_name in ('as_waf_lb', 'as_waf_dns'):
        data['variables']['httpBackendPort'] = "[parameters('applicationPort')]"
        data['variables']['httpsBackendPort'] = "[parameters('applicationSecurePort')]"
        data['variables']['f5NetworksSolutionScripts'] = "[concat('http://cdn.f5.com/product/cloudsolutions/solution-scripts/')]"
        data['variables']['commandArgs'] = "[concat('-o ', parameters('declarationUrl'), ' -m ', parameters('applicationProtocols'), ' -n ', parameters('applicationAddress'), ' -j ', parameters('applicationPort'), ' -k ', parameters('applicationSecurePort'), ' -h ', parameters('applicationPort'), ' -s ', parameters('applicationSecurePort'), ' -t ', toLower(parameters('applicationType')), ' -l ', toLower(parameters('blockingLevel')), ' -a ', parameters('customPolicy'), ' -c ', parameters('sslCert'), ' -r ', parameters('sslPswd'), ' -u svc_user')]"
        data['variables']['appScript'] = "IyEvYmluL2Jhc2gKZnVuY3Rpb24gcGFzc3dkKCkgewogIGVjaG8gfCBmNS1yZXN0LW5vZGUgL2NvbmZpZy9jbG91ZC9henVyZS9ub2RlX21vZHVsZXMvQGY1ZGV2Y2VudHJhbC9mNS1jbG91ZC1saWJzL3NjcmlwdHMvZGVjcnlwdERhdGFGcm9tRmlsZS5qcyAtLWRhdGEtZmlsZSAvY29uZmlnL2Nsb3VkLy5wYXNzd2QgfCBhd2sgJ3twcmludCAkMX0nCn0KCndoaWxlIGdldG9wdHMgbTpkOm46ajprOmg6czp0Omw6YTpjOnI6bzp1OiBvcHRpb24KZG8gY2FzZSAiJG9wdGlvbiIgIGluCiAgICAgICAgbykgZGVjbGFyYXRpb25Vcmw9JE9QVEFSRzs7CiAgICAgICAgbSkgbW9kZT0kT1BUQVJHOzsKICAgICAgICBuKSBwb29sX21lbWJlcj0kT1BUQVJHOzsKICAgICAgICBqKSB2c19odHRwX3BvcnQ9JE9QVEFSRzs7CiAgICAgICAgaykgdnNfaHR0cHNfcG9ydD0kT1BUQVJHOzsKICAgICAgICBoKSBwb29sX2h0dHBfcG9ydD0kT1BUQVJHOzsKICAgICAgICBzKSBwb29sX2h0dHBzX3BvcnQ9JE9QVEFSRzs7CiAgICAgICAgdCkgdHlwZT0kT1BUQVJHOzsKICAgICAgICBsKSBsZXZlbD0kT1BUQVJHOzsKICAgICAgICBhKSBwb2xpY3k9JE9QVEFSRzs7CiAgICAgICAgYykgc3NsX2NlcnQ9JE9QVEFSRzs7CiAgICAgICAgcikgc3NsX3Bhc3N3ZD0kT1BUQVJHOzsKICAgICAgICB1KSB1c2VyPSRPUFRBUkc7OwogICAgZXNhYwpkb25lCgpkZXBsb3llZD0ibm8iCmZpbGVfbG9jPSIvY29uZmlnL2Nsb3VkL2N1c3RvbV9jb25maWciCmRmbF9tZ210X3BvcnQ9YHRtc2ggbGlzdCBzeXMgaHR0cGQgc3NsLXBvcnQgfCBncmVwIHNzbC1wb3J0IHwgc2VkICdzL3NzbC1wb3J0IC8vO3MvIC8vZydgCnVybF9yZWdleD0iKGh0dHA6XC9cL3xodHRwczpcL1wvKT9bYS16MC05XSsoW1wtXC5dezF9W2EtejAtOV0rKSpcLlthLXpdezIsNX0oOlswLTldezEsNX0pPyhcLy4qKT8kIgoKaWYgW1sgJGRlY2xhcmF0aW9uVXJsID1+ICR1cmxfcmVnZXggXV07IHRoZW4KICAgIHJlc3BvbnNlX2NvZGU9JCgvdXNyL2Jpbi9jdXJsIC1zayAtdyAiJXtodHRwX2NvZGV9IiAkZGVjbGFyYXRpb25VcmwgLW8gJGZpbGVfbG9jKQogICAgaWYgW1sgJHJlc3BvbnNlX2NvZGUgPT0gMjAwIF1dOyB0aGVuCiAgICAgICAgIGVjaG8gIkN1c3RvbSBjb25maWcgZG93bmxvYWQgY29tcGxldGU7IGNoZWNraW5nIGZvciB2YWxpZCBKU09OLiIKICAgICAgICAgY2F0ICRmaWxlX2xvYyB8IGpxIC5jbGFzcwogICAgICAgICBpZiBbWyAkPyA9PSAwIF1dOyB0aGVuCiAgICAgICAgICAgICByZXNwb25zZV9jb2RlPSQoL3Vzci9iaW4vY3VybCAtc2t2dnUgJHVzZXI6JChwYXNzd2QpIC13ICIle2h0dHBfY29kZX0iIC1YIFBPU1QgLUggIkNvbnRlbnQtVHlwZTogYXBwbGljYXRpb24vanNvbiIgaHR0cHM6Ly9sb2NhbGhvc3Q6JGRmbF9tZ210X3BvcnQvbWdtdC9zaGFyZWQvYXBwc3Zjcy9kZWNsYXJlIC1kIEAkZmlsZV9sb2MgLW8gL2Rldi9udWxsKQoKICAgICAgICAgICAgIGlmIFtbICRyZXNwb25zZV9jb2RlID09IDIwMCB8fCAkcmVzcG9uc2VfY29kZSA9PSA1MDIgXV07IHRoZW4KICAgICAgICAgICAgICAgICAgZWNobyAiRGVwbG95bWVudCBvZiBhcHBsaWNhdGlvbiBzdWNjZWVkZWQuIgogICAgICAgICAgICAgICAgICBkZXBsb3llZD0ieWVzIgogICAgICAgICAgICAgZWxzZQogICAgICAgICAgICAgICAgIGVjaG8gIkZhaWxlZCB0byBkZXBsb3kgYXBwbGljYXRpb247IGNvbnRpbnVpbmcgd2l0aCByZXNwb25zZSBjb2RlICciJHJlc3BvbnNlX2NvZGUiJyIKICAgICAgICAgICAgIGZpCiAgICAgICAgIGVsc2UKICAgICAgICAgICAgIGVjaG8gIkN1c3RvbSBjb25maWcgd2FzIG5vdCB2YWxpZCBKU09OLCBjb250aW51aW5nIgogICAgICAgICBmaQogICAgZWxzZQogICAgICAgIGVjaG8gIkZhaWxlZCB0byBkb3dubG9hZCBjdXN0b20gY29uZmlnOyBjb250aW51aW5nIHdpdGggcmVzcG9uc2UgY29kZSAnIiRyZXNwb25zZV9jb2RlIiciCiAgICBmaQplbHNlCiAgICAgZWNobyAiQ3VzdG9tIGNvbmZpZyB3YXMgbm90IGEgVVJMLCBjb250aW51aW5nLiIKZmkKCmlmIFtbICRkZXBsb3llZCA9PSAibm8iICYmICRkZWNsYXJhdGlvblVybCA9PSAiTk9UX1NQRUNJRklFRCIgXV07IHRoZW4KICAgIGlwX3JlZ2V4PSdeWzAtOV17MSwzfVwuWzAtOV17MSwzfVwuWzAtOV17MSwzfVwuWzAtOV17MSwzfSQnCiAgICBkZmxfbWdtdF9wb3J0PWB0bXNoIGxpc3Qgc3lzIGh0dHBkIHNzbC1wb3J0IHwgZ3JlcCBzc2wtcG9ydCB8IHNlZCAncy9zc2wtcG9ydCAvLztzLyAvL2cnYAogICAgbW9kZT1gc2VkICJzLy0vXy9nIiA8PDwiJG1vZGUiYAogICAgcGF5bG9hZD0neyJjbGFzcyI6IkFEQyIsInNjaGVtYVZlcnNpb24iOiIzLjAuMCIsImxhYmVsIjoiYXV0b3NjYWxlX3dhZiIsImlkIjoiQVVUT1NDQUxFX1dBRiIsInJlbWFyayI6IkF1dG9zY2FsZSBXQUYiLCJ3YWYiOnsiY2xhc3MiOiJUZW5hbnQiLCJTaGFyZWQiOnsiY2xhc3MiOiJBcHBsaWNhdGlvbiIsInRlbXBsYXRlIjoic2hhcmVkIiwic2VydmljZUFkZHJlc3MiOnsiY2xhc3MiOiJTZXJ2aWNlX0FkZHJlc3MiLCJ2aXJ0dWFsQWRkcmVzcyI6IjAuMC4wLjAifSwicG9saWN5V0FGIjp7ImNsYXNzIjoiV0FGX1BvbGljeSIsImZpbGUiOiIvdG1wL2FzMzAtbGludXgtbWVkaXVtLnhtbCJ9fSwiaHR0cCI6eyJjbGFzcyI6IkFwcGxpY2F0aW9uIiwidGVtcGxhdGUiOiJodHRwIiwicG9vbCI6eyJjbGFzcyI6IlBvb2wiLCJtb25pdG9ycyI6WyJodHRwIl0sIm1lbWJlcnMiOlt7ImFkZHJlc3NEaXNjb3ZlcnkiOiJmcWRuIiwiYXV0b1BvcHVsYXRlIjp0cnVlLCJzZXJ2aWNlUG9ydCI6ODAsImhvc3RuYW1lIjoid3d3LmV4YW1wbGUuY29tIiwic2VydmVyQWRkcmVzc2VzIjpbIjI1NS4yNTUuMjU1LjI1NCJdfV19LCJzZXJ2aWNlTWFpbiI6eyJjbGFzcyI6IlNlcnZpY2VfSFRUUCIsInZpcnR1YWxBZGRyZXNzZXMiOlt7InVzZSI6Ii93YWYvU2hhcmVkL3NlcnZpY2VBZGRyZXNzIn1dLCJ2aXJ0dWFsUG9ydCI6ODAsInNuYXQiOiJhdXRvIiwic2VjdXJpdHlMb2dQcm9maWxlcyI6W3siYmlnaXAiOiIvQ29tbW9uL0xvZyBpbGxlZ2FsIHJlcXVlc3RzIn1dLCJwb29sIjoicG9vbCIsInBvbGljeVdBRiI6eyJ1c2UiOiIvd2FmL1NoYXJlZC9wb2xpY3lXQUYifX19LCJodHRwcyI6eyJjbGFzcyI6IkFwcGxpY2F0aW9uIiwidGVtcGxhdGUiOiJodHRwcyIsInNlcnZlclRMUyI6eyJjbGFzcyI6IlRMU19TZXJ2ZXIiLCJjZXJ0aWZpY2F0ZXMiOlt7ImNlcnRpZmljYXRlIjoiY2VydFNlcnZlciJ9XSwiYXV0aGVudGljYXRpb25UcnVzdENBIjp7ImJpZ2lwIjoiL0NvbW1vbi9jYS1idW5kbGUuY3J0In19LCJjZXJ0U2VydmVyIjp7ImNsYXNzIjoiQ2VydGlmaWNhdGUiLCJjZXJ0aWZpY2F0ZSI6eyJiaWdpcCI6Ii9Db21tb24vd2FmQ2VydC5jcnQifSwicHJpdmF0ZUtleSI6eyJiaWdpcCI6Ii9Db21tb24vd2FmQ2VydC5rZXkifX0sImNsaWVudFRMUyI6eyJjbGFzcyI6IlRMU19DbGllbnQifSwicG9vbCI6eyJjbGFzcyI6IlBvb2wiLCJtb25pdG9ycyI6WyJodHRwcyJdLCJtZW1iZXJzIjpbeyJhZGRyZXNzRGlzY292ZXJ5IjoiZnFkbiIsImF1dG9Qb3B1bGF0ZSI6dHJ1ZSwic2VydmljZVBvcnQiOjQ0MywiaG9zdG5hbWUiOiJ3d3cuZXhhbXBsZS5jb20iLCJzZXJ2ZXJBZGRyZXNzZXMiOlsiMjU1LjI1NS4yNTUuMjU0Il19XX0sInNlcnZpY2VNYWluIjp7ImNsYXNzIjoiU2VydmljZV9IVFRQUyIsInZpcnR1YWxBZGRyZXNzZXMiOlt7InVzZSI6Ii93YWYvU2hhcmVkL3NlcnZpY2VBZGRyZXNzIn1dLCJ2aXJ0dWFsUG9ydCI6NDQzLCJzZXJ2ZXJUTFMiOiJzZXJ2ZXJUTFMiLCJjbGllbnRUTFMiOiJjbGllbnRUTFMiLCJyZWRpcmVjdDgwIjp0cnVlLCJzbmF0IjoiYXV0byIsInNlY3VyaXR5TG9nUHJvZmlsZXMiOlt7ImJpZ2lwIjoiL0NvbW1vbi9Mb2cgaWxsZWdhbCByZXF1ZXN0cyJ9XSwicG9vbCI6InBvb2wiLCJwb2xpY3lXQUYiOnsidXNlIjoiL3dhZi9TaGFyZWQvcG9saWN5V0FGIn19fSwiaHR0cHNfb2ZmbG9hZCI6eyJjbGFzcyI6IkFwcGxpY2F0aW9uIiwidGVtcGxhdGUiOiJodHRwcyIsInNlcnZlclRMUyI6eyJjbGFzcyI6IlRMU19TZXJ2ZXIiLCJjZXJ0aWZpY2F0ZXMiOlt7ImNlcnRpZmljYXRlIjoiY2VydFNlcnZlciJ9XSwiYXV0aGVudGljYXRpb25UcnVzdENBIjp7ImJpZ2lwIjoiL0NvbW1vbi9jYS1idW5kbGUuY3J0In19LCJjZXJ0U2VydmVyIjp7ImNsYXNzIjoiQ2VydGlmaWNhdGUiLCJjZXJ0aWZpY2F0ZSI6eyJiaWdpcCI6Ii9Db21tb24vd2FmQ2VydC5jcnQifSwicHJpdmF0ZUtleSI6eyJiaWdpcCI6Ii9Db21tb24vd2FmQ2VydC5rZXkifX0sInBvb2wiOnsiY2xhc3MiOiJQb29sIiwibW9uaXRvcnMiOlsiaHR0cCJdLCJtZW1iZXJzIjpbeyJhZGRyZXNzRGlzY292ZXJ5IjoiZnFkbiIsImF1dG9Qb3B1bGF0ZSI6dHJ1ZSwic2VydmljZVBvcnQiOjgwLCJob3N0bmFtZSI6Ind3dy5leGFtcGxlLmNvbSIsInNlcnZlckFkZHJlc3NlcyI6WyIyNTUuMjU1LjI1NS4yNTQiXX1dfSwic2VydmljZU1haW4iOnsiY2xhc3MiOiJTZXJ2aWNlX0hUVFBTIiwidmlydHVhbEFkZHJlc3NlcyI6W3sidXNlIjoiL3dhZi9TaGFyZWQvc2VydmljZUFkZHJlc3MifV0sInZpcnR1YWxQb3J0Ijo4MCwic2VydmVyVExTIjoic2VydmVyVExTIiwic25hdCI6ImF1dG8iLCJzZWN1cml0eUxvZ1Byb2ZpbGVzIjpbeyJiaWdpcCI6Ii9Db21tb24vTG9nIGlsbGVnYWwgcmVxdWVzdHMifV0sInBvb2wiOiJwb29sIiwicG9saWN5V0FGIjp7InVzZSI6Ii93YWYvU2hhcmVkL3BvbGljeVdBRiJ9fX19fScKCiAgICAjIHZlcmlmeSB0aGF0IHRoZSBjdXN0b20gcG9saWN5IGlzIGEgVVJMCiAgICBpZiBbWyAkbGV2ZWwgPT0gImN1c3RvbSIgXV07IHRoZW4KICAgICAgICAgaWYgW1sgLW4gJHBvbGljeSAmJiAkcG9saWN5ICE9ICJOT1RfU1BFQ0lGSUVEIiBdXTsgdGhlbgogICAgICAgICAgICAgaWYgW1sgJHBvbGljeSA9fiAkdXJsX3JlZ2V4IF1dOyB0aGVuCiAgICAgICAgICAgICAgICAgIGN1c3RvbV9wb2xpY3k9JHBvbGljeQogICAgICAgICAgICAgICAgICAvdXNyL2Jpbi9jdXJsIC1zayAkY3VzdG9tX3BvbGljeSAtLXJldHJ5IDMgLW8gL3RtcC9jdXN0b21fcG9saWN5LnhtbAogICAgICAgICAgICAgICAgICBhc21fcG9saWN5PSIvdG1wL2N1c3RvbV9wb2xpY3kueG1sIgogICAgICAgICAgICAgZWxzZQogICAgICAgICAgICAgICAgICBlY2hvICJDdXN0b20gcG9saWN5IHdhcyBub3QgYSBVUkwsIGRlZmF1bHRpbmcgdG8gaGlnaCIKICAgICAgICAgICAgICAgICAgYXNtX3BvbGljeT0iL2NvbmZpZy9jbG91ZC9hc20tcG9saWN5LSR0eXBlLWhpZ2gueG1sIgogICAgICAgICAgICAgZmkKICAgICAgICAgZWxzZQogICAgICAgICAgICAgIGVjaG8gIkN1c3RvbSBwb2xpY3kgd2FzIG5vdCBzcGVjaWZpZWQsIGRlZmF1bHRpbmcgdG8gaGlnaCIKICAgICAgICAgICAgICBhc21fcG9saWN5PSIvY29uZmlnL2Nsb3VkL2FzbS1wb2xpY3ktJHR5cGUtaGlnaC54bWwiCiAgICAgICAgIGZpCiAgICBlbHNlCiAgICAgICAgIGFzbV9wb2xpY3k9Ii9jb25maWcvY2xvdWQvYXNtLXBvbGljeS0kdHlwZS0kbGV2ZWwueG1sIgogICAgZmkKCiAgICBpZiBbWyAkbW9kZSA9PSAiaHR0cHMiIHx8ICRtb2RlID09ICJodHRwX2h0dHBzIiB8fCAkbW9kZSA9PSAiaHR0cHNfb2ZmbG9hZCIgXV07IHRoZW4KICAgICAgICAgY2hhaW49Ii9Db21tb24vY2EtYnVuZGxlLmNydCIKCiAgICAgICAgIGVjaG8gIlN0YXJ0aW5nIENlcnRpZmljYXRlIGRvd25sb2FkIgoKICAgICAgICAgY2VydGlmaWNhdGVfbG9jYXRpb249JHNzbF9jZXJ0CgogICAgICAgICByZXNwb25zZV9jb2RlPSQoL3Vzci9iaW4vY3VybCAtc2sgLXUgJHVzZXI6JChwYXNzd2QpIC13ICIle2h0dHBfY29kZX0iICAtWCBQT1NUIC1IICJDb250ZW50LXR5cGU6IGFwcGxpY2F0aW9uL2pzb24iIGh0dHBzOi8vbG9jYWxob3N0OiRkZmxfbWdtdF9wb3J0L21nbXQvdG0vdXRpbC9iYXNoIC1kICd7ICJjb21tYW5kIjoicnVuIiwidXRpbENtZEFyZ3MiOiItYyBcImN1cmwgLWsgLXMgLWYgLS1yZXRyeSA1IC0tcmV0cnktZGVsYXkgMTAgLS1yZXRyeS1tYXgtdGltZSAxMCAtbyAvY29uZmlnL3RtcC5wZnggJyRjZXJ0aWZpY2F0ZV9sb2NhdGlvbidcIiIgfScgLW8gL2Rldi9udWxsKQoKICAgICAgICAgaWYgW1sgJHJlc3BvbnNlX2NvZGUgPT0gMjAwICBdXTsgdGhlbgogICAgICAgICAgICAgIGVjaG8gIkNlcnRpZmljYXRlIGRvd25sb2FkIGNvbXBsZXRlLiIKICAgICAgICAgZWxzZQogICAgICAgICAgICAgZWNobyAiRmFpbGVkIHRvIGRvd25sb2FkIFNTTCBjZXJ0OyBleGl0aW5nIHdpdGggcmVzcG9uc2UgY29kZSAnIiRyZXNwb25zZV9jb2RlIiciCiAgICAgICAgICAgICBleGl0IDEKICAgICAgICAgZmkKCiAgICAgICAgIHJlc3BvbnNlX2NvZGU9JCgvdXNyL2Jpbi9jdXJsIC1za3UgJHVzZXI6JChwYXNzd2QpIC13ICIle2h0dHBfY29kZX0iIC1YIFBPU1QgLUggIkNvbnRlbnQtVHlwZTogYXBwbGljYXRpb24vanNvbiIgaHR0cHM6Ly9sb2NhbGhvc3Q6JGRmbF9tZ210X3BvcnQvbWdtdC90bS9zeXMvY3J5cHRvL3BrY3MxMiAtZCAneyJjb21tYW5kIjogImluc3RhbGwiLCJuYW1lIjogIndhZkNlcnQiLCJvcHRpb25zIjogWyB7ICJmcm9tLWxvY2FsLWZpbGUiOiAiL2NvbmZpZy90bXAucGZ4IiB9LCB7ICJwYXNzcGhyYXNlIjogIiciJHNzbF9wYXNzd2QiJyIgfSBdIH0nIC1vIC9kZXYvbnVsbCkKCiAgICAgICAgIGlmIFtbICRyZXNwb25zZV9jb2RlID09IDIwMCAgXV07IHRoZW4KICAgICAgICAgICAgICBlY2hvICJDZXJ0aWZpY2F0ZSBpbnN0YWxsIGNvbXBsZXRlLiIKICAgICAgICAgZWxzZQogICAgICAgICAgICAgZWNobyAiRmFpbGVkIHRvIGluc3RhbGwgU1NMIGNlcnQ7IGV4aXRpbmcgd2l0aCByZXNwb25zZSBjb2RlICciJHJlc3BvbnNlX2NvZGUiJyIKICAgICAgICAgICAgIGV4aXQgMQogICAgICAgICBmaQogICAgZmkKCiAgICBwYXlsb2FkPSQoZWNobyAkcGF5bG9hZCB8IGpxIC1jIC0tYXJnIGFzbV9wb2xpY3kgJGFzbV9wb2xpY3kgJyAud2FmLlNoYXJlZC5wb2xpY3lXQUYuZmlsZSA9ICRhc21fcG9saWN5JykKCiAgICBwYXlsb2FkPSQoZWNobyAkcGF5bG9hZCB8IGpxIC1jIC0tYXJnIHBvb2xfaHR0cF9wb3J0ICRwb29sX2h0dHBfcG9ydCAtLWFyZyBwb29sX2h0dHBzX3BvcnQgJHBvb2xfaHR0cHNfcG9ydCAtLWFyZyB2c19odHRwX3BvcnQgJHZzX2h0dHBfcG9ydCAtLWFyZyB2c19odHRwc19wb3J0ICR2c19odHRwc19wb3J0ICcgLndhZi5odHRwLnBvb2wubWVtYmVyc1swXS5zZXJ2aWNlUG9ydCA9ICgkcG9vbF9odHRwX3BvcnQgfCB0b251bWJlcikgfCAud2FmLmh0dHAuc2VydmljZU1haW4udmlydHVhbFBvcnQgPSAoJHZzX2h0dHBfcG9ydCB8IHRvbnVtYmVyKSB8IC53YWYuaHR0cHMucG9vbC5tZW1iZXJzWzBdLnNlcnZpY2VQb3J0ID0gKCRwb29sX2h0dHBzX3BvcnQgfCB0b251bWJlcikgfCAud2FmLmh0dHBzLnNlcnZpY2VNYWluLnZpcnR1YWxQb3J0ID0gKCR2c19odHRwc19wb3J0IHwgdG9udW1iZXIpIHwgLndhZi5odHRwc19vZmZsb2FkLnBvb2wubWVtYmVyc1swXS5zZXJ2aWNlUG9ydCA9ICgkcG9vbF9odHRwX3BvcnQgfCB0b251bWJlcikgfCAud2FmLmh0dHBzX29mZmxvYWQuc2VydmljZU1haW4udmlydHVhbFBvcnQgPSAoJHZzX2h0dHBzX3BvcnQgfCB0b251bWJlciknKQoKICAgIGlmIFtbICRwb29sX21lbWJlciA9fiAkaXBfcmVnZXggXV07IHRoZW4KICAgICAgICAgcGF5bG9hZD0kKGVjaG8gJHBheWxvYWQgfCBqcSAtYyAnZGVsKC53YWYuaHR0cC5wb29sLm1lbWJlcnNbMF0uYXV0b1BvcHVsYXRlKSB8IGRlbCgud2FmLmh0dHAucG9vbC5tZW1iZXJzWzBdLmhvc3RuYW1lKSB8IGRlbCgud2FmLmh0dHAucG9vbC5tZW1iZXJzWzBdLmFkZHJlc3NEaXNjb3ZlcnkpIHwgIGRlbCgud2FmLmh0dHBzLnBvb2wubWVtYmVyc1swXS5hdXRvUG9wdWxhdGUpIHwgZGVsKC53YWYuaHR0cHMucG9vbC5tZW1iZXJzWzBdLmhvc3RuYW1lKSB8IGRlbCgud2FmLmh0dHBzLnBvb2wubWVtYmVyc1swXS5hZGRyZXNzRGlzY292ZXJ5KSB8IGRlbCgud2FmLmh0dHBzX29mZmxvYWQucG9vbC5tZW1iZXJzWzBdLmF1dG9Qb3B1bGF0ZSkgfCBkZWwoLndhZi5odHRwc19vZmZsb2FkLnBvb2wubWVtYmVyc1swXS5ob3N0bmFtZSkgfCBkZWwoLndhZi5odHRwc19vZmZsb2FkLnBvb2wubWVtYmVyc1swXS5hZGRyZXNzRGlzY292ZXJ5KScpCgogICAgICAgICBwYXlsb2FkPSQoZWNobyAkcGF5bG9hZCB8IGpxIC1jIC0tYXJnIHBvb2xfbWVtYmVyICRwb29sX21lbWJlciAnLndhZi5odHRwLnBvb2wubWVtYmVyc1swXS5zZXJ2ZXJBZGRyZXNzZXNbMF0gPSAkcG9vbF9tZW1iZXIgfCAud2FmLmh0dHBzLnBvb2wubWVtYmVyc1swXS5zZXJ2ZXJBZGRyZXNzZXNbMF0gPSAkcG9vbF9tZW1iZXIgfCAud2FmLmh0dHBzX29mZmxvYWQucG9vbC5tZW1iZXJzWzBdLnNlcnZlckFkZHJlc3Nlc1swXSA9ICRwb29sX21lbWJlcicpCiAgICBlbHNlCiAgICAgICAgIHBheWxvYWQ9JChlY2hvICRwYXlsb2FkIHwganEgLWMgJ2RlbCgud2FmLmh0dHAucG9vbC5tZW1iZXJzWzBdLnNlcnZlckFkZHJlc3NlcykgfCBkZWwoLndhZi5odHRwcy5wb29sLm1lbWJlcnNbMF0uc2VydmVyQWRkcmVzc2VzKSB8IGRlbCgud2FmLmh0dHBzX29mZmxvYWQucG9vbC5tZW1iZXJzWzBdLnNlcnZlckFkZHJlc3NlcyknKQoKICAgICAgICAgcGF5bG9hZD0kKGVjaG8gJHBheWxvYWQgfCBqcSAtYyAtLWFyZyBwb29sX21lbWJlciAkcG9vbF9tZW1iZXIgJy53YWYuaHR0cC5wb29sLm1lbWJlcnNbMF0uaG9zdG5hbWUgPSAkcG9vbF9tZW1iZXIgfCAud2FmLmh0dHBzLnBvb2wubWVtYmVyc1swXS5ob3N0bmFtZSA9ICRwb29sX21lbWJlciB8IC53YWYuaHR0cHNfb2ZmbG9hZC5wb29sLm1lbWJlcnNbMF0uaG9zdG5hbWUgPSAkcG9vbF9tZW1iZXInKQogICAgZmkKCiAgICBpZiBbWyAkbW9kZSA9PSAiaHR0cCIgXV07IHRoZW4KICAgICAgICBwYXlsb2FkPSQoZWNobyAkcGF5bG9hZCB8IGpxIC1jICdkZWwoLndhZi5odHRwcykgfCBkZWwoLndhZi5odHRwc19vZmZsb2FkKScpCiAgICBlbGlmIFtbICRtb2RlID09ICJodHRwcyIgXV07IHRoZW4KICAgICAgICBwYXlsb2FkPSQoZWNobyAkcGF5bG9hZCB8IGpxIC1jICdkZWwoLndhZi5odHRwKSB8IGRlbCgud2FmLmh0dHBzX29mZmxvYWQpIHwgLndhZi5odHRwcy5jZXJ0U2VydmVyLmNlcnRpZmljYXRlLmJpZ2lwID0gIi9Db21tb24vd2FmQ2VydC5jcnQiIHwgLndhZi5odHRwcy5jZXJ0U2VydmVyLnByaXZhdGVLZXkuYmlnaXAgPSAiL0NvbW1vbi93YWZDZXJ0LmtleSInKQogICAgZWxpZiBbWyAkbW9kZSA9PSAiaHR0cF9odHRwcyIgXV07IHRoZW4KICAgICAgICBwYXlsb2FkPSQoZWNobyAkcGF5bG9hZCB8IGpxIC1jICdkZWwoLndhZi5odHRwc19vZmZsb2FkKSB8IC53YWYuaHR0cHMuc2VydmljZU1haW4ucmVkaXJlY3Q4MCA9IGZhbHNlIHwgLndhZi5odHRwcy5jZXJ0U2VydmVyLmNlcnRpZmljYXRlLmJpZ2lwID0gIi9Db21tb24vd2FmQ2VydC5jcnQiIHwgLndhZi5odHRwcy5jZXJ0U2VydmVyLnByaXZhdGVLZXkuYmlnaXAgPSAiL0NvbW1vbi93YWZDZXJ0LmtleSInKQogICAgZWxzZQogICAgICAgIHBheWxvYWQ9JChlY2hvICRwYXlsb2FkIHwganEgLWMgJ2RlbCgud2FmLmh0dHApIHwgZGVsKC53YWYuaHR0cHMpIHwgLndhZi5odHRwc19vZmZsb2FkLmNlcnRTZXJ2ZXIuY2VydGlmaWNhdGUuYmlnaXAgPSAiL0NvbW1vbi93YWZDZXJ0LmNydCIgfCAud2FmLmh0dHBzX29mZmxvYWQuY2VydFNlcnZlci5wcml2YXRlS2V5LmJpZ2lwID0gIi9Db21tb24vd2FmQ2VydC5rZXkiJykKICAgIGZpCgogICAgIHJlc3BvbnNlX2NvZGU9JCgvdXNyL2Jpbi9jdXJsIC1za3Z2dSAkdXNlcjokKHBhc3N3ZCkgLXcgIiV7aHR0cF9jb2RlfSIgLVggUE9TVCAtSCAiQ29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi9qc29uIiBodHRwczovL2xvY2FsaG9zdDokZGZsX21nbXRfcG9ydC9tZ210L3NoYXJlZC9hcHBzdmNzL2RlY2xhcmUgLWQgIiRwYXlsb2FkIiAtbyAvZGV2L251bGwpCgogICAgIGlmIFtbICRyZXNwb25zZV9jb2RlID09IDIwMCB8fCAkcmVzcG9uc2VfY29kZSA9PSA1MDIgIF1dOyB0aGVuCiAgICAgICAgICBlY2hvICJEZXBsb3ltZW50IG9mIGFwcGxpY2F0aW9uIHN1Y2NlZWRlZC4iCiAgICBlbHNlCiAgICAgICAgIGVjaG8gIkZhaWxlZCB0byBkZXBsb3kgYXBwbGljYXRpb247IGV4aXRpbmcgd2l0aCByZXNwb25zZSBjb2RlICciJHJlc3BvbnNlX2NvZGUiJyIKICAgICAgICAgZXhpdCAxCiAgICAgZmkKIGZpCgplY2hvICJEZXBsb3ltZW50IGNvbXBsZXRlLiIKZXhpdA=="
elif template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'as_ltm_lb', 'as_ltm_dns', 'failover-api', 'failover-lb_1nic', 'failover-lb_3nic'):
    data['variables']['commandArgs'] = "[concat('-o ', parameters('declarationUrl'), ' -u svc_user')]"
    data['variables']['appScript'] = "IyEvYmluL2Jhc2gKZnVuY3Rpb24gcGFzc3dkKCkgewogIGVjaG8gfCBmNS1yZXN0LW5vZGUgL2NvbmZpZy9jbG91ZC9henVyZS9ub2RlX21vZHVsZXMvQGY1ZGV2Y2VudHJhbC9mNS1jbG91ZC1saWJzL3NjcmlwdHMvZGVjcnlwdERhdGFGcm9tRmlsZS5qcyAtLWRhdGEtZmlsZSAvY29uZmlnL2Nsb3VkLy5wYXNzd2QgfCBhd2sgJ3twcmludCAkMX0nCn0KCndoaWxlIGdldG9wdHMgbzp1OiBvcHRpb24KZG8gY2FzZSAiJG9wdGlvbiIgIGluCiAgICAgICAgbykgZGVjbGFyYXRpb25Vcmw9JE9QVEFSRzs7CiAgICAgICAgdSkgdXNlcj0kT1BUQVJHOzsKICAgIGVzYWMKZG9uZQoKZGVwbG95ZWQ9Im5vIgpmaWxlX2xvYz0iL2NvbmZpZy9jbG91ZC9jdXN0b21fY29uZmlnIgpkZmxfbWdtdF9wb3J0PWB0bXNoIGxpc3Qgc3lzIGh0dHBkIHNzbC1wb3J0IHwgZ3JlcCBzc2wtcG9ydCB8IHNlZCAncy9zc2wtcG9ydCAvLztzLyAvL2cnYAp1cmxfcmVnZXg9IihodHRwOlwvXC98aHR0cHM6XC9cLyk/W2EtejAtOV0rKFtcLVwuXXsxfVthLXowLTldKykqXC5bYS16XXsyLDV9KDpbMC05XXsxLDV9KT8oXC8uKik/JCIKCmlmIFtbICRkZWNsYXJhdGlvblVybCA9fiAkdXJsX3JlZ2V4IF1dOyB0aGVuCiAgICByZXNwb25zZV9jb2RlPSQoL3Vzci9iaW4vY3VybCAtc2sgLXcgIiV7aHR0cF9jb2RlfSIgJGRlY2xhcmF0aW9uVXJsIC1vICRmaWxlX2xvYykKICAgIGlmIFtbICRyZXNwb25zZV9jb2RlID09IDIwMCBdXTsgdGhlbgogICAgICAgICBlY2hvICJDdXN0b20gY29uZmlnIGRvd25sb2FkIGNvbXBsZXRlOyBjaGVja2luZyBmb3IgdmFsaWQgSlNPTi4iCiAgICAgICAgIGNhdCAkZmlsZV9sb2MgfCBqcSAuY2xhc3MKICAgICAgICAgaWYgW1sgJD8gPT0gMCBdXTsgdGhlbgogICAgICAgICAgICAgcmVzcG9uc2VfY29kZT0kKC91c3IvYmluL2N1cmwgLXNrdnZ1ICR1c2VyOiQocGFzc3dkKSAtdyAiJXtodHRwX2NvZGV9IiAtWCBQT1NUIC1IICJDb250ZW50LVR5cGU6IGFwcGxpY2F0aW9uL2pzb24iIGh0dHBzOi8vbG9jYWxob3N0OiRkZmxfbWdtdF9wb3J0L21nbXQvc2hhcmVkL2FwcHN2Y3MvZGVjbGFyZSAtZCBAJGZpbGVfbG9jIC1vIC9kZXYvbnVsbCkKCiAgICAgICAgICAgICBpZiBbWyAkcmVzcG9uc2VfY29kZSA9PSAyMDAgfHwgJHJlc3BvbnNlX2NvZGUgPT0gNTAyIF1dOyB0aGVuCiAgICAgICAgICAgICAgICAgIGVjaG8gIkRlcGxveW1lbnQgb2YgYXBwbGljYXRpb24gc3VjY2VlZGVkLiIKICAgICAgICAgICAgICAgICAgZGVwbG95ZWQ9InllcyIKICAgICAgICAgICAgIGVsc2UKICAgICAgICAgICAgICAgICBlY2hvICJGYWlsZWQgdG8gZGVwbG95IGFwcGxpY2F0aW9uOyBjb250aW51aW5nIHdpdGggcmVzcG9uc2UgY29kZSAnIiRyZXNwb25zZV9jb2RlIiciCiAgICAgICAgICAgICBmaQogICAgICAgICBlbHNlCiAgICAgICAgICAgICBlY2hvICJDdXN0b20gY29uZmlnIHdhcyBub3QgdmFsaWQgSlNPTiwgY29udGludWluZyIKICAgICAgICAgZmkKICAgIGVsc2UKICAgICAgICBlY2hvICJGYWlsZWQgdG8gZG93bmxvYWQgY3VzdG9tIGNvbmZpZzsgY29udGludWluZyB3aXRoIHJlc3BvbnNlIGNvZGUgJyIkcmVzcG9uc2VfY29kZSInIgogICAgZmkKZWxzZQogICAgIGVjaG8gIkN1c3RvbSBjb25maWcgd2FzIG5vdCBhIFVSTCwgY29udGludWluZy4iCmZpCgppZiBbWyAkZGVwbG95ZWQgPT0gIm5vIiAmJiAkZGVjbGFyYXRpb25VcmwgPT0gIk5PVF9TUEVDSUZJRUQiIF1dOyB0aGVuCiAgICBlY2hvICJBcHBsaWNhdGlvbiBkZXBsb3ltZW50IGZhaWxlZCBvciBjdXN0b20gVVJMIHdhcyBub3Qgc3BlY2lmaWVkLiIKZmkKCmVjaG8gIkRlcGxveW1lbnQgY29tcGxldGUuIgpleGl0"

# Add learning stack variables
if learningStack:
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
if stack_type in ('new-stack', 'existing-stack'):
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_1nic', 'as_ltm_lb', 'as_waf_lb'):
        pub_ip_def = { "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[variables('mgmtPublicIPAddressName')]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[variables('dnsLabel')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }
        if template_name in ('as_ltm_lb', 'as_waf_lb') and license_type == 'bigiq-payg':
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
if template_name in ('standalone_3nic', 'failover-lb_3nic'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }, { "name": "[variables('intSubnetName')]", "properties": { "addressPrefix": "[variables('intSubnetPrefix')]" } }]
if template_name in ('failover-api'):
    subnets = "[concat(take(variables('subnetArray'), 3), take(variables('addtlSubnetArray'), parameters('numberOfAdditionalNics')))]"
if template_name in ('standalone_n-nic'):
    subnets = "[concat(take(variables('subnetArray'), 3), take(variables('addtlSubnetArray'), parameters('numberOfAdditionalNics')))]"
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_1nic', 'failover-lb_3nic', 'failover-api'):
    if stack_type == 'new-stack':
        resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": network_api_version, "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }]
    scale_depends_on = ["[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]"]
    if stack_type == 'new-stack':
        scale_depends_on += ["[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]"]
        resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": network_api_version, "dependsOn": [ "[variables('mgmtNsgID')]" ], "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

###### Network Interface Resource(s) ######
depends_on = ["[variables('vnetId')]", "[variables('mgmtPublicIPAddressId')]", "[variables('mgmtNsgID')]"]
depends_on_ext = ["[variables('vnetId')]", "[variables('extNsgID')]", "extpipcopy"]
depends_on_ext_pub0 = ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '0')]"]
depends_on_ext_pub1 = ["[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '1')]"]
# Remove incorrect depends_on items based on stack and solution type
if stack_type == 'existing-stack':
    depends_on.remove("[variables('vnetId')]")
    depends_on_ext.remove("[variables('vnetId')]")
elif stack_type == 'production-stack':
    depends_on.remove("[variables('vnetId')]")
    depends_on.remove("[variables('mgmtPublicIPAddressId')]")
    depends_on_ext.remove("[variables('vnetId')]")
    depends_on_ext.remove("extpipcopy")
    depends_on_ext_pub0 = []
    depends_on_ext_pub1 = []
if template_name in ('failover-api', 'failover-lb_3nic'):
    depends_on.remove("[variables('mgmtPublicIPAddressId')]")

if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic',):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "dependsOn": depends_on, "location": location, "name": "[variables('mgmtNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[variables('mgmtNsgID')]" }, "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('mgmtSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": { "Id": "[variables('mgmtPublicIPAddressId')]" }, "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ] } }]
if template_name in ('standalone_2nic'):
    if stack_type in ('new-stack'):
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations', 1), 2)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations', 1), 2)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations', 1), 1), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations', 1), 1), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), 1, sub(copyIndex('ipConfigurations', 1), 2)))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ] } } ]
    if stack_type in ('existing-stack', 'production-stack'):
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations', 1), 2)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations', 1), 2)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations', 1), 1), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations', 1), 1), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), sub(copyIndex('ipConfigurations', 1), 1))))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ] } } ]
if template_name in ('standalone_3nic', 'standalone_n-nic'):
    if stack_type in ('new-stack'):
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations', 1), 2)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations', 1), 2)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations', 1), 1), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations', 1), 1), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), 1, sub(copyIndex('ipConfigurations', 1), 2)))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ] } }, { "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "dependsOn": depends_on_ext, "location": location, "name": "[variables('intNicName')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] } } ]
    if stack_type in ('existing-stack', 'production-stack'):
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations', 1), 2)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations', 1), 1), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations', 1), 2)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations', 1), 1), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations', 1), 1), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), sub(copyIndex('ipConfigurations', 1), 1))))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ] } }, { "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "dependsOn": depends_on_ext, "location": location, "name": "[variables('intNicName')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] } } ]
if template_name in ('standalone_n-nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "condition": "[greaterOrEquals(parameters('numberOfAdditionalNics'), 1)]", "copy": { "count": "[parameters('numberOfAdditionalNics')]", "name": "addtlniccopy" }, "dependsOn": depends_on + ["[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]"], "location": location, "name": "[concat(variables('instanceName'), '-addtlNic', copyIndex(1))]", "properties": { "ipConfigurations": [ { "name": "ipconfig", "properties": { "privateIPAllocationMethod": "Dynamic", "subnet": { "id": "[concat(variables('vnetId'), '/subnets/', variables('addtlNicRefSplit')[copyIndex()])]" } } } ] }, "tags": tags }]
if template_name in ('failover-lb_1nic'):
    resources_list += [{ "apiVersion": network_api_version, "type": "Microsoft.Network/networkInterfaces", "name": "[concat(variables('mgmtNicName'),copyindex())]", "location": location, "tags": tags, "dependsOn": depends_on + ["[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'),'/inboundNatRules/guimgt',copyindex())]", "[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'),'/inboundNatRules/sshmgt',copyindex())]"], "copy": { "count": "[parameters('numberOfInstances')]", "name": "niccopy" }, "properties": { "networkSecurityGroup": { "id": "[variables('mgmtNsgID')]" }, "ipConfigurations": [ { "name": "ipconfig1", "properties": { "privateIPAllocationMethod": "Static", "privateIPAddress": "[concat(variables('mgmtSubnetPrivateAddress'),add(variables('mgmtSubnetPrivateAddressSuffix'), copyindex()))]", "subnet": { "id": "[variables('mgmtSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('extLbId'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ], "loadBalancerInboundNatRules": [ { "id": "[concat(variables('extLbId'), '/inboundNatRules/', 'guimgt',copyIndex())]" }, { "id": "[concat(variables('extLbId'), '/inboundNatRules/', 'sshmgt',copyIndex())]" } ] } } ] } }]

# Can we shrink this down with a copy?
if template_name in ('failover-api', 'failover-lb_3nic'):
    resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on + ["[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'), '0')]"], "location": location, "name": "[concat(variables('mgmtNicName'), '0')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-mgmt-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(variables('mgmtPublicIPAddressName'), '0'))]" }, "privateIPAddress": "[variables('mgmtSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[variables('mgmtNsgId')]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on + ["[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'), '1')]"], "location": location, "name": "[concat(variables('mgmtNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-mgmt-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(variables('mgmtPublicIPAddressName'), '1'))]" }, "privateIPAddress": "[variables('mgmtSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[variables('mgmtNsgId')]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    if template_name in ('failover-api'):
        if stack_type in ('new-stack'):
            resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations'), 0), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations'), 1)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations'), 0), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations'), 1)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations'), 0), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations'), 0), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), sub(copyIndex('ipConfigurations'), 1))))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        if stack_type in ('existing-stack', 'production-stack'):
            resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0, "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "copy": [ { "name": "ipConfigurations", "count": "[add(variables('numberOfExternalIps'), 1)]", "input": { "name": "[if(equals(copyIndex('ipConfigurations'), 0), concat(variables('instanceName'), '-self-ipconfig'), concat(variables('resourceGroupName'), '-ext-ipconfig', sub(copyIndex('ipConfigurations'), 1)))]", "properties": { "PublicIpAddress": { "Id": "[if(equals(copyIndex('ipConfigurations'), 0), concat(variables('extSelfPublicIpAddressIdPrefix'), '0'), concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('ipConfigurations'), 1)))]" }, "primary": "[if(equals(copyIndex('ipConfigurations'), 0), 'True', 'False')]", "privateIPAddress": "[if(equals(copyIndex('ipConfigurations'), 0), variables('extSubnetPrivateAddress'), concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), sub(copyIndex('ipConfigurations'), 1))))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub1, "location": location, "name": "[concat(variables('extNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "condition": "[greaterOrEquals(parameters('numberOfAdditionalNics'), 1)]", "copy": { "count": "[if(greaterOrEquals(parameters('numberOfAdditionalNics'), 1), parameters('numberOfAdditionalNics'), 1)]", "name": "addtlniccopy0" }, "dependsOn": depends_on, "location": location, "name": "[concat(variables('addtlNicName'), copyIndex(1), '0')]", "properties": { "ipConfigurations": [ { "name": "ipconfig", "properties": { "privateIPAllocationMethod": "Dynamic", "subnet": { "id": "[concat(variables('vnetId'), '/subnets/', variables('addtlNicRefSplit')[copyIndex()])]" } } } ] }, "tags": tags }]
        resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "condition": "[greaterOrEquals(parameters('numberOfAdditionalNics'), 1)]", "copy": { "count": "[if(greaterOrEquals(parameters('numberOfAdditionalNics'), 1), parameters('numberOfAdditionalNics'), 1)]", "name": "addtlniccopy1" }, "dependsOn": depends_on, "location": location, "name": "[concat(variables('addtlNicName'), copyIndex(1), '1')]", "properties": { "ipConfigurations": [ { "name": "ipconfig", "properties": { "privateIPAllocationMethod": "Dynamic", "subnet": { "id": "[concat(variables('vnetId'), '/subnets/', variables('addtlNicRefSplit')[copyIndex()])]" } } } ] }, "tags": tags }]
    if template_name in ('failover-lb_3nic'):
        if stack_type in ('new-stack'):
            resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0 + ["[variables('extLbId')]"], "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '0')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig0')]", "properties": { "primary": False, "loadBalancerBackendAddressPools": "[if(equals(variables('numberOfExternalIps'), 0), take(variables('backEndAddressPoolArray'), 0), take(variables('backEndAddressPoolArray'), 1))]", "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 10)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
            resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub1 + ["[variables('extLbId')]"], "location": location, "name": "[concat(variables('extNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig1')]", "properties": { "primary": False, "loadBalancerBackendAddressPools": "[if(equals(variables('numberOfExternalIps'), 0), take(variables('backEndAddressPoolArray'), 0), take(variables('backEndAddressPoolArray'), 1))]", "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 11)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        if stack_type in ('existing-stack', 'production-stack'):
            resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0 + ["[variables('extLbId')]"], "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '0')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig0')]", "properties": { "primary": False, "loadBalancerBackendAddressPools": "[if(equals(variables('numberOfExternalIps'), 0), take(variables('backEndAddressPoolArray'), 0), take(variables('backEndAddressPoolArray'), 1))]", "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix0'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
            resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub1 + ["[variables('extLbId')]"], "location": location, "name": "[concat(variables('extNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('resourceGroupName'), '-ext-ipconfig1')]", "properties": { "primary": False, "loadBalancerBackendAddressPools": "[if(equals(variables('numberOfExternalIps'), 0), take(variables('backEndAddressPoolArray'), 0), take(variables('backEndAddressPoolArray'), 1))]", "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix1'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    if template_name in ('failover-lb_3nic'):
        resources_list += [{"apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub0 + ["[variables('intLbId')]"], "location": location, "name": "[concat(variables('intNicName'), '0')]", "properties": { "primary": True, "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "primary": True, "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } }, { "name": "[concat(variables('dnsLabel'), '-int-ipconfig-secondary')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress2')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" }, "loadBalancerBackendAddressPools": "[if(equals(parameters('internalLoadBalancerType'), 'DO_NOT_USE'), take(variables('backEndAddressPoolArray'), 0), skip(variables('backEndAddressPoolArray'), 1))]" } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces"}]
        resources_list += [{"apiVersion": network_api_version, "dependsOn": depends_on_ext + depends_on_ext_pub1 + ["[variables('intLbId')]"], "location": location, "name": "[concat(variables('intNicName'), '1')]", "properties": { "primary": True, "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "primary": True, "privateIPAddress": "[variables('intSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } }, { "name": "[concat(variables('dnsLabel'), '-int-ipconfig-secondary')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress3')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" }, "loadBalancerBackendAddressPools": "[if(equals(parameters('internalLoadBalancerType'), 'DO_NOT_USE'), take(variables('backEndAddressPoolArray'), 0), skip(variables('backEndAddressPoolArray'), 1))]" } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces"}]
    else:
        resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on_ext, "location": location, "name": "[concat(variables('intNicName'), '0')]", "properties": { "primary": True, "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
        resources_list += [{ "apiVersion": network_api_version, "dependsOn": depends_on_ext, "location": location, "name": "[concat(variables('intNicName'), '1')]", "properties": { "primary": True, "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]

# Add learning stack NIC(s)
if learningStack:
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": network_api_version, "dependsOn": depends_on, "location": location, "name": "[concat(variables('webVmName'), '-nic')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('webVmName'), '-nic', '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('webVmSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": None, "subnet": { "id": "[variables('intSubnetId')]" } } } ] } }]

###### Network Security Group Resource(s) ######
mgmt_nsg_security_rules = [{ "name": "mgmt_allow_https", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('bigIpMgmtPort')]", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }, { "name": "ssh_allow_22", "properties": { "description": "", "priority": 102, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }]
ext_nsg_security_rules = []
# Add learning stack NSG rules
if learningStack:
    ext_nsg_security_rules += [{ "name": "allow_example_app", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('webVmVsPort')]", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }]

if template_name in ('as_waf_lb', 'as_waf_dns'):
    mgmt_nsg_security_rules += [{ "name": "app_allow_http", "properties": { "description": "", "priority": 110, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpBackendPort')]", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }, { "name": "app_allow_https", "properties": { "description": "", "priority": 111, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpsBackendPort')]", "protocol": "Tcp", "direction": "Inbound", "access": "Allow" } }]

if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_1nic', 'failover-lb_3nic', 'as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    resources_list += [{ "apiVersion": network_api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-mgmt-nsg')]", "tags": tags, "properties": { "securityRules": mgmt_nsg_security_rules } }]
if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
    resources_list += [{ "apiVersion": network_api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-ext-nsg')]", "tags": tags, "properties": { "securityRules": ext_nsg_security_rules } }]

###### Load Balancer Resource(s) ######
probes_to_use = ""
lb_rules_to_use = ""
if template_name in ('as_waf_lb', 'as_waf_dns') or license_type == 'bigiq-payg':
    frontend_port = "[parameters('applicationPort')]"
    frontend_port_https = "[parameters('applicationSecurePort')]"
    backend_port = "[variables('httpBackendPort')]"
    backend_port_https = "[variables('httpsBackendPort')]"
    # Outbound connections for standard sku LB does not work without an LB rule, so add to LTM templates
    if template_name in ('as_ltm_lb', 'as_ltm_dns'):
        frontend_port = 80
        frontend_port_https = 443
        backend_port = 80
        backend_port_https = 443
    probes_to_use = [ { "name": "[variables('lbTcpProbeNameHttp')]", "properties": { "protocol": "Tcp", "port": backend_port, "intervalInSeconds": 15, "numberOfProbes": 3 } }, { "name": "[variables('lbTcpProbeNameHttps')]", "properties": { "protocol": "Tcp", "port": backend_port_https, "intervalInSeconds": 15, "numberOfProbes": 3 } } ]
    lb_rules_to_use = [{ "Name": "app-http", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('externalLoadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('externalLoadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttp')]" }, "protocol": "Tcp", "frontendPort": frontend_port, "backendPort": backend_port, "idleTimeoutInMinutes": 15 } }, { "Name": "app-https", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('externalLoadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('externalLoadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttps')]" }, "protocol": "Tcp", "frontendPort": frontend_port_https, "backendPort": backend_port_https, "idleTimeoutInMinutes": 15 } }]

if template_name == 'failover-lb_1nic':
    lb_fe_properties = { "publicIPAddress": { "id": "[variables('mgmtPublicIPAddressId')]" } }
    depends_on_pip = ["[variables('mgmtPublicIPAddressId')]"]
    if stack_type in ('production-stack'):
        lb_fe_properties = { "privateIPAddress":  "[variables('externalLoadBalancerAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } }
        depends_on_pip.remove("[variables('mgmtPublicIPAddressId')]")
    resources_list += [{ "apiVersion": network_api_version, "dependsOn": [] + depends_on_pip, "location": location, "tags": tags, "name": "[variables('externalLoadBalancerName')]", "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": lb_fe_properties } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ] }, "type": "Microsoft.Network/loadBalancers" }]
if template_name == 'failover-lb_3nic':
    resources_list += [{ "apiVersion": network_api_version, "condition": "[not(equals(variables('numberOfExternalIps'),0))]", "dependsOn": [ "extpipcopy" ], "location": location, "tags": tags, "name": "[variables('externalLoadBalancerName')]", "properties": { "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ], "copy": [ { "name": "frontendIPConfigurations", "count": "[if(not(equals(variables('numberOfExternalIps'), 0)), variables('numberOfExternalIps'), 1)]", "input": { "name": "[concat('loadBalancerFrontEnd', copyIndex('frontendIPConfigurations', 1))]", "properties": { "publicIPAddress": { "id": "[concat(variables('extPublicIPAddressIdPrefix'), sub(copyIndex('frontendIPConfigurations', 1), 1))]" } } } } ] }, "type": "Microsoft.Network/loadBalancers" }]
    probes_to_use = [{"name": "[concat('tcp-probe-', parameters('internalLoadBalancerProbePort'))]", "properties": { "protocol": "Tcp", "port": "[parameters('internalLoadBalancerProbePort')]", "intervalInSeconds": 5, "numberOfProbes": 2 }}]
    lb_rules_to_use = [{"name": "[if(equals(parameters('internalLoadBalancerType'),'Per-protocol'), concat('lbRule-', parameters('internalLoadBalancerProbePort')), 'allProtocolLbRule')]", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('internalLoadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('internalLoadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('internalLoadBalancerName')), '/probes/tcp-probe-', parameters('internalLoadBalancerProbePort'))]" }, "frontendPort": "[if(equals(parameters('internalLoadBalancerType'),'Per-protocol'), parameters('internalLoadBalancerProbePort'), 0)]", "backendPort": "[if(equals(parameters('internalLoadBalancerType'),'Per-protocol'), parameters('internalLoadBalancerProbePort'), 0)]", "enableFloatingIP": False, "idleTimeoutInMinutes": 15, "protocol": "[if(equals(parameters('internalLoadBalancerType'),'Per-protocol'), 'Tcp', 'All')]", "loadDistribution": "Default" }}]
    resources_list += [{ "apiVersion": network_api_version, "name": "[variables('internalLoadBalancerName')]", "condition": "[not(equals(parameters('internalLoadBalancerType'),'DO_NOT_USE'))]", "type": "Microsoft.Network/loadBalancers", "location": location, "tags": tags, "dependsOn": depends_on_ext, "properties": { "frontendIPConfigurations": [ { "name": "LoadBalancerFrontEnd", "properties": { "privateIPAddress":  "[variables('internalLoadBalancerAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ], "backendAddressPools": [ { "name": "LoadBalancerBackEnd" } ], "loadBalancingRules": lb_rules_to_use, "probes": probes_to_use } }]
if template_name in ('as_ltm_lb', 'as_waf_lb'):
    scale_ports = { 'ssh_start': 50001, 'ssh_end': 50100, 'https_start': 50101, 'https_end': 50200 }
    inbound_nat_pools_static = []
    if license_type == 'bigiq-payg':
        # Update ports if static VMSS is using start range
        scale_ports_static = { 'ssh_start': 50001, 'ssh_end': 50009, 'https_start': 50101, 'https_end': 50109 }
        scale_ports = { 'ssh_start': 50010, 'ssh_end': 50100, 'https_start': 50110, 'https_end': 50200 }
        inbound_nat_pools_static = [ { "name": "sshnatpool-static", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPortRangeStart": scale_ports_static['ssh_start'], "frontendPortRangeEnd": scale_ports_static['ssh_end'], "backendPort": 22 } }, { "name": "mgmtnatpool-static", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPortRangeStart": scale_ports_static['https_start'], "frontendPortRangeEnd": scale_ports_static['https_end'], "backendPort": "[variables('bigIpMgmtPort')]" } } ]
    inbound_nat_pools = [ { "name": "sshnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPortRangeStart": scale_ports['ssh_start'], "frontendPortRangeEnd": scale_ports['ssh_end'], "backendPort": 22 } }, { "name": "mgmtnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPortRangeStart":  scale_ports['https_start'], "frontendPortRangeEnd": scale_ports['https_end'], "backendPort": "[variables('bigIpMgmtPort')]" } } ]
    inbound_nat_pools = inbound_nat_pools + inbound_nat_pools_static
    lb_def = { "apiVersion": network_api_version, "name": "[variables('externalLoadBalancerName')]", "type": "Microsoft.Network/loadBalancers", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'))]" ], "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('mgmtPublicIPAddressId')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ], "inboundNatPools": inbound_nat_pools, "loadBalancingRules": lb_rules_to_use, "probes": probes_to_use } }
    if license_type == 'bigiq-payg':
        lb_def['sku'] = { "name": "Standard" }
    resources_list += [lb_def]

###### Load Balancer Inbound NAT Rule(s) ######
if template_name == 'failover-lb_1nic':
    resources_list += [{ "apiVersion": network_api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('externalLoadBalancerName'),'/guimgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPort": "[copyIndex(8443)]", "backendPort": "[variables('bigIpMgmtPort')]", "enableFloatingIP": False } }]
    resources_list += [{ "apiVersion": network_api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('externalLoadBalancerName'),'/sshmgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "Tcp", "frontendPort": "[copyIndex(8022)]", "backendPort": 22, "enableFloatingIP": False } }]

######## Availability Set Resource(s) ######
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-api', 'failover-lb_1nic', 'failover-lb_3nic'):
    avset = { "apiVersion": compute_api_version, "location": location, "name": "[variables('availabilitySetName')]", "tags": tags, "properties": { "PlatformUpdateDomainCount": 2, "PlatformFaultDomainCount": 2 }, "type": "Microsoft.Compute/availabilitySets" }
    # Only required for managed disks
    if environment == 'azure':
        avset['sku'] = { "name": "Aligned" }
    if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
        if stack_type in ('existing-stack', 'production-stack'):
            avset['condition'] = "[equals(toUpper(parameters('avSetChoice')), 'CREATE_NEW')]"
    resources_list += [avset]

###### Storage Account Resource(s) ######
resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "kind": "Storage", "location": location, "name": "[variables('newDataStorageAccountName')]", "tags": tags, "sku": { "name": "[variables('dataStorageAccountType')]", "tier": "Standard" }, "properties": {"supportsHttpsTrafficOnly": True} }]

###### Compute/image Resource(s) ######
if environment == 'azure':
    resources_list += [{"type": "Microsoft.Compute/images", "apiVersion": compute_api_version, "name": "[variables('newCustomImageName')]", "condition": "[and(variables('useCustomImage'), variables('createNewCustomImage'))]", "location": location, "tags": tags, "properties": {"storageProfile": {"osDisk": {"blobUri": "[variables('customImage')]", "osState": "Generalized", "osType": "Linux", "storageAccountType": "[if(contains(variables('premiumInstanceArray'), parameters('instanceType')), 'Premium_LRS', 'Standard_LRS')]"}}}}]

###### Compute/VM Resource(s) ######
depends_on = ["[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]"]
if environment == 'azure':
    depends_on.append("[variables('newCustomImageName')]")

if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'))]")
if template_name == 'standalone_1nic':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }]
if template_name in ('standalone_2nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]")
if template_name in ('standalone_3nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('intNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]")
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]")
if template_name in ('standalone_n-nic'):
    nic_reference = "[concat(take(variables('selfNicConfigArray'), 3), take(variables('addtlNicConfigArray').values, parameters('numberOfAdditionalNics')))]"
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]")
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]")
    depends_on.append("addtlniccopy")
if template_name in ('failover-lb_1nic'):
    nic_reference = [{ "id": "[concat(resourceId('Microsoft.Network/networkInterfaces',variables('mgmtNicName')),copyindex())]" }]
if template_name in ('failover-lb_3nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('mgmtNicName'), '0'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('extNicName'), '0'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('intNicName'), '0'))]", "properties": { "primary": False } }]
    nic_reference_2 = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('mgmtNicName'), '1'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('extNicName'), '1'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('intNicName'), '1'))]", "properties": { "primary": False } }]
if template_name in ('failover-api'):
    nic_reference = "[concat(take(variables('selfNicConfigArray')['0'], 3), take(variables('addtlNicConfigArray')['values0'], parameters('numberOfAdditionalNics')))]"
    nic_reference_2 = "[concat(take(variables('selfNicConfigArray')['1'], 3), take(variables('addtlNicConfigArray')['values1'], parameters('numberOfAdditionalNics')))]"
    depends_on.append("addtlniccopy0")
    depends_on.append("addtlniccopy1")

if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
    plan = "[if(variables('useCustomImage'), json('null'), variables('imagePlan'))]"
    storageProfile = "[if(variables('useCustomImage'), variables('storageProfileArray').customImage, variables('storageProfileArray').platformImage)]"
    # No managed disk support for Azure Stack yet
    if environment == 'azurestack':
        storageProfile = {"imageReference": "[if(variables('useCustomImage'), json('null'), variables('imageReference'))]", "osDisk": {"image": "[if(variables('useCustomImage'), variables('customImageReference'), json('null'))]", "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "osType": "Linux", "vhd": {"uri": "[if(variables('useCustomImage'), concat(variables('customImage'), '-', variables('instanceName'), '.vhd'), concat(reference(concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob, 'osdisks/', variables('instanceName'), '.vhd'))]"}}}
    resources_list += [{"apiVersion": compute_api_version, "type": "Microsoft.Compute/virtualMachines", "dependsOn": depends_on, "location": location, "name": "[variables('instanceName')]", "tags": tags, "plan": plan, "properties": { "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[reference(concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  nic_reference }, "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "osProfile": "[variables('osProfiles')[parameters('authenticationType')]]", "storageProfile": storageProfile }}]
if template_name == 'failover-lb_1nic':
    resources_list += [{ "apiVersion": compute_api_version, "type": "Microsoft.Compute/virtualMachines", "name": "[concat(variables('deviceNamePrefix'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), copyindex())]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "devicecopy" }, "plan": "[if(variables('useCustomImage'), json('null'), variables('imagePlan'))]", "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "osProfile": "[variables('osProfiles')[parameters('authenticationType')]]", "storageProfile": "[if(variables('useCustomImage'), variables('storageProfileArray').customImage, variables('storageProfileArray').platformImage)]", "networkProfile": { "networkInterfaces": nic_reference }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[reference(concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob]" } } } }]
if template_name in ('failover-api', 'failover-lb_3nic'):
    resources_list += [{ "apiVersion": compute_api_version, "dependsOn": depends_on + ["[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), '0')]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'), '0')]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'), '0')]"], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '0')]", "plan": "[if(variables('useCustomImage'), json('null'), variables('imagePlan'))]", "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('availabilitySetName'))]" }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[reference(concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces": nic_reference }, "osProfile": "[variables('osProfiles')[parameters('authenticationType')]]", "storageProfile": "[if(variables('useCustomImage'), variables('storageProfileArray').customImage, variables('storageProfileArray').platformImage)]" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines" }]
    resources_list += [{ "apiVersion": compute_api_version, "dependsOn": depends_on + ["[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), '1')]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'), '1')]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'), '1')]"], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '1')]", "plan": "[if(variables('useCustomImage'), json('null'), variables('imagePlan'))]", "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('availabilitySetName'))]" }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[reference(concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName')), providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).primaryEndpoints.blob]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces": nic_reference_2 }, "osProfile": "[variables('osProfiles')[parameters('authenticationType')]]", "storageProfile": "[if(variables('useCustomImage'), variables('storageProfileArray').customImage, variables('storageProfileArray').platformImage)]" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines" }]

# Add learning stack VM(s)
if learningStack:
   resources_list += [{"apiVersion": compute_api_version, "type": "Microsoft.Compute/virtualMachines", "dependsOn": ["[concat('Microsoft.Network/networkInterfaces/', variables('webVmName'), '-nic')]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]"], "location": location, "name": "[variables('webVmName')]", "tags": tags, "properties": { "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('webVmName'), '-nic'))]" }] }, "osProfile": "[variables('osProfiles')[parameters('authenticationType')]]", "storageProfile": { "imageReference": {"offer": "UbuntuServer", "publisher": "Canonical", "sku": "16.04.0-LTS", "version": "latest"}, "osDisk": {"createOption": "FromImage"}} } }]
###### Compute/VM Extension Resource(s) ######
command_to_execute = ''; command_to_execute2 = ''; post_cmd_to_execute = ''; post_cmd_to_execute2 = ''; route_add_cmd = ''; default_gw_cmd = "variables('tmmRouteGw')"

if template_name in ('standalone_1nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '.', variables('location'), '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('standalone_2nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '.', variables('location'), '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --wait-for ONBOARD_DONE --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --log-level info'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('standalone_3nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '.', variables('location'), '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --wait-for ONBOARD_DONE --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal --log-level info'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('standalone_n-nic'):
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '.', variables('location'), '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --wait-for ONBOARD_DONE --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal ', variables('netCmd'), ' --log-level info'<POST_CMD_TO_EXECUTE>)]"
if template_name in ('failover-lb_1nic'):
    # Two Extensions for failover-lb_1nic
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/cluster.js --output /var/log/cloud/azure/cluster.log --log-level info --host ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), ' --auto-sync --save-on-auto-sync; bash /config/cloud/deploy_app.sh ', variables('commandArgs')<POST_CMD_TO_EXECUTE>)]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix1')), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('deviceNamePrefix'), copyindex(1), '.azuresecurity.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/cluster.js --output /var/log/cloud/azure/cluster.log --log-level info --host ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix1')), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix1')), ' --join-group --device-group Sync --sync --remote-host ', concat(variables('mgmtSubnetPrivateAddress'), variables('mgmtSubnetPrivateAddressSuffix')), ' --remote-user svc_user --remote-password-url file:///config/cloud/.passwd'<POST_CMD_TO_EXECUTE2>)]"
if template_name in ('failover-api'):
    # Two Extensions for failover-api
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '0.', variables('location'), '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --wait-for ONBOARD_DONE --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 ', variables('netCmd'), ' --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal --log-level info; echo \"/usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs-azure/scripts/failoverProvider.js\" >> /config/failover/tgactive; echo \"/usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs-azure/scripts/failoverProvider.js\" >> /config/failover/tgrefresh; tmsh modify cm device ', concat(variables('instanceName'), '0.', variables('location'), '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress'), '; ', variables('failoverCmdArray')[parameters('bigIpVersion')], '; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/cluster.js --wait-for NETWORK_DONE --output /var/log/cloud/azure/cluster.log --log-level info --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', variables('intSubnetPrivateAddress'), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('instanceName'), '0.', variables('location'), '.cloudapp.azure.com'), ' --network-failover --auto-sync --save-on-auto-sync; bash /config/cloud/deploy_app.sh ', variables('commandArgs')<POST_CMD_TO_EXECUTE>)]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '1.', variables('location'), '.cloudapp.azure.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --wait-for ONBOARD_DONE --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 ', variables('netCmd'), ' --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress1'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress1'), <INT_MASK_CMD> ',vlan:internal --log-level info; echo \"/usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs-azure/scripts/failoverProvider.js\" >> /config/failover/tgactive; echo \"/usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs-azure/scripts/failoverProvider.js\" >> /config/failover/tgrefresh; tmsh modify cm device ', concat(variables('instanceName'), '1.', variables('location'), '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress1'), ' port 1026 } } mirror-ip ', variables('intSubnetPrivateAddress1'), '; ', variables('failoverCmdArray')[parameters('bigIpVersion')], '; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/cluster.js --wait-for NETWORK_DONE --output /var/log/cloud/azure/cluster.log --log-level info --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', variables('intSubnetPrivateAddress1'), ' --join-group --device-group Sync --sync --remote-host ', variables('mgmtSubnetPrivateAddress'), ' --remote-user svc_user --remote-password-url file:///config/cloud/.passwd'<POST_CMD_TO_EXECUTE2>)]"
if template_name in ('failover-lb_3nic'):
    # Two Extensions for failover-lb_3nic
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '0.', variables('location'), '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --wait-for ONBOARD_DONE --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), <INT_MASK_CMD> ',vlan:internal --log-level info; ', variables('failoverCmdArray')[parameters('enableNetworkFailover')].first, '; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/cluster.js --wait-for NETWORK_DONE --output /var/log/cloud/azure/cluster.log --log-level info --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', variables('intSubnetPrivateAddress'), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('instanceName'), '0.', variables('location'), '.cloudapp.azure.com'), ' --network-failover --auto-sync --save-on-auto-sync; bash /config/cloud/deploy_app.sh ', variables('commandArgs')<POST_CMD_TO_EXECUTE>)]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --hostname ', concat(variables('instanceName'), '1.', variables('location'), '.cloudapp.azure.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048<ANALYTICS_CMD> --module ltm:nominal; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/network.js --output /var/log/cloud/azure/network.log --wait-for ONBOARD_DONE --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --default-gw ', <DFL_GW_CMD>, ' --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress1'), <EXT_MASK_CMD> ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress1'), <INT_MASK_CMD> ',vlan:internal --log-level info; ', variables('failoverCmdArray')[parameters('enableNetworkFailover')].second, '; /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/cluster.js --wait-for NETWORK_DONE --output /var/log/cloud/azure/cluster.log --log-level info --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u svc_user --password-url file:///config/cloud/.passwd --password-encrypted --config-sync-ip ', variables('intSubnetPrivateAddress1'), ' --join-group --device-group Sync --sync --remote-host ', variables('mgmtSubnetPrivateAddress'), ' --remote-user svc_user --remote-password-url file:///config/cloud/.passwd'<POST_CMD_TO_EXECUTE2>)]"

## Base Start/Post Command to Execute
base_cmd_to_execute = "'function cp_logs() { cd /var/lib/waagent/custom-script/download && cp `ls -r | head -1`/std* /var/log/cloud/azure; cd /var/log/cloud/azure && cat stdout stderr > install.log; }; CLOUD_LIB_DIR=/config/cloud/azure/node_modules/@f5devcentral; mkdir -p $CLOUD_LIB_DIR && cp f5-cloud-libs.tar.gz* /config/cloud; mkdir -p /var/config/rest/downloads && cp ', variables('f5AS3Build'), ' /var/config/rest/downloads; mkdir -p /var/log/cloud/azure; /usr/bin/install -m 400 /dev/null /config/cloud/.passwd; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', variables('appScript'), ' | /usr/bin/base64 -d > /config/cloud/deploy_app.sh; chmod +x /config/cloud/deploy_app.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh; unset IFS; bash /config/installCloudLibs.sh; source $CLOUD_LIB_DIR/f5-cloud-libs/scripts/util.sh; encrypt_secret ', variables('singleQuote'), variables('adminPasswordOrKey'), variables('singleQuote'), ' \"/config/cloud/.passwd\" true; $CLOUD_LIB_DIR/f5-cloud-libs/scripts/createUser.sh --user svc_user --password-file /config/cloud/.passwd --password-encrypted;<BIGIQ_PWD_CMD><ANALYTICS_HASH> /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/onboard.js --no-reboot --output /var/log/cloud/azure/onboard.log --signal ONBOARD_DONE --log-level info --cloud azure --install-ilx-package file:///var/config/rest/downloads/', variables('f5AS3Build'), ' --host '"
waagent_restart_cmd = ", '; if grep -i \"PUT failed\" /var/log/waagent.log -q; then echo \"Killing waagent exthandler, daemon should restart it\"; pkill -f \"python -u /usr/sbin/waagent -run-exthandlers\"; fi'"

post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl;<ROUTE_ADD_CMD><BIGIQ_PWD_DELETE> bash /config/cloud/deploy_app.sh ', variables('commandArgs'), ' ; bash /config/customConfig.sh; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd

if template_name in 'failover-api':
    base_cmd_to_execute = "'function cp_logs() { cd /var/lib/waagent/custom-script/download && cp `ls -r | head -1`/std* /var/log/cloud/azure; cd /var/log/cloud/azure && cat stdout stderr > install.log; }; CLOUD_LIB_DIR=/config/cloud/azure/node_modules/@f5devcentral; mkdir -p $CLOUD_LIB_DIR && cp f5-cloud-libs*.tar.gz* /config/cloud; mkdir -p /var/config/rest/downloads && cp ', variables('f5AS3Build'), ' /var/config/rest/downloads; mkdir -p /var/log/cloud/azure; /usr/bin/install -m 400 /dev/null /config/cloud/.passwd; /usr/bin/install -m 400 /dev/null /config/cloud/.azCredentials; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 755 /dev/null /config/cloud/managedRoutes; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' > /config/verifyHash; echo -e ', variables('installCloudLibs'), ' > /config/installCloudLibs.sh; echo -e ', variables('appScript'), ' | /usr/bin/base64 -d > /config/cloud/deploy_app.sh; chmod +x /config/cloud/deploy_app.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh; echo -e ', parameters('managedRoutes'), ' > /config/cloud/managedRoutes; unset IFS; bash /config/installCloudLibs.sh; source $CLOUD_LIB_DIR/f5-cloud-libs/scripts/util.sh; encrypt_secret ', variables('singleQuote'), '{\"clientId\": \"', parameters('clientId'), '\", \"tenantId\": \"', parameters('tenantId'), '\", \"secret\": \"', parameters('servicePrincipalSecret'), '\", \"subscriptionId\": \"', variables('subscriptionID'), '\", \"storageAccount\": \"', variables('newDataStorageAccountName'), '\", \"storageKey\": \"', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('newDataStorageAccountName')), variables('storageApiVersion')).keys[0].value, '\", \"resourceGroupName\": \"', variables('resourceGroupName'), '\", \"uniqueLabel\": \"', variables('dnsLabel'), '\", \"location\": \"', variables('location'), '\"}', variables('singleQuote'), ' \"/config/cloud/.azCredentials\" \"\" true; encrypt_secret ', variables('singleQuote'), variables('adminPasswordOrKey'), variables('singleQuote'), ' \"/config/cloud/.passwd\" true; $CLOUD_LIB_DIR/f5-cloud-libs/scripts/createUser.sh --user svc_user --password-file /config/cloud/.passwd --password-encrypted;<BIGIQ_PWD_CMD><ANALYTICS_HASH> /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/onboard.js --no-reboot --output /var/log/cloud/azure/onboard.log --signal ONBOARD_DONE --log-level info --cloud azure --install-ilx-package file:///var/config/rest/downloads/', variables('f5AS3Build'), ' --host '"

    #post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl;<ROUTE_ADD_CMD><BIGIQ_PWD_DELETE> $(nohup bash /config/failover/tgactive &>/dev/null &); bash /config/customConfig.sh; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd

    post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl; base=', variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffixInt'), '; f3=$(echo $base | cut -d. -f1-3); last=$(echo $base | cut -d. -f4); for i in $(seq 1 ', variables('numberOfExternalIps'), '); do addr=${f3}.${last}; last=$((last+1)); tmsh create ltm virtual-address $addr address $addr; done;<ROUTE_ADD_CMD><BIGIQ_PWD_DELETE> $(nohup bash /config/failover/tgactive &>/dev/null &); bash /config/customConfig.sh; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd

if template_name in ('failover-lb_1nic', 'failover-lb_3nic'):
    base_cmd_to_execute = "'function cp_logs() { cd /var/lib/waagent/custom-script/download && cp `ls -r | head -1`/std* /var/log/cloud/azure; cd /var/log/cloud/azure && cat stdout stderr > install.log; }; CLOUD_LIB_DIR=/config/cloud/azure/node_modules/@f5devcentral; mkdir -p $CLOUD_LIB_DIR && cp f5-cloud-libs.tar.gz* /config/cloud; mkdir -p /var/config/rest/downloads && cp ', variables('f5AS3Build'), ' /var/config/rest/downloads; mkdir -p /var/log/cloud/azure; /usr/bin/install -m 400 /dev/null /config/cloud/.passwd; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', variables('appScript'), ' | /usr/bin/base64 -d > /config/cloud/deploy_app.sh; chmod +x /config/cloud/deploy_app.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh; unset IFS; bash /config/installCloudLibs.sh; source $CLOUD_LIB_DIR/f5-cloud-libs/scripts/util.sh; encrypt_secret ', variables('singleQuote'), variables('adminPasswordOrKey'), variables('singleQuote'), ' \"/config/cloud/.passwd\" true; $CLOUD_LIB_DIR/f5-cloud-libs/scripts/createUser.sh --user svc_user --password-file /config/cloud/.passwd --password-encrypted;<BIGIQ_PWD_CMD><ANALYTICS_HASH> /usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/onboard.js --no-reboot --output /var/log/cloud/azure/onboard.log --signal ONBOARD_DONE --log-level info --cloud azure --install-ilx-package file:///var/config/rest/downloads/', variables('f5AS3Build'), ' --host '"
    waagent_restart_cmd = ", '; if grep -i \"PUT failed\" /var/log/waagent.log -q; then echo \"Killing waagent exthandler, daemon should restart it\"; pkill -f \"python -u /usr/sbin/waagent -run-exthandlers\"; fi'"

    post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl;<ROUTE_ADD_CMD><BIGIQ_PWD_DELETE> bash /config/customConfig.sh; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd

# Link-local route command, for 2+ nic templates
if template_name in ('standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_3nic', 'failover-api'):
    route_add_cmd = " ', variables('routeCmdArray')[parameters('bigIpVersion')], ';"
# Default GW command is different for existing-stack
if stack_type in ('existing-stack', 'production-stack'):
    default_gw_cmd = "concat(take(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, add(lastIndexOf(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, '.'), 1)), add(int(take(split(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, '.')[3], indexOf(split(reference(variables('extSubnetRef'), variables('networkApiVersion')).addressPrefix, '.')[3], '/'))), 1))"

## Map in some commandToExecute Elements
post_cmd_to_execute = post_cmd_to_execute.replace('<BIGIQ_PWD_DELETE>', bigiq_pwd_delete)
post_cmd_to_execute = post_cmd_to_execute.replace('<ROUTE_ADD_CMD>', route_add_cmd)

command_to_execute = command_to_execute.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute).replace('<POST_CMD_TO_EXECUTE>', post_cmd_to_execute)
command_to_execute2 = command_to_execute2.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute).replace('<POST_CMD_TO_EXECUTE2>', post_cmd_to_execute)
command_to_execute = command_to_execute.replace('<EXT_MASK_CMD>', ext_mask_cmd).replace('<INT_MASK_CMD>', int_mask_cmd).replace('<DFL_GW_CMD>', default_gw_cmd)
command_to_execute2 = command_to_execute2.replace('<EXT_MASK_CMD>', ext_mask_cmd).replace('<INT_MASK_CMD>', int_mask_cmd).replace('<DFL_GW_CMD>', default_gw_cmd)
command_to_execute = command_to_execute.replace('<LICENSE1_COMMAND>', license1_command)
command_to_execute2 = command_to_execute2.replace('<LICENSE2_COMMAND>', license2_command)
command_to_execute = command_to_execute.replace('<BIGIQ_PWD_CMD>', big_iq_pwd_cmd)
command_to_execute2 = command_to_execute2.replace('<BIGIQ_PWD_CMD>', big_iq_pwd_cmd)

# Add Usage Analytics Hash and Metrics Command
metrics_hash_to_exec = "', variables('allowUsageAnalytics')[parameters('allowUsageAnalytics')].hashCmd, ';"
metrics_cmd_to_exec = "', variables('allowUsageAnalytics')[parameters('allowUsageAnalytics')].metricsCmd, '"
command_to_execute = command_to_execute.replace('<ANALYTICS_HASH>', metrics_hash_to_exec).replace('<ANALYTICS_CMD>', metrics_cmd_to_exec)
command_to_execute2 = command_to_execute2.replace('<ANALYTICS_HASH>', metrics_hash_to_exec).replace('<ANALYTICS_CMD>', metrics_cmd_to_exec)


## Define base file(s) to download
file_uris = [ "[concat('https://cdn.f5.com/product/cloudsolutions/f5-cloud-libs/', variables('f5CloudLibsTag'), '/f5-cloud-libs.tar.gz')]", "[concat('https://cdn.f5.com/product/cloudsolutions/f5-appsvcs-extension/', variables('f5AS3Tag'), '/dist/lts/', variables('f5AS3Build'))]", "[concat('https://cdn.f5.com/product/cloudsolutions/iapps/common/f5-service-discovery/', variables('f5CloudIappsSdTag'), '/f5.service_discovery.tmpl')]", "[concat('https://cdn.f5.com/product/cloudsolutions/iapps/common/f5-cloud-logger/', variables('f5CloudIappsLoggerTag'), '/f5.cloud_logger.v1.0.0.tmpl')]" ]

## Define command to execute(s)
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
    resources_list += [{"apiVersion": "[variables('computeApiVersion')]", "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('instanceName'),'/start')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('instanceName'))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": file_uris }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
if template_name == 'failover-lb_1nic':
    # Two Extensions for failover-lb_1nic
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('deviceNamePrefix'),0,'/start')]", "apiVersion": "[variables('computeApiVersion')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),0)]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": file_uris }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "copy": { "name": "extensionLoop", "count": "[sub(parameters('numberOfInstances'), 1)]" }, "name": "[concat(variables('deviceNamePrefix'),add(copyindex(),1),'/start')]", "apiVersion": "[variables('computeApiVersion')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),add(copyindex(),1))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": file_uris }, "protectedSettings": { "commandToExecute": command_to_execute2 } } }]
if template_name in ('failover-api', 'failover-lb_3nic'):
    if template_name in ('failover-api'):
        file_uris += ["[concat('https://cdn.f5.com/product/cloudsolutions/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/f5-cloud-libs-azure.tar.gz')]"]
    # Two Extensions for failover-api and failover-lb_3nic
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('dnsLabel'), '-', variables('instanceName'), '0')]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '0/start')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": file_uris }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('dnsLabel'), '-', variables('instanceName'), '1')]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '1/start')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute2 }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": file_uris }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]

# Add learning stack Custom Script Extension(s)
if learningStack:
    file_uris = ["[concat('https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/', variables('f5NetworksTag'), '/experimental/reference/learning-stack/scripts/init_web.sh')]"]
    command_to_execute = "[concat('./init_web.sh ', variables('f5NetworksTag'))]"
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('webVmName'))]" ], "location": location, "name": "[concat(variables('webVmName'), '/webstart')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": file_uris }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]

###### Compute VM Scale Set(s) ######
autoscale_file_uris = ["[concat('https://cdn.f5.com/product/cloudsolutions/f5-cloud-libs/', variables('f5CloudLibsTag'), '/f5-cloud-libs.tar.gz')]", "[concat('https://cdn.f5.com/product/cloudsolutions/f5-appsvcs-extension/', variables('f5AS3Tag'), '/dist/lts/', variables('f5AS3Build'))]", "[concat('https://cdn.f5.com/product/cloudsolutions/iapps/common/f5-service-discovery/', variables('f5CloudIappsSdTag'), '/f5.service_discovery.tmpl')]", "[concat('https://cdn.f5.com/product/cloudsolutions/iapps/common/f5-cloud-logger/', variables('f5CloudIappsLoggerTag'), '/f5.cloud_logger.v1.0.0.tmpl')]", "[concat('https://cdn.f5.com/product/cloudsolutions/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/f5-cloud-libs-azure.tar.gz')]"]
addtl_setup = ""
addtl_encrypt_calls = ""
addtl_script_args = ""
if template_name in ('as_ltm_dns', 'as_waf_dns'):
    addtl_encrypt_calls = " /usr/bin/install -m 400 /dev/null /config/cloud/.dnsPasswd; encrypt_secret ', variables('singleQuote'), parameters('dnsProviderPassword'), variables('singleQuote'), ' \"/config/cloud/.dnsPasswd\";"
    addtl_script_args += ", ' --dnsOptions \\\"--dns gtm --dns-ip-type ', parameters('dnsMemberIpType'), ' --dns-app-port ', parameters('dnsMemberPort'), ' --dns-provider-options host:', parameters('dnsProviderHost'), ',port:', parameters('dnsProviderPort'), ',user:', parameters('dnsProviderUser'), ',passwordUrl:file:///config/cloud/.dnsPasswd,passwordEncrypted:true,serverName:', variables('vmssName'), ',poolName:', parameters('dnsProviderPool'), ',datacenter:', parameters('dnsProviderDataCenter'), '\\\"'"
if template_name in ('as_waf_lb', 'as_waf_dns'):
    addtl_setup += "cp asm-policy.tar.gz *.tmpl /config/cloud; tar xfz /config/cloud/asm-policy.tar.gz -C /config/cloud; echo ', variables('appScript'), ' | /usr/bin/base64 -d > /config/cloud/deploy_app.sh; chmod +x /config/cloud/deploy_app.sh; "
    addtl_script_args += ", ' --wafScriptArgs \\\"', variables('commandArgs'), '\\\"'"
    autoscale_file_uris += ["[concat(variables('f5NetworksSolutionScripts'), 'asm-policy.tar.gz')]"]
if template_name in ('as_ltm_lb', 'as_ltm_dns'):
    addtl_setup += "echo ', variables('appScript'), ' | /usr/bin/base64 -d > /config/cloud/deploy_app.sh; chmod +x /config/cloud/deploy_app.sh; "
    addtl_script_args += ", ' --wafScriptArgs \\\"', variables('commandArgs'), '\\\"'"

if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    # Add TMM CPU metric option into autoscale templates - pass key into autoscale.sh
    addtl_script_args += ", ' --appInsightsKey ', reference(resourceId(variables('appInsightsNameArray')[1], 'Microsoft.Insights/components', variables('appInsightsNameArray')[0]), variables('appInsightsComponentsApiVersion')).InstrumentationKey"
    if template_name in ('as_waf_lb', 'as_waf_dns'):
        post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh modify cm device-group Sync asm-sync enabled; tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl;<BIGIQ_PWD_DELETE> bash /config/customConfig.sh; reboot_signal=\"/tmp/f5-cloud-libs-signals/REBOOT_REQUIRED\"; if [ -f $reboot_signal ]; then echo \"Reboot signaled by cloud libs, rebooting\"; rm -f $reboot_signal; reboot; else echo \"Cloud libs did not signal a reboot\"; fi; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd
    else:
        post_cmd_to_execute = ", '; if [[ $? == 0 ]]; then tmsh load sys application template f5.service_discovery.tmpl; tmsh load sys application template f5.cloud_logger.v1.0.0.tmpl;<BIGIQ_PWD_DELETE> bash /config/customConfig.sh; reboot_signal=\"/tmp/f5-cloud-libs-signals/REBOOT_REQUIRED\"; if [ -f $reboot_signal ]; then echo \"Reboot signaled by cloud libs, rebooting\"; rm -f $reboot_signal; reboot; else echo \"Cloud libs did not signal a reboot\"; fi; $(cp_logs); else $(cp_logs); exit 1; fi'" + waagent_restart_cmd
    autoscale_command_to_execute = "[concat('function cp_logs() { cd /var/lib/waagent/custom-script/download && cp `ls -r | head -1`/std* /var/log/cloud/azure; cd /var/log/cloud/azure && cat stdout stderr > install.log; }; CLOUD_LIB_DIR=/config/cloud/azure/node_modules/@f5devcentral; mkdir -p $CLOUD_LIB_DIR; mkdir -p /var/log/cloud/azure; <ADDTL_SETUP>/usr/bin/install -m 400 /dev/null /config/cloud/.passwd; /usr/bin/install -m 400 /dev/null /config/cloud/.azCredentials; cp f5-cloud-libs*.tar.gz* /config/cloud; mkdir -p /var/config/rest/downloads && cp ', variables('f5AS3Build'), ' /var/config/rest/downloads; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo -e ', variables('installCustomConfig'), ' >> /config/customConfig.sh; bash /config/installCloudLibs.sh; source $CLOUD_LIB_DIR/f5-cloud-libs/scripts/util.sh; encrypt_secret ', variables('singleQuote'), '{\"clientId\": \"', parameters('clientId'), '\", \"tenantId\": \"', parameters('tenantId'), '\", \"secret\": \"', parameters('servicePrincipalSecret'), '\", \"subscriptionId\": \"', variables('subscriptionID'), '\", \"storageAccount\": \"', variables('newDataStorageAccountName'), '\", \"storageKey\": \"', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('newDataStorageAccountName')), variables('storageApiVersion')).keys[0].value, '\", \"vmssName\": \"', variables('vmssName'), '\", \"resourceGroupName\": \"', variables('resourceGroupName'), '\", \"loadBalancerName\": \"', variables('externalLoadBalancerName'), '\", \"appInsightsName\": \"', variables('appInsightsName'), '\", \"appInsightsId\": \"', reference(resourceId(variables('appInsightsNameArray')[1], 'Microsoft.Insights/components', variables('appInsightsNameArray')[0]), variables('appInsightsComponentsApiVersion')).AppId, '\", \"location\": \"', variables('location'), '\"}', variables('singleQuote'), ' \"/config/cloud/.azCredentials\" \"\" true; encrypt_secret ', variables('singleQuote'), variables('adminPasswordOrKey'), variables('singleQuote'), ' \"/config/cloud/.passwd\" true; $CLOUD_LIB_DIR/f5-cloud-libs/scripts/createUser.sh --user svc_user --password-file /config/cloud/.passwd --password-encrypted;<BIGIQ_PWD_CMD><ADDTL_ENCRYPT_CALLS> ', variables('allowUsageAnalytics')[parameters('allowUsageAnalytics')].hashCmd, '; <SCALE_SCRIPT_CALL><POST_CMD_TO_EXECUTE>)]"
    scale_script_call = "/usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/runScript.js --output /var/log/cloud/azure/autoscale.log --log-level info --file $CLOUD_LIB_DIR/f5-cloud-libs-azure/scripts/autoscale.sh --shell /bin/bash --cl-args \"--logLevel info --backupUcs 7 --resourceGroup ', resourceGroup().name, ' --vmssName ', variables('vmssName'), ' --userName svc_user --password /config/cloud/.passwd --azureSecretFile /config/cloud/.azCredentials --managementPort ', variables('bigIpMgmtPort'), ' --ntpServer ', parameters('ntpServer'), ' --as3Build ', variables('f5AS3Build'), ' --timeZone ', parameters('timeZone'), variables('allowUsageAnalytics')[parameters('allowUsageAnalytics')].metricsCmd<ADDTL_SCRIPT_ARGS>"
    scale_script_call = scale_script_call.replace('<ADDTL_SCRIPT_ARGS>', addtl_script_args)
    # Add licensing (big-iq)
    if license_type == 'bigiq-payg':
        static_scale_script_call = scale_script_call + static_license1_command + ", '\" --signal AUTOSCALE_SCRIPT_DONE'"
    scale_script_call = scale_script_call + license1_command + ", '\" --signal AUTOSCALE_SCRIPT_DONE'"

    # Map in dynamic items
    post_cmd_to_execute = post_cmd_to_execute.replace('<BIGIQ_PWD_DELETE>', bigiq_pwd_delete)
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<ADDTL_SETUP>', addtl_setup).replace('<BIGIQ_PWD_CMD>', big_iq_pwd_cmd)
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<POST_CMD_TO_EXECUTE>', post_cmd_to_execute)
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<ADDTL_ENCRYPT_CALLS>', addtl_encrypt_calls)
    # Modified command to execute for static VMSS
    if license_type == 'bigiq-payg':
        static_autoscale_command_to_execute = autoscale_command_to_execute.replace('<SCALE_SCRIPT_CALL>', static_scale_script_call)
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<SCALE_SCRIPT_CALL>', scale_script_call)

if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    lb_inbound_nat_pools = [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/inboundNatPools/sshnatpool')]" }, { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/inboundNatPools/mgmtnatpool')]" } ]
    if template_name in ('as_ltm_lb', 'as_waf_lb'):
        ipConfigProperties = { "subnet": { "id": "[variables('mgmtSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/backendAddressPools/loadBalancerBackEnd')]" } ], "loadBalancerInboundNatPools": lb_inbound_nat_pools, "publicIpAddressConfiguration": "[if(equals(toLower(parameters('enableMgmtPublicIp')), 'no'), json('null'), variables('publicIpAddressConfiguration'))]" }
    elif template_name in ('as_ltm_dns', 'as_waf_dns'):
        ipConfigProperties = { "subnet": { "id": "[variables('mgmtSubnetId')]" }, "publicIpAddressConfiguration": "[variables('publicIpAddressConfiguration')]" }
    resources_list += [{ "type": "Microsoft.Compute/virtualMachineScaleSets", "apiVersion": compute_api_version, "name": "[variables('vmssName')]", "location": location, "tags": tags, "dependsOn": scale_depends_on, "sku": { "name": "[parameters('instanceType')]", "tier": "Standard", "capacity": "[parameters('vmScaleSetMinCount')]" }, "plan": "[if(variables('useCustomImage'), json('null'), variables('imagePlan'))]", "properties": { "upgradePolicy": { "mode": "Manual" }, "virtualMachineProfile": { "storageProfile": "[if(variables('useCustomImage'), variables('storageProfileArray').customImage, variables('storageProfileArray').platformImage)]", "osProfile": "[variables('osProfiles')[parameters('authenticationType')]]", "networkProfile": { "networkInterfaceConfigurations": [ { "name": "nic1", "properties": { "primary": True, "networkSecurityGroup": {"id": "[variables('mgmtNsgID')]"}, "ipConfigurations": [ { "name": "ipconfig1", "properties": ipConfigProperties } ] } } ] }, "extensionProfile": { "extensions": [ { "name":"main", "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": autoscale_file_uris }, "protectedSettings": { "commandToExecute": autoscale_command_to_execute } } } ] } }, "overprovision": False } }]
    if license_type == 'bigiq-payg':
        # Static VMSS
        lb_inbound_nat_pools = [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/inboundNatPools/sshnatpool-static')]" }, { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/inboundNatPools/mgmtnatpool-static')]" } ]
        ipConfigProperties = { "subnet": { "id": "[variables('mgmtSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('externalLoadBalancerName'), '/backendAddressPools/loadBalancerBackEnd')]" } ], "loadBalancerInboundNatPools": lb_inbound_nat_pools }
        resources_list += [{ "type": "Microsoft.Compute/virtualMachineScaleSets", "apiVersion": compute_api_version, "name": "[variables('staticVmssName')]", "location": location, "tags": static_vmss_tags, "dependsOn": scale_depends_on, "sku": { "name": "[parameters('instanceType')]", "tier": "Standard", "capacity": "[parameters('numberOfStaticInstances')]" }, "plan": "[if(variables('useCustomImage'), json('null'), variables('staticImagePlan'))]", "properties": { "upgradePolicy": { "mode": "Manual" }, "virtualMachineProfile": { "storageProfile": "[if(variables('useCustomImage'), variables('staticStorageProfileArray').customImage, variables('staticStorageProfileArray').platformImage)]", "osProfile": { "computerNamePrefix": "[variables('vmssName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[variables('adminPasswordOrKey')]", "linuxConfiguration": "[if(equals(parameters('authenticationType'), 'password'), json('null'), variables('linuxConfiguration'))]" }, "networkProfile": { "networkInterfaceConfigurations": [ { "name": "nic1", "properties": { "primary": True, "networkSecurityGroup": {"id": "[variables('mgmtNsgID')]"}, "ipConfigurations": [ { "name": "ipconfig1", "properties": ipConfigProperties } ] } } ] }, "extensionProfile": { "extensions": [ { "name":"main", "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": autoscale_file_uris }, "protectedSettings": { "commandToExecute": static_autoscale_command_to_execute } } } ] } }, "overprovision": False } }]

###### Compute VM Scale Set(s) AutoScale Settings ######
if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    depends_on = ["[variables('vmssId')]"]
    if license_type == 'bigiq-payg':
        depends_on.append("[variables('staticVmssId')]")
    resources_list += [{ "type": "Microsoft.Insights/autoscaleSettings", "apiVersion": "[variables('appInsightsApiVersion')]", "name": "autoscaleconfig", "location": location, "dependsOn": depends_on, "properties": { "name": "autoscaleconfig", "targetResourceUri": "[variables('vmssId')]", "enabled": True, "profiles": [ { "name": "Profile1", "capacity": { "minimum": "[parameters('vmScaleSetMinCount')]", "maximum": "[parameters('vmScaleSetMaxCount')]", "default": "[parameters('vmScaleSetMinCount')]" }, "rules": [ { "metricTrigger": { "metricName": "[variables('scaleMetricMap')[variables('cpuMetricName')].metricName]", "metricNamespace": "", "metricResourceUri": "[variables('scaleMetricMap')[variables('cpuMetricName')].metricResourceUri]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('scaleOutTimeWindow')]", "timeAggregation": "Average", "operator": "GreaterThan", "threshold": "[variables('scaleMetricMap')[variables('cpuMetricName')].thresholdOut]" }, "scaleAction": { "direction": "Increase", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } }, { "metricTrigger": { "metricName": "[variables('scaleMetricMap')[variables('cpuMetricName')].metricName]", "metricNamespace": "", "metricResourceUri": "[variables('scaleMetricMap')[variables('cpuMetricName')].metricResourceUri]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('scaleInTimeWindow')]", "timeAggregation": "Average", "operator": "LessThan", "threshold": "[variables('scaleMetricMap')[variables('cpuMetricName')].thresholdIn]" }, "scaleAction": { "direction": "Decrease", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } }, { "metricTrigger": { "metricName": "[variables('scaleMetricMap')[variables('throughputMetricName')].metricName]", "metricNamespace": "", "metricResourceUri": "[variables('scaleMetricMap')[variables('throughputMetricName')].metricResourceUri]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('scaleOutTimeWindow')]", "timeAggregation": "Average", "operator": "GreaterThan", "threshold": "[variables('scaleMetricMap')[variables('throughputMetricName')].thresholdOut]" }, "scaleAction": { "direction": "Increase", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } }, { "metricTrigger": { "metricName": "[variables('scaleMetricMap')[variables('throughputMetricName')].metricName]", "metricNamespace": "", "metricResourceUri": "[variables('scaleMetricMap')[variables('throughputMetricName')].metricResourceUri]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('scaleInTimeWindow')]", "timeAggregation": "Average", "operator": "LessThan", "threshold": "[variables('scaleMetricMap')[variables('throughputMetricName')].thresholdIn]" }, "scaleAction": { "direction": "Decrease", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } } ] } ], "notifications": [ { "operation": "Scale", "email": { "sendToSubscriptionAdministrator": False, "sendToSubscriptionCoAdministrators": False, "customEmails": "[variables('customEmail')]" }, "webhooks": [] } ] } }]

###### Appliction Insight Workspace(s) ######
# Add TMM CPU metric option into autoscale templates
if template_name in ('as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns'):
    resources_list += [{ "type": "Microsoft.Insights/components", "condition": "[contains(toUpper(parameters('appInsights')), 'CREATE_NEW')]", "kind": "other", "name": "[variables('appInsightsName')]", "apiVersion": "[variables('appInsightsComponentsApiVersion')]", "location": "[variables('appInsightsLocation')]", "tags": tags, "properties": { "ApplicationId": "[variables('appInsightsName')]", "Application_Type": "other" }, "dependsOn": [] }]

## Sort resources section - Expand to choose order of resources instead of just alphabetical?
resources_sorted = json.dumps(resources_list, sort_keys=True, indent=4, ensure_ascii=False)
data['resources'] = json.loads(resources_sorted, object_pairs_hook=OrderedDict)

# Prod Stack Strip Public IP Address Function
if stack_type == 'production-stack':
    master_helper.pub_ip_strip(data['variables'], 'PublicIpAddress', 'variables')
    master_helper.pub_ip_strip(data['resources'], 'PublicIpAddress', 'resources')

######################################## ARM Outputs ########################################
## Note: Change outputs if production-stack as public IP's are not attached to the BIG-IP's
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic'):
    if stack_type == 'production-stack':
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://', reference(variables('mgmtNicId')).ipConfigurations[0].properties.privateIPAddress, ':', variables('bigIpMgmtPort'))]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtNicId')).ipConfigurations[0].properties.privateIPAddress, ' ',22)]" }
    else:
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://', reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ':', variables('bigIpMgmtPort'))]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ' ',22)]" }
    # Add learning stack output(s)
    if learningStack:
        data['outputs']['EXAMPLE-APP-URL'] = { "type": "string", "value": "[concat('http://', reference(concat(variables('extPublicIPAddressIdPrefix'), '0')).dnsSettings.fqdn, ':', variables('webVmVsPort'))]" }
if template_name == 'failover-lb_1nic':
    if stack_type == 'production-stack':
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://', variables('externalLoadBalancerAddress'), ':8443')]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(variables('externalLoadBalancerAddress'), ' ', 8022)]" }
    else:
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':8443')]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',8022)]" }
if template_name in ('failover-api', 'failover-lb_3nic'):
    if stack_type == 'production-stack':
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(concat(variables('mgmtNicId'), '0')).ipConfigurations[0].properties.privateIPAddress, ':', variables('bigIpMgmtPort'))]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(concat(variables('mgmtNicId'), '0')).ipConfigurations[0].properties.privateIPAddress,' ',22)]" }
    else:
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(concat(variables('mgmtPublicIPAddressId'), '0')).dnsSettings.fqdn, ':', variables('bigIpMgmtPort'))]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(concat(variables('mgmtPublicIPAddressId'), '0')).dnsSettings.fqdn,' ',22)]" }
    # Add learning stack output(s)
    if learningStack:
        data['outputs']['EXAMPLE-APP-URL'] = { "type": "string", "value": "[concat('http://', reference(concat(variables('extPublicIPAddressIdPrefix'), '0')).dnsSettings.fqdn, ':', variables('webVmVsPort'))]" }
if template_name in ('as_ltm_lb', 'as_waf_lb'):
    if license_type == 'bigiq-payg':
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':50101', ' - 50109')]" }
        data['outputs']['GUI-URL-DYNAMIC'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':50110', ' - 50200')]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',50001, ' - 50009')]" }
        data['outputs']['SSH-URL-DYAMIC'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',50010, ' - 50100')]" }
    else:
        data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':50101', ' - 50200')]" }
        data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',50001, ' - 50100')]" }
if template_name in ('as_ltm_dns', 'as_waf_dns'):
    # Do nothing currently
    data['outputs']['GUI-URL'] = { "type": "string", "value": "N/A" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "N/A" }
######################################## End Create/Modify ARM Template Objects ########################################

## Write modified template(s) to appropriate location
with open(created_file, 'wb') as finished:
    json.dump(data, finished, indent=4, sort_keys=False, ensure_ascii=False)
with open(created_file_params, 'wb') as finished_params:
    json.dump(data_params, finished_params, indent=4, sort_keys=False, ensure_ascii=False)

######################################## Create/Modify Scripts ###########################################
# Manually adding templates to create scripts proc for now as a 'check'...
if template_name in ('standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic', 'failover-lb_1nic', 'failover-lb_3nic', 'failover-api', 'as_ltm_lb', 'as_ltm_dns', 'as_waf_lb', 'as_waf_dns') and artifact_location:
    s_data = {'template_info': template_info}
    bash_script = script_generator.script_creation(data, s_data, 'bash')
    ps_script = script_generator.script_creation(data, s_data, 'powershell')
######################################## END Create/Modify Scripts ########################################

######################################## Create/Modify README's ########################################
    readme_text = {'deploy_links': {}, 'ps_script': {}, 'bash_script': {}}
    ## Deploy Buttons ##
    readme_text['deploy_links']['version_tag'] = f5_networks_tag
    readme_text['deploy_links']['license_type'] = license_type
    ## Example Scripts - These are set above, just adding to README ##
    readme_text['bash_script'] = bash_script
    readme_text['ps_script'] = ps_script
    i_data['readme_text'] = readme_text

    #### Call function to create/update README ####
    folder_loc = 'files/readme_files/'
    i_data['files']['doc_text_file'] = folder_loc + 'template_text.yaml'
    i_data['files']['misc_readme_file'] = folder_loc + 'misc.README.txt'
    i_data['files']['base_readme'] = folder_loc + 'base.README.md'
    rG = readme_generator.ReadmeGen(data, i_data)
    rG.create()
######################################## END Create/Modify README's ########################################
