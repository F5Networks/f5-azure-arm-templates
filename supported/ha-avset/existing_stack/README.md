# Deploying the BIG-IP VE in Azure - HA Cluster: Active/Standby

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

## Introduction

This solution uses an ARM template to launch two BIG-IP VEs in an Active/Standby configuration with network failover enabled. Each pair of BIG-IP VEs is deployed in an Azure Availability Set, and can therefore be spread across different update and fault domains. Each BIG-IP VE has 3 network interfaces (NICs), one for management, one for external traffic, and one for internal traffic.

Traffic flows from the client through BIG-IP VE to the application servers. This is the standard "on-premise-like" cloud design where the compute instance of F5 is running with a management interface, a front-end application traffic (external) interface, and back-end application (internal) interface. This template is a result of Azure now supporting multiple public-to-private IP address mappings per NIC. 

This template supports creating up to 8 additional public/private IP address configurations for the external "application" NIC to be used for passing traffic to BIG-IP virtual servers.  Each virtual server should be configured with a destination address matching the private IP address value of the Azure IP configuration receiving traffic for the application. In the event the active BIG-IP VE becomes unavailable, the IP configuration(s) are migrated using network failover, seamlessly shifting application traffic to the current active BIG-IP VE.

The template also supports updating the next hop of Azure User-Defined Routes (UDRs) to use the active BIG-IP VEs internal self IP address. Specify a comma-delimited list of managedRoutes and a routeTableTag in the template to define the UDRs to be updated.  All UDRs with destinations matching managedRoutes and configured in Azure Route Tables tagged with "f5_ha:<routeTableTag>" will use the active BIG-IP VE as the next hop for those routes.

