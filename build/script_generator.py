#/usr/bin/python env
import sys
import os
import json

def lic_count_check(lic_key_count):
    """ Determine Number of Licenses Needed for BYOL Template """
    if lic_key_count > 1:
        return True
    else:
        return False

def lic_type_check(lic_type):
    """ Determine License Type for Template """
    if all(x in ['PAYG', 'BIG-IQ'] for x in lic_type):
        return 'PAYG,BIGIQ'
    elif all(x in  ['PAYG', 'BIG-IQ', 'BIG-IQ+PAYG'] for x in lic_type):
        return 'PAYG,BIGIQ,BIGIQ+PAYG'
    elif all(x in ['BYOL', 'PAYG'] for x in lic_type):
        return 'BYOL,PAYG'
    # For now don't add BIGIQ+PAYG option to 'all'
    elif all(x in ['BYOL', 'PAYG', 'BIG-IQ'] for x in lic_type):
        return True
    else:
        return lic_type

def build_deploy_cmd(language, base_deploy, deploy_cmd_params, template_info):
    """ Add License Items to Deployment Command for the Script """
    template_name = template_info['template_name']
    lic_type_all = lic_type_check(template_info['lic_support'][template_name])
    multi_lic = lic_count_check(template_info['lic_key_count'][template_name])
    if language == 'powershell':
        single_lic_cmd = ' -licenseKey1 "$licenseKey1"'
        multi_lic_cmd = ' -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2"'
        payg_cmd = ' -licensedBandwidth "$licensedBandwidth"'
        big_iq_cmd = ' -bigIqAddress "$bigIqAddress" -bigIqUsername "$bigIqUsername" -bigIqPassword $bigIqPasswordSecure -bigIqLicensePoolName "$bigIqLicensePoolName" -bigIqLicenseSkuKeyword1 "$bigIqLicenseSkuKeyword1" -bigIqLicenseUnitOfMeasure "$bigIqLicenseUnitOfMeasure"'
        big_iq_payg_cmd = ' -numberOfStaticInstances $numberOfStaticInstances'
    elif language == 'bash':
        single_lic_cmd = '\\"licenseKey1\\":{\\"value\\":\\"$licenseKey1\\"}}"'
        multi_lic_cmd = '\\"licenseKey1\\":{\\"value\\":\\"$licenseKey1\\"},\\"licenseKey2\\":{\\"value\\":\\"$licenseKey2\\"}}"'
        payg_cmd = '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"'
        big_iq_cmd = '\\"bigIqAddress\\":{\\"value\\":\\"$bigIqAddress\\"},\\"bigIqUsername\\":{\\"value\\":\\"$bigIqUsername\\"}},\\"bigIqPassword\\":{\\"value\\":\\"$bigIqPassword\\"}},\\"bigIqLicensePoolName\\":{\\"value\\":\\"$bigIqLicensePoolName\\"}},\\"bigIqLicenseSkuKeyword1\\":{\\"value\\":\\"$bigIqLicenseSkuKeyword1\\"}},\\"bigIqLicenseUnitOfMeasure\\":{\\"value\\":\\"$bigIqLicenseUnitOfMeasure\\"}}"'
        big_iq_payg_cmd = ',\\"numberOfStaticInstances\\":{\\"value\\":$numberOfStaticInstances}}"'
    if multi_lic is True:
        byol_cmd = deploy_cmd_params + multi_lic_cmd
    else:
        byol_cmd = deploy_cmd_params + single_lic_cmd
    payg_cmd = deploy_cmd_params + payg_cmd
    big_iq_cmd = deploy_cmd_params + big_iq_cmd
    ## Compile full license Command ##
    if language == 'powershell':
        if_byol = 'if ($licenseType -eq "BYOL") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BYOL\\azuredeploy.json"; $parametersFilePath = ".\BYOL\\azuredeploy.parameters.json" }\n  '
        if_payg = 'if ($licenseType -eq "PAYG") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\\azuredeploy.json"; $parametersFilePath = ".\PAYG\\azuredeploy.parameters.json" }\n  '
        if_bigiq = 'if ($licenseType -eq "BIGIQ") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BIGIQ\\azuredeploy.json"; $parametersFilePath = ".\BIGIQ\\azuredeploy.parameters.json" }\n  $bigIqPasswordSecure = ConvertTo-SecureString -String $bigIqPassword -AsPlainText -Force\n  '
        if lic_type_all is True:
            deploy_cmd = if_byol + base_deploy + byol_cmd + '\n} else' + if_payg + base_deploy + payg_cmd + '\n} else' + if_bigiq + base_deploy + big_iq_cmd + '\n} else {\n  Write-Error -Message "Please select a valid license type of PAYG, BYOL or BIGIQ."\n}'
        elif lic_type_all == 'PAYG,BIGIQ':
            deploy_cmd = if_payg + base_deploy + payg_cmd + '\n} else' + if_bigiq + base_deploy + big_iq_cmd + '\n} else {\n  Write-Error -Message "Please select a valid license type of PAYG or BIGIQ."\n}'
        elif lic_type_all == 'PAYG,BIGIQ,BIGIQ+PAYG':
            deploy_cmd = if_payg + base_deploy + payg_cmd + '\n} else' + if_bigiq + base_deploy + big_iq_cmd + '\n} elseif ($licenseType -eq "BIGIQ_PAYG") {\n  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BIGIQ_PAYG\\azuredeploy.json"; $parametersFilePath = ".\BIGIQ_PAYG\\azuredeploy.parameters.json" }\n  $bigIqPasswordSecure = ConvertTo-SecureString -String $bigIqPassword -AsPlainText -Force\n  ' + base_deploy + big_iq_cmd + big_iq_payg_cmd + '\n} else {\n  Write-Error -Message "Please select a valid license type of PAYG, BIGIQ or BIGIQ_PAYG."\n}'
        elif lic_type_all == 'BYOL,PAYG':
            deploy_cmd = if_byol + base_deploy + byol_cmd + '\n} else' + if_payg + base_deploy + payg_cmd + '\n} else {\n  Write-Error -Message "Please select a valid license type of PAYG or BYOL."\n}'
        else:
            deploy_cmd = if_payg + base_deploy + deploy_cmd_params + ' -licensedBandwidth "$licensedBandwidth"' + '\n} else {\n  Write-Error -Message "Please select a valid license type of PAYG."\n}'
    elif language == 'bash':
        if lic_type_all is True:
            deploy_cmd = 'if [ $licenseType == "BYOL" ]; then\n    ' + base_deploy + byol_cmd + '\nelif [ $licenseType == "PAYG" ]; then\n    ' + base_deploy + payg_cmd + '\nelif [ $licenseType == "BIGIQ" ]; then\n    ' + base_deploy + big_iq_cmd + '\nelse\n    echo "Please select a valid license type of PAYG, BYOL or BIGIQ."\n    exit 1\nfi'
        elif lic_type_all == 'PAYG,BIGIQ':
            deploy_cmd = 'if [ $licenseType == "PAYG" ]; then\n    ' + base_deploy + payg_cmd + '\nelif [ $licenseType == "BIGIQ" ]; then\n    ' + base_deploy + big_iq_cmd + '\nelse\n    echo "Please select a valid license type of PAYG or BIGIQ."\n    exit 1\nfi'
        elif lic_type_all == 'PAYG,BIGIQ,BIGIQ+PAYG':
            deploy_cmd = 'if [ $licenseType == "PAYG" ]; then\n    ' + base_deploy + payg_cmd + '\nelif [ $licenseType == "BIGIQ" ]; then\n    ' + base_deploy + big_iq_cmd + '\nelif [ $licenseType == "BIGIQ_PAYG" ]; then\n    ' + base_deploy + big_iq_cmd[:-1] + big_iq_payg_cmd + '\nelse\n    echo "Please select a valid license type of PAYG, BIGIQ or BIGIQ_PAYG."\n    exit 1\nfi'
        elif lic_type_all == 'BYOL,PAYG':
            deploy_cmd = 'if [ $licenseType == "BYOL" ]; then\n    ' + base_deploy + byol_cmd + '\nelif [ $licenseType == "PAYG" ]; then\n    ' + base_deploy + payg_cmd + '\nelse\n    echo "Please select a valid license type of PAYG or BYOL."\n    exit 1\nfi'
        else:
            deploy_cmd = 'if [ $licenseType == "PAYG" ]; then\n    '  + base_deploy + deploy_cmd_params + '\\"licensedBandwidth\\":{\\"value\\":\\"$licensedBandwidth\\"}}"' + '\nelse\n    echo "Please select a valid license type of PAYG."\n    exit 1\nfi'
    # Return full deployment create command
    return deploy_cmd

