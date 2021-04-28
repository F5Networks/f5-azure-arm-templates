#  expectValue = "gone from sync-status"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 50

HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["guI-URL"].value' --raw-output | cut -d' ' -f1`

response=`curl -ku dewpoint:'<AUTOFILL PASSWORD>' -s --connect-timeout 10 $HOST/mgmt/tm/cm/sync-status`
#echo $response

# Check that only device ID 1 (querying 0 which doesn't display itself) exists in the json response
if ! echo $response | grep -i "vmss_[2-9]"; then
     echo "Device with ID 2 is gone from sync-status"
fi
