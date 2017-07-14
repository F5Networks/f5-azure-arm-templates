#/usr/bin/python env
import sys
import os

def lic_count_check(lic_key_count):
    """ Determine Number of Licenses Needed for BYOL Template """
    if lic_key_count > 1:
        return True
    else:
        return False

def lic_type_check(lic_type):
    """ Determine License Type for Template """
    if 'All' in lic_type:
        return True
    else:
        return lic_type

def handle_lic_cmd(language, base_deploy, deploy_cmd_params, template_info):
    """ Add License Items to Deployment Command for the Script """
    template_name = template_info['template_name']
    lic_type_all = lic_type_check(template_info['lic_support'][template_name])
    multi_lic = lic_count_check(template_info['lic_key_count'][template_name])
    if language == 'powershell':
        single_lic_cmd = ' -licenseKey1 "$licenseKey1"'
        multi_lic_cmd = ' -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2"'
        payg_cmd = ' -licensedBandwidth "$licensedBandwidth"'
        big_iq_cmd = ' -bigIqLicenseHost "$bigIqLicenseHost" -bigIqLicenseUsername "$bigIqLicenseUsername" -bigIqLicensePassword $bigiq_pwd -bigIqLicensePool "$bigIqLicensePool"'
    elif language == 'bash':
        single_lic_cmd = '\\"licenseKey1\\":{\\"value\\":\\"$licenseKey1\\"}}"'
        multi_lic_cmd = '\\"licenseKey1\\":{\\"value\\":\\"$licenseKey1\\"},\\"licenseKey2\\":{\\"value\\":\\"$licenseKey2\\"}}"'
        payg_cmd = '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
        big_iq_cmd = '\\"bigIqLicenseHost\\":{\\"value\\":\\"$bigIqLicenseHost\\"},\\"bigIqLicenseUsername\\":{\\"value\\":\\"$bigIqLicenseUsername\\"}},\\"bigIqLicensePassword\\":{\\"value\\":\\"$bigIqLicensePassword\\"}},\\"bigIqLicensePool\\":{\\"value\\":\\"$bigIqLicensePool\\"}}"'
    if lic_type_all is True:
        if multi_lic is True:
            byol_cmd = deploy_cmd_params + multi_lic_cmd
        else:
            byol_cmd = deploy_cmd_params + single_lic_cmd
        payg_cmd = deploy_cmd_params + payg_cmd
        big_iq_cmd = deploy_cmd_params + big_iq_cmd
    ## Compile full license Command ##
    if language == 'powershell':
        if lic_type_all is True:
            deploy_cmd = 'if ($licenseType -eq "BYOL") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BYOL\\azuredeploy.json"; $parametersFilePath = ".\BYOL\\azuredeploy.parameters.json" }\n  ' + base_deploy + byol_cmd + '\n} elseif ($licenseType -eq "PAYG") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\\azuredeploy.json"; $parametersFilePath = ".\PAYG\\azuredeploy.parameters.json" }\n  ' + base_deploy + payg_cmd + '\n} elseif ($licenseType -eq "BIGIQ") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BIGIQ\\azuredeploy.json"; $parametersFilePath = ".\BIGIQ\\azuredeploy.parameters.json" }\n  $bigiq_pwd = ConvertTo-SecureString -String $bigIqLicensePassword -AsPlainText -Force\n  ' + base_deploy + big_iq_cmd + '\n} else {\n  Write-Error -Message "Please select a valid license type of PAYG, BYOL or BIGIQ."\n}'
        else:
            deploy_cmd = base_deploy + deploy_cmd_params + ' -licensedBandwidth "$licensedBandwidth"'
    elif language == 'bash':
        if lic_type_all is True:
            deploy_cmd = 'if [ $licenseType == "BYOL" ]; then\n    ' + base_deploy + byol_cmd + '\nelif [ $licenseType == "PAYG" ]; then\n    ' + base_deploy + payg_cmd + '\nelif [ $licenseType == "BIGIQ" ]; then\n    ' + base_deploy + big_iq_cmd + '\nelse\n    echo "Please select a valid license type of PAYG, BYOL or BIGIQ."\n    exit 1\nfi'
        else:
            deploy_cmd = base_deploy + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
    # Return full deployment create command
    return deploy_cmd

