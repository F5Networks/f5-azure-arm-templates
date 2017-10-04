#/usr/bin/python env
import re
import yaml

class ReadmeGen(object):
    """ Primary class for the readme generator """
    def __init__(self):
        self.data = {}
        self.i_data = {}
        self.loaded_files = {}

    def open_files(self, files):
        """ Open files, should be a dict with key being name and value being file location"""
        fd = {}
        for f in files:
            with open(files[f]) as file_str:
                if 'yaml' in files[f]:
                    fd[f] = yaml.load(file_str.read())
                else:
                    fd[f] = file_str.read()
        self.loaded_files = fd
        return

    def get_custom_text(self, parent_key, child_key, template_name=None):
        """ Pull in custom text for each solution from the YAML file """
        yaml_dict = self.loaded_files['doc_text_file']
        try:
            yaml_value = yaml_dict[parent_key][child_key]
        except KeyError:
            yaml_value = "Please input a value."
        try:
            support_type = self.i_data['support_type']
        except:
            support_type = None
        if not template_name:
            template_name = self.i_data['template_info']['template_name']
        # Check if supported/experimental/template_name keys exist, defaults to 'default'
        if isinstance(yaml_value, dict):
            if support_type in yaml_value: 
                yaml_value = yaml_value[support_type]
            elif template_name in yaml_value:
                if isinstance(yaml_value[template_name], dict) and support_type in yaml_value[template_name]: 
                    yaml_value = yaml_value[template_name][support_type]
                else:
                    yaml_value = yaml_value[template_name]
            else:
                yaml_value = yaml_value['default']
        return yaml_value

    def param_exist(self, param):
        """ Check if a specific parameter exists, will add that blob in README if true """
        for p in self.data['parameters']:
            if param in p:
                return True
        return False

    def misc_readme_grep(self, tag):
        """ Pull in any additional items that exist in the misc README file, based on <TAG> """
        text = self.loaded_files['misc_readme_file']
        reg_ex = tag + '{{' + r"(.*?)}}"
        tag_text = re.findall(reg_ex, text, re.DOTALL)
        return "".join(tag_text)

    def md_param_array(self):
        """ Create README example paramaters: | adminUsername | Yes | Description | """
        template_name = self.i_data['template_info']['template_name']
        license_params = self.i_data['license_params']
        lic_type = self.i_data['readme_text']['deploy_links']['lic_support'][template_name]
        param_array = ""
        license_flag = True
        for p in self.data['parameters']:
            mandatory = 'Yes'
            # Specify optional parameters that README, need to pull in all license options
            if 'license' in p.lower():
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
                            param_array += "| " + key + " | " + mandatory + " | " + self.get_custom_text('parameter_list', key) + " |\n"
            else:
                param_array += "| " + p + " | " + mandatory + " | " + self.data['parameters'][p]['metadata']['description'] + " |\n"
        return param_array

    def stack_type_check(self):
        """ Determine what stack type the template is, return appropriate readme text """
        t_loc = self.i_data['template_location']
        if 'existing_stack' in t_loc:
            stack_type_text = self.get_custom_text('stack_type_text', 'existing_stack')
        elif 'prod_stack' in t_loc:
            stack_type_text = self.get_custom_text('stack_type_text', 'prod_stack')
        else:
            stack_type_text = self.get_custom_text('stack_type_text', 'new_stack')
        return stack_type_text

    def sp_access_required(self):
        """ Determine what Service Principal Access is needed, return full Service Principal Text """
        text = self.misc_readme_grep('<SERVICE_PRINCIPAL_TXT>')
        template_name = self.i_data['template_info']['template_name']
        api_access_required = self.i_data['template_info']['api_access_needed'][template_name]
        if api_access_required == 'read_write':
            text = text.replace('<SP_REQUIRED_ACCESS>', self.get_custom_text('sp_access_text', 'read_write'))
        else:
            text = text.replace('<SP_REQUIRED_ACCESS>', self.get_custom_text('sp_access_text', 'read'))
        return text

    def md_version_map(self):
        """ Create BIG-IP version map: | Azure BIG-IP Image Version | BIG-IP Version | """
        data = self.data
        param_array = ""
        for version in data['parameters']['bigIpVersion']['allowedValues']:
            param_array += "| " + version + " | " + self.get_custom_text('license_map', version) + " |\n"
        return param_array

    def create_deploy_links(self):
        """ Create deploy to Azure buttons/links """
        t_loc = self.i_data['template_location']
        template_name = self.i_data['template_info']['template_name']
        lic_type = self.i_data['readme_text']['deploy_links']['lic_support'][template_name]
        v_tag = self.i_data['readme_text']['deploy_links']['version_tag']
        deploy_links = ''
        base_url = 'https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2F' + v_tag
        if 'All' in lic_type:
            lic_list = ['BYOL', 'PAYG', 'BIG-IQ']
        elif isinstance(lic_type, list):
            lic_list = lic_type
        else:
            lic_list = [lic_type]
        for lic in lic_list:
            deploy_links += '''   - **<LIC_TYPE>**<LIC_TEXT> <br><a href="<DEPLOY_LINK_URL>">\n    <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>\n\n'''
            t_loc = t_loc.replace('/', '%2F')
            t_loc = t_loc.replace('..', '')
            t_loc = t_loc.replace('PAYG', lic).replace('BYOL', lic).replace('BIGIQ', lic).replace('BIG-IQ', 'BIGIQ')
            url = base_url + t_loc
            deploy_links = deploy_links.replace('<DEPLOY_LINK_URL>', url).replace('<LIC_TYPE>', lic)
            deploy_links = deploy_links.replace('<LIC_TEXT>', self.get_custom_text('license_text', lic))
        return deploy_links

    def create(self, data, i_data):
        """ Main proc to create readme """
        self.data = data
        self.i_data = i_data
        # Open Files
        self.open_files(i_data['files'])
        ####### Text Values for README templates #######
        template_name = i_data['template_info']['template_name']
        readme_location = i_data['template_info']['location']
        final_readme = readme_location + 'README.md'
        post_config_text = ''; sp_text = ''; extra_prereq_text = ''; tg_config_text = ''
        if 'supported' in readme_location:
            self.i_data['support_type'] = 'supported'
            help_text = self.get_custom_text('help_text', 'supported')
        else:
            self.i_data['support_type'] = 'experimental'
            help_text = self.get_custom_text('help_text', 'experimental')
        title_text = self.get_custom_text('title_text', template_name)
        intro_text = self.get_custom_text('intro_text', template_name)
        example_text = self.get_custom_text('config_example_text', template_name)
        stack_type_text = self.stack_type_check()
        version_map = self.md_version_map()
        deploy_links = self.create_deploy_links()
        bash_script = i_data['readme_text']['bash_script']
        ps_script = i_data['readme_text']['ps_script']

        ### Check for optional readme items ###
        # Add service principal text if needed
        if self.param_exist('servicePrincipalSecret'):
            sp_text = self.sp_access_required()
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'service_principal') + '\n'
        # Post-Deployment Configuration Text Substitution
        if 'autoscale' in template_name:
            post_config_text = self.misc_readme_grep('<POST_CONFIG_AUTOSCALE_TXT>')
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'post_config') + '\n'
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'master_election') + '\n'
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'config_backup') + '\n'
        if self.param_exist('numberOfExternalIps'):
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'post_config') + '\n'
            if template_name in 'ha-avset':
                post_config_text = self.misc_readme_grep('<POST_CONFIG_FAILOVER_TXT>')
                extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'rg_limit') + '\n'
            else:
                post_config_text = self.misc_readme_grep('<POST_CONFIG_TXT>')
        if self.param_exist('numberOfAdditionalNics'):
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'nic_sizing') + '\n'
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'addtl_nic_config') + '\n'
        if template_name in ('ha-avset'):
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'traffic_group_msg') + '\n'
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'udr_tags') + '\n'
        if template_name in ('waf_autoscale'):
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'asm_sync') + '\n'
        if template_name in ('ha-avset'):
            extra_prereq_text += '  - ' + self.get_custom_text('prereq_text', 'tg_config') + '\n'
            tg_config_text = self.misc_readme_grep('<TG_CONFIG_TEXT>')

        ### Map in dynamic values ###
        readme = self.loaded_files['base_readme']
        readme = readme.replace('<TITLE_TXT>', title_text)
        readme = readme.replace('<INTRO_TXT>', intro_text)
        readme = readme.replace('<STACK_TYPE_TXT>', stack_type_text)
        readme = readme.replace('<EXTRA_PREREQS>', extra_prereq_text)
        readme = readme.replace('<VERSION_MAP_TXT>', version_map)
        readme = readme.replace('<HELP_TXT>', help_text)
        readme = readme.replace('<DEPLOY_LINKS>', deploy_links)
        readme = readme.replace('<EXAMPLE_PARAMS>', self.md_param_array())
        readme = readme.replace('<PS_SCRIPT>', ps_script)
        readme = readme.replace('<BASH_SCRIPT>', bash_script)
        readme = readme.replace('<EXAMPLE_TEXT>', example_text)
        readme = readme.replace('<POST_CONFIG_TXT>', post_config_text)
        readme = readme.replace('<SERVICE_PRINCIPAL>', sp_text)
        readme = readme.replace('<TG_CONFIG_TEXT>', tg_config_text)

        ### Write to solution location ###
        with open(final_readme, 'w') as readme_complete:
            readme_complete.write(readme)
        ## End README creation Function
        return 'README Created for ' + template_name