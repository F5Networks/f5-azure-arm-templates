"""Template Generator readme module """

import re
import yaml


class ReadmeGen(object):
    """ Primary class for the readme generator """
    def __init__(self, data, i_data, variables):
        self.data = data or {}
        self.i_data = i_data or {}
        self.loaded_files = {}
        self.variables = variables or {}

    def open_files(self, files):
        """ Open files, should be a dict with key being name and value being file location"""
        file_dict = {}
        for _file in files:
            with open(files[_file]) as file_str:
                if 'yaml' in files[_file]:
                    file_dict[_file] = yaml.load(file_str.read())
                else:
                    file_dict[_file] = file_str.read()
        self.loaded_files = file_dict

    def get_custom_text(self, parent_key, child_key=None, t_key=None):  # pylint: disable=too-many-branches, too-many-statements
        """ Pull in custom text from the YAML file, enhanced logic """
        yaml_dict = self.loaded_files['doc_text_file']
        ret = ''
        try:
            if t_key is not None:
                yaml_value = yaml_dict[parent_key][child_key][t_key]
            elif child_key is not None:
                yaml_value = yaml_dict[parent_key][child_key]
            else:
                yaml_value = yaml_dict[parent_key]
        except KeyError:
            yaml_value = None
        try:
            support_type = self.i_data['support_type']
        except KeyError:
            support_type = None
        if isinstance(yaml_value, dict):
            # consume logic in yaml file, if exists
            # check for exclusion
            if 'exclude' in yaml_value:
                exclude = yaml_value['exclude']
                if 'stackType' in exclude:
                    if self.stack_type_check() in exclude['stackType']:
                        return None
                if 'licenseType' in exclude:
                    if self.license_type_check() in exclude['licenseType']:
                        return None
                if 'environment' in exclude:
                    if self.env_type_check() in exclude['environment']:
                        return None
                if 'lb_method' in exclude:
                    if self.variables['lb_method'] in exclude['lb_method']:
                        return None
            # Check if more specific value exists
            if 'templateName' in yaml_value:
                template_name = self.i_data['template_info']['template_name']
                yvalue = yaml_value['templateName']
                if template_name in yvalue:
                    yvalue_tmpl = yvalue[template_name]
                    if isinstance(yvalue_tmpl, dict) and support_type in yvalue_tmpl:
                        ret = yvalue_tmpl[support_type]
                    else:
                        ret = yvalue_tmpl
                else:
                    ret = yaml_value['default']
                    try:
                        ret = yvalue[self.license_type_check()]
                    except KeyError:
                        pass
            elif 'environment' in yaml_value:
                yvalue = yaml_value['environment']
                environment = self.env_type_check()
                if environment in yvalue:
                    ret = yvalue[environment]
                else:
                    ret = yaml_value['default']
            elif 'supportType' in yaml_value:
                yvalue = yaml_value['supportType']
                if support_type in yvalue:
                    ret = yvalue[support_type]
                else:
                    ret = yaml_value['default']
            elif 'stackType' in yaml_value:
                yvalue = yaml_value['stackType']
                if self.variables["stack"] in yaml_value["stackType"]:
                    ret = yvalue[self.variables["stack"]]
                else:
                    ret = yaml_value['default']
            else:
                ret = yaml_value['default']
        else:
            ret = yaml_value
        return ret

    def get_tmpl_text(self, p_key, s_key, t_key):
        """ Pull in custom template text for each solution, prefer get_custom_text """

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
        elif t_key in ('title', 'intro', 'config_ex_text', 'config_ex_link') and t_key in yvalue:
            sp_type_key = 'support_type'
            if isinstance(yvalue[t_key], dict) and sp_type_key in yvalue[t_key]:
                try:
                    result = yvalue[t_key][sp_type_key][sp_type]
                except KeyError:
                    result = yvalue[t_key]['default']
            else:
                result = yvalue[t_key]
        return result

    @staticmethod
    def clean_up(readme):
        """ Final clean up of README file """
        # Remove extra new lines
        readme = readme.replace('\n\n\n\n', '\n\n').replace('\n\n\n', '\n\n')
        return readme

    @staticmethod
    def delete_tags(readme):
        """ Delete left over tags from the README file """
        reg_ex = r"<([A-Z-_]{0,50})>"
        tag_text = re.findall(reg_ex, readme)
        for match in tag_text:
            readme = readme.replace('<' + match + '>', '')
        return readme

    def param_exist(self, param):
        """ Check if a specific parameter exists, will add that blob in README if true """
        for parameter in self.data['parameters']:
            if param in parameter:
                return True
        return False

    def md_param_array(self):
        """ Create README example parameters: | adminUsername | Yes | Description | """
        param_array = ""
        for parameter in self.data['parameters']:
            mandatory = 'Yes'
            # Specify optional parameters for README, need to pull in all license specific options
            if self.i_data["environment"] == "azure":
                param_array += "| %s | %s | %s |\n" % (
                    parameter,
                    mandatory,
                    self.data['parameters'][parameter]['metadata']['description']
                )
            if self.i_data["environment"] == "gce":
                param_array += "| %s | %s | %s |\n" % (
                    parameter,
                    self.data['parameters'][parameter]["required"],
                    self.data['parameters'][parameter]['description']
                )
        return param_array

    def license_type_check(self):
        """ Determine the license type of the template """
        lic_type = self.i_data['template_location'].lower().split("/")[-2]
        if lic_type not in ('bigiq-payg', 'payg', 'bigiq', 'byol'):
            lic_type = 'unknown type'
        return lic_type

    def resolve_license_type_with_description(self):
        """ Resolve license type with description """
        descriptions = {
            "byol": "(bring your own license)",
            "payg": "(pay as you go) hourly"
        }

        lic_type = self.i_data['template_location'].lower().split("/")[-2]
        if lic_type not in ('payg', 'byol'):
            lic_type = 'unknown type'
            return lic_type
        return str(lic_type).upper() + " " + descriptions[lic_type]

    def resolve_solution_type(self):
        """ Determing solution type"""
        if "autoscale" in self.variables["type"]:
            return self.variables["type"]

        return self.i_data["template_info"]["template_name"].split("_")[0]

    def resolve_parameter_file_location(self):
        """ Resolves parameter file location"""
        return self.i_data["template_location"].split("/").pop().replace(".py", ".yaml")

    def support_type_check(self):
        """ Determine the support type of the template """
        sp_type = self.i_data['template_location'].lower().split("/")[1]
        if sp_type not in ('supported', 'experimental'):
            sp_type = 'unknown type'
        return sp_type

    def stack_type_check(self):
        """ Determine the stack type of the template """
        tmpl_location = self.i_data['template_location'].lower()
        if 'new-stack' in tmpl_location:
            ret = 'new-stack'
        elif 'existing-stack' in tmpl_location:
            ret = 'existing-stack'
        elif 'production-stack' in tmpl_location:
            ret = 'production-stack'
        elif 'learning-stack' in tmpl_location:
            ret = 'learning-stack'
        else:
            ret = 'unknown type'
        return ret

    def env_type_check(self):
        """ Determine the environment of the template """
        environment = self.i_data['environment'].lower()
        if 'azurestack' in environment:
            ret = 'azureStack'
        elif 'azure' in environment:
            ret = 'azureCloud'
        elif 'gce' in environment:
            ret = 'googleCloud'
        else:
            ret = 'unknown type'
        return ret

    def sp_access_required(self, text):
        """ Determine what Service Principal Access is needed, map in what is needed """
        template_name = self.i_data['template_info']['template_name']
        api_access_required = self.i_data['template_info']['api_access_required'][template_name]
        if template_name in ('as_waf_lb', 'as_waf_dns'):
            stack_check = self.stack_type_check()
            license_check = self.license_type_check()
            api_access_required = api_access_required[stack_check][license_check]
        if api_access_required == 'required':
            text = text.replace('<SP_REQUIRED_ACCESS>', self.get_custom_text(
                'sp_access_text', None))
        return text

    def md_version_map(self):
        """ Create BIG-IP/BIG-IQ version map """
        # byol images have different options based on version
        byol_check = self.license_type_check() in ('bigiq-payg', 'bigiq', 'byol')
        # Check product version
        product_version_key = 'bigIpVersion'
        if 'bigiq' in self.i_data['template_info']['template_name']:
            product_version_key = 'bigIqVersion'
            base_header = "| Azure BIG-IQ Image Version | BIG-IQ Version |"
            param_array = base_header + "\n| --- | --- |"
            param_array += "\n"
            for version in self.data['parameters'][product_version_key]['allowedValues']:
                param_array += "| %s | %s |" % (
                    version, self.get_custom_text('license_map', version, 'build'))
                param_array += "\n"
        else:
            base_header = "| Azure BIG-IP Image Version | BIG-IP Version |"
            if byol_check:
                header = base_header + " Important: Boot location options note |"
                param_array = header + "\n| --- | --- | --- |"
            else:
                param_array = base_header + "\n| --- | --- |"
            param_array += "\n"
            if product_version_key in self.data['parameters']:
                version = self.data['parameters'][product_version_key]['defaultValue']
                print('Version:' + version)
                param_array += "| %s | %s |" % (version, self.get_custom_text(
                    'license_map', version, 'build'))
                if byol_check:
                    param_array += " " + self.get_custom_text(
                        'license_map', version, 'bootLocations') + " |"
                param_array += "\n"
        return param_array

    def create_deploy_links(self):
        """ Create deploy to Azure buttons/links """
        t_loc = self.i_data['template_location']
        lic_type = self.i_data['readme_text']['deploy_links']['license_type']
        v_tag = self.i_data['readme_text']['deploy_links']['version_tag']
        deploy_links = ''
        base_url = ("https://portal.azure.com/#create/Microsoft.Template/uri/"
                    "https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2F"
                    "f5-azure-arm-templates%2F"
                    ) + v_tag
        if isinstance(lic_type, list):
            lic_list = lic_type
        else:
            lic_list = [lic_type]
        # should be 1:1 pairing, leave in loop for now, will just loop once
        for lic in lic_list:
            deploy_links = ('- **<LIC_TYPE>**<LIC_TEXT>\n\n'
                            '  [![Deploy to Azure](http://azuredeploy.net/deploybutton.png)]'
                            '(<DEPLOY_LINK_URL>)\n'
                            )
            t_loc = "/" + self.i_data['support_type'] + t_loc.split(self.i_data['support_type'])[1]
            t_loc = t_loc.replace('/', '%2F').replace('..', '')
            url = base_url + t_loc
            deploy_links = deploy_links.replace('<DEPLOY_LINK_URL>', url)
            deploy_links = deploy_links.replace('<LIC_TYPE>', lic.upper())
            deploy_links = deploy_links.replace(
                '<LIC_TEXT>', self.get_custom_text('license_text', lic))
        return deploy_links

    def create(self):  # pylint: disable=too-many-branches, too-many-locals, too-many-statements
        """ Main proc to create readme """
        i_data = self.i_data
        # Open Files
        self.open_files(i_data['files'])
        # Text Values for README templates
        template_name = i_data['template_info']['template_name']
        readme_location = i_data['template_info']['location']
        if 'supported' in readme_location:
            self.i_data['support_type'] = 'supported'
            help_text = self.get_custom_text('help_text', 'supported')
        else:
            self.i_data['support_type'] = 'experimental'
            help_text = self.get_custom_text('help_text', 'experimental')
        title_text = self.get_tmpl_text('templates', template_name, 'title')
        intro_text = self.get_custom_text('templates', template_name, 'intro')
        example_text = self.get_tmpl_text('templates', template_name, 'config_ex_text')
        traffic_group_config = self.get_custom_text(
            'templates', template_name, 'traffic_group_config')
        create_virtual_servers = self.get_custom_text(
            'templates', template_name, 'create_virtual_servers')
        additional_security_notes = self.get_custom_text(
            'templates', template_name, 'additional_security_notes')
        support_notes = self.get_custom_text('templates', template_name, 'support_notes')
        supported_bigip_versions = self.get_custom_text(
            'templates', template_name, 'supported_bigip_versions')
        backup_and_recovery = self.get_custom_text(
            'templates', template_name, 'backup_and_recovery')
        extra_prereq = self.get_tmpl_text('templates', template_name, 'prereq_list')
        extra_config_note = self.get_tmpl_text('templates', template_name, 'config_note_list')
        config_ex_link = self.get_tmpl_text('templates', template_name, 'config_ex_link')
        stack_type_text = self.get_custom_text('stack_type_text', self.stack_type_check())
        version_map = self.md_version_map()
        docs = self.get_custom_text('templates', template_name, "docs")
        if self.i_data["environment"] == "azure":
            deploy_links = self.create_deploy_links()
            bash_script = [l for l in i_data['readme_text']['bash_script'].split('\n')
                           if "Example Command" in l][0]
            ps_script = [l for l in i_data['readme_text']['ps_script'].split('\n')
                         if "Example Command" in l][0]
        # Map in dynamic values
        self.variables["TITLE_TXT"] = title_text.replace(
            "<LICENSE__TYPE>", self.license_type_check().upper()
        ).replace("<STACK__TYPE>", " ".join(
            [s.capitalize() for s in self.stack_type_check().split("-")]))
        self.variables["INTRO_TXT"] = intro_text.replace(
            "<LICENSE__TYPE>", self.resolve_license_type_with_description()
        ).replace("<LICENSE__TYPE>", self.license_type_check().upper())
        self.variables["EXTRA_PREREQS"] = extra_prereq
        self.variables["EXTRA_CONFIG_NOTES"] = extra_config_note
        if config_ex_link is not None:
            self.variables["CONFIG_EXAMPLE_LINK"] = config_ex_link
        else:
            self.variables["CONFIG_EXAMPLE_LINK"] = ""
        self.variables["VERSION_MAP_TXT"] = version_map
        if self.i_data["environment"] == "azure":
            self.variables["DEPLOY_LINKS"] = deploy_links
            self.variables["EXAMPLE_PARAMS"] = self.md_param_array()
            self.variables["PS_SCRIPT"] = ps_script
            self.variables["BASH_SCRIPT"] = bash_script
            self.variables["HELP_TEXT"] = help_text
            self.variables["EXAMPLE_TEXT"] = example_text
            post_config_text = self.get_custom_text(
                'solution_text', self.variables['type'], 'post_config')
            self.variables["POST_CONFIG_TXT"] = post_config_text
        if self.i_data["environment"] == "gce":
            self.variables["EXAMPLE_PARAMS"] = self.md_param_array()
        self.variables["CONFIG_EXAMPLE"] = example_text
        if traffic_group_config is not None:
            self.variables["TRAFFIC_GROUP_CONFIG"] = traffic_group_config
        else:
            self.variables["TRAFFIC_GROUP_CONFIG"] = ""
        if create_virtual_servers is not None:
            self.variables["CREATE_VIRTUAL_SERVERS"] = create_virtual_servers
        else:
            self.variables["CREATE_VIRTUAL_SERVERS"] = ""
        self.variables["SOLUTION_TYPE"] = self.resolve_solution_type()
        self.variables["LINK_TO_TEMPLATE_PARAMETERS"] = "%s: [**%s**](%s)" % (
            self.license_type_check().upper(),
            self.resolve_parameter_file_location(),
            self.resolve_parameter_file_location()
        )
        self.variables["LINK_TO_TEMPLATE"] = "(%s)" % (
            self.i_data["template_location"].split("/").pop())
        self.variables["SOLUTION_TYPE"] = self.resolve_solution_type()
        self.variables["STACK_TYPE_TXT"] = stack_type_text
        if docs is not None:
            self.variables["DOCUMENTAION"] = docs
        else:
            self.variables["DOCUMENTAION"] = ""
        if additional_security_notes is not None:
            self.variables["ADDITIONAL_SECURITY"] = additional_security_notes
        else:
            self.variables["ADDITIONAL_SECURITY"] = ""
        if support_notes is not None:
            self.variables["SUPPORT_NOTES"] = support_notes
        else:
            self.variables["SUPPORT_NOTES"] = ""
        if supported_bigip_versions is not None:
            self.variables["SUPPORTED_BIGIP_VERSIONS"] = supported_bigip_versions
        else:
            self.variables["SUPPORTED_BIGIP_VERSIONS"] = ""
        if supported_bigip_versions is not None:
            self.variables["BACKUP_AND_RECOVERY"] = backup_and_recovery
        else:
            self.variables["BACKUP_AND_RECOVERY"] = ""
