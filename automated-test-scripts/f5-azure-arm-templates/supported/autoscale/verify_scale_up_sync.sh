#  expectValue = "is in sync-status"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 90

## Account for it possibly being autoscale DNS
if [[ $(echo <TEMPLATE URL> | grep -E '(via-dns)') ]]; then
    HOST=https://`az vmss list-instance-public-ips --name <RESOURCE GROUP>-vmss --resource-group <RESOURCE GROUP> | jq .[0].ipAddress --raw-output`:8443
else
    HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["guI-URL"].value' --raw-output | cut -d' ' -f1`
fi
echo "Verify Host: $HOST"

response=`curl -ku dewpoint:'<AUTOFILL PASSWORD>' -s --connect-timeout 10 ${HOST}/mgmt/tm/cm/sync-status | jq .`
#echo $response

# Check that device ID 2 (querying 0 which doesn't display itself) exists in the json response
if echo $response | grep -i "vmss_[2-9]"; then
     echo "Device with ID 2 is is in sync-status"
fi