def script_param_array(data):
    """ Create Dynamic Parameter Array - (Parameter, default value, mandatory parameter flag, skip parameter flag) """
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
        if 'license' in parameter.lower():
            skip_param = True
        elif parameter == 'tagValues':
            skip_param = True
        param_array.append([parameter, default_value, mandatory, skip_param])
    return param_array

def script_creation(template_info, data, default_payg_bw, language):
    """ Primary Function to Create the Script """
    template_name = template_info['template_name']
    script_location = template_info['location']
    lic_type_all = lic_type_check(template_info['lic_support'][template_name])
    multi_lic = lic_count_check(template_info['lic_key_count'][template_name])
    param_str = ''; mandatory_cmd = ''; pwd_cmd = ''; sps_cmd = ''; ssl_pwd_cmd = ''; lic2_param = ''
    if language == 'powershell':
        deploy_cmd_params = ''; script_dash = ' -'
        meta_script = 'files/script_files/base.deploy_via_ps.ps1'; script_loc = script_location + 'Deploy_via_PS.ps1'
        base_ex = '## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth ' + default_payg_bw
        base_deploy = '$deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose '
    elif language == 'bash':
        deploy_cmd_params = '"{'; script_dash = ' --'; lic_check = ''; lic2_check = ''
        meta_script = 'files/script_files/base.deploy_via_bash.sh'; script_loc = script_location + 'deploy_via_bash.sh'
        base_ex = '## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth ' + default_payg_bw
        base_deploy = 'azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p '
        mandatory_variables = ''; lic_params = ''
        # Need to add bash license params prior to dynamic parameters
        # Create license parameters, expand to be a for loop?
        license_args = ['licensedBandwidth', 'licenseKey1']
        if multi_lic is True:
            lic2_param = 'licenseKey2:,'
            license_args.append('licenseKey2')
            lic2_check += '    if [ -z $licenseKey2 ] ; then\n            read -p "Please enter value for licenseKey2:" licenseKey2\n    fi\n'
        for license_arg in license_args:
            param_str += '\n        --' + license_arg+ ')\n            ' + license_arg + '=$2\n            shift 2;;'
    else:
        return 'Only supporting powershell and bash for now!'

    ######## Loop through Dynamic Parameter Array ########
    for parameter in script_param_array(data):
        mandatory_cmd = ''; param_value = ',\n'
        ## Specify any parameters that should be skipped ##
        if parameter[3]:
            continue
        ## Specify any parameters that should be mandatory ##
        if parameter[2]:
            if language == 'powershell':
                mandatory_cmd = '\n  [Parameter(Mandatory=$True)]'
            elif language == 'bash':
                mandatory_variables += parameter[0] + ' '
        ## Specify non-mandatory parameters default value ##
        if parameter[2] is False:
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
            ## Handle bash quoting for int's in ARM template create command ##
            if isinstance(parameter[1], int):
                deploy_cmd_params += '\\"' + parameter[0] + '\\":{\\"value\\":$' + parameter[0] + '},'
            else:
                deploy_cmd_params += '\\"' + parameter[0] + '\\":{\\"value\\":\\"$' + parameter[0] + '\\"},'
            param_str += '\n        --' + parameter[0] + ')\n            ' + parameter[0] + '=$2\n            shift 2;;'
        ## Add parameter to example command ##
        if parameter[1]:
            ## Handle special example command cases ##
            if parameter[0] == 'restrictedSrcAddress':
                parameter[1] = '"' + str(parameter[1]) + '"'

            base_ex += script_dash + parameter[0] + ' ' + str(parameter[1])
        else:
            base_ex += script_dash + parameter[0] + ' ' + '<value>'

    ######## Add additional Scripting Items, such as licensing ########
    if language == 'powershell':
        ## Specify any additional example command script parameters ##
        addtl_ex_param = ['resourceGroupName']
        ## Create license parameters ##
        if lic_type_all is True:
            if multi_lic is True:
                lic2_param = '\n\n  [string]\n  $licenseKey2 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey2"}),'
            big_iq_params = '\n\n  [string]\n  $bigIqLicenseHost = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicenseHost"}),\n\n  [string]\n  $bigIqLicenseUsername = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicenseUsername"}),\n\n  [string]\n  $bigIqLicensePassword = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicensePassword"}),\n\n  [string]\n  $bigIqLicensePool = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicensePool"}),'
            lic_params = '\n  [string]\n  $licensedBandwidth = $(if($licenseType -eq "PAYG") { Read-Host -prompt "licensedBandwidth"}),\n\n  [string]\n  $licenseKey1 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey1"}),' + lic2_param + big_iq_params
        else:
            lic_params = '\n  [string]\n  $licensedBandwidth = $(if($licenseType -eq "PAYG") { Read-Host -prompt "licensedBandwidth"}),'
        deploy_cmd = handle_lic_cmd(language, base_deploy, deploy_cmd_params, template_info)
    elif language == 'bash':
        ## Specify any additional example command script parameters ##
        addtl_ex_param = ['resourceGroupName', 'azureLoginUser', 'azureLoginPassword']
        ## Add any additional mandatory parameters ##
        for required_param in ['resourceGroupName', 'licenseType']:
            mandatory_variables += required_param + ' '
        ## Add any additional parameters to the deployment command ##
        for addtl_param in ['tagValues']:
            deploy_cmd_params += '\\"' + addtl_param + '\\":{\\"value\\":$' + addtl_param + '},'
        ## Create license parameters ##
        if lic_type_all is True:
            lic_check_big_iq = '\n# Prompt for BIGIQ parameters if not supplied and BIGIQ is selected\nif [ $licenseType == "BIGIQ" ]; then\n	big_iq_vars="bigIqLicenseHost bigIqLicenseUsername bigIqLicensePassword bigIqLicensePool"\n	for variable in $big_iq_vars\n			do\n			if [ -z ${!variable} ] ; then\n					read -p "Please enter value for $variable:" $variable\n			fi\n	done\nfi\n'
            lic_check = '# Prompt for license key if not supplied and BYOL is selected\nif [ $licenseType == "BYOL" ]; then\n    if [ -z $licenseKey1 ] ; then\n            read -p "Please enter value for licenseKey1:" licenseKey1\n    fi\n' + lic2_check + '    template_file="./BYOL/azuredeploy.json"\n    parameter_file="./BYOL/azuredeploy.parameters.json"\nfi\n# Prompt for licensed bandwidth if not supplied and PAYG is selected\nif [ $licenseType == "PAYG" ]; then\n    if [ -z $licensedBandwidth ] ; then\n            read -p "Please enter value for licensedBandwidth:" licensedBandwidth\n    fi\n    template_file="./PAYG/azuredeploy.json"\n    parameter_file="./PAYG/azuredeploy.parameters.json"\nfi' + lic_check_big_iq
        else:
            lic_check = '# Prompt for licensed bandwidth if not supplied and PAYG is selected\nif [ $licenseType == "PAYG" ]; then\n    if [ -z $licensedBandwidth ] ; then\n            read -p "Please enter value for licensedBandwidth:" licensedBandwidth\n    fi\n    template_file="./azuredeploy.json"\n    parameter_file="./azuredeploy.parameters.json"\nfi'
        deploy_cmd = handle_lic_cmd(language, base_deploy, deploy_cmd_params, template_info)

    ## Handle adding additional example command script parameters ##
    for named_param in addtl_ex_param:
        base_ex += script_dash + named_param + ' <value>'

    ######## Map in Dynamic values to the Base Meta Script  ########
    with open(meta_script, 'r') as script:
        script_str = script.read()
    script_str = script_str.replace('<EXAMPLE_CMD>', base_ex)
    script_str = script_str.replace('<DEPLOYMENT_CREATE>', deploy_cmd)
    script_str = script_str.replace('<PWD_CMD>', pwd_cmd)
    script_str = script_str.replace('<SPS_CMD>', sps_cmd)
    script_str = script_str.replace('<SSL_PWD_CMD>', ssl_pwd_cmd)
    script_str = script_str.replace('<LICENSE_PARAMETERS>', lic_params)
    script_str = script_str.replace('<DYNAMIC_PARAMETERS>', param_str)
    if language == 'bash':
        script_str = script_str.replace('<REQUIRED_PARAMETERS>', mandatory_variables)
        script_str = script_str.replace('<LICENSE_CHECK>', lic_check)
    # Write to actual script location
    with open(script_loc, 'w') as script_complete:
        script_complete.write(script_str)
    ## End Script_Creation Proc
    return script_str
