#!/bin/bash

## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth 200m --vmScaleSetMinCount 2 --vmScaleSetMaxCount 4 --autoScaleMetric F5_TMM_Traffic --appInsights CREATE_NEW --calculatedBandwidth 200m --scaleOutThreshold 90 --scaleInThreshold 10 --scaleTimeWindow 10 --adminUsername azureuser --adminPassword <value> --dnsLabel <value> --instanceType Standard_DS2_v2 --imageName Best --bigIpVersion 13.1.0200 --vnetName <value> --vnetResourceGroupName <value> --mgmtSubnetName <value> --solutionDeploymentName <value> --applicationProtocols http-https --applicationAddress <value> --applicationServiceFqdn NOT_SPECIFIED --applicationPort 80 --applicationSecurePort 443 --sslCert NOT_SPECIFIED --sslPswd NOT_SPECIFIED --applicationType Linux --blockingLevel medium --customPolicy NOT_SPECIFIED --tenantId <value> --clientId <value> --servicePrincipalSecret <value> --notificationEmail OPTIONAL --ntpServer 0.pool.ntp.org --timeZone UTC --allowUsageAnalytics Yes --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

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
        --bigIqAddress)
            bigIqAddress=$2
            shift 2;;
        --bigIqUsername)
            bigIqUsername=$2
            shift 2;;
        --bigIqPassword)
            bigIqPassword=$2
            shift 2;;
        --bigIqLicensePoolName)
            bigIqLicensePoolName=$2
            shift 2;;
        --vmScaleSetMinCount)
            vmScaleSetMinCount=$2
            shift 2;;
        --vmScaleSetMaxCount)
            vmScaleSetMaxCount=$2
            shift 2;;
        --autoScaleMetric)
            autoScaleMetric=$2
            shift 2;;
        --appInsights)
            appInsights=$2
            shift 2;;
        --calculatedBandwidth)
            calculatedBandwidth=$2
            shift 2;;
        --scaleOutThreshold)
            scaleOutThreshold=$2
            shift 2;;
        --scaleInThreshold)
            scaleInThreshold=$2
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
        --vnetName)
            vnetName=$2
            shift 2;;
        --vnetResourceGroupName)
            vnetResourceGroupName=$2
            shift 2;;
        --mgmtSubnetName)
            mgmtSubnetName=$2
            shift 2;;
        --solutionDeploymentName)
            solutionDeploymentName=$2
            shift 2;;
        --applicationProtocols)
            applicationProtocols=$2
            shift 2;;
        --applicationAddress)
            applicationAddress=$2
            shift 2;;
        --applicationServiceFqdn)
            applicationServiceFqdn=$2
            shift 2;;
        --applicationPort)
            applicationPort=$2
            shift 2;;
        --applicationSecurePort)
            applicationSecurePort=$2
            shift 2;;
        --sslCert)
            sslCert=$2
            shift 2;;
        --sslPswd)
            sslPswd=$2
            shift 2;;
        --applicationType)
            applicationType=$2
            shift 2;;
        --blockingLevel)
            blockingLevel=$2
            shift 2;;
        --customPolicy)
            customPolicy=$2
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
        --notificationEmail)
            notificationEmail=$2
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
        --tagValues)
            tagValues=$2
            shift 2;;
        --allowUsageAnalytics)
            allowUsageAnalytics=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

#If a required parameter is not passed, the script will prompt for it below
required_variables="vmScaleSetMinCount vmScaleSetMaxCount autoScaleMetric appInsights calculatedBandwidth scaleOutThreshold scaleInThreshold scaleTimeWindow adminUsername adminPassword dnsLabel instanceType imageName bigIpVersion vnetName vnetResourceGroupName mgmtSubnetName solutionDeploymentName applicationProtocols applicationAddress applicationServiceFqdn applicationPort applicationSecurePort sslCert sslPswd applicationType blockingLevel customPolicy tenantId clientId servicePrincipalSecret notificationEmail ntpServer timeZone allowUsageAnalytics resourceGroupName licenseType "
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
    template_file="./PAYG/azuredeploy.json"
    parameter_file="./PAYG/azuredeploy.parameters.json"
