#!/bin/bash

## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
## Example Command: ./deploy_via_bash.sh --adminUsername azureuser --authenticationType password --adminPasswordOrKey <value> --dnsLabel <value> --instanceType Standard_DS2_v2 --imageName Best1Gbps --bigIpVersion 15.0.100000 --bigIpModules asm:nominal --vnetName <value> --vnetResourceGroupName <value> --mgmtSubnetName <value> --declarationUrl NOT_SPECIFIED --ntpServer 0.pool.ntp.org --timeZone UTC --customImage OPTIONAL --allowUsageAnalytics Yes --vmScaleSetMinCount 2 --vmScaleSetMaxCount 4 --appInsights CREATE_NEW --scaleOutCpuThreshold 80 --scaleInCpuThreshold 20 --scaleOutThroughputThreshold 20000000 --scaleInThroughputThreshold 10000000 --scaleOutTimeWindow 10 --scaleInTimeWindow 10 --notificationEmail OPTIONAL --useAvailabilityZones Yes --autoscaleTimeout 10 --provisionPublicIP Yes --applicationProtocols http-https --applicationAddress <value> --applicationPort 80 --applicationSecurePort 443 --sslCert NOT_SPECIFIED --sslPswd NOT_SPECIFIED --applicationType Linux --blockingLevel medium --customPolicy NOT_SPECIFIED --dnsMemberIpType private --dnsMemberPort 80 --dnsProviderHost <value> --dnsProviderPort 443 --dnsProviderUser <value> --dnsProviderPassword <value> --dnsProviderPool autoscale_pool --dnsProviderDataCenter azure_datacenter --tenantId <value> --clientId <value> --servicePrincipalSecret <value> --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

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
        --authenticationType)
            authenticationType=$2
            shift 2;;
        --adminPasswordOrKey)
            adminPasswordOrKey=$2
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
        --bigIpModules)
            bigIpModules=$2
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
        --declarationUrl)
            declarationUrl=$2
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
        --vmScaleSetMinCount)
            vmScaleSetMinCount=$2
            shift 2;;
        --vmScaleSetMaxCount)
            vmScaleSetMaxCount=$2
            shift 2;;
        --appInsights)
            appInsights=$2
            shift 2;;
        --scaleOutCpuThreshold)
            scaleOutCpuThreshold=$2
            shift 2;;
        --scaleInCpuThreshold)
            scaleInCpuThreshold=$2
            shift 2;;
        --scaleOutThroughputThreshold)
            scaleOutThroughputThreshold=$2
            shift 2;;
        --scaleInThroughputThreshold)
            scaleInThroughputThreshold=$2
            shift 2;;
        --scaleOutTimeWindow)
            scaleOutTimeWindow=$2
            shift 2;;
        --scaleInTimeWindow)
            scaleInTimeWindow=$2
            shift 2;;
        --notificationEmail)
            notificationEmail=$2
            shift 2;;
        --useAvailabilityZones)
            useAvailabilityZones=$2
            shift 2;;
        --autoscaleTimeout)
            autoscaleTimeout=$2
            shift 2;;
        --provisionPublicIP)
            provisionPublicIP=$2
            shift 2;;
        --applicationProtocols)
            applicationProtocols=$2
            shift 2;;
        --applicationAddress)
            applicationAddress=$2
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
        --dnsMemberIpType)
            dnsMemberIpType=$2
            shift 2;;
        --dnsMemberPort)
            dnsMemberPort=$2
            shift 2;;
        --dnsProviderHost)
            dnsProviderHost=$2
            shift 2;;
        --dnsProviderPort)
            dnsProviderPort=$2
            shift 2;;
        --dnsProviderUser)
            dnsProviderUser=$2
            shift 2;;
        --dnsProviderPassword)
            dnsProviderPassword=$2
            shift 2;;
        --dnsProviderPool)
            dnsProviderPool=$2
            shift 2;;
        --dnsProviderDataCenter)
            dnsProviderDataCenter=$2
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
required_variables="adminUsername authenticationType adminPasswordOrKey dnsLabel instanceType imageName bigIpVersion bigIpModules vnetName vnetResourceGroupName mgmtSubnetName declarationUrl ntpServer timeZone customImage allowUsageAnalytics vmScaleSetMinCount vmScaleSetMaxCount appInsights scaleOutCpuThreshold scaleInCpuThreshold scaleOutThroughputThreshold scaleInThroughputThreshold scaleOutTimeWindow scaleInTimeWindow notificationEmail useAvailabilityZones autoscaleTimeout provisionPublicIP applicationProtocols applicationAddress applicationPort applicationSecurePort sslCert sslPswd applicationType blockingLevel customPolicy dnsMemberIpType dnsMemberPort dnsProviderHost dnsProviderPort dnsProviderUser dnsProviderPassword dnsProviderPool dnsProviderDataCenter tenantId clientId servicePrincipalSecret resourceGroupName "
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
az group deployment create --verbose --no-wait --template-file $template_file -g $resourceGroupName -n $resourceGroupName --parameters "{\"adminUsername\":{\"value\":\"$adminUsername\"},\"authenticationType\":{\"value\":\"$authenticationType\"},\"adminPasswordOrKey\":{\"value\":\"$adminPasswordOrKey\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"bigIpModules\":{\"value\":\"$bigIpModules\"},\"vnetName\":{\"value\":\"$vnetName\"},\"vnetResourceGroupName\":{\"value\":\"$vnetResourceGroupName\"},\"mgmtSubnetName\":{\"value\":\"$mgmtSubnetName\"},\"declarationUrl\":{\"value\":\"$declarationUrl\"},\"ntpServer\":{\"value\":\"$ntpServer\"},\"timeZone\":{\"value\":\"$timeZone\"},\"customImage\":{\"value\":\"$customImage\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"allowUsageAnalytics\":{\"value\":\"$allowUsageAnalytics\"},\"vmScaleSetMinCount\":{\"value\":$vmScaleSetMinCount},\"vmScaleSetMaxCount\":{\"value\":$vmScaleSetMaxCount},\"appInsights\":{\"value\":\"$appInsights\"},\"scaleOutCpuThreshold\":{\"value\":$scaleOutCpuThreshold},\"scaleInCpuThreshold\":{\"value\":$scaleInCpuThreshold},\"scaleOutThroughputThreshold\":{\"value\":$scaleOutThroughputThreshold},\"scaleInThroughputThreshold\":{\"value\":$scaleInThroughputThreshold},\"scaleOutTimeWindow\":{\"value\":$scaleOutTimeWindow},\"scaleInTimeWindow\":{\"value\":$scaleInTimeWindow},\"notificationEmail\":{\"value\":\"$notificationEmail\"},\"useAvailabilityZones\":{\"value\":\"$useAvailabilityZones\"},\"autoscaleTimeout\":{\"value\":$autoscaleTimeout},\"provisionPublicIP\":{\"value\":\"$provisionPublicIP\"},\"applicationProtocols\":{\"value\":\"$applicationProtocols\"},\"applicationAddress\":{\"value\":\"$applicationAddress\"},\"applicationPort\":{\"value\":\"$applicationPort\"},\"applicationSecurePort\":{\"value\":\"$applicationSecurePort\"},\"sslCert\":{\"value\":\"$sslCert\"},\"sslPswd\":{\"value\":\"$sslPswd\"},\"applicationType\":{\"value\":\"$applicationType\"},\"blockingLevel\":{\"value\":\"$blockingLevel\"},\"customPolicy\":{\"value\":\"$customPolicy\"},\"dnsMemberIpType\":{\"value\":\"$dnsMemberIpType\"},\"dnsMemberPort\":{\"value\":\"$dnsMemberPort\"},\"dnsProviderHost\":{\"value\":\"$dnsProviderHost\"},\"dnsProviderPort\":{\"value\":\"$dnsProviderPort\"},\"dnsProviderUser\":{\"value\":\"$dnsProviderUser\"},\"dnsProviderPassword\":{\"value\":\"$dnsProviderPassword\"},\"dnsProviderPool\":{\"value\":\"$dnsProviderPool\"},\"dnsProviderDataCenter\":{\"value\":\"$dnsProviderDataCenter\"},\"tenantId\":{\"value\":\"$tenantId\"},\"clientId\":{\"value\":\"$clientId\"},\"servicePrincipalSecret\":{\"value\":\"$servicePrincipalSecret\"}}"