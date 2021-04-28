# Azure BIG-IP VE HA Template
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
## Introduction


You can deploy your web applications by creating a cluster of F5 BIG-IP VEs that uses the Local Traffic Manager™ (LTM®) module.

When you deploy your applications by using a cluster of F5 BIG-IPs, the BIG-IP VE instances are all in Active status (not Active-Standby), and are used as a single device, for redundancy and scalability, rather than failover. If one device goes down, Azure keeps load balancing to the other.

Using this solution, the F5 BIG-IP VEs are fully configured in front of your application.  When complete, the BIG-IPs pass traffic through the newly created Azure Public IP.  After acceptance testing, you must complete the configuration by changing the DNS entry for your application to point at the newly created public IP address, and then lock down the Network Security Group rules to prevent any traffic from reaching your application except through the F5 BIG-IPs.

Before you deploy web applications with an F5 BIG-IP, you need a license from F5.

You choose the license and corresponding Azure instance based on the number of cores and throughput you need. The instances listed below are minimums; you can choose larger instances if you want.

| Cores | Througput | Minimum Azure Instance |
| --- | --- | --- |
| 2 | 25 Mbps | D2_v2 |
| 4 | 200 Mbps | A3 Standard or D3_v2 |
| 8 | 1 Gbps | A4 or A7 Standard or D4v2 |

## Supported BIG-IP versions
Below is a map that shows the available options for the template parameter 'bigIpVersion' as it corresponds to the BIG-IP version itself.

| Azure BIG-IP Image Version | BIG-IP Version |
| --- | --- |
| 13.0.021 | 13.0.0 HF2 Build 2.10.1671 |
| 12.1.24 | 12.1.2 HF1 Build 1.34.271 |
| latest | This will select the latest BIG-IP version available |

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
| applicationProtocols | x | The protocol that will be used to configure the application virtual servers. The only allowed values for these templates are http, https, or https-offload. |
| applicationAddress | x | The public IP address or DNS FQDN of the application that this BIG-IP will front. |
| applicationPort | x | The unencrypted port that your application is listening on (for example, 80). This field is required in the http and https-offload deployment scenarios. |
| applicationSecurePort | x | The encrypted port that your application is listening on (for example, 443). This field is required in the https deployment scenario. |
| vaultName | x | The name of the Azure Key Vault where you have stored your SSL cert and key in .pfx format as a secret. This field is required in the https and https-offload deployment scenarios. |
| vaultResourceGroup | x | The name of the Azure Resource Group where the previously entered Key Vault is located. This field is required in the https and https-offload deployment scenarios. |
| secretUrl | x | The public URL of the Azure Key Vault secret where your SSL cert and key are stored in .pfx format. This field is required in the https and https-offload deployment scenarios. |
| certThumbprint | x | The thumbprint of the SSL cert stored in Azure Key Vault. This field is required in the https and https-offload deployment scenarios. |
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

### HTTP ###
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fexperimental%2Freference%2Fcluster%2F1nic%2Fhttp%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>

### HTTPS ###
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fexperimental%2Freference%2Fcluster%2F1nic%2Fhttps%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>

### SSL OFFLOAD ###
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fexperimental%2Freference%2Fcluster%2F1nic%2Fhttps-offload%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>


### <a name="powershell"></a>PowerShell Script Example

