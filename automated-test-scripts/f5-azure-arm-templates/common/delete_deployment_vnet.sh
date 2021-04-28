#  expectValue = "Succeeded"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

if [[ $(echo <TEMPLATE URL> | grep -E '(failover/same-net/via-api/n-nic/existing-stack)') ]]; then
    az group delete --verbose --no-wait -n <RESOURCE GROUP>-vnet --yes
    echo "Succeeded"
else
    echo "Succeeded"
fi
