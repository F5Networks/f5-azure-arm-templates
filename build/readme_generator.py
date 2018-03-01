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

    def misc_readme_grep(self, tag):
        """ Pull in any additional items that exist in the misc README file, based on <TAG> """
        text = self.loaded_files['misc_readme_file']
        reg_ex = tag + '{{' + r"(.*?)}}"
        tag_text = re.findall(reg_ex, text, re.DOTALL)
        return "".join(tag_text)

    def get_custom_text(self, parent_key, child_key=None, template_name=None):
        """ Pull in custom text from the YAML file """
        yaml_dict = self.loaded_files['doc_text_file']
        try:
            if child_key is not None:
                yaml_value = yaml_dict[parent_key][child_key]
            else:
                yaml_value = yaml_dict[parent_key]
        except KeyError:
            yaml_value = "No Value"
        try:
            support_type = self.i_data['support_type']
        except KeyError:
            support_type = None
        if isinstance(yaml_value, dict):
            if 'exclude' in yaml_value:
                exclude = yaml_value['exclude']
                if 'stack_type' in exclude:
                    if self.stack_type_check() in exclude['stack_type']:
                        return None
            if 'template_name' in yaml_value:
                yvalue = yaml_value['template_name']
                if template_name in yvalue:
                    yvalue_tmpl = yvalue[template_name]
                    if isinstance(yvalue_tmpl, dict) and support_type in yvalue_tmpl:
                        yaml_value = yvalue_tmpl[support_type]
                    else:
                        yaml_value = yvalue_tmpl
                else:
                    yaml_value = yaml_value['default']
            else:
                yaml_value = yaml_value['default']
        return yaml_value

    def get_tmpl_text(self, p_key, s_key, t_key):
        """ Pull in custom template text for each solution from the YAML file """
        ydict = self.loaded_files['doc_text_file']
        yvalue = ydict[p_key][s_key]
        sp_type = self.i_data['support_type']
        result = ''
        if t_key in ('prereq_list', 'config_note_list') and t_key in yvalue:
            t_list = yvalue[t_key]
            for item in t_list:
                if isinstance(item, dict):
                    result += '- ' + item[next(iter(item))] + '\n'
                else:
                    result_value = self.get_custom_text('note_text', item)
                    if result_value is not None:
                        result += '- ' + result_value + '\n'
        elif t_key == 'extra_text':
            result = self.loaded_files['base_readme']
            if t_key in yvalue:
                for item in yvalue['extra_text']:
                    if isinstance(item, dict):
                        key = next(iter(item))
                        value = item[key]
                    else: 
                        key = item
                        value = item
                    result = result.replace(key, self.misc_readme_grep(value))
        elif t_key in ('title', 'intro', 'config_ex_text') and t_key in yvalue:
            if isinstance(yvalue[t_key], dict) and sp_type in yvalue[t_key]:
                result = yvalue[t_key][sp_type]
            else:
                result = yvalue[t_key]
        return result

    def clean_up(self, readme):
        """ Final clean up of README file """
        # Remove extra new lines
        readme = readme.replace('\n\n\n\n', '\n\n').replace('\n\n\n', '\n\n')
        return readme

    def delete_tags(self, readme):
        """ Delete left over tags from the README file """
        reg_ex = r"<([A-Z-_]{0,50})>"
        tag_text = re.findall(reg_ex, readme)
        for match in tag_text:
            readme = readme.replace('<' + match + '>', '')
        return readme

    def param_exist(self, param):
        """ Check if a specific parameter exists, will add that blob in README if true """
        for p in self.data['parameters']:
            if param in p:
                return True
        return False

    def md_param_array(self):
        """ Create README example parameters: | adminUsername | Yes | Description | """
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
        """ Determine what stack type the template is """
        t_loc = self.i_data['template_location']
        if 'new_stack' in t_loc:
            stack_type = 'new_stack'
        elif 'existing_stack' in t_loc:
            stack_type = 'existing_stack'
        elif 'prod_stack' in t_loc:
            stack_type = 'prod_stack'
        elif 'learning_stack' in t_loc:
            stack_type = 'learning_stack'
        else:
            stack_type = 'unkown_stack_type'
        return stack_type

    def sp_access_required(self, text):
        """ Determine what Service Principal Access is needed, map in what is needed """
        template_name = self.i_data['template_info']['template_name']
        api_access_required = self.i_data['template_info']['api_access_required'][template_name]
        if api_access_required == 'required':
            text = text.replace('<SP_REQUIRED_ACCESS>', self.get_custom_text('sp_access_text', None, template_name))
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
        if isinstance(lic_type, list):
            lic_list = lic_type
        else:
            lic_list = [lic_type]
        for lic in lic_list:
            deploy_links += '''- **<LIC_TYPE>**<LIC_TEXT>\n\n  [![Deploy to Azure](http://azuredeploy.net/deploybutton.png)](<DEPLOY_LINK_URL>)\n\n'''
            t_loc = t_loc.replace('/', '%2F').replace('..', '')
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
        if 'supported' in readme_location:
            self.i_data['support_type'] = 'supported'
            help_text = self.get_custom_text('help_text', 'supported')
        else:
            self.i_data['support_type'] = 'experimental'
            help_text = self.get_custom_text('help_text', 'experimental')
        title_text = self.get_tmpl_text('templates', template_name, 'title')
        intro_text = self.get_tmpl_text('templates', template_name, 'intro')
        example_text = self.get_tmpl_text('templates', template_name, 'config_ex_text')
        extra_prereq = self.get_tmpl_text('templates', template_name, 'prereq_list')
        extra_config_note = self.get_tmpl_text('templates', template_name, 'config_note_list')
        stack_type_text = self.get_custom_text('stack_type_text', self.stack_type_check())
        version_map = self.md_version_map()
        deploy_links = self.create_deploy_links()
        bash_script = [l for l in i_data['readme_text']['bash_script'].split('\n') if "Example Command" in l][0]
        ps_script = [l for l in i_data['readme_text']['ps_script'].split('\n') if "Example Command" in l][0]
        ### Map in dynamic values ###
        readme = self.loaded_files['base_readme']
        readme = readme.replace('<TITLE_TXT>', title_text).replace('<INTRO_TXT>', intro_text)
        readme = readme.replace('<STACK_TYPE_TXT>', stack_type_text)
        readme = readme.replace('<EXTRA_PREREQS>', extra_prereq).replace('<EXTRA_CONFIG_NOTES>', extra_config_note)
        readme = readme.replace('<VERSION_MAP_TXT>', version_map).replace('<HELP_TXT>', help_text)
        readme = readme.replace('<DEPLOY_LINKS>', deploy_links).replace('<EXAMPLE_PARAMS>', self.md_param_array())
        readme = readme.replace('<PS_SCRIPT>', ps_script).replace('<BASH_SCRIPT>', bash_script)
        readme = readme.replace('<EXAMPLE_TEXT>', example_text)
        self.loaded_files['base_readme'] = readme
        readme = self.get_tmpl_text('templates', template_name, 'extra_text')
        readme = self.sp_access_required(readme)
        readme = self.delete_tags(readme)
        readme = self.clean_up(readme)
        ### Write to solution location ###
        with open(final_readme, 'w') as readme_complete:
            readme_complete.write(readme)
        ## End README creation Function
        return 'README Created for ' + template_name