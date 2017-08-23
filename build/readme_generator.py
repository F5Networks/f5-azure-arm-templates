#/usr/bin/python env
import re
import yaml

# Create Functions for README creation
def get_custom_text(parent_key, child_key):
    """ Pull in custom text for each solution from the YAML file """
    yaml_doc_loc = "files/readme_files/template_text.yaml"
    with open(yaml_doc_loc) as doc:
        yaml_doc = doc.read()
    yaml_dict = yaml.load(yaml_doc)
    return yaml_dict[parent_key][child_key]

def param_exist(data, param):
    """ Check if a specific parameter exists, will add that blob in README if true """
    for parameter in data['parameters']:
        if param in parameter:
            return True
    return False

def misc_readme_grep(tag, misc_file):
    """ Pull in any additional items that exist in the misc README file, based on <TAG> """
    with open(misc_file, 'r') as file_str:
        text = file_str.read()
    reg_ex = tag + '{{' + r"(.*?)}}"
    tag_text = re.findall(reg_ex, text, re.DOTALL)
    return "".join(tag_text)

def md_param_array(data, license_params, lic_type):
    """ Create README example paramaters: | adminUsername | Yes | Description | """
    param_array = ""
    license_flag = True
    for parameter in data['parameters']:
        mandatory = 'Yes'
        # Specify optional parameters that README, need to pull in all license options
        if 'license' in parameter.lower():
            if license_flag:
                license_flag = False
                for key in license_params:
                    if key == 'licensedBandwidth':
                        mandatory = 'PAYG only:'
                    elif 'licenseKey' in key:
                        mandatory = 'BYOL only:'
                    else:
                        mandatory = 'BIG-IQ licensing only:'
                    if lic_type == 'PAYG' and key != 'licensedBandwidth':
                        continue
                    elif all(x in ['PAYG', 'BIG-IQ'] for x in lic_type) and 'licenseKey' in key:
                        continue                       
                    else:
                        param_array += "| " + key + " | " + mandatory + " | " + license_params[key] + " |\n"
        else:
            param_array += "| " + parameter + " | " + mandatory + " | " + data['parameters'][parameter]['metadata']['description'] + " |\n"
    return param_array

def stack_type_check(template_location):
    """ Determine what stack type the template is, return appropriate readme text """
    if 'existing_stack' in template_location:
        stack_type_text = get_custom_text('stack_type_text', 'existing_stack')
    else:
        stack_type_text = get_custom_text('stack_type_text', 'new_stack')
    return stack_type_text

def sp_access_needed(api_access_needed, misc_readme):
    """ Determine what Service Principal Access is needed, return full Service Principal Text """
    sp_text = misc_readme_grep('<SERVICE_PRINCIPAL_TXT>', misc_readme)
    if api_access_needed == 'read_write':
        sp_text = sp_text.replace('<SP_REQUIRED_ACCESS>', get_custom_text('sp_access_text', 'read_write'))
    else:
        sp_text = sp_text.replace('<SP_REQUIRED_ACCESS>', get_custom_text('sp_access_text', 'read'))
    return sp_text

def md_version_map(data):
    """ Create BIG-IP version map: | Azure BIG-IP Image Version | BIG-IP Version | """
    param_array = ""
    for version in data['parameters']['bigIpVersion']['allowedValues']:
        param_array += "| " + version + " | " + get_custom_text('license_map', version) + " |\n"
    return param_array

def create_deploy_links(version_tag, lic_type, template_location):
    """ Create deploy to Azure buttons/links """
    deploy_links = ''
    base_url = 'https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2F' + version_tag
    if 'All' in lic_type:
        lic_list = ['BYOL', 'PAYG', 'BIG-IQ']
    elif isinstance(lic_type, list):
        lic_list = lic_type
    else:
        lic_list = [lic_type]
    for lic in lic_list:
        deploy_links += '''   - **<LIC_TYPE>**<LIC_TEXT> <br><a href="<DEPLOY_LINK_URL>">\n    <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>\n\n'''
        template_location = template_location.replace('/', '%2F')
        template_location = template_location.replace('..', '')
        template_location = template_location.replace('PAYG', lic).replace('BYOL', lic).replace('BIGIQ', lic).replace('BIG-IQ', 'BIGIQ')
        url = base_url + template_location
        deploy_links = deploy_links.replace('<DEPLOY_LINK_URL>', url).replace('<LIC_TYPE>', lic)
        deploy_links = deploy_links.replace('<LIC_TEXT>', get_custom_text('license_text', lic))
    return deploy_links

