#!/bin/bash

# Example Script to automate deployment of ARM template(s) into Azure, using azure cli 1.0

# Define Variables
random_number=$(cat /dev/urandom | tr -dc '0-99999' | fold -w 8 | head -n 1)
resource_group="f52nicauto$random_number"
adminusername="azureuser"
adminpassword="P4ssw0rd!azure"
dnslabelprefix="f52nicauto$random_number"
vmname="f52nicvm01"
vmsize="Standard_D2_v2"
licensetoken="XXXX-XXXX"
region="westus"
template_file="azuredeploy.json"
parameter_file="azuredeploy.parameters.json"


# Login to Azure, for simplicity in this example using username and password directly in the script
azure login -u administrator365@discoveryeselabs.com -p P4ssw0rd!

# Switch to ARM mode
azure config mode arm

# Create ARM Group
azure group create -n $resource_group -l $region

# Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
# such as can been done with Powershell...oh well!
azure group deployment create -f $template_file -g $resource_group -n $resource_group -p "{\"adminUsername\":{\"value\":\"$adminusername\"},\"adminPassword\":{\"value\":\"$adminpassword\"},\"dnsLabelPrefix\":{\"value\":\"$dnslabelprefix\"},\"vmName\":{\"value\":\"$vmname\"},\"vmSize\":{\"value\":\"$vmsize\"},\"licenseToken1\":{\"value\":\"$licensetoken\"}}"



