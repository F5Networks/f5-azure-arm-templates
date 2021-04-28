""" Template Generator main module """

import os
import json
import errno
import base64
import argparse
import logging as log
import yaml

from jinja2 import Environment, FileSystemLoader

import master_helper  # pylint: disable=import-error
import script_generator  # pylint: disable=import-error
import readme_generator  # pylint: disable=import-error

log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FACTORY_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_REPO_PATH = os.path.normpath(os.path.join(FACTORY_PATH, '../../../'))

STRUCTURE_FILES = {
    'azure': os.path.join(FACTORY_PATH, 'azure/azure_input.yaml'),
    'azureStack': os.path.join(FACTORY_PATH, 'azure/azure_input.yaml'),
    'gce': os.path.join(FACTORY_PATH, 'gce/gce_input.yaml')
}
CLOUDS = STRUCTURE_FILES.keys()

# load constants file
with open(os.path.join(FACTORY_PATH, 'common/constants.yml')) as _f:
    CONST_DATA = yaml.full_load(_f.read())

# CHANGE VARIABLES AT RELEASE TIME
F5_AZURE_CONTENT_VERSION = CONST_DATA['repo_metadata']['azure']['version']
F5_AZURE_STACK_CONTENT_VERSION = CONST_DATA['repo_metadata']['azureStack']['version']
F5_GOOGLE_TEMPLATE_VERSION = CONST_DATA['repo_metadata']['gce']['version']
COMMENT_OUT = CONST_DATA['comment_out_verify']

# dictionary contains F5 cloud libraries and paths
REPO_DEPENDENCIES = CONST_DATA['repo_dependencies']


########################################################################################
# Helper function to retrieve latest versions of F5 cloud libraries from constants file
########################################################################################
def get_repo_dependency_versions():
    """Create doc string """
    return {i: REPO_DEPENDENCIES[i]['version'] for i in REPO_DEPENDENCIES}


class Template(object):
    """Class to render terraform template."""

    def __init__(self, cloud, name):
        # Define a lookup order:
        #   - old-style templates first (e.g., ./aws)
        #   - cloud-specific template (e.g., ./clouds/aws)
        #   - root directory
        #   - base templates (./base directory)
        searchpath = [os.path.join(FACTORY_PATH, cloud)]
        loader = FileSystemLoader(searchpath)
        env = Environment(loader=loader)
        self.template = env.get_template(name)

    def render_to_file(self, variables, path):
        """Render template with Jinja2 blocks."""

        self.template.stream(variables).dump(path)

    @staticmethod
    def sort_block(path, block_name):
        """ Sort JSON data """

        with open(path, 'r+') as _file:
            template_data = json.load(_file)
            template_data[block_name] = json.loads(
                json.dumps(template_data[block_name], sort_keys=False, ensure_ascii=False, indent=4)
            )
        with open(path, 'w') as _file:
            json.dump(template_data, _file, indent=4)


def make_dir(path):
    """Create doc string """
    try:
        os.mkdir(path)
    except OSError as err:
        if err.errno == errno.EEXIST:
            pass
        else:
            raise


# temporary here for backward compatibility with old read.me generator
def compatible_template_name(variables):
    """Create doc string """
    template_name = ''
    nics = variables['nics']
    if nics == "n":
        nics += "-"
    if variables['type'] in ("failover", "autoscale"):
        lb_method = variables['lb_method']
        if '-' in lb_method:
            lb_method = lb_method.split('-')[1]
    if variables['type'] == "standalone":
        template_name = "%s_%snic" % (variables['type'], nics)
    elif variables['type'] == "failover":
        template_name = "%s-%s_%snic" % (variables['type'], lb_method, nics)
    elif variables['type'] == 'autoscale':
        template_name = "%s_%s_%s" % (variables['type'], variables['solution'], lb_method)
    elif variables['type'] == "bigiq":
        template_name = "%s_%s_%snic" % (
            variables['type'], variables['bigiq_solution'], variables['nics'])
    return template_name