def readme_creation(template_info, data, license_params, readme_text, template_location):
    """ Main proc to create readme """
    template_name = template_info['template_name']
    readme_location = template_info['location']
    folder_loc = 'files/readme_files/'
    base_readme = folder_loc + 'base.README.md'
    misc_readme = folder_loc + 'misc.README.txt'
    final_readme = readme_location + 'README.md'
    with open(base_readme, 'r') as readme:
        readme = readme.read()
    post_config_text = ''; sp_text = ''; extra_prereq_text = ''
    api_access_needed = template_info['api_access_needed'][template_name]
    lic_type = readme_text['deploy_links']['lic_support'][template_name]

    ####### Text Values for README templates #######
    title_text = get_custom_text('title_text', template_name)
    intro_text = get_custom_text('intro_text', template_name)
    example_text = get_custom_text('config_example_text', template_name)
    stack_type_text = stack_type_check(template_location)
    if 'supported' in readme_location:
        help_text = get_custom_text('help_text', 'supported')
    else:
        help_text = get_custom_text('help_text', 'experimental')
    version_map = md_version_map(data)
    deploy_links = create_deploy_links(readme_text['deploy_links']['version_tag'], lic_type, template_location)
    bash_script = readme_text['bash_script']
    ps_script = readme_text['ps_script']

    ### Check for optional readme items ###
    # Add service principal text if needed
    if param_exist(data, 'servicePrincipalSecret'):
        sp_text = sp_access_needed(api_access_needed, misc_readme)
        extra_prereq_text += '  - ' + get_custom_text('prereq_text', 'service_principal') + '\n'
    # Post-Deployment Configuration Text Substitution
    if 'autoscale' in template_name:
        post_config_text = misc_readme_grep('<POST_CONFIG_AUTOSCALE_TXT>', misc_readme)
        extra_prereq_text += '  - ' + get_custom_text('prereq_text', 'post_config') + '\n'
    if param_exist(data, 'numberOfExternalIps'):
        extra_prereq_text += '  - ' + get_custom_text('prereq_text', 'post_config') + '\n'
        if template_name in 'ha-avset':
            post_config_text = misc_readme_grep('<POST_CONFIG_FAILOVER_TXT>', misc_readme)
            extra_prereq_text += '  - ' + get_custom_text('prereq_text', 'rg_limit') + '\n'
        else:
            post_config_text = misc_readme_grep('<POST_CONFIG_TXT>', misc_readme)
    if param_exist(data, 'numberOfAdditionalNics'):
        extra_prereq_text += '  - ' + get_custom_text('prereq_text', 'nic_sizing') + '\n'
        extra_prereq_text += '  - ' + get_custom_text('prereq_text', 'addtl_nic_config') + '\n'
    if template_name in ('ha-avset'):
        extra_prereq_text += '  - ' + get_custom_text('prereq_text', 'traffic_group_msg') + '\n'
    if template_name in ('waf_autoscale'):
        extra_prereq_text += '  - ' + get_custom_text('prereq_text', 'asm_sync') + '\n'

    ### Map in dynamic values ###
    readme = readme.replace('<TITLE_TXT>', title_text)
    readme = readme.replace('<INTRO_TXT>', intro_text)
    readme = readme.replace('<STACK_TYPE_TXT>', stack_type_text)
    readme = readme.replace('<EXTRA_PREREQS>', extra_prereq_text)
    readme = readme.replace('<VERSION_MAP_TXT>', version_map)
    readme = readme.replace('<HELP_TXT>', help_text)
    readme = readme.replace('<DEPLOY_LINKS>', deploy_links)
    readme = readme.replace('<EXAMPLE_PARAMS>', md_param_array(data, license_params, lic_type))
    readme = readme.replace('<PS_SCRIPT>', ps_script)
    readme = readme.replace('<BASH_SCRIPT>', bash_script)
    readme = readme.replace('<EXAMPLE_TEXT>', example_text)
    readme = readme.replace('<POST_CONFIG_TXT>', post_config_text)
    readme = readme.replace('<SERVICE_PRINCIPAL>', sp_text)

    ### Write to solution location ###
    with open(final_readme, 'w') as readme_complete:
        readme_complete.write(readme)
    ## End README creation Function
    return 'README Created for ' + template_name
