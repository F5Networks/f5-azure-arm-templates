# f5-azure-arm-1nic

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

## Introduction

This solution implements an ARM Template to deploy a base example of F5 in a cloud-focused single NIC deployment.  This is the standard Cloud design where the compute instance of
F5 is running with a single interface, where both management and data plane traffic is processed.  This is a traditional model in the cloud where the deployment is considered one-armed.

## Documentation

Please see the project documentation - This is still being created

## Installation

You have three options for deploying this template: 
  - Using the Azure deploy button 
  - Using [PowerShell](#powershell)
  - Using [CLI Tools](#cli)

### <a name="azure"></a>Azure deploy button

Use this button to deploy the template: 

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fsupported%2Fazure-arm-1nic%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>



### <a name="powershell"></a>PowerShell

```powershell
    # Params below match to parameters in the azuredeploy.json that are gen-unique, otherwise pointing to
    # the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
    # can be supplied inline when running this script but if they are not then the default will be used as specified in the param arguments
    # Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -adminPassword yourpassword -dnsLabelPrefix f51nicdeploy01 -vmName f51nic -licenseToken XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -resourceGroupName f51nicdeploy01

    param(
    [Parameter(Mandatory=$True)]
    [string]
    $adminUsername,

    [Parameter(Mandatory=$True)]
    [string]
    $adminPassword,

    [Parameter(Mandatory=$True)]
    [string]
    $dnsLabelPrefix,

    [Parameter(Mandatory=$True)]
    [string]
    $vmName,

    [string]
    $vmSize = "Standard_D2_v2",

    [Parameter(Mandatory=$True)]
    [string]
    $licenseToken,

    [Parameter(Mandatory=$True)]
    [string]
    $resourceGroupName,

    [string]
    $region = "West US",

    [string]
    $templateFilePath = "azuredeploy.json",

    [string]
    $parametersFilePath = "azuredeploy.parameters.json",

    [Parameter(Mandatory=$True)]
    [string]
    $EmailTo
    )

    # Connect to Azure, right now it is only interactive login
    Login-AzureRmAccount

    # Create Resource Group for ARM Deployment
    New-AzureRmResourceGroup -Name $resourceGroupName -Location "$region"

    # Create Arm Deployment
    $pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabelPrefix "$dnsLabelPrefix" -vmName "$vmName" -vmSize "$vmSize" -licenseToken1 "$licensetoken"

    # Print Output of Deployment to Console
    $deployment
```


### <a name="cli"></a>Azure CLI(1.0) Usage
-----
```
    #!/bin/bash

    # Script to deploy 1nic/2nic ARM template into Azure, using azure cli 1.0
    # Example Command: ./deploy_via_bash.sh -u azureuser -p 'yourpassword' -d f51nicdeploy01 -n f51nic -l XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -r f51nicdeploy01 -y adminstrator@domain.com -z 'yourpassword'

    # Assign Script Paramters and Define Variables
    # Specify static items, change these as needed or make them parameters (vm_size is already an optional paramter)
    region="westus"
    template_file="azuredeploy.json"
    parameter_file="azuredeploy.parameters.json"
    vm_size="Standard_D2_v2"

    while getopts u:p:d:n:s:l:r:y:z: option
    do	case "$option"  in
            u) admin_username=$OPTARG;;
            p) admin_password=$OPTARG;;
            d) dns_label_prefix=$OPTARG;;
            n) vm_name=$OPTARG;;
            s) vm_size=$OPTARG;;
            l) license_token=$OPTARG;;
            r) resource_group_name=$OPTARG;;
            y) azure_user=$OPTARG;;
            z) azure_pwd=$OPTARG;;
        esac
    done
    # Check for Mandatory Args
    if [ ! "$admin_username" ] || [ ! "$admin_password" ] || [ ! "$dns_label_prefix" ] || [ ! "$vm_name" ] || [ ! "$license_token" ] || [ ! "$resource_group_name" ] || [ ! "$azure_user" ] || [ ! "$azure_pwd" ]
    then
        echo "One of the mandatory parameters was not specified!"
        exit 1
    fi


    # Login to Azure, for simplicity in this example using username and password as supplied as script arguments y and z
    azure login -u $azure_user -p $azure_pwd

    # Switch to ARM mode
    azure config mode arm

    # Create ARM Group
    azure group create -n $resource_group_name -l $region

    # Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
    # such as can been done with PowerShell...oh well!
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabelPrefix\":{\"value\":\"$dns_label_prefix\"},\"vmName\":{\"value\":\"$vm_name\"},\"vmSize\":{\"value\":\"$vm_size\"},\"licenseToken1\":{\"value\":\"$license_token\"}}"

```


## Design Patterns


The goal is for the design patterns for all the iterative examples of F5 being deployed via ARM templates to closely match as much as possible.

### List of Patterns For Contributing Developers


 1. Still working on patterns to use

## Filing Issues

See the Issues section of `Contributing <CONTRIBUTING.md>`__.

## Contributing

See `Contributing <CONTRIBUTING.md>`__

## Test


Before you open a pull request, your code must have passed a deployment into Azure with the intended result

## Unit Tests

Simply deploying the ARM template and completing use case fulfills a functional test



## Copyright

Copyright 2014-2016 F5 Networks Inc.


## License


Apache V2.0
~~~~~~~~~~~
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

Contributor License Agreement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Individuals or business entities who contribute to this project must have
completed and submitted the `F5 Contributor License Agreement`