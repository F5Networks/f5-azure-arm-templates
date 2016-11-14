# Deploying the BIG-IP VE in Azure - Two NIC

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Doc Status](http://readthedocs.org/projects/f5-sdk/badge/?version=latest)](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0.html)

## Introduction

- This solution implements an ARM Template to deploy a full stack example of F5 in a two NIC deployment, it also deploys a web server and configures F5 to pass traffic to that web server.

- In a two NIC implementation, interface #1 is for management and data-plane traffic from the Internet, and interface #2 is connected into the Azure networks where traffic is processed by the pool members in a traditional two-ARM design.

## Documentation

The ***BIG-IP Virtual Edition and Microsoft Azure: Setup*** guide (https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0.html) decribes how to create the configuration manually without using the ARM template.

## Installation

You have three options for deploying this template:
  - Using the Azure deploy button
  - Using [PowerShell](#powershell)

### <a name="azure"></a>Azure deploy button

Use this button to deploy the template:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fexperimental%2Freference%2Fstandalone%2F2nic+webserver%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>

### Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| adminUsername | x | A user name to login to the BIG-IPs.  The default value is "azureuser". |
| adminPassword | x | A strong password for the BIG-IPs. Remember this password; you will need it later. |
| dnsLabel | x | Unique DNS Name for the public IP address used to access the BIG-IPs for management. |
| instanceName | x | The hostname to be configured for the VM. |
| instanceType | x | The desired Azure Virtual Machine instance size. |
| imageName | x | The desired F5 image to deploy. |
| licenseKey1 | x | The license token from the F5 licensing server. This license will be used for the first F5 BIG-IP. |
| restrictedSrcAddress | x | Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources. |
| tagValues | x | Additional key-value pair tags to be added to each Azure resource. |


### <a name="powershell"></a>PowerShell Script Example

```powershell
    # Params below match to parameteres in the azuredeploy.json that are gen-unique, otherwsie pointing to
    # the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
    # can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
    # Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -adminPassword yourpassword -dnsLabel f52nicdeploy01 -instanceName f52nic -licenseKey1 XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -resourceGroupName f52nicdeploy01 -EmailTo user@f5.com

    param(
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
    $instanceName,

    [string]
    $instanceType = "Standard_D2_v2",

    [string]
    $imageName = "Best",

    [Parameter(Mandatory=$True)]
    [string]
    $licenseKey1,

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
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceName "$instanceName" -instanceType "$instanceType" -licenseKey1 "$licenseKey1" -restrictedSrcAddress "$restrictedSrcAddress" -imageName "$imageName"

    # Print Output of Deployment to Console
    $deployment
```

=======


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