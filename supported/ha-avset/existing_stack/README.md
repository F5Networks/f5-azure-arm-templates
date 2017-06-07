# Deploying the BIG-IP VE in Azure - HA in an Availability Set, Existing Stack

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

## Introduction

This solution uses an ARM template to launch a two BIG-IP VEs in an Active/Standby configuration with network failover enabled in an existing stack. Each pair of BIG-IP VEs is deployed in an Azure Availability Set, and can therefore be spread across different update and fault domains. Each BIG-IP VE has 3 network interfaces (NICs), one for management, one for external traffic, and one for internal traffic.

Traffic flows from the BIG-IP VE to the application servers. This is the standard "on-premise-like" cloud design where the compute instance of F5 is running with a management interface, a front-end application traffic (Virtual Server) interface, and back-end application interface.  This template is a result of Azure now supporting multiple public IP addresses to multiple private IP addresses per NIC.  This template also has the ability to create specify additional Public/Private IP addresses for the external "application" NIC to be used for passing traffic to virtual servers in a more traditional fashion. In the event the active BIG-IP VE become unavailable, traffic seamlessly shifts to the standby BIG-IP VE using network failover.

You can choose to deploy the BIG-IP VE with your own F5 BIG-IP license (BYOL), or use Pay as You Go (PAYG) licensing.
This README file is for the ARM template in an existing stack.  If you want to deploy into a new stack, see https://github.com/F5Networks/cloudsolutions/f5-azure-arm-templates/tree/master/experimental/ha-avset/new_stack/README.md



