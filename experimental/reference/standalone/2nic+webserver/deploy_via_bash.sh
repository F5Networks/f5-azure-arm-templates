#!/bin/bash

# Bash Script to deploy an ARM template into Azure, using azure cli 1.0
# Example Command: ./deploy_via_bash.sh --adminusr azureuser --adminpwd 'yourpassword' --dnslabel f5dnslabel --instname f5vm01 --key1 XXXXX-XXXXX-XXXXX-XXXXX-XXXXX --websrvr Both --vsport 80 --rgname f5rgname --azureusr administrator@domain.com --azurepwd 'yourpassword'

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters (instance_type is already an optional paramter)
region="westus"
template_file="azuredeploy.json"
parameter_file="azuredeploy.parameters.json"
instance_type="Standard_D2_v2"
image_name="Best"
web_server="Both"
vs_port="443"
restricted_source_address="*"
tag_values="{\"application\":\"APP\",\"environment\":\"ENV\",\"group\":\"GROUP\",\"owner\":\"OWNER\",\"cost\":\"COST\"}"

ARGS=`getopt -o a:b:c:d:e:f:g:h:i:j:k:l:m: --long adminusr:,adminpwd:,dnslabel:,instname:,insttype:,imgname:,key1:,rstsrcaddr:,websrvr:,vsport:,rgname:,azureusr:,azurepwd: -n $0 -- "$@"`
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
        -g|--key1)
            license_key_1=$2
            shift 2;;
        -h|--rstsrcaddr)
            restricted_source_address=$2
            shift 2;;
        -i|--websrvr)
            web_server=$2
            shift 2;;
        -j|--vsport)
            vs_port=$2
            shift 2;;
        -k|--rgname)
            resource_group_name=$2
            shift 2;;
        -l|--azureusr)
            azure_user=$2
            shift 2;;
        -m|--azurepwd)
            azure_pwd=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
sleep 3

#If a required paramater is not passed, the script will prompt for it below
required_variables="admin_username admin_password dns_label instance_name license_key_1 resource_group_name azure_user azure_pwd"
for variable in $required_variables
        do
        if [ -v ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done

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
azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"instanceName\":{\"value\":\"$instance_name\"},\"instanceType\":{\"value\":\"$instance_type\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"imageName\":{\"value\":\"$image_name\"},\"restrictedSrcAddress\":{\"value\":\"$restricted_source_address\"},\"webServer\":{\"value\":\"$web_server\"},\"vsPort\":{\"value\":\"$vs_port\"},\"tagValues\":{\"value\":$tag_values}}"