**Networking Stack Type:** This template deploys into an existing networking stack; the networking infrastructure must be available prior to deploying. See the [Template Parameters Section](#template-parameters) for required networking objects.

## Prerequisites and configuration notes
  - **Important**: When you configure the admin password for the BIG-IP VE in the template, you cannot use the characters **#** or **'** (single quote).
  - If you are deploying the BYOL template, you must have a valid BIG-IP license token.
  - See the **[Configuration Example](#config)** section for a configuration diagram and description for this solution.
  - See the important note about [optionally changing the BIG-IP Management port](#changing-the-big-ip-configuration-utility-gui-port).
  - This template supports service discovery.  See the [Service Discovery section](#service-discovery) for details.
  - This template requires service principal.  See the [Service Principal Setup section](#service-principal-authentication) for details.
  - This template has some optional post-deployment configuration.  See the [Post-Deployment Configuration section](#post-deployment-configuration) for details.
  - This template requires that the resource group name the deployment uses to be no longer than **35** characters as a result of limitations to tag size within Azure.


## Security
This ARM template downloads helper code to configure the BIG-IP system. If your organization is security conscious and you want to verify the integrity of the template, you can open the template and ensure the following lines are present. See [Security Detail](#securitydetail) for the exact code.
In the *variables* section:
  - In the *verifyHash* variable: search for **script-signature** and then a hashed signature.
  - In the *installCloudLibs* variable: ensure this includes **tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz**.

Additionally, F5 provides checksums for all of our supported templates. For instructions and the checksums to compare against, see https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014.

## Supported BIG-IP versions
The following is a map that shows the available options for the template parameter **bigIpVersion** as it corresponds to the BIG-IP version itself. Only the latest version of BIG-IP VE is posted in the Azure Marketplace. For older versions, see downloads.f5.com.

| Azure BIG-IP Image Version | BIG-IP Version |
| --- | --- |
| 13.0.021 | 13.0.0 HF2 Build 2.10.1671 |
| 12.1.24 | 12.1.2 HF1 Build 1.34.271 |
| latest | This will select the latest BIG-IP version available |


## Supported instance types and hypervisors
  - For a list of supported Azure instance types for this solutions, see the **Azure instances for BIG-IP VE** section of https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0/1.html#guid-71265d82-3a1a-43d2-bae5-892c184cc59b

  - For a list versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and Microsoft Azure, see https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html.

### Help
Because this template has been created and fully tested by F5 Networks, it is fully supported by F5. This means you can get assistance if necessary from F5 Technical Support.

We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 ARM templates.  This channel is typically monitored Monday-Friday 9-5 PST by F5 employees who will offer best-effort support.


## Installation

You have three options for deploying this solution:
  - Using the Azure deploy buttons
  - Using [PowerShell](#powershell)
  - Using [CLI Tools](#cli)

### <a name="azure"></a>Azure deploy buttons

Use the appropriate button, depending on what type of BIG-IP licensing required:
   - **BYOL** <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Frelease-3.2.0.0%2Fsupported%2Fha-avset%2Fexisting_stack%2FBYOL%2Fazuredeploy.json">
    <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>

   - **PAYG** <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Frelease-3.2.0.0%2Fsupported%2Fha-avset%2Fexisting_stack%2FPAYG%2Fazuredeploy.json">
    <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>



### Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| adminUsername | Yes | User name for the Virtual Machine. |
| adminPassword | Yes | Password to login to the Virtual Machine. |
| dnsLabel | Yes | Unique DNS Name for the Public IP address used to access the Virtual Machine |
| instanceName | Yes | Name of the Virtual Machine. |
| instanceType | Yes | Azure instance size of the Virtual Machine. |
| imageName | Yes | F5 SKU (IMAGE) to you want to deploy. |
| bigIpVersion | Yes | F5 BIG-IP version you want to use. |
| licenseKey1 | No | The license token for the F5 BIG-IP VE (BYOL) |
| licenseKey2 | No | The license token for the F5 BIG-IP VE (BYOL). This field is required when deploying two or more devices. |
| licensedBandwidth | No | The amount of licensed bandwidth (Mbps) you want the PAYG image to use. |
| numberOfExternalIps | Yes | The number of public/private IP addresses you want to deploy for the application traffic (external) NIC on the BIG-IP VE to be used for virtual servers. |
| vnetName | Yes | The name of the existing virtual network to which you want to connect the BIG-IP VEs. |
| vnetResourceGroupName | Yes | The name of the resource group that contains the Virtual Network where the BIG-IP VE will be placed. |
| mgmtSubnetName | Yes | Name of the existing MGMT subnet - with external access to the Internet. |
| mgmtIpAddressRangeStart | Yes | The static private IP address you would like to assign to the management self IP of the first BIG-IP. The next contiguous address will be used for the second BIG-IP device. |
| externalSubnetName | Yes | Name of the existing external subnet - with external access to Internet. |
| externalIpSelfAddressRangeStart | Yes | The static private IP address you would like to assign to the external self IP (primary) of the first BIG-IP. The next contiguous address will be used for the second BIG-IP device. |
| externalIpAddressRangeStart | Yes | The static private IP address (secondary) you would like to assign to the first shared Azure public IP. An additional private IP address will be assigned for each public IP address you specified in numberOfExternalIps.  For example, inputting 10.100.1.50 here and choosing 2 in numberOfExternalIps would result in 10.100.1.50 and 10.100.1.51 being configured as static private IP addresses for external virtual servers. |
| internalSubnetName | Yes | Name of the existing internal subnet. |
| internalIpAddressRangeStart | Yes | The static private IP address you would like to assign to the internal self IP of the first BIG-IP. The next contiguous address will be used for the second BIG-IP device. |
| tenantId | Yes | Your Azure service principal application tenant ID. |
| clientId | Yes | Your Azure service principal application client ID. |
| servicePrincipalSecret | Yes | Your Azure service principal application secret. |
| managedRoutes | Yes | A comma-delimited list of route destinations to be managed by this cluster.  For example: 0.0.0.0/0,192.168.1.0/24. |
| routeTableTag | Yes | Azure tag value to identify the route tables to be managed by this cluster. For example tag value: myRoute.  Example Azure tag: f5_ha:myRoute. |
| ntpServer | Yes | If you would like to change the NTP server the BIG-IP uses replace the default ntp server with your choice. |
| timeZone | Yes | If you would like to change the time zone the BIG-IP uses then enter your chocie. This is in the format of the Olson timezone string from /usr/share/zoneinfo, such as UTC, US/Central or Europe/London. |
| restrictedSrcAddress | Yes | This field restricts management access to a specific network or address. Enter an IP address or address range in CIDR notation, or asterisk for all sources |
| tagValues | Yes | Default key/value resource tags will be added to the resources in this deployment, if you would like the values to be unique adjust them as needed for each key. |


### <a name="powershell"></a>PowerShell Script Example

```powershell
## Script parameters being asked for below match to parameters in the azuredeploy.json file, otherwise pointing to the ##
## azuredeploy.parameters.json file for values to use.  Some options below are mandatory, some(such as region) can     ##
## be supplied inline when running this script but if they aren't then the default will be used as specificed below.   ##
## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth 200m -adminUsername azureuser -adminPassword <value> -dnsLabel <value> -instanceName f5vm01 -instanceType Standard_DS3_v2 -imageName Good -bigIpVersion 13.0.021 -numberOfExternalIps 1 -vnetName <value> -vnetResourceGroupName <value> -mgmtSubnetName <value> -mgmtIpAddressRangeStart <value> -externalSubnetName <value> -externalIpSelfAddressRangeStart <value> -externalIpAddressRangeStart <value> -internalSubnetName <value> -internalIpAddressRangeStart <value> -tenantId <value> -clientId <value> -servicePrincipalSecret <value> -managedRoutes NOT_SPECIFIED -routeTableTag NOT_SPECIFIED -ntpServer 0.pool.ntp.org -timeZone UTC -restrictedSrcAddress "*" -resourceGroupName <value> 

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
  $externalIpSelfAddressRangeStart,

  [Parameter(Mandatory=$True)]
  [string]
  $externalIpAddressRangeStart,

  [Parameter(Mandatory=$True)]
  [string]
  $internalSubnetName,

  [Parameter(Mandatory=$True)]
  [string]
  $internalIpAddressRangeStart,

  [Parameter(Mandatory=$True)]
  [string]
  $tenantId,

  [Parameter(Mandatory=$True)]
  [string]
  $clientId,

  [Parameter(Mandatory=$True)]
  [string]
  $servicePrincipalSecret,

  [Parameter(Mandatory=$True)]
  [string]
  $managedRoutes,

  [Parameter(Mandatory=$True)]
  [string]
  $routeTableTag,

  [Parameter(Mandatory=$True)]
  [string]
  $ntpServer,

  [Parameter(Mandatory=$True)]
  [string]
  $timeZone,

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
$sps = ConvertTo-SecureString -String $servicePrincipalSecret -AsPlainText -Force
if ($licenseType -eq "BYOL") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BYOL\azuredeploy.json"; $parametersFilePath = ".\BYOL\azuredeploy.parameters.json" }
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceName "$instanceName" -instanceType "$instanceType" -imageName "$imageName" -bigIpVersion "$bigIpVersion" -numberOfExternalIps "$numberOfExternalIps" -vnetName "$vnetName" -vnetResourceGroupName "$vnetResourceGroupName" -mgmtSubnetName "$mgmtSubnetName" -mgmtIpAddressRangeStart "$mgmtIpAddressRangeStart" -externalSubnetName "$externalSubnetName" -externalIpSelfAddressRangeStart "$externalIpSelfAddressRangeStart" -externalIpAddressRangeStart "$externalIpAddressRangeStart" -internalSubnetName "$internalSubnetName" -internalIpAddressRangeStart "$internalIpAddressRangeStart" -tenantId "$tenantId" -clientId "$clientId" -servicePrincipalSecret $sps -managedRoutes "$managedRoutes" -routeTableTag "$routeTableTag" -ntpServer "$ntpServer" -timeZone "$timeZone" -restrictedSrcAddress "$restrictedSrcAddress"  -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2"
} elseif ($licenseType -eq "PAYG") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\azuredeploy.json"; $parametersFilePath = ".\PAYG\azuredeploy.parameters.json" }
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceName "$instanceName" -instanceType "$instanceType" -imageName "$imageName" -bigIpVersion "$bigIpVersion" -numberOfExternalIps "$numberOfExternalIps" -vnetName "$vnetName" -vnetResourceGroupName "$vnetResourceGroupName" -mgmtSubnetName "$mgmtSubnetName" -mgmtIpAddressRangeStart "$mgmtIpAddressRangeStart" -externalSubnetName "$externalSubnetName" -externalIpSelfAddressRangeStart "$externalIpSelfAddressRangeStart" -externalIpAddressRangeStart "$externalIpAddressRangeStart" -internalSubnetName "$internalSubnetName" -internalIpAddressRangeStart "$internalIpAddressRangeStart" -tenantId "$tenantId" -clientId "$clientId" -servicePrincipalSecret $sps -managedRoutes "$managedRoutes" -routeTableTag "$routeTableTag" -ntpServer "$ntpServer" -timeZone "$timeZone" -restrictedSrcAddress "$restrictedSrcAddress"  -licensedBandwidth "$licensedBandwidth"
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
## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth 200m --adminUsername azureuser --adminPassword <value> --dnsLabel <value> --instanceName f5vm01 --instanceType Standard_DS3_v2 --imageName Good --bigIpVersion 13.0.021 --numberOfExternalIps 1 --vnetName <value> --vnetResourceGroupName <value> --mgmtSubnetName <value> --mgmtIpAddressRangeStart <value> --externalSubnetName <value> --externalIpSelfAddressRangeStart <value> --externalIpAddressRangeStart <value> --internalSubnetName <value> --internalIpAddressRangeStart <value> --tenantId <value> --clientId <value> --servicePrincipalSecret <value> --managedRoutes NOT_SPECIFIED --routeTableTag NOT_SPECIFIED --ntpServer 0.pool.ntp.org --timeZone UTC --restrictedSrcAddress "*" --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

# Assign Script Parameters and Define Variables
# Specify static items below, change these as needed or make them parameters
region="westus"
restrictedSrcAddress="*"
tagValues='{"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}'

# Parse the command line arguments, primarily checking full params as short params are just placeholders
while [[ $# -gt 1 ]]; do
    case "$1" in
        --resourceGroupName)
            resourceGroupName=$2
            shift 2;;
        --azureLoginUser)
            azureLoginUser=$2
            shift 2;;
        --azureLoginPassword)
            azureLoginPassword=$2
            shift 2;;
        --licenseType)
            licenseType=$2
            shift 2;;
        --licensedBandwidth)
            licensedBandwidth=$2
            shift 2;;
        --licenseKey1)
            licenseKey1=$2
            shift 2;;
        --licenseKey2)
            licenseKey2=$2
            shift 2;;
        --adminUsername)
            adminUsername=$2
            shift 2;;
        --adminPassword)
            adminPassword=$2
            shift 2;;
        --dnsLabel)
            dnsLabel=$2
            shift 2;;
        --instanceName)
            instanceName=$2
            shift 2;;
        --instanceType)
            instanceType=$2
            shift 2;;
        --imageName)
            imageName=$2
            shift 2;;
        --bigIpVersion)
            bigIpVersion=$2
            shift 2;;
        --numberOfExternalIps)
            numberOfExternalIps=$2
            shift 2;;
        --vnetName)
            vnetName=$2
            shift 2;;
        --vnetResourceGroupName)
            vnetResourceGroupName=$2
            shift 2;;
        --mgmtSubnetName)
            mgmtSubnetName=$2
            shift 2;;
        --mgmtIpAddressRangeStart)
            mgmtIpAddressRangeStart=$2
            shift 2;;
        --externalSubnetName)
            externalSubnetName=$2
            shift 2;;
        --externalIpSelfAddressRangeStart)
            externalIpSelfAddressRangeStart=$2
            shift 2;;
        --externalIpAddressRangeStart)
            externalIpAddressRangeStart=$2
            shift 2;;
        --internalSubnetName)
            internalSubnetName=$2
            shift 2;;
        --internalIpAddressRangeStart)
            internalIpAddressRangeStart=$2
            shift 2;;
        --tenantId)
            tenantId=$2
            shift 2;;
        --clientId)
            clientId=$2
            shift 2;;
        --servicePrincipalSecret)
            servicePrincipalSecret=$2
            shift 2;;
        --managedRoutes)
            managedRoutes=$2
            shift 2;;
        --routeTableTag)
            routeTableTag=$2
            shift 2;;
        --ntpServer)
            ntpServer=$2
            shift 2;;
        --timeZone)
            timeZone=$2
            shift 2;;
        --restrictedSrcAddress)
            restrictedSrcAddress=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

#If a required parameter is not passed, the script will prompt for it below
required_variables="adminUsername adminPassword dnsLabel instanceName instanceType imageName bigIpVersion numberOfExternalIps vnetName vnetResourceGroupName mgmtSubnetName mgmtIpAddressRangeStart externalSubnetName externalIpSelfAddressRangeStart externalIpAddressRangeStart internalSubnetName internalIpAddressRangeStart tenantId clientId servicePrincipalSecret managedRoutes routeTableTag ntpServer timeZone resourceGroupName licenseType "
for variable in $required_variables
        do
        if [ -z ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done

# Prompt for license key if not supplied and BYOL is selected
if [ $licenseType == "BYOL" ]; then
    if [ -z $licenseKey1 ] ; then
            read -p "Please enter value for licenseKey1:" licenseKey1
    fi
    if [ -z $licenseKey2 ] ; then
            read -p "Please enter value for licenseKey2:" licenseKey2
    fi
    template_file="./BYOL/azuredeploy.json"
    parameter_file="./BYOL/azuredeploy.parameters.json"
fi
# Prompt for licensed bandwidth if not supplied and PAYG is selected
if [ $licenseType == "PAYG" ]; then
    if [ -z $licensedBandwidth ] ; then
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
    azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceName\":{\"value\":\"$instanceName\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"numberOfExternalIps\":{\"value\":$numberOfExternalIps},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"mgmtIpAddressRangeStart\":{\"value\":\"$mgmtIpAddressRangeStart\"},\"externalSubnetName\":{\"value\":\"$externalSubnetName\"},\"externalIpSelfAddressRangeStart\":{\"value\":\"$externalIpSelfAddressRangeStart\"},\"externalIpAddressRangeStart\":{\"value\":\"$externalIpAddressRangeStart\"},\"internalSubnetName\":{\"value\":\"$internalSubnetName\"},\"internalIpAddressRangeStart\":{\"value\":\"$internalIpAddressRangeStart\"},\"tenantId\":{\"value\":\"$tenantId\"},\"clientId\":{\"value\":\"$clientId\"},\"servicePrincipalSecret\":{\"value\":\"$servicePrincipalSecret\"},\"managedRoutes\":{\"value\":\"$managedRoutes\"},\"routeTableTag\":{\"value\":\"$routeTableTag\"},\"ntpServer\":{\"value\":\"$ntpServer\"},\"timeZone\":{\"value\":\"$timeZone\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"licenseKey1\":{\"value\":\"$licenseKey1\"},\"licenseKey2\":{\"value\":\"$licenseKey2\"}}"
elif [ $licenseType == "PAYG" ]; then
    azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceName\":{\"value\":\"$instanceName\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"numberOfExternalIps\":{\"value\":$numberOfExternalIps},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"mgmtIpAddressRangeStart\":{\"value\":\"$mgmtIpAddressRangeStart\"},\"externalSubnetName\":{\"value\":\"$externalSubnetName\"},\"externalIpSelfAddressRangeStart\":{\"value\":\"$externalIpSelfAddressRangeStart\"},\"externalIpAddressRangeStart\":{\"value\":\"$externalIpAddressRangeStart\"},\"internalSubnetName\":{\"value\":\"$internalSubnetName\"},\"internalIpAddressRangeStart\":{\"value\":\"$internalIpAddressRangeStart\"},\"tenantId\":{\"value\":\"$tenantId\"},\"clientId\":{\"value\":\"$clientId\"},\"servicePrincipalSecret\":{\"value\":\"$servicePrincipalSecret\"},\"managedRoutes\":{\"value\":\"$managedRoutes\"},\"routeTableTag\":{\"value\":\"$routeTableTag\"},\"ntpServer\":{\"value\":\"$ntpServer\"},\"timeZone\":{\"value\":\"$timeZone\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"licensedBandwidth\":{\"value\":\"$licensedBandwidth\"}}"
else
    echo "Please select a valid license type of PAYG or BYOL."
    exit 1
fi
```

## Configuration Example <a name="config">

The following is an example configuration diagram for this solution deployment. In this scenario, each BIG-IP has one NIC for management, one NIC for external traffic and one NIC for internal traffic.  This is the traditional BIG-IP deployment model where data-plane, management and internal traffic is separate. The IP addresses in this example may be different in your implementation.

![Configuration Example](images/azure-example-diagram.png)

## Post-Deployment Configuration
Use this section for optional configuration changes after you have deployed the template.

### Additional Public IP Addresses - Failover
This ARM template supports using up to 8 public IP addresses.  After you initially deploy the template, if you want to include additional public IP addresses (up to the template-supported limit of 8) and/or if you want to add or remove the user-defined routes (UDRs) to be managed by the BIG-IP, use the following guidance.  If you want to include more than 8 public IP addresses, see [Adding more than 8 Public IP addresses](#adding-more-than-8-public-ip-addresses-to-the-deployment)

#### Adding up to 8 public IP addresses
To add public IP addresses up to the template-supported limit of 8 or if you want to add or remove the user-defined routes managed by the BIG-IP system after you have initially deployed the template, use the Azure Portal to redeploy the template, updating the parameters for the changes you want to make.  Use the following guidance:

1.	Ensure that the first BIG-IP (VM 0) in the cluster is in an active state (from the BIG-IP Configuration utility, click **Device Management>Devices**, the device with the lowest IP address should be active).
2.	From the Azure Portal, click the Azure Resource Group where you deployed the template.
3.	Click **Deployments**.
4.	Find the deployment and highlight it in the list (should be named Microsoft.Template)
5.	Click **Redeploy**.
6.	For the Resource Group, click Use existing and select the resource group in which you initially deployed.
7.	Enter the Admin password and Service Principal Secret parameters with the same values used in the initial deployment.
8.	To add public IP addresses, change the value of the **Number Of External Ips** parameter to the number of IP addresses you want to use.
9.	To add or change managed routes, change the value of the **Managed Routes** parameter.
10.	Agree to the terms and conditions.
11.	Click **Purchase**.

#### Adding more than 8 public IP addresses to the deployment
The deployment template supports creation of 1-8 external public IP addresses for application traffic (first one is used for external NIC Self IP). Use the following guidance to add **more** public IP addresses to the deployment:

  -	Create a new Azure public IP address resource in the deployment resource group.  You ***must*** use the following syntax: ```<ResourceGroupName>-ext-pip<number>```.  For example: **SeattleResourceGroup-ext-pip9**.
  -	Create a new IP configuration resource in the properties of the external Azure network interface (for example *myResourceGroupName-ext0*).  You ***must*** use the following syntax: ```<ResourceGroupName>-ext-ipconfig<number>```.  For example: **SeattleResourceGroup-ext-ipconfig9**.
  -	Add these Azure tags to the public IP address resource:
    -	For example: ```f5_privateIp=10.10.10.10``` (the tag value should correspond to the new private IP address of the IP configurations).
    -	For example: ```ext_SubnetId=/subscriptions/<subscriptionId>/resourceGroups/<myResourceGroupName>/providers/Microsoft.Network/virtualNetworks/*< myVnetName >*/subnets/<mySubnetName>``` (you can get this value from resources.azure.com: **Subscriptions > Resource Groups > myResourceGroupName > providers > Microsoft.Network > virtualNetworks > myVnetName > subnets > mySubnetName.id**).
  - Again, you MUST follow the resource naming conventions in the provided examples for failover to work correctly.

When you create virtual servers on the BIG-IP VE for these new additional addresses, the BIG-IP virtual server destination IP address should match the Azure Private IP Address of the IP configuration that corresponds to the Public IP address of your application. See the BIG-IP documentation for specific instructions on creating virtual servers.


## Documentation

The ***BIG-IP Virtual Edition and Microsoft Azure: Setup*** guide (https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0.html) describes how to create the configuration manually without using the ARM template.

### Service Discovery
Once you launch your BIG-IP instance using the ARM template, you can use the Service Discovery iApp template on the BIG-IP VE to automatically update pool members based on auto-scaled cloud application hosts.  In the iApp template, you enter information about your cloud environment, including the tag key and tag value for the pool members you want to include, and then the BIG-IP VE programmatically discovers (or removes) members using those tags.

#### Tagging
In Microsoft Azure, you have three options for tagging objects that the Service Discovery iApp uses. Note that you select public or private IP addresses within the iApp.
  - *Tag a VM resource*<br>
The BIG-IP VE will discover the primary public or private IP addresses for the primary NIC configured for the tagged VM.
  - *Tag a NIC resource*<br>
The BIG-IP VE will discover the primary public or private IP addresses for the tagged NIC.  Use this option if you want to use the secondary NIC of a VM in the pool.
  - *Tag a Virtual Machine Scale Set resource*<br>
The BIG-IP VE will discover the primary private IP address for the primary NIC configured for each Scale Set instance.  Note you must select Private IP addresses in the iApp template if you are tagging a Scale Set.

The iApp first looks for NIC resources with the tags you specify.  If it finds NICs with the proper tags, it does not look for VM resources. If it does not find NIC resources, it looks for VM resources with the proper tags. In either case, it then looks for Scale Set resources with the proper tags.

**Important**: Make sure the tags and IP addresses you use are unique. You should not tag multiple Azure nodes with the same key/tag combination if those nodes use the same IP address.

To launch the template:
  1.	From the BIG-IP VE web-based Configuration utility, on the Main tab, click **iApps > Application Services > Create**.
  2.	In the **Name** field, give the template a unique name.
  3.	From the **Template** list, select **f5.service_discovery**.  The template opens.
  4.	Complete the template with information from your environment.  For assistance, from the Do you want to see inline help? question, select Yes, show inline help.
  5.	When you are done, click the **Finished** button.

### Service Principal Authentication
This solution requires access to the Azure API to determine how the BIG-IP VEs should be configured.  The most efficient and security-conscious way to handle this is to utilize Azure service principal authentication, for all the typical security reasons.  The following provides information/links on the options for configuring a service principal within Azure if this is the first time it is needed in a subscription.

_Ensure that however the creation of the service principal occurs to verify it only has minimum required access based on the solutions need(read vs read/write) prior to this template being deployed and used by the solution within the resource group selected(new or existing)._

The end result should be possession of a client(application) ID, tenant ID and service principal secret that can login to the same subscription this template will be deployed into.  Ensuring this is fully functioning prior to deploying this ARM template will save on some troubleshooting post-deployment if the service principal is in fact not fully configured.

#### 1. Azure Portal

Follow the steps outlined in the [Azure Portal documentation](https://azure.microsoft.com/en-us/documentation/articles/resource-group-create-service-principal-portal/) to generate the service principal.

#### 2. Azure CLI

This method can be used with either the [Azure CLI v2.0 (Python)](https://github.com/Azure/azure-cli) or the [Azure Cross-Platform CLI (npm module)](https://github.com/Azure/azure-xplat-cli).

_Using the Python Azure CLI v2.0 - requires just one step_
```shell
$ az ad sp create-for-rbac
```

_Using the Node.js cross-platform CLI - requires additional steps for setting up_
https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-authenticate-service-principal-cli

#### 3. Azure PowerShell
Follow the steps outlined in the [Azure Powershell documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-authenticate-service-principal) to generate the service principal.

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
### Changing the BIG-IP Configuration utility (GUI) port
Depending on the deployment requirements, the default managament port for the BIG-IP may need to be changed. To change the Management port, see [Changing the Configuration utility port](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-0-0/2.html#GUID-3E6920CD-A8CD-456C-AC40-33469DA6922E) for instructions.<br>
***Important***: The default port provisioned is dependent on 1) which BIG-IP version you choose to deploy as well as 2) how many interfaces (NICs) are configured on that BIG-IP. BIG-IP v13.x and later in a single-NIC configuration uses port 8443. All prior BIG-IP versions default to 443 on the MGMT interface.<br>
***Important***: If you perform the procedure to change the port, you must check the Azure Network Security Group associated with the interface on the BIG-IP that was deployed and adjust the ports accordingly.

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