def get_verify_hash(release_prep, tag, cloud):
    """Get verify hash

    Notes
    ----
    Azure consumes verify hash as a string, which requires escaping
    Google consumes verify hash as a base64 encoded string, to avoid escaping

    Parameters
    ----------
    release_prep : bool
        flag which will perform additional steps (such as download fresh verify hash)
    tag: str
        cloud libs tag to download hash from
    cloud : str
        indicates cloud, results in different formatting (see Notes section)


    Returns
    -------
    str
        the verify hash file contents as a string
    """
    # Automate Verify Hash - the verify_hash function will go out and pull in the latest hash file
    # if release-prep flag is included.  Otherwise it will pull from local verifyHash file
    cloud_libs_base_url = 'https://raw.githubusercontent.com/F5Networks/f5-cloud-libs'
    verify_hash_url = '%s/%s/dist/verifyHash' % (cloud_libs_base_url, tag)
    verify_hash = master_helper.verify_hash(verify_hash_url, release_prep)

    # different clouds handle the hash in unique ways, account for that
    if cloud == 'azure':
        verify_hash = verify_hash.replace('\n', '\\n').replace('\"', '\\\"')
    elif cloud == 'gce':
        verify_hash = base64.b64encode(verify_hash.encode('ascii')).decode('ascii')
    return verify_hash


class TemplateParser(object):
    """Create class doc string """
    template_name = ""
    result_file = ""

    def __init__(self, parameters, additional_parameters={}):  # pylint: disable=dangerous-default-value
        """Create doc string """
        self.parameters = parameters
        self.additional_parameters = additional_parameters

    @staticmethod
    def make_dir(path):
        """Create doc string """
        try:
            os.mkdir(path)
        except OSError as err:
            if err.errno == errno.EEXIST:
                pass
            else:
                raise

    def setup(self):
        """Create doc string """

    def parse_parameters(self, parameters=None, path='', variables={}):  # pylint: disable=dangerous-default-value
        """Create doc string """
        if not parameters:
            parameters = self.parameters
        path = os.path.join(path, parameters["path"])
        variables[parameters['name']] = parameters['value']
        self.make_dir(path)
        for subtype in parameters['subtypes']:
            if subtype.get('subtypes'):
                self.parse_parameters(subtype, path, variables)
            else:
                variables[subtype['name']] = subtype['value']
                variables.update(self.additional_parameters)
                final_path = os.path.join(path, subtype["path"])
                self.make_dir(final_path)
                variables.update({"template_path": final_path})
                self.parse_template(final_path, variables)

    # Implement me in each Cloud Parser
    def parse_template(self, result_path, variables):
        """Create doc string """

    # Parent function of 'write_template()'
    # If additional processing (ex: sorting Azure Templates) is needed,
    # implement in Cloud Specific Provider
    def write_template(self, template_path, variables):
        """Create doc string """
        template = Template(variables['cloud'], self.template_name)
        result_file = os.path.join(FACTORY_PATH, template_path, self.result_file)
        template.render_to_file(variables, result_file)

    # Implement me in each Cloud Parser
    def get_cloud_specific_variables(self):  # pylint: disable=no-self-use
        """Get cloud-specific variables."""
        return {}

    # Implement me in each Cloud Parser
    def create_readme_and_script(self, template_location, variables):
        """Create doc string """


