#  expectValue = "Public IP exists on Instance 1"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 15

ipConfigurations=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-int1 | jq .ipConfigurations)
echo "IPConfigurations: "
echo $ipConfigurations

status=$(echo $ipConfigurations | jq '.[] | select (.publicIPAddress.id != null) | select (.publicIPAddress.id | contains("<INT PIP>""))' | jq -r .provisioningState)

echo "Status: $status"
if [ "$status" = "Succeeded" ]; then
    echo "Public IP exists on Instance 1"
fi