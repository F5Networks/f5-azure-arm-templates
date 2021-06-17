#!/usr/bin/env bash
#  expectValue = "License pool keys set"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10

if [[ "<CLUSTER>" == "Yes" ]]; then
    IP=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip0 | jq .ipAddress --raw-output)
    IP2=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip1 | jq .ipAddress --raw-output)
else
    IP=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-<MGMT PIP1> | jq .ipAddress --raw-output)
fi


if [ "<TOKEN AUTH>" = "Yes" ]; then
    # BIG-IQ uses Token Auth
    token=$(curl -k -H 'Content-Type: application/json' -X POST https://$IP/mgmt/shared/authn/login -d '{"username":"<ADMIN USER>", "password":"<AUTOFILL PASSWORD>"}' | jq -r .token.token)
    response=$(curl -sk -H "X-F5-Auth-Token: $token" https://${IP}/mgmt/cm/device/licensing/pool/initial-activation/<AUTOFILL CLPV2 LICENSE KEY> | jq '. | select(.name == "production") | .status');
else
    response=$(curl -sk -u <ADMIN USER>:<AUTOFILL PASSWORD> https://${IP}/mgmt/cm/device/licensing/pool/initial-activation/<AUTOFILL CLPV2 LICENSE KEY> | jq '. | select(.name == "production") | .status');
fi
echo "Response: $response"

if [[ "$response" == *"READY"* || "<LICENSE POOL KEYS>" == "Do Not Create" ]] ; then
    echo "License pool keys set"
fi