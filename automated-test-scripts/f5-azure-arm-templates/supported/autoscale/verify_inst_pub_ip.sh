#  expectValue = "PASS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30
PASS_MSG="Test Result: PASS"

# Only via-lb
if [[ "<RESOURCE GROUP>" != *"via-lb"* ]] ; then
    echo "Skipping: $PASS_MSG"
    exit
fi

response=$(az vmss list-instance-public-ips --name <RESOURCE GROUP>-vmss --resource-group <RESOURCE GROUP>)
length=$(echo $response | jq '. | length')
echo "Debug - Length: $length"
# Check length of array is >= 1 if enable set to yes, otherwise should be 0
enable_mgmt_pub_ip="<CREATE PUBLIC IP>"
if [[ "${enable_mgmt_pub_ip,,}" == "yes" && $length -ge 1 ]] ; then
    echo $PASS_MSG
elif [[ "${enable_mgmt_pub_ip,,}" == "no" && $length -eq 0 ]] ; then
    echo $PASS_MSG
fi
