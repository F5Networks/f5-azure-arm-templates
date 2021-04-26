#!/bin/bash

## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
<EXAMPLE_CMD>

# Assign Script Parameters and Define Variables
# Specify static items below, change these as needed or make them parameters
region="westus"
tagValues='{"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}'

# Parse the command line arguments, primarily checking full params as short params are just placeholders
while [[ $# -gt 1 ]]; do
    case "$1" in
<DYNAMIC_PARAMETERS>
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
        --restrictedSrcAddress)
            restrictedSrcAddress=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

#If a required parameter is not passed, the script will prompt for it below
required_variables="<REQUIRED_PARAMETERS>"
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
<DEPLOYMENT_CREATE>