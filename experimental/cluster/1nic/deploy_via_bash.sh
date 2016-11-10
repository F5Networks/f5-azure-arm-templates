#!/bin/bash

# Bash Script to deploy ARM template into Azure, using azure cli 1.0
# Example Command: ./deploy_via_bash.sh --sdname sdname01 --nbrinstances 2 --adminusr azureuser --adminpwd 'password' --dnslabel label01 --key1 XXXX-XXXX --key2 XXXX-XXXX --rgname examplerg --azureusr loginuser --azurepwd loginpwd

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters (instance_type is already an optional paramter)
region="westus"
template_file="azuredeploy.json"
parameter_file="azuredeploy.parameters.json"
instance_type="Standard_D2_v2"
image_name="Best"
restricted_source_address="*"
tag_values="{\"application\":\"APP\",\"environment\":\"ENV\",\"group\":\"GROUP\",\"owner\":\"OWNER\",\"cost\":\"COST\"}"


ARGS=`getopt -o a:b:c:d:e:f:g:h:i:j:k:l:m: --long sdname:,nbrinstances:,adminusr:,adminpwd:,insttype:,imgname:,dnslabel:,key1:,key2:,rstsrcaddr:,rgname:,azureusr:,azurepwd: -n $0 -- "$@"`
eval set -- "$ARGS"


# Parse the command line arguments, primarily checking full params as short params are just placeholders
while true; do
    case "$1" in
        -a|--sdname)
            solution_deployment_name=$2
            shift 2;;
        -b|--nbrinstances)
            number_of_instances=$2
            shift 2;;
        -c|--adminusr)
            admin_username=$2
            shift 2;;
        -d|--adminpwd)
            admin_password=$2
            shift 2;;
        -e|--insttype)
            instance_type=$2
            shift 2;;
        -f|--imgname)
            image_name=$2
            shift 2;;
        -g|--dnslabel)
            dns_label=$2
            shift 2;;
        -h|--key1)
            license_key_1=$2
            shift 2;;
        -i|--key2)
            license_key_2=$2
            shift 2;;
        -j|--rstsrcaddr)
            restricted_source_address=$2
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

#If a required paramater is not passed, the script will prompt for it below
required_variables="solution_deployment_name number_of_instances admin_username admin_password dns_label license_key_1 license_key_2 resource_group_name azure_user azure_pwd"
for variable in $required_variables
        do
        if [ -v ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done

# Login to Azure, for simplicity in this example using username and password supplied as script arguments --azureusr and --azurepwd
azure login -u $azure_user -p $azure_pwd

# Switch to ARM mode
azure config mode arm

# Create ARM Group
azure group create -n $resource_group_name -l $region

# Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
# such as can been done with Powershell...oh well!
azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"solutionDeploymentName\":{\"value\":\"$solution_deployment_name\"},\"numberOfInstances\":{\"value\":$number_of_instances},\"instanceType\":{\"value\":\"$instance_type\"},\"imageName\":{\"value\":\"$image_name\"},\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"licenseKey2\":{\"value\":\"$license_key_2\"},\"restrictedSrcAddress\":{\"value\":\"$restricted_source_address\"},\"tagValues\":{\"value\":$tag_values}}"