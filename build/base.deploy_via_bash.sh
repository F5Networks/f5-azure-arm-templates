#!/bin/bash

## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
<EXAMPLE_CMD>

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters
region="westus"
restrictedSrcAddress="*"
tagValues='{"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}'

<PARAMETERS>
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
            shift 2;;<LICENSE_PARAMETERS><DYNAMIC_PARAMETERS>
        --)
            shift
            break;;
    esac
done

#If a required paramater is not passed, the script will prompt for it below
required_variables="<REQUIRED_PARAMETERS>"
for variable in $required_variables
        do
        if [ -v ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done

<LICENSE_CHECK>

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
# such as can been done with Powershell...oh well!
<DEPLOYMENT_CREATE>