class AzureTemplateParser(TemplateParser):
    """Create class doc string """
    result_file = 'azuredeploy.json'
    RESULT_PARAMETERS_FILE = 'azuredeploy.parameters.json'
    template_name = "base.azuredeploy.json"

    def __init__(self, parameters=None, additional_parameters=None):
        """Create doc string """
        super(AzureTemplateParser, self).__init__(
            parameters=parameters, additional_parameters=additional_parameters
        )
        self.parameters = parameters
        self.additional_parameters = additional_parameters
        if additional_parameters['environment'] == 'azurestack':
            self.f5_networks_tag = f"v{F5_AZURE_STACK_CONTENT_VERSION}"
            self.additional_parameters['latest_content_version'] = F5_AZURE_STACK_CONTENT_VERSION
        else:
            self.f5_networks_tag = f"v{F5_AZURE_CONTENT_VERSION}"
            self.additional_parameters['latest_content_version'] = F5_AZURE_CONTENT_VERSION

    def setup(self):
        self.additional_parameters.update(self.get_cloud_specific_variables())

    def parse_template(self, result_path, variables):
        log.info(result_path)
        self.write_template(template_path=result_path, variables=variables)
        result_file = os.path.join(FACTORY_PATH, result_path, self.result_file)
        self.create_readme_and_script(os.path.join(FACTORY_PATH, result_path), variables)
        self.parse_parameters_file(variables, result_path, result_file)

    def write_template(self, template_path, variables):
        template = Template(variables['cloud'], self.template_name)
        result_file = os.path.join(FACTORY_PATH, template_path, self.result_file)
        template.render_to_file(variables, result_file)
        # Sort, and format each section in Azure Template
        template.sort_block(result_file, "parameters")
        template.sort_block(result_file, "variables")
        template.sort_block(result_file, "resources")

    def get_cloud_specific_variables(self):
        return {
            'verify_hash': self.additional_parameters['verify_hash'],
            'f5_networks_tag': self.f5_networks_tag,
            'f5_networks_latest_tag': self.f5_networks_tag
        }

    def parse_parameters_file(self, variables, result_path, result_file, cloud='azure'):
        """Create doc string """
        template = Template(cloud, "base.azuredeploy.parameters.json")
        result_parameters_file = os.path.join(
            FACTORY_PATH, result_path, self.RESULT_PARAMETERS_FILE)
        with open(result_file, 'r+') as _file:
            template_data = json.load(_file)
        parameters = template_data["parameters"]
        data_params = {}
        for parameter in parameters:
            # Add parameters into parameters file
            data_params[parameter] = {"value": parameters[parameter].get('defaultValue', '')}
        data_param_json = json.dumps(data_params, indent=4)
        variables.update({"parameters": data_param_json})
        template.render_to_file(variables, result_parameters_file)
        template.sort_block(result_parameters_file, "parameters")
        # create parameters files for azure

    # temporary here for backward compatibility with old read.me generator
    @staticmethod
    def compatible_template_name(variables):
        """Create doc string """
        nics = variables['nics']
        if nics == "n":
            nics += "-"
        if variables['type'] in ("failover", "autoscale"):
            lb_method = variables['lb_method']
            if '-' in lb_method:
                lb_method = lb_method.split('-')[1]

        if variables['type'] == "standalone":
            return "%s_%snic" % (variables['type'], nics)
        if variables['type'] == "failover":
            if lb_method == 'api':
                return "%s-%s" % (variables['type'], lb_method)
            return "%s-%s_%snic" % (variables['type'], lb_method, nics)
        if variables['type'] == 'autoscale':
            return "%s_%s" % (variables['solution'], lb_method)
        return ''

    def create_readme_and_script(self, template_location, variables):
        """Create doc string """
        template_info = {
            'template_name': compatible_template_name(variables),
            'location': template_location + '/',
            'api_access_required': {
                'standalone_1nic': None,
                'standalone_2nic': None,
                'standalone_3nic': None,
                'standalone_n-nic': None,
                'failover-lb_1nic': None,
                'failover-lb_3nic': None,
                'failover-api_3nic': 'required',
                'failover-api_2nic': 'required',
                'autoscale_ltm_lb': 'required',
                'autoscale_ltm_dns': 'required',
                'autoscale_waf_dns': {
                    'existing-stack': {
                        'bigiq': 'required',
                        'payg': 'required'
                    },
                    'new-stack': {
                        'bigiq': 'required',
                        'payg': 'required'
                    }
                },
                'autoscale_waf_lb': {
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
                },
                'bigiq_standalone_2nic': None,
                'bigiq_cluster_2nic': None
            }
        }
        split_path = template_location.split('/')
        split_path[0] = ''
        split_path.append(self.result_file)
        i_data = {
            'template_info': template_info,
            'readme_text': {},
            'template_location': '/'.join(split_path),
            'environment': variables['environment'],
            'files': {}
        }

        bash_script = ""
        ps_script = ""
        data = None

        # Create/Modify Scripts
        # Manually adding templates to create scripts proc for now as a 'check'...
        if template_info['template_name'] in (
                'standalone_1nic', 'standalone_2nic', 'standalone_3nic', 'standalone_n-nic',
                'failover-lb_1nic', 'failover-lb_3nic', 'failover-api_n-nic',
                'autoscale_ltm_lb', 'autoscale_ltm_dns', 'autoscale_waf_lb', 'autoscale_waf_dns',
                'bigiq_standalone_2nic', 'bigiq_cluster_2nic') and template_location:
            with open(os.path.join(template_location, self.result_file), 'r') as _file:
                data = yaml.load(_file.read())
            bash_script = script_generator.script_creation(data, i_data, 'bash')
            ps_script = script_generator.script_creation(data, i_data, 'powershell')
        # END Create/Modify Scripts

        # Create/Modify README's
        readme_text = {'deploy_links': {}, 'ps_script': {}, 'bash_script': {}}
        # Deploy Buttons
        readme_text['deploy_links']['version_tag'] = variables['f5_networks_tag']
        readme_text['deploy_links']['license_type'] = variables['license_type']
        # Example Scripts - These are set above, just adding to README
        readme_text['bash_script'] = bash_script
        readme_text['ps_script'] = ps_script
        i_data['readme_text'] = readme_text

        # Call function to create/update README
        i_data['files']['doc_text_file'] = os.path.join(
            FACTORY_PATH, variables["cloud"], 'files/readme_files/template_text.yaml')
        i_data['files']['base_readme'] = os.path.join(
            FACTORY_PATH, variables["cloud"], 'files/readme_files/base.README.md')
        if template_info['template_name'] in ('bigiq_standalone_2nic', 'bigiq_cluster_2nic'):
            i_data['files']['base_readme'] = os.path.join(
                FACTORY_PATH, variables["cloud"], 'files/readme_files/base.BIGIQ_README.md')
        readme_gen = readme_generator.ReadmeGen(data, i_data, variables)
        readme_gen.create()
        # Use BIGIQ_README base for BIG-IQ templates
        if template_info['template_name'] in ('bigiq_standalone_2nic', 'bigiq_cluster_2nic'):
            base_readme_file = 'base.BIGIQ_README.md'
        else:
            base_readme_file = 'base.README.md'
        template = Template('azure', f"files/readme_files/{base_readme_file}")
        template.render_to_file(variables, os.path.join(template_location, "README.md"))


