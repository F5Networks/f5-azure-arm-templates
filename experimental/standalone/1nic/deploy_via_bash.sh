#!/bin/bash

# Script to deploy 1nic/2nic ARM template into Azure, using azure cli 1.0
# Example Command: ./deploy_via_bash.sh -u azureuser -p 'yourpassword' -d f51nicdeploy01 -n f51nic -l XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -r f51nicdeploy01 -y adminstrator@domain.com -z 'yourpassword'

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters (instance_type is already an optional paramter)
region="westus"
template_file="azuredeploy.json"
parameter_file="azuredeploy.parameters.json"
instance_type="Standard_D2_v2"
image_name="Best"

while getopts u:p:d:n:s:k:l:r:y:z: option
do	case "$option"  in
        u) admin_username=$OPTARG;;
        p) admin_password=$OPTARG;;
	    d) dns_label=$OPTARG;;
        n) instance_name=$OPTARG;;
        s) instance_type=$OPTARG;;
        k) image_name=$OPTARG;;
        l) license_key_1=$OPTARG;;
        r) resource_group_name=$OPTARG;;
		y) azure_user=$OPTARG;;
		z) azure_pwd=$OPTARG;;
    esac
done
# Check for Mandatory Args
if [ ! "$admin_username" ] || [ ! "$admin_password" ] || [ ! "$dns_label" ] || [ ! "$instance_name" ] || [ ! "$license_key_1" ] || [ ! "$resource_group_name" ] || [ ! "$azure_user" ] || [ ! "$azure_pwd" ]
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
azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"instanceName\":{\"value\":\"$instance_name\"},\"instanceType\":{\"value\":\"$instance_type\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"imageName\":{\"value\":\"$image_name\"}}"



