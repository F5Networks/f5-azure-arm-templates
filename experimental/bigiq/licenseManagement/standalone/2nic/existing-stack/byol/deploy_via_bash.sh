#!/bin/bash

## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
## Example Command: ./deploy_via_bash.sh --adminUsername azureuser --adminPassword <value> --masterKey <value> --dnsLabel <value> --instanceName f5vm01 --instanceType Standard_D4s_v3 --bigIqVersion 6.1.000000 --bigIqLicenseKey1 <value> --licensePoolKeys Do_Not_Create --regPoolKeys Do_Not_Create --numberOfInternalIps 1 --vnetName <value> --vnetResourceGroupName <value> --mgmtSubnetName <value> --mgmtIpAddress <value> --internalSubnetName <value> --internalIpAddressRangeStart <value> --avSetChoice CREATE_NEW --ntpServer 0.pool.ntp.org --timeZone UTC --customImage OPTIONAL --allowUsageAnalytics Yes --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

# Assign Script Parameters and Define Variables
# Specify static items below, change these as needed or make them parameters
region="westus"
restrictedSrcAddress="*"
tagValues='{"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}'

# Parse the command line arguments, primarily checking full params as short params are just placeholders
while [[ $# -gt 1 ]]; do
    case "$1" in
        --adminUsername)
            adminUsername=$2
            shift 2;;
        --adminPassword)
            adminPassword=$2
            shift 2;;
        --masterKey)
            masterKey=$2
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
        --bigIqVersion)
            bigIqVersion=$2
            shift 2;;
        --bigIqLicenseKey1)
            bigIqLicenseKey1=$2
            shift 2;;
        --licensePoolKeys)
            licensePoolKeys=$2
            shift 2;;
        --regPoolKeys)
            regPoolKeys=$2
            shift 2;;
        --numberOfInternalIps)
            numberOfInternalIps=$2
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
        --mgmtIpAddress)
            mgmtIpAddress=$2
            shift 2;;
        --internalSubnetName)
            internalSubnetName=$2
            shift 2;;
        --internalIpAddressRangeStart)
            internalIpAddressRangeStart=$2
            shift 2;;
        --avSetChoice)
            avSetChoice=$2
            shift 2;;
        --ntpServer)
            ntpServer=$2
            shift 2;;
        --timeZone)
            timeZone=$2
            shift 2;;
        --customImage)
            customImage=$2
            shift 2;;
        --restrictedSrcAddress)
            restrictedSrcAddress=$2
            shift 2;;
        --tagValues)
            tagValues=$2
            shift 2;;
        --allowUsageAnalytics)
            allowUsageAnalytics=$2
            shift 2;;
        --resourceGroupName)
            resourceGroupName=$2
            shift 2;;
        --region)
            region=$2
            shift 2;;
        --azureLoginUser)
            azureLoginUser=$2
            shift 2;;
        --azureLoginPassword)
            azureLoginPassword=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

#If a required parameter is not passed, the script will prompt for it below
required_variables="adminUsername adminPassword masterKey dnsLabel instanceName instanceType bigIqVersion bigIqLicenseKey1 licensePoolKeys regPoolKeys numberOfInternalIps vnetName vnetResourceGroupName mgmtSubnetName mgmtIpAddress internalSubnetName internalIpAddressRangeStart avSetChoice ntpServer timeZone customImage allowUsageAnalytics resourceGroupName "
for variable in $required_variables
        do
        if [ -z ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done

echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
sleep 3

# Login to Azure, for simplicity in this example using username and password supplied as script arguments --azureLoginUser and --azureLoginPassword
# Perform Check to see if already logged in
az account show > /dev/null 2>&1
if [[ $? != 0 ]] ; then
        az login -u $azureLoginUser -p $azureLoginPassword
fi

# Create ARM Group
az group create -n $resourceGroupName -l $region

# Deploy ARM Template, right now cannot specify parameter file and parameters inline via Azure CLI
template_file="./azuredeploy.json"
parameter_file="./azuredeploy.parameters.json"
az group deployment create --verbose --no-wait --template-file $template_file -g $resourceGroupName -n $resourceGroupName --parameters "{\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"masterKey\":{\"value\":\"$masterKey\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceName\":{\"value\":\"$instanceName\"},\"instanceType\":{\"value\":\"$instanceType\"},\"bigIqVersion\":{\"value\":\"$bigIqVersion\"},\"bigIqLicenseKey1\":{\"value\":\"$bigIqLicenseKey1\"},\"licensePoolKeys\":{\"value\":\"$licensePoolKeys\"},\"regPoolKeys\":{\"value\":\"$regPoolKeys\"},\"numberOfInternalIps\":{\"value\":$numberOfInternalIps},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"mgmtIpAddress\":{\"value\":\"$mgmtIpAddress\"},\"internalSubnetName\":{\"value\":\"$internalSubnetName\"},\"internalIpAddressRangeStart\":{\"value\":\"$internalIpAddressRangeStart\"},\"avSetChoice\":{\"value\":\"$avSetChoice\"},\"ntpServer\":{\"value\":\"$ntpServer\"},\"timeZone\":{\"value\":\"$timeZone\"},\"customImage\":{\"value\":\"$customImage\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"allowUsageAnalytics\":{\"value\":\"$allowUsageAnalytics\"}}"