#!/bin/bash

## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth 200m --vmScaleSetMinCount 2 --vmScaleSetMaxCount 4 --scaleOutThroughput 90 --scaleInThroughput 10 --scaleTimeWindow 10 --adminUsername azureuser --adminPassword <value> --dnsLabel <value> --instanceType Standard_D2_v2 --imageName Best --bigIpVersion 13.0.000 --solutionDeploymentName <value> --applicationProtocols http-https --applicationAddress <value> --applicationServiceFqdn NOT_SPECIFIED --applicationPort 80 --applicationSecurePort 443 --sslCert NOT_SPECIFIED --sslPswd NOT_SPECIFIED --applicationType Linux --blockingLevel medium --customPolicy NOT_SPECIFIED --tenantId <value> --clientId <value> --servicePrincipalSecret <value> --restrictedSrcAddress "*" --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters
region="westus"
restrictedSrcAddress="*"
tagValues='{"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}'

ARGS=`getopt -o a:b:c:d:e:f:g:h:i:j:k:l:m:n:o:p:q:r:s:t:u:v:w:x:y:z:aa:bb:cc:dd:ee:ff: --long resourceGroupName:,azureLoginUser:,azureLoginPassword:,licenseType:,licensedBandwidth:,licenseKey1:,vmScaleSetMinCount:,vmScaleSetMaxCount:,scaleOutThroughput:,scaleInThroughput:,scaleTimeWindow:,adminUsername:,adminPassword:,dnsLabel:,instanceType:,imageName:,bigIpVersion:,solutionDeploymentName:,applicationProtocols:,applicationAddress:,applicationServiceFqdn:,applicationPort:,applicationSecurePort:,sslCert:,sslPswd:,applicationType:,blockingLevel:,customPolicy:,tenantId:,clientId:,servicePrincipalSecret:,restrictedSrcAddress: -n $0 -- "$@"`
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
        -g|--vmScaleSetMinCount)
            vmScaleSetMinCount=$2
            shift 2;;
        -h|--vmScaleSetMaxCount)
            vmScaleSetMaxCount=$2
            shift 2;;
        -i|--scaleOutThroughput)
            scaleOutThroughput=$2
            shift 2;;
        -j|--scaleInThroughput)
            scaleInThroughput=$2
            shift 2;;
        -k|--scaleTimeWindow)
            scaleTimeWindow=$2
            shift 2;;
        -l|--adminUsername)
            adminUsername=$2
            shift 2;;
        -m|--adminPassword)
            adminPassword=$2
            shift 2;;
        -n|--dnsLabel)
            dnsLabel=$2
            shift 2;;
        -o|--instanceType)
            instanceType=$2
            shift 2;;
        -p|--imageName)
            imageName=$2
            shift 2;;
        -q|--bigIpVersion)
            bigIpVersion=$2
            shift 2;;
        -r|--solutionDeploymentName)
            solutionDeploymentName=$2
            shift 2;;
        -s|--applicationProtocols)
            applicationProtocols=$2
            shift 2;;
        -t|--applicationAddress)
            applicationAddress=$2
            shift 2;;
        -u|--applicationServiceFqdn)
            applicationServiceFqdn=$2
            shift 2;;
        -v|--applicationPort)
            applicationPort=$2
            shift 2;;
        -w|--applicationSecurePort)
            applicationSecurePort=$2
            shift 2;;
        -x|--sslCert)
            sslCert=$2
            shift 2;;
        -y|--sslPswd)
            sslPswd=$2
            shift 2;;
        -z|--applicationType)
            applicationType=$2
            shift 2;;
        -aa|--blockingLevel)
            blockingLevel=$2
            shift 2;;
        -bb|--customPolicy)
            customPolicy=$2
            shift 2;;
        -cc|--tenantId)
            tenantId=$2
            shift 2;;
        -dd|--clientId)
            clientId=$2
            shift 2;;
        -ee|--servicePrincipalSecret)
            servicePrincipalSecret=$2
            shift 2;;
        -ff|--restrictedSrcAddress)
            restrictedSrcAddress=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

#If a required paramater is not passed, the script will prompt for it below
required_variables="vmScaleSetMinCount vmScaleSetMaxCount scaleOutThroughput scaleInThroughput scaleTimeWindow adminUsername adminPassword dnsLabel instanceType imageName bigIpVersion solutionDeploymentName applicationProtocols applicationAddress applicationServiceFqdn applicationPort applicationSecurePort sslCert sslPswd applicationType blockingLevel customPolicy tenantId clientId servicePrincipalSecret resourceGroupName licenseType "
for variable in $required_variables
        do
        if [ -v ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done

# Prompt for licensed bandwidth if not supplied and PAYG is selected
if [ $licenseType == "PAYG" ]; then
    if [ -v $licensedBandwidth ] ; then
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
azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"vmScaleSetMinCount\":{\"value\":$vmScaleSetMinCount},\"vmScaleSetMaxCount\":{\"value\":$vmScaleSetMaxCount},\"scaleOutThroughput\":{\"value\":$scaleOutThroughput},\"scaleInThroughput\":{\"value\":$scaleInThroughput},\"scaleTimeWindow\":{\"value\":$scaleTimeWindow},\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"solutionDeploymentName\":{\"value\":\"$solutionDeploymentName\"},\"applicationProtocols\":{\"value\":\"$applicationProtocols\"},\"applicationAddress\":{\"value\":\"$applicationAddress\"},\"applicationServiceFqdn\":{\"value\":\"$applicationServiceFqdn\"},\"applicationPort\":{\"value\":\"$applicationPort\"},\"applicationSecurePort\":{\"value\":\"$applicationSecurePort\"},\"sslCert\":{\"value\":\"$sslCert\"},\"sslPswd\":{\"value\":\"$sslPswd\"},\"applicationType\":{\"value\":\"$applicationType\"},\"blockingLevel\":{\"value\":\"$blockingLevel\"},\"customPolicy\":{\"value\":\"$customPolicy\"},\"tenantId\":{\"value\":\"$tenantId\"},\"clientId\":{\"value\":\"$clientId\"},\"servicePrincipalSecret\":{\"value\":\"$servicePrincipalSecret\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"licensedBandwidth\":{\"value\":\"$licensedBandwidth\"}}"