#  expectValue = "Succeeded"
#  expectFailValue = "Failed"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 60

# Limit output, only report provisioningState
result=$(az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq .properties.provisioningState)

if echo $result | grep Succeeded; then
    echo $result
else
    echo $result
    echo "sleeping for 2 minutes before retry"
    sleep 120
fi