## Prerequisites and configuration notes
  - **Important**: When you configure the admin password for the BIG-IP VE in the template, you cannot use the characters **#** or **'** (single quote).
  - If you are deploying the BYOL template, you must have two valid BIG-IP license tokens.
  - See the **[Configuration Example](#config)** section for a configuration diagram and description for this solution.
  - The management port for the BIG-IP Configuration utility is **8443**.  This allows you to use 443 for application traffic.
  - Your Azure environment must be configured to use service principal authentication.  If you have not yet configured service principal authentication, see https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal.

## Security
This ARM template downloads helper code to configure the BIG-IP system. If your organization is security conscious and you want to verify the integrity of the template, you can open the template and ensure the following lines are present. See [Security Detail](#securitydetail) for the exact code.
In the *variables* section:
  - In the *verifyHash* variable: search for **script-signature** and then a hashed signature.
  - In the *installCloudLibs* variable: ensure this includes **tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz**.

Additionally, F5 provides checksums for all of our supported templates. For instructions and the checksums to compare against, see https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014.

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
  - **BYOL** <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv3.1.3.0%2Fexperimental%2Fha-avset%2Fexisting_stack%2FBYOL%2Fazuredeploy.json">
    <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>

  - **PAYG** <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv3.1.3.0%2Fexperimental%2Fha-avset%2Fexisting_stack%2FPAYG%2Fazuredeploy.json">
    <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>
### Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| adminUsername | Yes | A user name to login to the BIG-IP VEs.  The default value is "azureuser". |
| adminPassword | Yes | A strong password for the BIG-IP VEs. This must not include **#** or **'** (single quote). Remember this password, you will need it later. |
| dnsLabel | Yes | Unique DNS label that is used as a part of the hostname for the public IP address used to access the BIG-IP VEs for management. You can find the DNS label by clicking the resource group, then the public IP address(es) that end with "-mgmt-pip" and looking at the DNS label of each. |
| instanceName | Yes | The hostname you want to use for the Virtual Machine. |
| instanceType | Yes | The Azure Virtual Machine instance size you want to use. |
| imageName | Yes | The F5 image you want to deploy. |
| bigIpVersion | Yes | F5 BIG-IP version you want to use. |
| licenseKey1 | Yes (BYOL only) | For BYOL only. The license token from the F5 licensing server. This license is used for the first F5 BIG-IP VE. |
| licenseKey2 | Yes (BYOL only) | For BYOL only. The license token from the F5 licensing server. This license is used for the second F5 BIG-IP VE. |
| licensedBandwidth | Yes (PAYG only) | For PAYG only. The amount of licensed bandwidth (Mbps) you want the PAYG image to use. |
| numberOfExternalIps | Yes | The number of public/private IP addresses you want to deploy for the application traffic (external) NIC on the BIG-IP to be used for virtual servers. |
| vnetName | Yes | The name of the existing virtual network in which you want to connect the BIG-IP VEs. |
| vnetResourceGroupName | Yes | The name of the resource group that contains the Virtual Network in which the BIG-IP will be placed. |
| mgmtSubnetName | Yes | Name of the existing management subnet - with external access to Internet. |
| mgmtIpAddressRangeStart | Yes | The static private IP address you want to assign to the management self IP of the first BIG-IP VE. The next contiguous address is used for the second BIG-IP VE device. |
| externalSubnetName | Yes | Name of the existing external subnet - with external access to Internet. |
| externalIpPrimaryAddressRangeStart | Yes | The static private IP address you want to assign to the external self IP (primary) of the first BIG-IP VE. The next contiguous address is used for the second BIG-IP VE device. |
| externalIpSecondaryAddressRangeStart | Yes | The static private IP address (secondary) you want to assign to the first shared Azure public IP. An additional private IP address are assigned for each public IP address you specified in numberOfExternalIps.  For example, adding 10.100.1.50 here and choosing 2 in numberOfExternalIps would result in 10.100.1.50 and 10.100.1.51 being configured as static private IP addresses for external virtual servers. |
| internalSubnetName | Yes | Name of the existing internal subnet. |
| internalIpAddressRangeStart | Yes | The static private IP address you want to assign to the internal self IP of the first BIG-IP VE. The next contiguous address will be used for the second BIG-IP VE device. |
| restrictedSrcAddress | Yes | Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or an asterisk for all sources. |
| tenantId | Yes | Your Azure service principal application tenant ID. |
| clientId | Yes | Your Azure service principal application ID, also referred to as client ID. |
| servicePrincipalSecret | Yes | Your Azure service principal application secret. |
| tagValues | Yes | Additional key-value pair tags to be added to each Azure resource. |
| managedRoutes | | A comma-delimited list of UDR destinations to be managed by this cluster (for example 192.168.0.0/24,192.168.1.0/24,192.168.2.0/24). |
| routeTableTag | | Azure tag to identify the route tables to be managed by this cluster. This can be any single word, in order for the routes to be managed by BIG-IP, you must create a tag on the route table with the key "f5_ha" and the value of the routeTable tag (for example f5_ha:myRoute). |


### <a name="powershell"></a>PowerShell Script Example

```powershell
    ## Script parameters being asked for below match to parameters in the azuredeploy.json file, otherwise pointing to the ##
## azuredeploy.parameters.json file for values to use.  Some options below are mandatory, some(such as region) can     ##
## be supplied inline when running this script but if they aren't then the default will be used as specified below.   ##
## Example Command: .\Deploy_via_PS.ps1 --licenseType PAYG --licensedBandwidth 200m --adminUsername azureuser --adminPassword <value> --dnsLabel <value> --instanceName f5vm01 --instanceType Standard_D3_v2 --imageName Good --bigIpVersion 13.0.021 --numberOfExternalIps 1 --vnetName <value> --vnetResourceGroupName <value> --mgmtSubnetName <value> --mgmtIpAddressRangeStart <value> --externalSubnetName <value> --externalIpPrimaryAddressRangeStart <value> --externalIpSecondaryAddressRangeStart <value> --internalSubnetName <value> --internalIpAddressRangeStart <value> --restrictedSrcAddress "*" --managedRoutes <value> --routeTableTag <value> --tenantId <value> --clientId <value> --secret <value> --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

param(

  [Parameter(Mandatory=$True)]
  [string]
  $licenseType,

  [string]
  $licensedBandwidth = $(if($licenseType -eq "PAYG") { Read-Host -prompt "licensedBandwidth"}),

  [string]
  $licenseKey1 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey1"}),

  [string]
  $licenseKey2 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey2"}),

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
  $mgmtIpAddressRangeStart,

  [Parameter(Mandatory=$True)]
  [string]
  $externalSubnetName,

  [Parameter(Mandatory=$True)]
  [string]
  $externalIpPrimaryAddressRangeStart,

  [Parameter(Mandatory=$True)]
  [string]
  $externalIpSecondaryAddressRangeStart,

  [Parameter(Mandatory=$True)]
  [string]
  $internalSubnetName,

  [Parameter(Mandatory=$True)]
  [string]
  $internalIpAddressRangeStart,

  [string]
  $restrictedSrcAddress = "*",

  [Parameter(Mandatory=$True)]
  [string]
  $tenantId,

  [Parameter(Mandatory=$True)]
  [string]
  $clientId,

  [Parameter(Mandatory=$True)]
  [string]
  $secret,

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
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceName "$instanceName" -instanceType "$instanceType" -imageName "$imageName" -bigIpVersion "$bigIpVersion" -numberOfExternalIps "$numberOfExternalIps" -vnetName "$vnetName" -vnetResourceGroupName "$vnetResourceGroupName" -mgmtSubnetName "$mgmtSubnetName" -mgmtIpAddressRangeStart "$mgmtIpAddressRangeStart" -externalSubnetName "$externalSubnetName" -externalIpPrimaryAddressRangeStart "$externalIpPrimaryAddressRangeStart" -externalIpSecondaryAddressRangeStart "$externalIpSecondaryAddressRangeStart" -internalSubnetName "$internalSubnetName" -internalIpAddressRangeStart "$internalIpAddressRangeStart" -restrictedSrcAddress "$restrictedSrcAddress" -licenseKey1 "$licenseKey1 -licenseKey2 "$licenseKey2"
} elseif ($licenseType -eq "PAYG") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\azuredeploy.json"; $parametersFilePath = ".\PAYG\azuredeploy.parameters.json" }
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceName "$instanceName" -instanceType "$instanceType" -imageName "$imageName" -bigIpVersion "$bigIpVersion" -numberOfExternalIps "$numberOfExternalIps" -vnetName "$vnetName" -vnetResourceGroupName "$vnetResourceGroupName" -mgmtSubnetName "$mgmtSubnetName" -mgmtIpAddressRangeStart "$mgmtIpAddressRangeStart" -externalSubnetName "$externalSubnetName" -externalIpPrimaryAddressRangeStart "$externalIpPrimaryAddressRangeStart" -externalIpSecondaryAddressRangeStart "$externalIpSecondaryAddressRangeStart" -internalSubnetName "$internalSubnetName" -internalIpAddressRangeStart "$internalIpAddressRangeStart" -restrictedSrcAddress "$restrictedSrcAddress" -licensedBandwidth "$licensedBandwidth"
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
## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth 200m --adminUsername azureuser --adminPassword <value> --dnsLabel <value> --instanceName f5vm01 --instanceType Standard_D3_v2 --imageName Good --bigIpVersion 13.0.021 --numberOfExternalIps 1 --vnetName <value> --vnetResourceGroupName <value> --mgmtSubnetName <value> --mgmtIpAddressRangeStart <value> --externalSubnetName <value> --externalIpPrimaryAddressRangeStart <value> --externalIpSecondaryAddressRangeStart <value> --internalSubnetName <value> --internalIpAddressRangeStart <value> --restrictedSrcAddress "*" --managedRoutes <value> --routeTableTag <value> --tenantId <value> --clientId <value> --secret <value> --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

# Assign Script Parameters and Define Variables
# Specify static items, change these as needed or make them parameters
region="westus"
restrictedSrcAddress="*"
tagValues='{"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}'

ARGS=`getopt -o a:b:c:d:e:f:g:h:i:j:k:l:m:n:o:p:q:r:s:t:u:v:w:x:y:z:aa:bb:cc:dd: --long resourceGroupName:,azureLoginUser:,azureLoginPassword:,licenseType:,licensedBandwidth:,licenseKey1:,licenseKey2:,adminUsername:,adminPassword:,dnsLabel:,instanceName:,instanceType:,imageName:,bigIpVersion:,numberOfExternalIps:,vnetName:,vnetResourceGroupName:,mgmtSubnetName:,mgmtIpAddressRangeStart:,externalSubnetName:,externalIpPrimaryAddressRangeStart:,externalIpSecondaryAddressRangeStart:,internalSubnetName:,internalIpAddressRangeStart:,restrictedSrcAddress:,managedRoutes:,routeTableTag:,tenantId:,clientId:,secret: -n $0 -- "$@"`
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
        -g|--licenseKey2)
            licenseKey2=$2
            shift 2;;
        -h|--adminUsername)
            adminUsername=$2
            shift 2;;
        -i|--adminPassword)
            adminPassword=$2
            shift 2;;
        -j|--dnsLabel)
            dnsLabel=$2
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
        -s|--mgmtIpAddressRangeStart)
            mgmtIpAddressRangeStart=$2
            shift 2;;
        -t|--externalSubnetName)
            externalSubnetName=$2
            shift 2;;
        -u|--externalIpPrimaryAddressRangeStart)
            externalIpPrimaryAddressRangeStart=$2
            shift 2;;
        -v|--externalIpSecondaryAddressRangeStart)
            externalIpSecondaryAddressRangeStart=$2
            shift 2;;
        -w|--internalSubnetName)
            internalSubnetName=$2
            shift 2;;
        -x|--internalIpAddressRangeStart)
            internalIpAddressRangeStart=$2
            shift 2;;
        -y|--restrictedSrcAddress)
            restrictedSrcAddress=$2
            shift 2;;
        -z|--managedRoutes)
            managedRoutes=$2
            shift 2;;
        -aa|--routeTableTag)
            routeTableTag=$2
            shift 2;;
        -bb|--tenantId)
            tenantId=$2
            shift 2;;
        -cc|--clientId)
            clientId=$2
            shift 2;;
        -dd|--secret)
            secret=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

#If a required parameter is not passed, the script will prompt for it below
required_variables="adminUsername adminPassword dnsLabel instanceName instanceType imageName bigIpVersion numberOfExternalIps vnetName vnetResourceGroupName mgmtSubnetName mgmtIpAddressRangeStart externalSubnetName externalIpPrimaryAddressRangeStart externalIpSecondaryAddressRangeStart internalSubnetName internalIpAddressRangeStart resourceGroupName licenseType tenantId clientId secret "
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
    if [ -v $licenseKey2 ] ; then
            read -p "Please enter value for licenseKey2:" licenseKey2
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
    azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceName\":{\"value\":\"$instanceName\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"licenseKey1\":{\"value\":\"$licenseKey1\"},\"licenseKey2\":{\"value\":\"$licenseKey2\"},\"numberOfExternalIps\":{\"value\": $numberOfExternalIps},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"mgmtIpAddressRangeStart\":{\"value\":\"$mgmtIpAddressRangeStart\"},\"externalSubnetName\":{\"value\":\"$externalSubnetName\"},\"externalIpPrimaryAddressRangeStart\":{\"value\":\"$externalIpPrimaryAddressRangeStart\"},\"externalIpSecondaryAddressRangeStart\":{\"value\":\"$externalIpSecondaryAddressRangeStart\"},\"internalSubnetName\":{\"value\":\"$internalSubnetName\"},\"internalIpAddressRangeStart\":{\"value\":\"$internalIpAddressRangeStart\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"managedRoutes\":{\"value\":\"$managedRoutes\"},\"routeTableTag\":{\"value\":\"$routeTableTag\"},\"tenantId\":{\"value\":\"$tenantId\"},\"clientId\":{\"value\":\"$clientId\"},\"servicePrincipalSecret\":{\"value\":\"$secret\"}}"
elif [ $licenseType == "PAYG" ]; then
    azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p   "{\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceName\":{\"value\":\"$instanceName\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"licenseKey1\":{\"value\":\"$licenseKey1\"},\"licenseKey2\":{\"value\":\"$licenseKey2\"},\"numberOfExternalIps\":{\"value\": $numberOfExternalIps},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"mgmtIpAddressRangeStart\":{\"value\":\"$mgmtIpAddressRangeStart\"},\"externalSubnetName\":{\"value\":\"$externalSubnetName\"},\"externalIpPrimaryAddressRangeStart\":{\"value\":\"$externalIpPrimaryAddressRangeStart\"},\"externalIpSecondaryAddressRangeStart\":{\"value\":\"$externalIpSecondaryAddressRangeStart\"},\"internalSubnetName\":{\"value\":\"$internalSubnetName\"},\"internalIpAddressRangeStart\":{\"value\":\"$internalIpAddressRangeStart\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"managedRoutes\":{\"value\":\"$managedRoutes\"},\"routeTableTag\":{\"value\":\"$routeTableTag\"},\"licensedBandwidth\":{\"value\":\"$licensedBandwidth\"},\"tenantId\":{\"value\":\"$tenantId\"},\"clientId\":{\"value\":\"$clientId\"},\"servicePrincipalSecret\":{\"value\":\"$secret\"}}"
else
    echo "Please select a valid license type of PAYG or BYOL."
    exit 1
fi
```

## Configuration Example <a name="config">

The following is a configuration diagram for this deployment.  In this configuration, each BIG-IP VE has 3 NICs, one for management, one for external, and one for internal.  This is in a more traditional deployment model where data-plane and management traffic are separate.  Should the active BIG-IP VE become unavailable, traffic seamlessly shifts to the standby BIG-IP VE using network failover.<br>
The IP addresses in this example may be different in your implementation.

![Configuration example](../images/azure-multi-nic-ha.png)


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
               "commandToExecute": "[concat('tmsh create sys application service my_deployment { device-group none template f5.ip_forwarding traffic-group none variables replace-all-with { basic__addr { value 0.0.0.0 } basic__forward_all { value No } basic__mask { value 0.0.0.0 } basic__port { value 0 } basic__vlan_listening { value internal } options__advanced { value no }options__display_help { value hide } } }')]"
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
completed and submitted the `F5 Contributor License Agreement`