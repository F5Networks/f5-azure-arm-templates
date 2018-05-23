#/usr/bin/python env
import sys
import os
import json

def build_deploy_cmd(base_deploy, deploy_cmd_params):
    """ Deployment Command for the Script """
    deploy_cmd = base_deploy + deploy_cmd_params
    # Return full deployment create command
    return deploy_cmd

def script_param_array(data, i_data):
    """ Create Dynamic Parameter Array - (parameter, dfl value, mandatory flag, skip flag, parameter type) """
    param_array = []
    for parameter in data['parameters']:
        mandatory = True
        skip_param = False
        try:
            if data['parameters'][parameter]['defaultValue'] != 'REQUIRED':
                default_value = data['parameters'][parameter]['defaultValue']
        except:
            default_value = None
        try:
            param_type = data['parameters'][parameter]['type']
        except:
            param_type = None
        # Specify parameters that aren't mandatory or should be skipped
        if parameter in ('restrictedSrcAddress', 'tagValues'):
            mandatory = False

        param_array.append([parameter, default_value, mandatory, skip_param, param_type])
    return param_array

def script_creation(data, i_data, language):
    """ Primary Function to Create the Deployment Script """
    ######## Define Base Set of Variables ########
    template_info = i_data['template_info']
    script_location = template_info['location']
    parameters = ''
    pwd_cmds = ''
    dict_cmds = ''
    deploy_cmd_params = ''
    required_parameters = ''
    if language == 'powershell':
        script_dash = ' -'
        meta_script = 'files/script_files/base.deploy_via_ps.ps1'
        script_loc = script_location + 'Deploy_via_PS.ps1'
        base_ex = '## Example Command: .\Deploy_via_PS.ps1'
        base_deploy = '$deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose '
        ## Specify any additional example command script parameters ##
        addtl_ex_param = ['resourceGroupName']
    elif language == 'bash':
        script_dash = ' --'
        meta_script = 'files/script_files/base.deploy_via_bash.sh'
        script_loc = script_location + 'deploy_via_bash.sh'
        base_ex = '## Example Command: ./deploy_via_bash.sh'
        base_deploy = 'azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p '
        ## Specify any additional example command script parameters ##
        addtl_ex_param = ['resourceGroupName', 'azureLoginUser', 'azureLoginPassword']
    else:
        return 'Only supporting powershell and bash for now!'

    ######## Loop through Parameter Array ########
    for parameter in script_param_array(data, i_data):
        mandatory_cmd = ''
        param_value = ','
        ## Skip parameters if skip flag set ##
        if parameter[3]:
            continue
        ## Handle mandatory parameters ##
        if parameter[2]:
            if language == 'powershell':
                mandatory_cmd = ' [Parameter(Mandatory=$True)]'
            elif language == 'bash':
                required_parameters += parameter[0] + ' '
        else:
            if isinstance(parameter[1], dict):
                param_value = " = '" + json.dumps(parameter[1]) + "',"
            else:
                param_value = ' = "' + str(parameter[1]) + '",'
        if language == 'powershell':
            if parameter[4] == 'securestring':
                param = '$' + parameter[0]
                param_secure = param + 'Secure'
                deploy_cmd_params += '-' + parameter[0] + ' ' + param_secure + ' '
                pwd_cmds += param_secure + ' = ConvertTo-SecureString -String ' + param + ' -AsPlainText -Force\n'
            else:
                deploy_cmd_params += '-' + parameter[0] + ' $' + parameter[0] + ' '
            if isinstance(parameter[1], dict):
                parameters += '\n ' + mandatory_cmd +  ' $' + parameter[0] + param_value
                dict_cmds += '(ConvertFrom-Json $' + parameter[0] + ').psobject.properties | ForEach -Begin {$' + parameter[0] + '=@{}} -process {$' + parameter[0] + '."$($_.Name)" = $_.Value}\n'
            else:
                parameters += '\n  [string]' + mandatory_cmd +  ' $' + parameter[0] + param_value
        elif language == 'bash':
            parameters += '\n        --' + parameter[0] + ')\n            ' + parameter[0] + '=$2\n            shift 2;;'
            ## Handle bash quoting for integers and dict object type in template create command ##
            if isinstance(parameter[1], int) or isinstance(parameter[1], dict):
                deploy_cmd_params += '\\"' + parameter[0] + '\\":{\\"value\\":$' + parameter[0] + '},'
            else:
                deploy_cmd_params += '\\"' + parameter[0] + '\\":{\\"value\\":\\"$' + parameter[0] + '\\"},'
        ## Add parameter to example command, use default value if exists ##
        if parameter[2]:
            if parameter[1] or isinstance(parameter[1], int):
                base_ex += script_dash + parameter[0] + ' ' + str(parameter[1])
            else:
                base_ex += script_dash + parameter[0] + ' ' + '<value>'

    ######## Add any additional script items ########
    if language == 'bash':
        if deploy_cmd_params[-1:] == ',':
            deploy_cmd_params = deploy_cmd_params[:-1]
        deploy_cmd_params = '"{' + deploy_cmd_params + '}"'
        ## Add any additional mandatory parameters ##
        for required_param in ['resourceGroupName']:
            required_parameters += required_param + ' '
    ## Handle adding additional example command script parameters ##
    for named_param in addtl_ex_param:
        base_ex += script_dash + named_param + ' <value>'

    ######## Map in dynamic values to the Base Meta Script  ########
    with open(meta_script, 'r') as script:
        script_str = script.read()
    script_str = script_str.replace('<EXAMPLE_CMD>', base_ex)
    script_str = script_str.replace('<DEPLOYMENT_CREATE>', build_deploy_cmd(base_deploy, deploy_cmd_params))
    script_str = script_str.replace('<PWD_CMDS>', pwd_cmds)
    script_str = script_str.replace('<DICT_CMDS>', dict_cmds)
    script_str = script_str.replace('<DYNAMIC_PARAMETERS>', parameters)
    script_str = script_str.replace('<REQUIRED_PARAMETERS>', required_parameters)
    ######## Write to specified script location ########
    with open(script_loc, 'w') as script_complete:
        script_complete.write(script_str)
    ## End Script_Creation Proc
    return script_str