fi
# Prompt for BIGIQ parameters if not supplied and BIGIQ is selected
if [ $licenseType == "BIGIQ" ]; then
	big_iq_vars="bigIqAddress bigIqUsername bigIqPassword bigIqLicensePoolName"
	for variable in $big_iq_vars
			do
			if [ -z ${!variable} ] ; then
					read -p "Please enter value for $variable:" $variable
			fi
	done
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
if [ $licenseType == "PAYG" ]; then
    azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"vmScaleSetMinCount\":{\"value\":$vmScaleSetMinCount},\"vmScaleSetMaxCount\":{\"value\":$vmScaleSetMaxCount},\"autoScaleMetric\":{\"value\":\"$autoScaleMetric\"},\"appInsights\":{\"value\":\"$appInsights\"},\"calculatedBandwidth\":{\"value\":\"$calculatedBandwidth\"},\"scaleOutThreshold\":{\"value\":$scaleOutThreshold},\"scaleInThreshold\":{\"value\":$scaleInThreshold},\"scaleTimeWindow\":{\"value\":$scaleTimeWindow},\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"solutionDeploymentName\":{\"value\":\"$solutionDeploymentName\"},\"applicationProtocols\":{\"value\":\"$applicationProtocols\"},\"applicationAddress\":{\"value\":\"$applicationAddress\"},\"applicationServiceFqdn\":{\"value\":\"$applicationServiceFqdn\"},\"applicationPort\":{\"value\":\"$applicationPort\"},\"applicationSecurePort\":{\"value\":\"$applicationSecurePort\"},\"sslCert\":{\"value\":\"$sslCert\"},\"sslPswd\":{\"value\":\"$sslPswd\"},\"applicationType\":{\"value\":\"$applicationType\"},\"blockingLevel\":{\"value\":\"$blockingLevel\"},\"customPolicy\":{\"value\":\"$customPolicy\"},\"tenantId\":{\"value\":\"$tenantId\"},\"clientId\":{\"value\":\"$clientId\"},\"servicePrincipalSecret\":{\"value\":\"$servicePrincipalSecret\"},\"notificationEmail\":{\"value\":\"$notificationEmail\"},\"ntpServer\":{\"value\":\"$ntpServer\"},\"timeZone\":{\"value\":\"$timeZone\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"allowUsageAnalytics\":{\"value\":\"$allowUsageAnalytics\"},\"licensedBandwidth\":{\"value\":\"$licensedBandwidth\"}}"
elif [ $licenseType == "BIGIQ" ]; then
    azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"vmScaleSetMinCount\":{\"value\":$vmScaleSetMinCount},\"vmScaleSetMaxCount\":{\"value\":$vmScaleSetMaxCount},\"autoScaleMetric\":{\"value\":\"$autoScaleMetric\"},\"appInsights\":{\"value\":\"$appInsights\"},\"calculatedBandwidth\":{\"value\":\"$calculatedBandwidth\"},\"scaleOutThreshold\":{\"value\":$scaleOutThreshold},\"scaleInThreshold\":{\"value\":$scaleInThreshold},\"scaleTimeWindow\":{\"value\":$scaleTimeWindow},\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"solutionDeploymentName\":{\"value\":\"$solutionDeploymentName\"},\"applicationProtocols\":{\"value\":\"$applicationProtocols\"},\"applicationAddress\":{\"value\":\"$applicationAddress\"},\"applicationServiceFqdn\":{\"value\":\"$applicationServiceFqdn\"},\"applicationPort\":{\"value\":\"$applicationPort\"},\"applicationSecurePort\":{\"value\":\"$applicationSecurePort\"},\"sslCert\":{\"value\":\"$sslCert\"},\"sslPswd\":{\"value\":\"$sslPswd\"},\"applicationType\":{\"value\":\"$applicationType\"},\"blockingLevel\":{\"value\":\"$blockingLevel\"},\"customPolicy\":{\"value\":\"$customPolicy\"},\"tenantId\":{\"value\":\"$tenantId\"},\"clientId\":{\"value\":\"$clientId\"},\"servicePrincipalSecret\":{\"value\":\"$servicePrincipalSecret\"},\"notificationEmail\":{\"value\":\"$notificationEmail\"},\"ntpServer\":{\"value\":\"$ntpServer\"},\"timeZone\":{\"value\":\"$timeZone\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"allowUsageAnalytics\":{\"value\":\"$allowUsageAnalytics\"},\"bigIqAddress\":{\"value\":\"$bigIqAddress\"},\"bigIqUsername\":{\"value\":\"$bigIqUsername\"}},\"bigIqPassword\":{\"value\":\"$bigIqPassword\"}},\"bigIqLicensePoolName\":{\"value\":\"$bigIqLicensePoolName\"}}"
else
    echo "Please select a valid license type of PAYG or BIGIQ."
    exit 1
fi