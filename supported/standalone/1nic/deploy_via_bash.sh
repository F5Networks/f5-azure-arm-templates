#!/bin/bash

# Bash Script to deploy an ARM template into Azure, using azure cli 1.0
# Example Command: ./deploy_via_bash.sh --adminusr azureuser --adminpwd 'yourpassword' --dnslabel f5dnslabel --instname f5vm01 --rgname f5rgname --lictype payg --azureusr administrator@domain.com --azurepwd 'yourpassword'

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters (instance_type is already an optional paramter)
region="westus"
template_file="./PAYG/azuredeploy.json"
parameter_file="./PAYG/azuredeploy.parameters.json"
instance_type="Standard_D2_v2"
image_name="Best"
restricted_source_address="*"
tag_values="{\"application\":\"APP\",\"environment\":\"ENV\",\"group\":\"GROUP\",\"owner\":\"OWNER\",\"cost\":\"COST\"}"

ARGS=`getopt -o a:b:c:d:e:f:g:h:i:j:k:l: --long adminusr:,adminpwd:,dnslabel:,instname:,insttype:,imgname:,lictype:,key1:,rstsrcaddr:,rgname:,azureusr:,azurepwd: -n $0 -- "$@"`
eval set -- "$ARGS"


# Parse the command line arguments, primarily checking full params as short params are just placeholders
while true; do
    case "$1" in
        -a|--adminusr)
            admin_username=$2
            shift 2;;
        -b|--adminpwd)
            admin_password=$2
            shift 2;;
        -c|--dnslabel)
            dns_label=$2
            shift 2;;
        -d|--instname)
            instance_name=$2
            shift 2;;
        -e|--insttype)
            instance_type=$2
            shift 2;;
        -f|--imgname)
            image_name=$2
            shift 2;;
        -g|--lictype)
            license_type=$2
            shift 2;;
        -h|--key1)
            license_key_1=$2
            shift 2;;
        -i|--rstsrcaddr)
            restricted_source_address=$2
            shift 2;;
        -j|--rgname)
            resource_group_name=$2
            shift 2;;
        -k|--azureusr)
            azure_user=$2
            shift 2;;
        -l|--azurepwd)
            azure_pwd=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done
#If a required parameter is not passed, the script will prompt for it below
required_variables="admin_username admin_password dns_label instance_name license_type resource_group_name azure_user azure_pwd"
for variable in $required_variables
        do
        if [ -v ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done
# Prompt for license key if not supplied and byol is selected
if [ $license_type == "byol" ]; then
    if [ -v $license_key_1 ] ; then
            read -p "Please enter value for license_key_1:" license_key_1
    fi
    template_file="./BYOL/azuredeploy.json"
    parameter_file="./BYOL/azuredeploy.parameters.json"
fi

echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
sleep 3

# Login to Azure, for simplicity in this example using username and password supplied as script arguments --azureusr and --azurepwd
# Perform Check to see if already logged in
azure account show > /dev/null 2>&1
if [[ $? != 0 ]] ; then
        azure login -u $azure_user -p $azure_pwd
fi

# Switch to ARM mode
azure config mode arm

# Create ARM Group
azure group create -n $resource_group_name -l $region

# Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
# such as can been done with Powershell...oh well!
if [ $license_type == "byol" ]; then
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"instanceName\":{\"value\":\"$instance_name\"},\"instanceType\":{\"value\":\"$instance_type\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"imageName\":{\"value\":\"$image_name\"},\"restrictedSrcAddress\":{\"value\":\"$restricted_source_address\"},\"tagValues\":{\"value\":$tag_values}}"
elif [ $license_type == "payg" ]; then
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"instanceName\":{\"value\":\"$instance_name\"},\"instanceType\":{\"value\":\"$instance_type\"},\"imageName\":{\"value\":\"$image_name\"},\"restrictedSrcAddress\":{\"value\":\"$restricted_source_address\"},\"tagValues\":{\"value\":$tag_values}}"
else
    echo "Uh oh, shouldn't make it here! Ensure license type is either payg or byol"
    exit 1
fi