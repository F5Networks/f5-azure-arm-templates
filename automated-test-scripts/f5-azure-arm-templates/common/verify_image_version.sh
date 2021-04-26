#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10

if [[ <IMAGE URN> == 'OPTIONAL' ]]; then
    VERSION='<BIGIP VERSION>'
else
    IFS=':' read -r -a URNARRAY <<< "<IMAGE URN>"
    VERSION="${URNARRAY[3]}"
fi

echo "VERSION: $VERSION"

# only check the first VM since all instance plans in a template are generated from the same line of code
if [[ $(echo <TEMPLATE URL> | grep -E '(autoscale)') ]]; then
    RESPONSE=$(az vmss show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-vmss | jq -r .virtualMachineProfile.storageProfile.imageReference.version)
elif [[ $(echo <TEMPLATE URL> | grep -E '(standalone)') ]]; then
    RESPONSE=$(az vm show -g <RESOURCE GROUP> -n f5vm01 | jq -r .storageProfile.imageReference.version)
elif [[ $(echo <TEMPLATE URL> | grep -E '(failover/same-net/via-api)') || $(echo <TEMPLATE URL> | grep -E '(failover/same-net/via-lb/3nic)') ]]; then
    RESPONSE=$(az vm show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-f5vm0 | jq -r .storageProfile.imageReference.version)
elif [[ $(echo <TEMPLATE URL> | grep -E '(failover/same-net/via-lb/1nic)') ]]; then
    RESPONSE=$(az vm show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-device0 | jq -r .storageProfile.imageReference.version)
else
    echo "Couldn't find a valid solution!"
fi

echo "RESPONSE: $RESPONSE"

if [[ $RESPONSE == $VERSION ]]; then
    echo "Succeeded"
else
    echo "Failed"
fi