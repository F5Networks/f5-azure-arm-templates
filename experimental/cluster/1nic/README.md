# Azure BIG-IP VE HA Template

## Introduction

You can deploy your web applications by creating a cluster of F5 BIG-IP VEs that uses the Local Traffic Manager™ (LTM®) module.

When you deploy your applications by using a cluster of F5 BIG-IPs, the BIG-IP VE instances are all in Active status (not Active-Standby), and are used as a single device, for redundancy and scalability, rather than failover. If one device goes down, Azure will keep load balancing to the other.

The F5 BIG-IP VEs will be fully configured in front of your application.  When completed, the BIG-IPs will pass traffic through the newly created Azure Public IP.  After acceptance testing, you will want to complete the configuration by changing the DNS entry for your application to point at the newly created public IP address, and then lock down the Network Security Group rules to prevent any traffic from reaching your application except through the F5 BIG-IPs.

Before you deploy web applications with an F5 BIG-IP, you need a license from F5.

You choose the license and corresponding Azure instance based on the number of cores and throughput you need. The instances listed below are minimums; you can choose larger instances if you want.

| Cores | Througput | Minimum Azure Instance |
| --- | --- | --- |
| 2 | 25 Mbps | D2_v2 |
| 4 | 200 Mbps | A3 Standard or D3_v2 |
| 8 | 1 Gbps | A4 or A7 Standard or D4v2 |


## Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| deploymentName | x | A unique name for your application. |
| numberOfInstances | x | The number of BIG-IPs that will be deployed in front of your application.  The only allowed value for this template is 2. |
| instanceTypee | x | The desired Azure Virtual Machine instance size. |
| f5Sku | x | The desired F5 image to deploy. |
| adminUsername | x | A user name to login to the BIG-IPs.  The default value is "azureuser". |
| adminPassword | x | A strong password for the BIG-IPs. Remember this password; you will need it later. |
| dnsLabel | x | Unique DNS Name for the public IP address used to access the BIG-IPs for management. |
| licenseKey1 | x | The license token from the F5 licensing server. This license will be used for the first F5 BIG-IP. |
| licenseKey2 | x | The license token from the F5 licensing server. This license will be used for the second F5 BIG-IP. |
| restrictedSrcAddress | x | Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources. |
| tagValues | x | Additional key-value pair tags to be added to each Azure resource. |


## Documentation

Please see the project documentation - This is still being created


## Installation

You have three options for deploying this template:
  - Using the Azure deploy button
  - Using [PowerShell](#powershell)
  - Using [CLI Tools](#cli)

### <a name="azure"></a>Azure deploy button

Use these buttons to deploy the template(s):

### BASE (No application) ###
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fexperimental%2Fcluster%2F1nic%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>


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
    $f5Sku = "Best",

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
    if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\templates\http\azuredeploy.json"; $parametersFilePath = ".\templates\http\azuredeploy.parameters.json" }
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -solutionDeploymentName "$solutionDeploymentName" -numberOfInstances "$numberOfInstances" -instanceType "$instanceType" -f5Sku "$f5Sku" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2" -restrictedSrcAddress "$restrictedSrcAddress"

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

    while getopts m:d:n:h:s:c:u:p: option
     do	case "$option"  in
             m) mode=$OPTARG;;
             d) deployment=$OPTARG;;
             n) pool_member=$OPTARG;;
             h) pool_http_port=$OPTARG;;
             s) pool_https_port=$OPTARG;;
             c) thumbprint=$OPTARG;;
             u) user=$OPTARG;;
             p) passwd=$OPTARG;;
         esac
     done

    # Check for Mandatory Args
    if [ ! "$mode" ] || [ ! "$deployment" ] || [ ! "$user" ] || [ ! "$passwd" ]
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
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$user\"},\"adminPassword\":{\"value\":\"$passwd\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"deploymentName\":{\"value\":\"$deployment_name\"},\"instanceSize\":{\"value\":\"$instance_size\"},\"licenseToken1\":{\"value\":\"$license_token\"}}"

```

## Results

This template will create a new resource group, and inside this new resource group it will configure the following:

* Availability Set
* Azure Load Balancer
* Network Security Group
* Storage Account
* Public IP Address
* Network Interface objects for the F5 devices
* F5 Virtual Machines

## Connecting to the management interface of the BIG-IP VEs

After the deployment successfully finishes, you can find the BIG-IP Management UI\SSH URLs by doing the following:

* Find the resource group that was deployed, which is the same name as the "dnsLabel".  When you click on this object you will see the deployment status.
* Click on the deployment status, and then the deployment.
* In the "Outputs" section you will find the URL's and ports that you can use to connect to the F5 cluster.

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