class GoogleTemplateParser(TemplateParser):
    """Create class doc string """
    result_file = ""
    parameters_file = ""
    template_name = ""
    cloud = "gce"

    def __init__(self, parameters, additional_parameters):
        """Create class doc string """
        super(GoogleTemplateParser, self).__init__(
            parameters=parameters, additional_parameters=additional_parameters)
        self.f5_networks_tag = f"v{F5_GOOGLE_TEMPLATE_VERSION}"
        self.additional_parameters['latest_content_version'] = F5_GOOGLE_TEMPLATE_VERSION
        self.additional_parameters['comment_out'] = COMMENT_OUT

    def setup(self):
        self.additional_parameters.update(self.get_cloud_specific_variables())

    def get_cloud_specific_variables(self):
        return {
            'verify_hash': self.additional_parameters['verify_hash'],
            'f5_networks_tag': self.f5_networks_tag,
            'f5_networks_latest_tag': self.f5_networks_tag
        }

    def parse_template(self, result_path, variables):
        log.info("Result Path:" + result_path)
        if variables["type"] == "standalone":
            result_file_name = "f5-%s-%s-%snic-bigip" % (
                variables["stack"], variables["license_type"], variables["nics"])
        elif variables["type"] == "failover":
            result_file_name = "f5-%s-same-net-cluster-%s-%snic-bigip" % (
                variables["stack"], variables["license_type"], variables["nics"])
        elif variables["type"] == "autoscale":
            result_file_name = "f5-%s-%s-bigip-%s" % (
                variables["license_type"], variables["type"], variables["solution"])

        variables.update({"name": result_file_name})
        self.result_file = result_file_name + ".py"
        self.parameters_file = result_file_name + ".py.schema"
        if variables["type"] == "standalone":
            self.template_name = variables["state"] + "/template_standalone.py.jn2"
        elif variables["type"] == "failover":
            self.template_name = variables["state"] + "/template_failover.py.jn2"
        elif variables["type"] == "autoscale":
            self.template_name = variables["state"] + "/template_autoscale.py.jn2"
        self.write_template(template_path=result_path, variables=variables)
        self.create_readme_and_script(os.path.join(FACTORY_PATH, result_path), variables)
        self.parse_parameters_file(variables, result_path)
        # Standalone, failover, and autoscale templates include schema files
        if variables["type"] in ("standalone", "failover", "autoscale"):
            self.parse_schema_file(variables, result_path)

    def parse_parameters_file(self, variables, result_path):
        """Create doc string """
        if variables["type"] == "standalone":
            template = Template(self.cloud, variables["state"] + "/template_standalone.yaml.jn2")
        elif variables["type"] == "failover":
            template = Template(self.cloud, variables["state"] + "/template_failover.yaml.jn2")
        else:
            template = Template(self.cloud, variables["state"] + "/template_autoscale.yaml.jn2")
        parameters_file_name = self.result_file.split(".")[0] + ".yaml"
        result_parameters_file = os.path.join(FACTORY_PATH, result_path, parameters_file_name)
        template.render_to_file(variables, result_parameters_file)

    def parse_schema_file(self, variables, result_path):
        """Create doc string """
        if variables["type"] == "standalone":
            template = Template(self.cloud, variables["state"] + "/template_standalone.schema.jn2")
        elif variables["type"] == "failover":
            template = Template(self.cloud, variables["state"] + "/template_failover.schema.jn2")
        else:
            template = Template(self.cloud, variables["state"] + "/template_autoscale.schema.jn2")
        parameters_file_name = self.result_file.split(".")[0] + ".py.schema"
        result_schema_file = os.path.join(FACTORY_PATH, result_path, parameters_file_name)
        template.render_to_file(variables, result_schema_file)

    def create_readme_and_script(self, template_location, variables):
        template_info = {
            'template_name': compatible_template_name(variables),
            'location': template_location + '/',
            'api_access_required': {
                'standalone_1nic': None,
                'standalone_2nic': None,
                'standalone_3nic': None,
                'failover-lb_3nic': None,
                'failover-api_3nic': 'required',
                'failover-api_2nic': 'required',
                'autoscale_waf_lb': 'required'
            }
        }

        split_path = template_location.split('/')
        split_path[0] = ''
        split_path.append(self.result_file)
        i_data = {
            'template_info': template_info,
            'readme_text': {},
            'template_location': '/'.join(split_path),
            'environment': variables['environment'],
            'files': {}
        }

        log.debug("Template: %s" % (template_info['template_name']))
        if template_info['template_name'] in (
                'standalone_1nic', 'standalone_2nic', 'standalone_3nic',
                'failover-lb_3nic', 'failover-api_3nic', 'failover-api_2nic',
                'autoscale_waf_lb') and template_info['location']:
            data = None
            with open(os.path.join(template_location, self.parameters_file), 'r') as _file:
                data = yaml.full_load(_file.read())

        template_parameters = {
            'parameters': data["properties"]
        }

        # Include required filed for every property
        for item in template_parameters["parameters"]:
            if item in data["required"]:
                template_parameters["parameters"][item]["required"] = "Yes"
            else:
                template_parameters["parameters"][item]["required"] = "No"

        readme_text = {'deploy_links': {}}
        # Deploy Buttons
        readme_text['deploy_links']['version_tag'] = variables['f5_networks_tag']
        readme_text['deploy_links']['license_type'] = variables['license_type']
        # Example Scripts - These are set above, just adding to README
        i_data['readme_text'] = readme_text

        # Call function to create/update README
        i_data['files']['doc_text_file'] = os.path.join(
            FACTORY_PATH, variables["cloud"], 'files/readme_files/template_text.yaml')
        i_data['files']['base_readme'] = os.path.join(
            FACTORY_PATH, variables["cloud"], 'files/readme_files/base.README.md.jn2')
        readme_gen = readme_generator.ReadmeGen(template_parameters, i_data, variables)
        readme_gen.create()
        result_readme_file = os.path.join(template_location, "README.md")
        template = Template(self.cloud, "files/readme_files/base.README.md.jn2")
        template.render_to_file(variables, result_readme_file)