def script_param_array(data, i_data):
    """ Create Dynamic Parameter Array - (Parameter, default value, mandatory parameter flag, skip parameter flag) """
    param_array = []
    for parameter in data['parameters']:
        mandatory = True; skip_param = False
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
        if parameter in i_data['license_params']:
            skip_param = True
        param_array.append([parameter, default_value, mandatory, skip_param, param_type])
    return param_array

def script_creation(data, i_data, language):
    """ Primary Function to Create the Deployment Script """
    ######## Define Base Set of Variables ########
    template_info = i_data['template_info']
    default_payg_bw = i_data['default_payg_bw']
    template_name = template_info['template_name']
    script_location = template_info['location']
    lic_type_all = lic_type_check(template_info['lic_support'][template_name])
    multi_lic = lic_count_check(template_info['lic_key_count'][template_name])
    param_str = ''; pwd_cmds = ''; dict_cmds = ''; lic2_param = ''; mandatory_vars = ''; lic_check = ''; lic2_check = ''; lic_params = ''
    if language == 'powershell':
        deploy_cmd_params = ''; script_dash = ' -'
        meta_script = 'files/script_files/base.deploy_via_ps.ps1'; script_loc = script_location + 'Deploy_via_PS.ps1'
        base_ex = '## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth ' + default_payg_bw
        base_deploy = '$deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose '
        ###### Create license parameters ######
        if multi_lic is True:
            lic2_param = '\n  [string] $licenseKey2 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey2"}),'
        payg_params = '  [string] $licensedBandwidth = $(if($licenseType -eq "PAYG") { Read-Host -prompt "licensedBandwidth"}),'
        big_iq_params = '\n  [string] $bigIqAddress = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqAddress"}),\n  [string] $bigIqUsername = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqUsername"}),\n  [string] $bigIqPassword = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqPassword"}),\n  [string] $bigIqLicensePoolName = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicensePoolName"}),\n  [string] $bigIqLicenseSkuKeyword1 = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicenseSkuKeyword1"}),\n  [string] $bigIqLicenseUnitOfMeasure = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicenseUnitOfMeasure"}),'
        big_iq_payg_params = '  [string] $licensedBandwidth = $(if($licenseType -like "*PAYG*") { Read-Host -prompt "licensedBandwidth"}),\n  [string] $bigIqAddress = $(if($licenseType -like "*BIGIQ*") { Read-Host -prompt "bigIqAddress"}),\n  [string] $bigIqUsername = $(if($licenseType -like "*BIGIQ*") { Read-Host -prompt "bigIqUsername"}),\n  [string] $bigIqPassword = $(if($licenseType -like "*BIGIQ*") { Read-Host -prompt "bigIqPassword"}),\n  [string] $bigIqLicensePoolName = $(if($licenseType -like "*BIGIQ*") { Read-Host -prompt "bigIqLicensePoolName"}),\n  [string] $bigIqLicenseSkuKeyword1 = $(if($licenseType -like "*BIGIQ*") { Read-Host -prompt "bigIqLicenseSkuKeyword1"}),\n  [string] $bigIqLicenseUnitOfMeasure = $(if($licenseType -like "*BIGIQ*") { Read-Host -prompt "bigIqLicenseUnitOfMeasure"}),\n  [string] $numberOfStaticInstances = $(if($licenseType -eq "BIGIQ_PAYG") { Read-Host -prompt "numberOfStaticInstances"}),'
        if lic_type_all is True:
            lic_params = payg_params + '\n  [string] $licenseKey1 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey1"}),' + lic2_param + big_iq_params
        elif lic_type_all == 'PAYG,BIGIQ':
            lic_params = payg_params + big_iq_params
        elif lic_type_all == 'PAYG,BIGIQ,BIGIQ+PAYG':
            lic_params = big_iq_payg_params
        elif lic_type_all == 'BYOL,PAYG':
            lic_params = payg_params + '\n  [string] $licenseKey1 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey1"}),' + lic2_param       
        else:
            lic_params = payg_params
        ## Specify any additional example command script parameters ##
        addtl_ex_param = ['resourceGroupName']
    elif language == 'bash':
        deploy_cmd_params = '"{'; script_dash = ' --'
        meta_script = 'files/script_files/base.deploy_via_bash.sh'; script_loc = script_location + 'deploy_via_bash.sh'
        base_ex = '## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth ' + default_payg_bw
        base_deploy = 'azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p '
        ###### Create license parameters ######

        if multi_lic is True:
            lic2_check += '    if [ -z $licenseKey2 ] ; then\n            read -p "Please enter value for licenseKey2:" licenseKey2\n    fi\n    template_file="./BYOL/azuredeploy.json"\n    parameter_file="./BYOL/azuredeploy.parameters.json"\nfi\n'

        if_byol = '# Prompt for license key if not supplied and BYOL is selected\nif [ $licenseType == "BYOL" ]; then\n    if [ -z $licenseKey1 ] ; then\n            read -p "Please enter value for licenseKey1:" licenseKey1\n    fi\n'
        byol_args = ['licenseKey1', 'licenseKey2']
        if_payg = '# Prompt for licensed bandwidth if not supplied and PAYG is selected\nif [ $licenseType == "PAYG" ]; then\n    if [ -z $licensedBandwidth ] ; then\n            read -p "Please enter value for licensedBandwidth:" licensedBandwidth\n    fi\n    template_file="./PAYG/azuredeploy.json"\n    parameter_file="./PAYG/azuredeploy.parameters.json"\nfi'
        payg_args = ['licensedBandwidth']
        if_bigiq = '\n# Prompt for BIGIQ parameters if not supplied and BIGIQ is selected\nif [ $licenseType == "BIGIQ" ]; then\n	big_iq_vars="bigIqAddress bigIqUsername bigIqPassword bigIqLicensePoolName bigIqLicenseSkuKeyword1 bigIqLicenseUnitOfMeasure"\n	for variable in $big_iq_vars\n			do\n			if [ -z ${!variable} ] ; then\n					read -p "Please enter value for $variable:" $variable\n			fi\n	done\nfi\n'
        bigiq_args = ['bigIqAddress', 'bigIqUsername', 'bigIqPassword', 'bigIqLicensePoolName', 'bigIqLicenseSkuKeyword1', 'bigIqLicenseUnitOfMeasure']
        bigiq_payg_args = ['numberOfStaticInstances']
        license_args = []
        if lic_type_all is True:
            lic_check = if_byol + lic2_check + if_payg + if_bigiq
            # BIG-IQ + PAYG not in lic_type_all for now
            license_args = byol_args + payg_args + bigiq_args
        elif lic_type_all == 'PAYG,BIGIQ':
            lic_check = if_payg + if_bigiq
            license_args = payg_args + bigiq_args
        elif lic_type_all == 'PAYG,BIGIQ,BIGIQ+PAYG':
            lic_check = if_payg + if_bigiq + '\n# Prompt for BIGIQ_PAYG parameters if not supplied and BIGIQ_PAYG is selected\nif [ $licenseType == "BIGIQ_PAYG" ]; then\n	big_iq_payg_vars="licensedBandwidth bigIqAddress bigIqUsername bigIqPassword bigIqLicensePoolName bigIqLicenseSkuKeyword1 bigIqLicenseUnitOfMeasure numberOfStaticInstances"\n	for variable in $big_iq_payg_vars\n			do\n			if [ -z ${!variable} ] ; then\n					read -p "Please enter value for $variable:" $variable\n			fi\n	done\nfi\n'
            license_args = payg_args + bigiq_args + bigiq_payg_args
        elif lic_type_all == 'BYOL,PAYG':
            lic_check = if_byol + lic2_check + if_payg
            license_args = byol_args + payg_args
        else:
            lic_check = if_payg

        if multi_lic is not True:
            license_args = [l for l in license_args if not l == 'licenseKey2']
        for license_arg in license_args:
            param_str += '\n        --' + license_arg + ')\n            ' + license_arg + '=$2\n            shift 2;;'
        ## Specify any additional example command script parameters ##
        addtl_ex_param = ['resourceGroupName', 'azureLoginUser', 'azureLoginPassword']
    else:
        return 'Only supporting powershell and bash for now!'

    ######## Loop through Dynamic Parameter Array ########
    for parameter in script_param_array(data, i_data):
        mandatory_cmd = ''; param_value = ','
        ## Skip specified parameters ##
        if parameter[3]:
            continue
        ## Set specified mandatory parameters, otherwise use default value  ##
        if parameter[2]:
            if language == 'powershell':
                mandatory_cmd = ' [Parameter(Mandatory=$True)]'
            elif language == 'bash':
                mandatory_vars += parameter[0] + ' '
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
                param_str += '\n ' + mandatory_cmd +  ' $' + parameter[0] + param_value
                dict_cmds += '(ConvertFrom-Json $' + parameter[0] + ').psobject.properties | ForEach -Begin {$' + parameter[0] + '=@{}} -process {$' + parameter[0] + '."$($_.Name)" = $_.Value}\n'
            else:
                param_str += '\n  [string]' + mandatory_cmd +  ' $' + parameter[0] + param_value
        elif language == 'bash':
            param_str += '\n        --' + parameter[0] + ')\n            ' + parameter[0] + '=$2\n            shift 2;;'
            ## Handle bash quoting for int's and dict's in template create command ##
            if isinstance(parameter[1], int) or isinstance(parameter[1], dict):
                deploy_cmd_params += '\\"' + parameter[0] + '\\":{\\"value\\":$' + parameter[0] + '},'
            else:
                deploy_cmd_params += '\\"' + parameter[0] + '\\":{\\"value\\":\\"$' + parameter[0] + '\\"},'
        ## Add parameter to example command, use default value if exists ##
        if parameter[0] not in ('restrictedSrcAddress', 'tagValues'):
            if parameter[1] or isinstance(parameter[1], int):
                base_ex += script_dash + parameter[0] + ' ' + str(parameter[1])
            else:
                base_ex += script_dash + parameter[0] + ' ' + '<value>'

    ######## Add any additional script items ########
    if language == 'bash':
        ## Add any additional mandatory parameters ##
        for required_param in ['resourceGroupName', 'licenseType']:
            mandatory_vars += required_param + ' '
    ## Handle adding additional example command script parameters ##
    for named_param in addtl_ex_param:
        base_ex += script_dash + named_param + ' <value>'

    ######## Map in Dynamic values to the Base Meta Script  ########
    with open(meta_script, 'r') as script:
        script_str = script.read()
    script_str = script_str.replace('<EXAMPLE_CMD>', base_ex)
    script_str = script_str.replace('<DEPLOYMENT_CREATE>', build_deploy_cmd(language, base_deploy, deploy_cmd_params, template_info))
    script_str = script_str.replace('<PWD_CMDS>', pwd_cmds)
    script_str = script_str.replace('<DICT_CMDS>', dict_cmds)
    script_str = script_str.replace('<LICENSE_PARAMETERS>', lic_params)
    script_str = script_str.replace('<DYNAMIC_PARAMETERS>', param_str)
    script_str = script_str.replace('<REQUIRED_PARAMETERS>', mandatory_vars)
    script_str = script_str.replace('<LICENSE_CHECK>', lic_check)
    ######## Write to specified script location ########
    with open(script_loc, 'w') as script_complete:
        script_complete.write(script_str)
    ## End Script_Creation Proc
    return script_str
