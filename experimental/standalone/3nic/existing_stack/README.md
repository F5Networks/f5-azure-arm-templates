# Deploying the BIG-IP VE in Azure - 3 NIC (Traditional Deployment, Existing Networking Stack)

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

## Introduction

This solution uses an ARM template to launch a three NIC deployment of a cloud-focused BIG-IP VE in an existing stack in Microsoft Azure. Traffic flows from the BIG-IP VE to the application servers. This is the standard "on-premise like" cloud design where the compute instance of F5 is running with a management, front-end application traffic(Virtual Server) and back-end application interfaces.

This template is a result of Azure adding support for multiple public/private IP addresses for each NIC.  This template also has the ability to create specify additional Public/Private IP addresses for the external "application" NIC to be used for passing traffic to virtual servers in a more traditional fashion.

You can choose to deploy the BIG-IP VE with your own F5 BIG-IP license (BYOL), or use Pay as You Go (PAYG) licensing.



## Prerequisites and configuration notes
  - **Important**: When you configure the admin password for the BIG-IP VE in the template, you cannot use the characters **#** or **'** (single quote).
  - If you are deploying the BYOL template, you must have a valid BIG-IP license token.
  - See the **[Configuration Example](#config)** section for a configuration diagram and description for this solution.
  - See the important note about [optionally changing the BIG-IP Management port](#changing-the-big-ip-configuration-utility-gui-port).


## Security
This ARM template downloads helper code to configure the BIG-IP system. If your organization is security conscious and you want to verify the integrity of the template, you can open the template and ensure the following lines are present. See [Security Detail](#securitydetail) for the exact code.
In the *variables* section:
  - In the *verifyHash* variable: search for **script-signature** and then a hashed signature.
  - In the *installCloudLibs* variable: ensure this includes **tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz**.

Additionally, F5 provides checksums for all of our supported templates. For instructions and the checksums to compare against, see https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014.

## Supported BIG-IP versions
Below is a map that shows the available options for the template parameter 'bigIpVersion' as it corresponds to the BIG-IP version itself.

| Azure BIG-IP Image Version | BIG-IP Version |
| --- | --- |
| 13.0.021 | 13.0.0 HF2 Build 2.10.1671 |
| 12.1.24 | 12.1.2 HF1 Build 1.34.271 |
| latest | This will select the latest BIG-IP version available |

## Supported instance types and hypervisors
  - For a list of supported Azure instance types for this solutions, see the **Azure instances for BIG-IP VE** section of https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0/1.html#guid-71265d82-3a1a-43d2-bae5-892c184cc59b

  - For a list versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and Microsoft Azure, see https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html.

### Help
We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 ARM templates.  This channel is typically monitored Monday-Friday 9-5 PST by F5 employees who will offer best-effort support.<br>

While this template has been created by F5 Networks, it is in the experimental directory and therefore has not completed full testing and is subject to change.  F5 Networks does not offer technical support for templates in the experimental directory. For supported templates, see the templates in the **supported** directory.


## Installation

You have three options for deploying this solution:
  - Using the Azure deploy buttons
  - Using [PowerShell](#powershell)
  - Using [CLI Tools](#cli)

### <a name="azure"></a>Azure deploy buttons

Use the appropriate button, depending on whether you are using BYOL or PAYG licensing:

  - **BYOL** <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv3.1.4.0%2Fexperimental%2Fstandalone%2F3nic%2Fexisting_stack%2FBYOL%2Fazuredeploy.json">
    <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>

  - **PAYG** <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv3.1.4.0%2Fexperimental%2Fstandalone%2F3nic%2Fexisting_stack%2FPAYG%2Fazuredeploy.json">
    <img src="http://azuredeploy.net/deploybutton.png"/></a>

### Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| adminUsername | x | A user name to login to the BIG-IP VEs.  The default value is "azureuser". |
| adminPassword | x | A strong password for the BIG-IP VEs. This must not include **#** or **'** (single quote). Remember this password, you will need it later. |
| dnsLabel | x | Unique DNS Name for the public IP address used to access the BIG-IP VEs for management. |
| dnsLabelPrefix | x | Unique DNS Name prefix for the Public IP address(es) used to access the data plan for application traffic objects (such as virtual servers and pools). |
| instanceName | x | The hostname you want to use for the Virtual Machine. |
| instanceType | x | Azure instance size of the Virtual Machine. |
| imageName | x | The F5 image you want to deploy. |
| bigIpVersion | x | F5 BIG-IP version you want to use. |
| licenseKey1 | | For BYOL only. The license token from the F5 licensing server. This license will be used for the first F5 BIG-IP. |
| licensedBandwidth | | For PAYG only. The amount of licensed bandwidth (Mbps) you want the PAYG image to use. |
| numberOfExternalIps | x | The number of public/private IP address you want to deploy for the application traffic (external) NIC on the BIG-IP VE to be used for virtual servers. |
| vnetName | x | The name of the existing virtual network to which you want to connect the BIG-IP VEs. |
| vnetResourceGroupName | x | The name of the resource group that contains the Virtual Network where the BIG-IP VE will be placed. |
| mgmtSubnetName | x | Name of the existing MGMT subnet - with external access to Internet. |
| mgmtIpAddress | x | MGMT subnet IP Address to use for the BIG-IP management IP. |
| externalSubnetName | x | Name of the existing external subnet - with external access to Internet. |
| externalIpAddressRangeStart | x | The starting range you want to use for the private IP address(es).  This depends on how many public/private IP addresses you selected in 'numberOfExternalIps'.  For example, if you enter 10.100.1.50 here and chose 2 for numberOfExternalIps, then 10.100.1.50 is used for the BIG-IP VE self IP address, and 10.100.1.51 and 10.100.1.52 are created as static IP addresses for use as virtual servers. |
| internalIpAddress | x | Internal subnet IP Address to use for the BIG-IP internal self IP address. |
| restrictedSrcAddress | x | This field restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources. |
| tagValues | x | Additional key-value pair tags to be added to each Azure resource. |

### <a name="powershell"></a>PowerShell Script Example

```powershell
    ## Script parameters being asked for below match to parameters in the azuredeploy.json file, otherwise pointing to the ##
    ## azuredeploy.parameters.json file for values to use.  Some options below are mandatory, some(such as region) can     ##
    ## be supplied inline when running this script but if they aren't then the default will be used as specificed below.   ##
    ## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth 200m -adminUsername azureuser -adminPassword <value> -dnsLabel <value> -dnsLabelPrefix <value> -instanceName f5vm01 -instanceType Standard_D3_v2 -imageName Good -bigIpVersion 13.0.021 -numberOfExternalIps 1 -vnetName <value> -vnetResourceGroupName <value> -mgmtSubnetName <value> -mgmtIpAddress <value> -externalSubnetName <value> -externalIpAddressRangeStart <value> -internalSubnetName <value> -internalIpAddress <value> -restrictedSrcAddress "*" -resourceGroupName <value>

    param(

    [Parameter(Mandatory=$True)]
    [string]
    $licenseType,

    [string]
    $licensedBandwidth = $(if($licenseType -eq "PAYG") { Read-Host -prompt "licensedBandwidth"}),

    [string]
    $licenseKey1 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey1"}),

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
    $dnsLabelPrefix,

    [Parameter(Mandatory=$True)]
    [string]
    $instanceName,

    [Parameter(Mandatory=$True)]
    [string]
    $instanceType,

    [Parameter(Mandatory=$True)]
    [string]
    $imageName,

    [Parameter(Mandatory=$True)]
    [string]
    $bigIpVersion,

    [Parameter(Mandatory=$True)]
    [string]
    $numberOfExternalIps,

    [Parameter(Mandatory=$True)]
    [string]
    $vnetName,

    [Parameter(Mandatory=$True)]
    [string]
    $vnetResourceGroupName,

    [Parameter(Mandatory=$True)]
    [string]
    $mgmtSubnetName,

    [Parameter(Mandatory=$True)]
    [string]
    $mgmtIpAddress,

    [Parameter(Mandatory=$True)]
    [string]
    $externalSubnetName,

    [Parameter(Mandatory=$True)]
    [string]
    $externalIpAddressRangeStart,

    [Parameter(Mandatory=$True)]
    [string]
    $internalSubnetName,

    [Parameter(Mandatory=$True)]
    [string]
    $internalIpAddress,

    [string]
    $restrictedSrcAddress = "*",

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
    if ($licenseType -eq "BYOL") {
    if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BYOL\azuredeploy.json"; $parametersFilePath = ".\BYOL\azuredeploy.parameters.json" }
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -dnsLabelPrefix "$dnsLabelPrefix" -instanceName "$instanceName" -instanceType "$instanceType" -imageName "$imageName" -bigIpVersion "$bigIpVersion" -numberOfExternalIps "$numberOfExternalIps" -vnetName "$vnetName" -vnetResourceGroupName "$vnetResourceGroupName" -mgmtSubnetName "$mgmtSubnetName" -mgmtIpAddress "$mgmtIpAddress" -externalSubnetName "$externalSubnetName" -externalIpAddressRangeStart "$externalIpAddressRangeStart" -internalSubnetName "$internalSubnetName" -internalIpAddress "$internalIpAddress" -restrictedSrcAddress "$restrictedSrcAddress"  -licenseKey1 "$licenseKey1"
    } elseif ($licenseType -eq "PAYG") {
    if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\azuredeploy.json"; $parametersFilePath = ".\PAYG\azuredeploy.parameters.json" }
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -dnsLabelPrefix "$dnsLabelPrefix" -instanceName "$instanceName" -instanceType "$instanceType" -imageName "$imageName" -bigIpVersion "$bigIpVersion" -numberOfExternalIps "$numberOfExternalIps" -vnetName "$vnetName" -vnetResourceGroupName "$vnetResourceGroupName" -mgmtSubnetName "$mgmtSubnetName" -mgmtIpAddress "$mgmtIpAddress" -externalSubnetName "$externalSubnetName" -externalIpAddressRangeStart "$externalIpAddressRangeStart" -internalSubnetName "$internalSubnetName" -internalIpAddress "$internalIpAddress" -restrictedSrcAddress "$restrictedSrcAddress"  -licensedBandwidth "$licensedBandwidth"
    } else {
    Write-Error -Message "Please select a valid license type of PAYG or BYOL."
    }

    # Print Output of Deployment to Console
    $deployment

```

=======

### <a name="cli"></a>Azure CLI(1.0) Script Example

```bash
    #!/bin/bash

    ## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
    ## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth 200m --adminUsername azureuser --adminPassword <value> --dnsLabel <value> --dnsLabelPrefix <value> --instanceName f5vm01 --instanceType Standard_D3_v2 --imageName Good --bigIpVersion 13.0.021 --numberOfExternalIps 1 --vnetName <value> --vnetResourceGroupName <value> --mgmtSubnetName <value> --mgmtIpAddress <value> --externalSubnetName <value> --externalIpAddressRangeStart <value> --internalSubnetName <value> --internalIpAddress <value> --restrictedSrcAddress "*" --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

    # Assign Script Paramters and Define Variables
    # Specify static items, change these as needed or make them parameters
    region="westus"
    restrictedSrcAddress="*"
    tagValues='{"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}'

    ARGS=`getopt -o a:b:c:d:e:f:g:h:i:j:k:l:m:n:o:p:q:r:s:t:u:v:w:x: --long resourceGroupName:,azureLoginUser:,azureLoginPassword:,licenseType:,licensedBandwidth:,licenseKey1:,adminUsername:,adminPassword:,dnsLabel:,dnsLabelPrefix:,instanceName:,instanceType:,imageName:,bigIpVersion:,numberOfExternalIps:,vnetName:,vnetResourceGroupName:,mgmtSubnetName:,mgmtIpAddress:,externalSubnetName:,externalIpAddressRangeStart:,internalSubnetName:,internalIpAddress:,restrictedSrcAddress: -n $0 -- "$@"`
    eval set -- "$ARGS"

    # Parse the command line arguments, primarily checking full params as short params are just placeholders
    while true; do
        case "$1" in
            -a|--resourceGroupName)
                resourceGroupName=$2
                shift 2;;
            -b|--azureLoginUser)
                azureLoginUser=$2
                shift 2;;
            -c|--azureLoginPassword)
                azureLoginPassword=$2
                shift 2;;
            -d|--licenseType)
                licenseType=$2
                shift 2;;
            -e|--licensedBandwidth)
                licensedBandwidth=$2
                shift 2;;
            -f|--licenseKey1)
                licenseKey1=$2
                shift 2;;
            -g|--adminUsername)
                adminUsername=$2
                shift 2;;
            -h|--adminPassword)
                adminPassword=$2
                shift 2;;
            -i|--dnsLabel)
                dnsLabel=$2
                shift 2;;
            -j|--dnsLabelPrefix)
                dnsLabelPrefix=$2
                shift 2;;
            -k|--instanceName)
                instanceName=$2
                shift 2;;
            -l|--instanceType)
                instanceType=$2
                shift 2;;
            -m|--imageName)
                imageName=$2
                shift 2;;
            -n|--bigIpVersion)
                bigIpVersion=$2
                shift 2;;
            -o|--numberOfExternalIps)
                numberOfExternalIps=$2
                shift 2;;
            -p|--vnetName)
                vnetName=$2
                shift 2;;
            -q|--vnetResourceGroupName)
                vnetResourceGroupName=$2
                shift 2;;
            -r|--mgmtSubnetName)
                mgmtSubnetName=$2
                shift 2;;
            -s|--mgmtIpAddress)
                mgmtIpAddress=$2
                shift 2;;
            -t|--externalSubnetName)
                externalSubnetName=$2
                shift 2;;
            -u|--externalIpAddressRangeStart)
                externalIpAddressRangeStart=$2
                shift 2;;
            -v|--internalSubnetName)
                internalSubnetName=$2
                shift 2;;
            -w|--internalIpAddress)
                internalIpAddress=$2
                shift 2;;
            -x|--restrictedSrcAddress)
                restrictedSrcAddress=$2
                shift 2;;
            --)
                shift
                break;;
        esac
    done

    #If a required parameter is not passed, the script will prompt for it below
    required_variables="adminUsername adminPassword dnsLabel dnsLabelPrefix instanceName instanceType imageName bigIpVersion numberOfExternalIps vnetName vnetResourceGroupName mgmtSubnetName mgmtIpAddress externalSubnetName externalIpAddressRangeStart internalSubnetName internalIpAddress resourceGroupName licenseType "
    for variable in $required_variables
            do
            if [ -v ${!variable} ] ; then
                    read -p "Please enter value for $variable:" $variable
            fi
    done

    # Prompt for license key if not supplied and BYOL is selected
    if [ $licenseType == "BYOL" ]; then
        if [ -v $licenseKey1 ] ; then
                read -p "Please enter value for licenseKey1:" licenseKey1
        fi
        template_file="./BYOL/azuredeploy.json"
        parameter_file="./BYOL/azuredeploy.parameters.json"
    fi
    # Prompt for licensed bandwidth if not supplied and PAYG is selected
    if [ $licenseType == "PAYG" ]; then
        if [ -v $licensedBandwidth ] ; then
                read -p "Please enter value for licensedBandwidth:" licensedBandwidth
        fi
        template_file="./PAYG/azuredeploy.json"
        parameter_file="./PAYG/azuredeploy.parameters.json"
    fi

    echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
    sleep 3

    # Login to Azure, for simplicity in this example using username and password supplied as script arguments --azureLoginUser and --azureLoginPassword
    # Perform Check to see if already logged in
    azure account show > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
            azure login -u $azureLoginUser -p $azureLoginPassword
    fi

    # Switch to ARM mode
    azure config mode arm

    # Create ARM Group
    azure group create -n $resourceGroupName -l $region

    # Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
    if [ $licenseType == "BYOL" ]; then
        azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"dnsLabelPrefix\":{\"value\":\"$dnsLabelPrefix\"},\"instanceName\":{\"value\":\"$instanceName\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"numberOfExternalIps\":{\"value\":$numberOfExternalIps},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"mgmtIpAddress\":{\"value\":\"$mgmtIpAddress\"},\"externalSubnetName\":{\"value\":\"$externalSubnetName\"},\"externalIpAddressRangeStart\":{\"value\":\"$externalIpAddressRangeStart\"},\"internalSubnetName\":{\"value\":\"$internalSubnetName\"},\"internalIpAddress\":{\"value\":\"$internalIpAddress\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"licenseKey1\":{\"value\":\"$licenseKey1\"}}"
    elif [ $licenseType == "PAYG" ]; then
        azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"dnsLabelPrefix\":{\"value\":\"$dnsLabelPrefix\"},\"instanceName\":{\"value\":\"$instanceName\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"numberOfExternalIps\":{\"value\":$numberOfExternalIps},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"mgmtIpAddress\":{\"value\":\"$mgmtIpAddress\"},\"externalSubnetName\":{\"value\":\"$externalSubnetName\"},\"externalIpAddressRangeStart\":{\"value\":\"$externalIpAddressRangeStart\"},\"internalSubnetName\":{\"value\":\"$internalSubnetName\"},\"internalIpAddress\":{\"value\":\"$internalIpAddress\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"licensedBandwidth\":{\"value\":\"$licensedBandwidth\"}}"
    else
        echo "Please select a valid license type of PAYG or BYOL."
        exit 1
    fi
```

## Configuration Example <a name="config">

The following is a simple configuration diagram for this 3 NIC deployment.  In a 3 NIC scenario, one NIC is for management, one is for external and the last is for internal.  This is in a more traditional deployment model where data-plane and management traffic is separate.<br>
The IP addresses in this example may be different in your implementation.

![3 NIC configuration example](images/azure-3-nic.png)

### Changing the BIG-IP Configuration utility (GUI) port
The Management port shown in the example diagram is **443**, however you can alternatively use **8443** in your configuration if you need to use port 443 for application traffic.  To change the Management port, see [Changing the Configuration utility port](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-0-0/2.html#GUID-3E6920CD-A8CD-456C-AC40-33469DA6922E) for instructions.<br>
***Important***: The default port provisioned is dependent on 1) which BIG-IP version you choose to deploy as well as 2) how many interfaces (NICs) are configured on that BIG-IP. BIG-IP v13.x and later in a single-NIC configuration uses port 8443. All prior BIG-IP versions default to 443 on the MGMT interface.<br>
***Important***: If you perform the procedure to change the port, you must check the Azure Network Security Group associated with the interface on the BIG-IP that was deployed and adjust the ports accordingly.

## Documentation

The ***BIG-IP Virtual Edition and Microsoft Azure: Setup*** guide (https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0.html) describes how to create the configuration manually without using the ARM template.

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


## Security Details <a name="securitydetail"></a>
This section has the code snippet for each the lines you should ensure are present in your template file if you want to verify the integrity of the helper code in the template.

Note the hashed script-signature may be different in your template.<br>


```json
"variables": {
    "apiVersion": "2015-06-15",
    "location": "[resourceGroup().location]",
    "singleQuote": "'",
    "f5CloudLibsTag": "release-2.0.0",
    "expectedHash": "8bb8ca730dce21dff6ec129a84bdb1689d703dc2b0227adcbd16757d5eeddd767fbe7d8d54cc147521ff2232bd42eebe78259069594d159eceb86a88ea137b73",
    "verifyHash": "[concat(variables('singleQuote'), 'cli script /Common/verifyHash {\nproc script::run {} {\n        if {[catch {\n            set file_path [lindex $tmsh::argv 1]\n            set expected_hash ', variables('expectedHash'), '\n            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n            if { $expected_hash eq $computed_hash } {\n                exit 0\n            }\n            tmsh::log err {Hash does not match}\n            exit 1\n        }]} {\n            tmsh::log err {Unexpected error in verifyHash}\n            exit 1\n        }\n    }\n    script-signature fc3P5jEvm5pd4qgKzkpOFr9bNGzZFjo9pK0diwqe/LgXwpLlNbpuqoFG6kMSRnzlpL54nrnVKREf6EsBwFoz6WbfDMD3QYZ4k3zkY7aiLzOdOcJh2wECZM5z1Yve/9Vjhmpp4zXo4varPVUkHBYzzr8FPQiR6E7Nv5xOJM2ocUv7E6/2nRfJs42J70bWmGL2ZEmk0xd6gt4tRdksU3LOXhsipuEZbPxJGOPMUZL7o5xNqzU3PvnqZrLFk37bOYMTrZxte51jP/gr3+TIsWNfQEX47nxUcSGN2HYY2Fu+aHDZtdnkYgn5WogQdUAjVVBXYlB38JpX1PFHt1AMrtSIFg==\n}', variables('singleQuote'))]",
    "installCloudLibs": "[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit\nfi\necho loaded verifyHash\necho verifying f5-cloud-libs.targ.gz\n/usr/bin/tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz\nif [ $? != 0 ]; then\necho f5-cloud-libs.tar.gz is not valid\nexit\nfi\necho verified f5-cloud-libs.tar.gz\necho expanding f5-cloud-libs.tar.gz\ntar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud\ntouch /config/cloud/cloudLibsReady', variables('singleQuote'))]",
```


## Filing Issues
If you find an issue, we would love to hear about it.
You have a choice when it comes to filing issues:
  - Use the **Issues** link on the GitHub menu bar in this repository for items such as enhancement or feature requests and non-urgent bug fixes. Tell us as much as you can about what you found and how you found it.
  - Contact F5 Technical support via your typical method for more time sensitive changes and other issues requiring immediate support.



## Copyright

Copyright 2014-2017 F5 Networks Inc.


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
completed and submitted the [F5 Contributor License Agreement](http://f5-openstack-docs.readthedocs.io/en/latest/cla_landing.html).