```powershell
    # Params below match to parameteres in the azuredeploy.json that are gen-unique, otherwsie pointing to
    # the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
    # can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
    # Example Command: .\Deploy_via_PS.ps1 -solutionDeploymentName deploynamestring -numberOfInstances 2 -adminUsername azureuser -adminPassword password
    # -dnsLabel dnslabestring -licenseKey1 XXXX-XXXX-XXXX-XXXX -licenseKey2 XXXX-XXXX-XXXX-XXXX -applicationProtocols https -applicationAddress web01.discovery.com -applicationPort OPTIONAL
    # -applicationSecurePort 443 -vaultName keyvault -vaultResourceGroup keyvaultresourcegroup -secretUrl https://secreturl -certThumbprint XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX -templateFilePath .\templates\https\azuredeploy.json
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

    [Parameter(Mandatory=$True)]
    [ValidateSet("http","https","https-offload")]
    [string]
    $applicationProtocols,

    [Parameter(Mandatory=$True)]
    [string]
    $applicationAddress,

    [string]
    $applicationPort = $(if($applicationProtocols -ne "https") { Read-Host -prompt "applicationPort"}),

    [string]
    $applicationSecurePort = $(if($applicationProtocols -ne "http") { Read-Host -prompt "applicationSecurePort"}),

    [string]
    $vaultName = $(if($applicationProtocols -ne "http") { Read-Host -prompt "vaultName"}),

    [string]
    $vaultResourceGroup = $(if($applicationProtocols -ne "http") { Read-Host -prompt "vaultResourceGroup"}),

    [string]
    $secretUrl = $(if($applicationProtocols -ne "http") { Read-Host -prompt "secretUrl"}),

    [string]
    $certThumbprint = $(if($applicationProtocols -ne "http") { Read-Host -prompt "certThumbprint"}),

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

    # Need to change parameters based on mode, also defaulting relative path if not specifically included in script execution
    if ($applicationProtocols -eq "http") {
    if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\http\azuredeploy.json"; $parametersFilePath = ".\http\azuredeploy.parameters.json" }
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -solutionDeploymentName "$solutionDeploymentName" -numberOfInstances "$numberOfInstances" -instanceType "$instanceType" -imageName "$imageName" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2" -applicationProtocols "$applicationProtocols" -applicationAddress "$applicationAddress" -restrictedSrcAddress "$restrictedSrcAddress"
    } elseif ($applicationProtocols -eq "https-offload") {
    if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\https-offload\azuredeploy.json"; $parametersFilePath = ".\https-offload\azuredeploy.parameters.json" }
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -solutionDeploymentName "$solutionDeploymentName" -numberOfInstances "$numberOfInstances" -instanceType "$instanceType" -imageName "$imageName" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2" -applicationProtocols "$applicationProtocols" -applicationAddress "$applicationAddress" -applicationSecurePort "$applicationSecurePort" -vaultName "$vaultName" -vaultResourceGroup "$vaultResourceGroup" -secretUrl "$secretUrl" -certThumbprint "$certThumbprint" -restrictedSrcAddress "$restrictedSrcAddress"
    } elseif ($applicationProtocols -eq "https") {
    if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\https\azuredeploy.json"; $parametersFilePath = ".\https\azuredeploy.parameters.json" }
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -solutionDeploymentName "$solutionDeploymentName" -numberOfInstances "$numberOfInstances" -instanceType "$instanceType" -imageName "$imageName" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2" -applicationProtocols "$applicationProtocols" -applicationAddress "$applicationAddress" -applicationSecurePort "$applicationSecurePort" -vaultName "$vaultName" -vaultResourceGroup "$vaultResourceGroup" -secretUrl "$secretUrl" -certThumbprint "$certThumbprint" -restrictedSrcAddress "$restrictedSrcAddress"
    } else {
    Write-Host "Uh oh, shouldn't get here as validating applicationProtocols variable in params!"
    exit
    }

    # Print Output of Deployment to Console
    $deployment
```


### <a name="cli"></a>Azure CLI(1.0) Usage

```
    #!/bin/bash

    # Example Script is coming...

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

## Deploying Custom Configuration to an Azure Virtual Machine

This sample code uses the CustomScript extension resource to configure the f5.ip_forwarding iApp on BIG-IP VE in Azure Resource Manager.

The CustomScript extension resource name must reference the Azure virtual machine name and must have a dependency on that virtual machine. You can use only one CustomScript extension resource per virtual machine; however, you can combine multiple semicolon-delimited commands in a single extension resource definition.

Warning: F5 does not support the template if you change anything other than the CustomScript extension resource.

```
{
     "type": "Microsoft.Compute/virtualMachines/extensions",
     "name": "[concat(variables('virtualMachineName'),'/start')]",
     "apiVersion": "2016-03-30",
     "location": "[resourceGroup().location] "
     "dependsOn": [
          "[concat('Microsoft.Compute/virtualMachines/',variables('virtualMachineName'))]"
     ],
     "properties": {
          "publisher": "Microsoft.Azure.Extensions",
          "type": "CustomScript",
          "typeHandlerVersion": "2.0",
          "settings": {
          },
          "protectedSettings": {
               "commandToExecute": "[concat('tmsh create sys application service my_deployment { device-group none template f5.ip_forwarding traffic-group none variables replace-all-with { basic__addr { value 0.0.0.0 } basic__forward_all { value No } basic__mask { value 0.0.0.0 } basic__port { value 0 } basic__vlan_listening { value default } options__advanced { value no }options__display_help { value hide } } }')]"
          }
     }
}
```

## Deploying Custom Configuration to an Azure Virtual Machine

This sample code uses the CustomScript extension resource to configure the f5.ip_forwarding iApp on BIG-IP VE in Azure Resource Manager.

The CustomScript extension resource name must reference the Azure virtual machine name and must have a dependency on that virtual machine. You can use only one CustomScript extension resource per virtual machine; however, you can combine multiple semicolon-delimited commands in a single extension resource definition.

Warning: F5 does not support the template if you change anything other than the CustomScript extension resource.

```
{
     "type": "Microsoft.Compute/virtualMachines/extensions",
     "name": "[concat(variables('virtualMachineName'),'/start')]",
     "apiVersion": "2016-03-30",
     "location": "[resourceGroup().location] "
     "dependsOn": [
          "[concat('Microsoft.Compute/virtualMachines/',variables('virtualMachineName'))]"
     ],
     "properties": {
          "publisher": "Microsoft.Azure.Extensions",
          "type": "CustomScript",
          "typeHandlerVersion": "2.0",
          "settings": {
          },
          "protectedSettings": {
               "commandToExecute": "[concat('tmsh create sys application service my_deployment { device-group none template f5.ip_forwarding traffic-group none variables replace-all-with { basic__addr { value 0.0.0.0 } basic__forward_all { value No } basic__mask { value 0.0.0.0 } basic__port { value 0 } basic__vlan_listening { value default } options__advanced { value no }options__display_help { value hide } } }')]"
          }
     }
}
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