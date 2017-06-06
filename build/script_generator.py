#/usr/bin/python env
import sys
import os

### Update deployment scripts and write to appropriate location ###
def script_param_array(data, language):
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
def script_creation(template_name, data, script_location, default_payg_bw, language):
    param_str = ''; mandatory_cmd = ''; payg_cmd = ''; byol_cmd = ''; pwd_cmd = ''; sps_cmd = ''; ssl_pwd_cmd = ''; license2_param = ''
    if language == 'powershell':
        deploy_cmd_params = ''; script_dash = ' -'
        meta_script = 'base.deploy_via_ps.ps1'; script_loc = script_location + 'Deploy_via_PS.ps1'
        base_ex = '## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth ' + default_payg_bw
    elif language == 'bash':
        deploy_cmd_params = '"{'; script_dash = ' --'; license_check = ''; license2_check = ''
        meta_script = 'base.deploy_via_bash.sh'; script_loc = script_location + 'deploy_via_bash.sh'
        base_ex = '## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth ' + default_payg_bw
        mandatory_variables = ''; license_params = ''
        # Need to add bash license params prior to dynamic parameters
        # Create license parameters, expand to be a for loop?
        license_args = ['licensedBandwidth','licenseKey1']
        if template_name in ('cluster_base'):
            license2_param = 'licenseKey2:,'
            license_args.append('licenseKey2')
            license2_check += '    if [ -z $licenseKey2 ] ; then\n            read -p "Please enter value for licenseKey2:" licenseKey2\n    fi\n'
        for license_arg in license_args:
            param_str += '\n        --' + license_arg+ ')\n            ' + license_arg + '=$2\n            shift 2;;'
    else:
        return 'Only supporting powershell and bash for now!'

    # Loop through Dynamic Parameter Array
    for parameter in script_param_array(data, language):
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
            param_str += '\n        --' + parameter[0] + ')\n            ' + parameter[0] + '=$2\n            shift 2;;'
        # Add param to example command
        if parameter[1]:
            # Add quotes around restrictedSrcAddress
            if parameter[0] == 'restrictedSrcAddress':
                parameter[1] = '"' + str(parameter[1]) + '"'
            base_ex += script_dash + parameter[0] + ' ' + str(parameter[1])
        else:
            base_ex += script_dash + parameter[0] + ' ' + '<value>'

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
        license_check = '# Prompt for license key if not supplied and BYOL is selected\nif [ $licenseType == "BYOL" ]; then\n    if [ -z $licenseKey1 ] ; then\n            read -p "Please enter value for licenseKey1:" licenseKey1\n    fi\n' + license2_check + '    template_file="./BYOL/azuredeploy.json"\n    parameter_file="./BYOL/azuredeploy.parameters.json"\nfi\n# Prompt for licensed bandwidth if not supplied and PAYG is selected\nif [ $licenseType == "PAYG" ]; then\n    if [ -z $licensedBandwidth ] ; then\n            read -p "Please enter value for licensedBandwidth:" licensedBandwidth\n    fi\n    template_file="./PAYG/azuredeploy.json"\n    parameter_file="./PAYG/azuredeploy.parameters.json"\nfi'
        # Right now auto scale is only PAYG
        if template_name in ('ltm_autoscale', 'waf_autoscale'):
            license_check = '# Prompt for licensed bandwidth if not supplied and PAYG is selected\nif [ $licenseType == "PAYG" ]; then\n    if [ -z $licensedBandwidth ] ; then\n            read -p "Please enter value for licensedBandwidth:" licensedBandwidth\n    fi\n    template_file="./azuredeploy.json"\n    parameter_file="./azuredeploy.parameters.json"\nfi'
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
        elif template_name in ('cluster_base'):
            byol_cmd = create_cmd + deploy_cmd_params + '\\"licenseKey1\\":{\\"value\\":\\"$licenseKey1\\"},\\"licenseKey2\\":{\\"value\\":\\"$licenseKey2\\"}}"'
            payg_cmd = create_cmd + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
        deploy_cmd = 'if [ $licenseType == "BYOL" ]; then\n    ' + byol_cmd + '\nelif [ $licenseType == "PAYG" ]; then\n    ' + payg_cmd + '\nelse\n    echo "Please select a valid license type of PAYG or BYOL."\n    exit 1\nfi'
        if template_name in ('1nic', '2nic', '3nic', 'cluster_base'):
            deploy_cmd = 'if [ $licenseType == "BYOL" ]; then\n    ' + byol_cmd + '\nelif [ $licenseType == "PAYG" ]; then\n    ' + payg_cmd + '\nelse\n    echo "Please select a valid license type of PAYG or BYOL."\n    exit 1\nfi'
        elif template_name in ('ltm_autoscale', 'waf_autoscale'):
            deploy_cmd = create_cmd + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
    # Map necessary script items, handle encoding
    ex_cmd = base_ex
    param_str = param_str
    # Map script as needed
    with open(meta_script, 'r') as script:
        script_str = script.read()
    script_str = script_str.replace('<EXAMPLE_CMD>', ex_cmd)
    script_str = script_str.replace('<DEPLOYMENT_CREATE>', deploy_cmd)
    script_str = script_str.replace('<PWD_CMD>', pwd_cmd)
    script_str = script_str.replace('<SPS_CMD>', sps_cmd)
    script_str = script_str.replace('<SSL_PWD_CMD>', ssl_pwd_cmd)
    script_str = script_str.replace('<LICENSE_PARAMETERS>', license_params)
    script_str = script_str.replace('<DYNAMIC_PARAMETERS>', param_str)
    if language == 'bash':
        script_str = script_str.replace('<REQUIRED_PARAMETERS>', mandatory_variables)
        script_str = script_str.replace('<LICENSE_CHECK>', license_check)
    # Write to actual script location
    with open(script_loc, 'w') as script_complete:
        script_complete.write(script_str)
    ## End Script_Creation Proc
    return script_str
