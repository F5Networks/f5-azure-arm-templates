#!/usr/bin/env bash
#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 5

TMP_DIR='/tmp/<DEWPOINT JOB ID>'
PORT=$(az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["guI-URL"].value' --raw-output | cut -d' ' -f2 | cut -d':' -f3)
echo "PORT:$PORT"
# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

# Get BIG-IP management
case <CREATE PUBLIC IP> in
"No")
    HOST0=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt0 | jq .ipConfigurations[0].privateIpAddress -r)
    HOST1=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt1 | jq .ipConfigurations[0].privateIpAddress -r)
    BASTION_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bastionIp"].value' --raw-output | cut -d' ' -f1`
    echo "BASTION HOST: $BASTION_HOST"
    response=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' https://${HOST0}:${PORT}/mgmt/shared/cloud-failover/declare")
    response2=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' https://${HOST1}:${PORT}/mgmt/shared/cloud-failover/declare") ;;
*)
    HOST0=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip0 | jq .ipAddress -r)
    HOST1=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip1 | jq .ipAddress -r)
    response=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST0}:${PORT}/mgmt/shared/cloud-failover/declare)
    response2=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST1}:${PORT}/mgmt/shared/cloud-failover/declare) ;;
esac

echo "CFE Declaration1: $response\n"
echo "CFE Declaration1: $response2\n"

# Evaluate
if echo $response | jq -r .message | grep 'success' && echo $response2 | jq -r .message | grep 'success'; then
    result="SUCCESS"
else
    result="FAILED"
fi
echo "$result"