class UnsupportedCloudError(Exception):
    """Unsupported cloud exception."""


def parse_args():
    """Parse arguments

    Parameters
    ----------
    None


    Returns
    -------
    dict
        a dictionary of parsed arguments
        {
            'arg': 'foo'
        }
    """

    parser = argparse.ArgumentParser(description='Template factory')
    parser.add_argument("-r", "--release-prep", action="store_true", default=False,
                        help="Release Prep Flag: If passed will equal True.")
    # add cloud switches to argument parser
    for cloud in CLOUDS:
        parser.add_argument("--%s" % cloud, action="store_true", default=False,
                            help="Generate %s templates" % cloud)

    return vars(parser.parse_args())


def create_parser(cloud, parameters, additional_parameters):
    """ Create doc string """
    if cloud == "azure":
        return AzureTemplateParser(parameters, additional_parameters)
    if cloud == "gce":
        return GoogleTemplateParser(parameters, additional_parameters)
    raise UnsupportedCloudError("Cloud type `%s' is not supported" % cloud)


def process_cloud(cloud, release_prep):
    """Create doc string """
    input_file = STRUCTURE_FILES[cloud]
    repo_dep_versions = get_repo_dependency_versions()

    with open(input_file, 'r') as _f:
        input_data = _f.read()
    cloud_parameters = yaml.full_load(input_data)

    # note: this is currently only a single item in the input file top-level array
    for _cloud in cloud_parameters:
        cloud_name = _cloud["value"]
        additional_parameters = {
            'environment': cloud,
            'verify_hash': get_verify_hash(
                release_prep, repo_dep_versions['f5_cloud_libs'], cloud_name),
            'f5_cloud_libs_latest_tag': repo_dep_versions['f5_cloud_libs'],
            'f5_cloud_libs_azure_latest_tag': repo_dep_versions['f5_cloud_libs_azure'],
            'f5_cloud_libs_gce_latest_tag': repo_dep_versions['f5_cloud_libs_gce'],
            'f5_as3_latest_tag': repo_dep_versions['f5_appsvcs_extension'],
            'f5_as3_latest_build': REPO_DEPENDENCIES['f5_appsvcs_extension']['builds']['lts'],
            'f5_cfe_latest_tag': repo_dep_versions['f5_cfe_extension'],
            'f5_cfe_latest_build': REPO_DEPENDENCIES['f5_cfe_extension']['builds']['latest']
        }

        parser = create_parser(cloud_name, _cloud, additional_parameters)
        parser.setup()
        parser.parse_parameters(path=BASE_REPO_PATH, parameters=None, variables={})


def main(args):
    """ Main function - if run as a script """
    # if a specific cloud is provided, generate templates for only the clouds explicitly
    # specified.  Allows more than one for flexibility, such as --gce and --azure
    clouds_to_process = [i for i in CLOUDS if i in args.keys() and args[i]] or CLOUDS

    # ok, now process clouds
    for cloud in clouds_to_process:
        if args[cloud]:
            log.info("Starting template and readme files generation for " + cloud + " cloud")
            process_cloud(cloud, args['release_prep'])
            log.info("Finished generating template and readme files for " + cloud + " cloud")
        else:
            log.info("Skipping %s cloud. %s" % (
                cloud,
                'Provide the corresponding input parameter to process. Example: --%s' % (cloud)
            ))


if __name__ == "__main__":
    main(args=parse_args())
