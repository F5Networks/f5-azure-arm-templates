#!/usr/bin/env bash
#  expectValue = "Registration Key is set"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

if [[ "<CLUSTER>" == "Yes" ]]; then
    IP=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip0 | jq .ipAddress --raw-output)
    IP2=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip1 | jq .ipAddress --raw-output)
else
    IP=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-<MGMT PIP1> | jq .ipAddress --raw-output)
fi
PORT=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["ssH-URL"].value' --raw-output | cut -d' ' -f2`

response=""
if echo <PASSWORD TYPE> | grep -iq "sshPublicKey"; then
    ssh-keygen -R $IP 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP} -p $PORT 'modify auth user <ADMIN USER> shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER@${IP} -p $PORT 'tmsh show sys license')
else
    ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP} -p $PORT 'modify auth user <ADMIN USER> shell bash'
    response=$(sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP} -p $PORT 'tmsh show sys license')
fi

echo "Response: $response"

if echo $response | grep '<AUTOFILL BIGIQ LICENSE KEY>'; then
    echo "Registration Key is set"
fi