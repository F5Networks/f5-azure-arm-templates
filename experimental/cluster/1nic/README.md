# Deploying a BIG-IP VE Cluster in Azure - Single NIC
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
## Introduction

This ARM template deploys a cluster of F5 BIG-IP VEs that ensures you have the highest level of availability for your applications. You can also enable F5's L4/L7 security features, access control, and intelligent traffic management.

When you deploy your applications using a cluster of F5 BIG-IPs, the BIG-IP VE instances are all in Active status (not Active-Standby), and are used as a single device for redundancy and scalability, rather than failover. If one device goes down, Azure keeps load balancing to the other.

Using this solution, the F5 BIG-IP VEs are fully configured in front of your application.  When complete, the BIG-IPs pass traffic through the newly created Azure Public IP.  After acceptance testing, you must complete the configuration by changing the DNS entry for your application to point at the newly created public IP address, and then lock down the Network Security Group rules to prevent any traffic from reaching your application except through the F5 BIG-IPs.

Before you deploy web applications with an F5 BIG-IP, you need a license from F5.


## Documentation

See the project documentation - This is still being created


## Installation

You have three options for deploying this template:
  - Using the Azure deploy button
  - Using [PowerShell](#powershell)
  - Using [CLI Tools](#cli)

### <a name="azure"></a>Azure deploy button

Use the following button to deploy the template.  See the Template parameters section to see the information you need to succesfully deploy the template.

**BASE (No application)**<br>
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fexperimental%2Fcluster%2F1nic%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>

## Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| deploymentName | x | A unique name for your application. |
| numberOfInstances | x | The number of BIG-IPs that will be deployed in front of your application.  The only allowed value for this template is 2. |
| instanceType | x | The desired Azure Virtual Machine instance size. |
| imageName | x | The desired F5 image to deploy. |
| adminUsername | x | A user name to login to the BIG-IPs.  The default value is "azureuser". |
| adminPassword | x | A strong password for the BIG-IPs. Remember this password; you will need it later. |
| dnsLabel | x | Unique DNS Name for the public IP address used to access the BIG-IPs for management. |
| licenseKey1 | x | The license token from the F5 licensing server. This license will be used for the first F5 BIG-IP. |
| licenseKey2 | x | The license token from the F5 licensing server. This license will be used for the second F5 BIG-IP. |
| restrictedSrcAddress | x | Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources. |
| tagValues | x | Additional key-value pair tags to be added to each Azure resource. |



### <a name="powershell"></a>PowerShell

```powershell
    # Params below match to parameteres in the azuredeploy.json that are gen-unique, otherwsie pointing to
    # the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
    # can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
    # Example Command: .\Deploy_via_PS.ps1 -solutionDeploymentName deploynamestring -numberOfInstances 2 -adminUsername azureuser -adminPassword password
    # -dnsLabel dnslabestring -licenseKey1 XXXX-XXXX-XXXX-XXXX -licenseKey2 XXXX-XXXX-XXXX-XXXX -templateFilePath .\templates\https\azuredeploy.json
    # -resourceGroupName rgname -parametersFilePath .\templates\https\azuredeploy.parameters.json

    param(
    [Parameter(Mandatory=$True)]
    [string]
    $solutionDeploymentName,

    [Parameter(Mandatory=$True)]
    [ValidateSet("2")]
    [string]
    $numberOfInstances,

    [string]
    $instanceType = "Standard_D2_v2",

    [string]
    $imageName = "Best",

    [Parameter(Mandatory=$True)]
    [string]
    $adminUsername,

    [Parameter(Mandatory=$True)]
    [string]
    $adminPassword,

    [Parameter(Mandatory=$True)]
    [string]
    $dnsLabel,

    [Parameter(Mandatory=$True)]
    [string]
    $licenseKey1,

    [Parameter(Mandatory=$True)]
    [string]
    $licenseKey2,

    [string]
    $restrictedSrcAddress  = "*",

    [Parameter(Mandatory=$True)]
    [string]
    $resourceGroupName,

    [string]
    $region = "West US",

    [string]
    $templateFilePath = "azuredeploy.json",

    [string]
    $parametersFilePath = "azuredeploy.parameters.json"
    )

    Write-Host "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged." -foregroundcolor green
    Start-Sleep -s 3

    # Connect to Azure, right now it is only interactive login
    try {
        Write-Host "Checking if already logged in!"
        Get-AzureRmSubscription | Out-Null
        Write-Host "Already logged in, continuing..."
        }
        Catch {
        Write-Host "Not logged in, please login..."
        Login-AzureRmAccount
        }

    # Create Resource Group for ARM Deployment
    New-AzureRmResourceGroup -Name $resourceGroupName -Location "$region"

    # Create Arm Deployment
    $pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force

    # Create Arm Deployment
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -solutionDeploymentName "$solutionDeploymentName" -numberOfInstances "$numberOfInstances" -instanceType "$instanceType" -imageName "$imageName" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2" -restrictedSrcAddress "$restrictedSrcAddress"

    # Print Output of Deployment to Console
    $deployment
```


### <a name="cli"></a>Azure CLI(1.0) Usage
-----
```
    #!/bin/bash

    # Bash Script to deploy ARM template into Azure, using azure cli 1.0
    # Example Command: ./deploy_via_bash.sh --sdname sdname01 --nbrinstances 2 --adminusr azureuser --adminpwd 'password' --dnslabel label01 --key1 XXXX-XXXX --key2 XXXX-XXXX --rgname examplerg --azureusr loginuser --azurepwd loginpwd

    # Assign Script Paramters and Define Variables
    # Specify static items, change these as needed or make them parameters (instance_type is already an optional paramter)
    region="westus"
    template_file="azuredeploy.json"
    parameter_file="azuredeploy.parameters.json"
    instance_type="Standard_D2_v2"
    image_name="Best"
    restricted_source_address="*"
    tag_values="{\"application\":\"APP\",\"environment\":\"ENV\",\"group\":\"GROUP\",\"owner\":\"OWNER\",\"cost\":\"COST\"}"


    ARGS=`getopt -o a:b:c:d:e:f:g:h:i:j:k:l:m: --long sdname:,nbrinstances:,adminusr:,adminpwd:,insttype:,imgname:,dnslabel:,key1:,key2:,rstsrcaddr:,rgname:,azureusr:,azurepwd: -n $0 -- "$@"`
    eval set -- "$ARGS"


    # Parse the command line arguments, primarily checking full params as short params are just placeholders
    while true; do
        case "$1" in
            -a|--sdname)
                solution_deployment_name=$2
                shift 2;;
            -b|--nbrinstances)
                number_of_instances=$2
                shift 2;;
            -c|--adminusr)
                admin_username=$2
                shift 2;;
            -d|--adminpwd)
                admin_password=$2
                shift 2;;
            -e|--insttype)
                instance_type=$2
                shift 2;;
            -f|--imgname)
                image_name=$2
                shift 2;;
            -g|--dnslabel)
                dns_label=$2
                shift 2;;
            -h|--key1)
                license_key_1=$2
                shift 2;;
            -i|--key2)
                license_key_2=$2
                shift 2;;
            -j|--rstsrcaddr)
                restricted_source_address=$2
                shift 2;;
            -k|--rgname)
                resource_group_name=$2
                shift 2;;
            -l|--azureusr)
                azure_user=$2
                shift 2;;
            -m|--azurepwd)
                azure_pwd=$2
                shift 2;;
            --)
                shift
                break;;
        esac
    done

    echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
    sleep 3

    #If a required paramater is not passed, the script will prompt for it below
    required_variables="solution_deployment_name number_of_instances admin_username admin_password dns_label license_key_1 license_key_2 resource_group_name azure_user azure_pwd"
    for variable in $required_variables
            do
            if [ -v ${!variable} ] ; then
                    read -p "Please enter value for $variable:" $variable
            fi
    done

    # Login to Azure, for simplicity in this example using username and password supplied as script arguments --azureusr and --azurepwd
    # Perform Check to see if already logged in
    azure account show > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
            azure login -u $azure_user -p $azure_pwd
    fi

    # Switch to ARM mode
    azure config mode arm

    # Create ARM Group
    azure group create -n $resource_group_name -l $region

    # Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
    # such as can been done with Powershell...oh well!
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"solutionDeploymentName\":{\"value\":\"$solution_deployment_name\"},\"numberOfInstances\":{\"value\":$number_of_instances},\"instanceType\":{\"value\":\"$instance_type\"},\"imageName\":{\"value\":\"$image_name\"},\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"licenseKey2\":{\"value\":\"$license_key_2\"},\"restrictedSrcAddress\":{\"value\":\"$restricted_source_address\"},\"tagValues\":{\"value\":$tag_values}}"

```

## Results

This template creates a new resource group. Inside this new resource group it configures the following:

* Availability Set
* Azure Load Balancer
* Network Security Group
* Storage Account
* Public IP Address
* Network Interface objects for the F5 devices
* F5 Virtual Machines

## Connecting to the management interface of the BIG-IP VEs

After the deployment successfully finishes, you can find the BIG-IP Management UI\SSH URLs by doing the following:

* Find the Resource Group that deployed, which is the same name as the "dnsLabel".  When you click this object you see the deployment status.
* Click the Deployment Status, and then the Deployment.
* In the "Outputs" area, you find the URLs and ports you can use to connect to the F5 cluster.

## Design Patterns

The goal is for the design patterns for all the iterative examples of F5 being deployed via ARM templates to closely match as much as possible.


### List of Patterns For Contributing Developers

 1. Still working on patterns to use


## Filing Issues

See the Issues section of `Contributing <CONTRIBUTING.md>`__.


## Contributing

See `Contributing <CONTRIBUTING.md>`__


## Test

Before you open a pull request, your code must have passed a deployment into Azure with the intended result.


## Unit Tests

Simply deploying the ARM template and completing use case fulfills a functional test.


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