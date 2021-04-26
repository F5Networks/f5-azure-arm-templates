#  expectValue = "Succeeded"
#  expectFailValue = "Failed"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

if [[ <EXT ALB EXISTS> == "Yes" ]]; then
    az network lb show -g <RESOURCE GROUP> --name <RESOURCE GROUP>-existing-lb | jq .provisioningState
else
    echo "Succeeded"
fi
