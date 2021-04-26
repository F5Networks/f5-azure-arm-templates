#  expectValue = "success"
#  scriptTimeout = 2
#  replayEnabled = false
#  replayTimeout = 0

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

# Get BIG-IP management/external IPs
HOST=$(az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["guI-URL"].value' --raw-output | cut -d' ' -f1)
echo "Verify Host: $HOST"
EXT0=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-ext0 | jq .ipConfigurations[0].privateIpAddress -r)
echo "Verify EXT0: $EXT0"
EXT1=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-ext1 | jq .ipConfigurations[0].privateIpAddress -r)
echo "Verify EXT1: $EXT1"

# This is the route created by the azure-vnet-bastion.json template
ROUTE='192.168.3.0/24'

DATA='{"class": "Cloud_Failover", "environment": "azure", "externalStorage": {"scopingTags": {"f5_cloud_failover_label": "<RESOURCE GROUP>"}}, "failoverAddresses": {"scopingTags": {"f5_cloud_failover_label": "<RESOURCE GROUP>"}}, "failoverRoutes": {"enabled": true, "scopingTags": {"f5_cloud_failover_label": "<RESOURCE GROUP>"}, "scopingAddressRanges": [{"range": "'"$ROUTE"'"}], "defaultNextHopAddresses": {"discoveryType": "static", "items": ["'"$EXT0"'", "'"$EXT1"'"]}}}'

# POST the new CFE config
case <CREATE PUBLIC IP> in
"No")
    BASTION_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bastionIp"].value' --raw-output | cut -d' ' -f1`
    echo "Verify bastion host: $BASTION_HOST"
    NEW_CFE_RESPONSE=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 -X POST -H 'Content-Type: application/json' $HOST/mgmt/shared/cloud-failover/declare -d '${DATA}' | jq -r .message") ;;
*)
    NEW_CFE_RESPONSE=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 -X POST -H 'Content-Type: application/json' $HOST/mgmt/shared/cloud-failover/declare -d "${DATA}" | jq -r .message) ;;
esac

echo $NEW_CFE_RESPONSE