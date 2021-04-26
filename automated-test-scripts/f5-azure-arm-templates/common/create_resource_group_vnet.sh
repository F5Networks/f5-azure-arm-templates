#  expectValue = "Succeeded"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

if [[ $(echo <TEMPLATE URL> | grep -E '(failover/same-net/via-api/n-nic/existing-stack)') ]]; then
    az group create --location <REGION> --name <RESOURCE GROUP>-vnet --tags creator=dewdrop delete=True
else
    echo "Succeeded"
fi