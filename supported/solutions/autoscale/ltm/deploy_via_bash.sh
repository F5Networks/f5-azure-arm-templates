#!/bin/bash

## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth 200m --vmScaleSetMinCount 2 --vmScaleSetMaxCount 4 --scaleOutThroughput 90 --scaleInThroughput 10 --scaleTimeWindow 10 --adminUsername azureuser --adminPassword <value> --dnsLabel <value> --instanceType Standard_DS2_v2 --imageName Good --bigIpVersion 13.0.021 --tenantId <value> --clientId <value> --servicePrincipalSecret <value> --ntpServer 0.pool.ntp.org --timeZone UTC --restrictedSrcAddress "*" --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

# Assign Script parameters and Define Variables
# Specify static items, change these as needed or make them parameters
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
        --vmScaleSetMinCount)
            vmScaleSetMinCount=$2
            shift 2;;
        --vmScaleSetMaxCount)
            vmScaleSetMaxCount=$2
            shift 2;;
        --scaleOutThroughput)
            scaleOutThroughput=$2
            shift 2;;
        --scaleInThroughput)
            scaleInThroughput=$2
            shift 2;;
        --scaleTimeWindow)
            scaleTimeWindow=$2
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
        --instanceType)
            instanceType=$2
            shift 2;;
        --imageName)
            imageName=$2
            shift 2;;
        --bigIpVersion)
            bigIpVersion=$2
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
required_variables="vmScaleSetMinCount vmScaleSetMaxCount scaleOutThroughput scaleInThroughput scaleTimeWindow adminUsername adminPassword dnsLabel instanceType imageName bigIpVersion tenantId clientId servicePrincipalSecret ntpServer timeZone resourceGroupName licenseType "
for variable in $required_variables
        do
        if [ -z ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done

# Prompt for licensed bandwidth if not supplied and PAYG is selected
if [ $licenseType == "PAYG" ]; then
    if [ -z $licensedBandwidth ] ; then
            read -p "Please enter value for licensedBandwidth:" licensedBandwidth
    fi
    template_file="./azuredeploy.json"
    parameter_file="./azuredeploy.parameters.json"
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
azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"vmScaleSetMinCount\":{\"value\":$vmScaleSetMinCount},\"vmScaleSetMaxCount\":{\"value\":$vmScaleSetMaxCount},\"scaleOutThroughput\":{\"value\":$scaleOutThroughput},\"scaleInThroughput\":{\"value\":$scaleInThroughput},\"scaleTimeWindow\":{\"value\":$scaleTimeWindow},\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"tenantId\":{\"value\":\"$tenantId\"},\"clientId\":{\"value\":\"$clientId\"},\"servicePrincipalSecret\":{\"value\":\"$servicePrincipalSecret\"},\"ntpServer\":{\"value\":\"$ntpServer\"},\"timeZone\":{\"value\":\"$timeZone\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"licensedBandwidth\":{\"value\":\"$licensedBandwidth\"}}"