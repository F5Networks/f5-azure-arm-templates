#!/bin/bash

# Script to deploy 1nic/2nic ARM template into Azure, using azure cli 1.0
# Example Command: ./deploy_via_bash.sh -u azureuser -p 'yourpassword' -d f52nicdeploy01 -n f52nic -l XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -r f52nicdeploy01 -y adminstrator@domain.com -z 'yourpassword'

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters (vm_size is already an optional paramter)
region="westus"
template_file="azuredeploy.json"
parameter_file="azuredeploy.parameters.json"
vm_size="Standard_D2_v2"

while getopts u:p:d:n:s:l:r:y:z: option
do	case "$option"  in
        u) admin_username=$OPTARG;;
        p) admin_password=$OPTARG;;
	    d) dns_label_prefix=$OPTARG;;
        n) vm_name=$OPTARG;;
        s) vm_size=$OPTARG;;
        l) license_token=$OPTARG;;
        r) resource_group_name=$OPTARG;;
		y) azure_user=$OPTARG;;
		z) azure_pwd=$OPTARG;;
    esac
done
# Check for Mandatory Args
if [ ! "$admin_username" ] || [ ! "$admin_password" ] || [ ! "$dns_label_prefix" ] || [ ! "$vm_name" ] || [ ! "$license_token" ] || [ ! "$resource_group_name" ] || [ ! "$azure_user" ] || [ ! "$azure_pwd" ]
then
    echo "One of the mandatory parameters was not specified!"
    exit 1
fi


# Login to Azure, for simplicity in this example using username and password as supplied as script arguments y and z
azure login -u $azure_user -p $azure_pwd

# Switch to ARM mode
azure config mode arm

# Create ARM Group
azure group create -n $resource_group_name -l $region

# Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
# such as can been done with Powershell...oh well!
azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabelPrefix\":{\"value\":\"$dns_label_prefix\"},\"vmName\":{\"value\":\"$vm_name\"},\"vmSize\":{\"value\":\"$vm_size\"},\"licenseToken1\":{\"value\":\"$license_token\"}}"



