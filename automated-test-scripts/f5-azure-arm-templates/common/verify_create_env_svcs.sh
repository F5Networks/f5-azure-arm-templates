#  expectValue = "too much winning"
#  expectFailValue = "womp womp"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 1800

# always do vnet-bastion
DEPLOYMENT_COUNT=1

case <LICENSE TYPE> in
bigiq)
    ((DEPLOYMENT_COUNT++)) ;;
*)
    echo "Not licensed with BIG-IQ" ;;
esac

if [[ $(echo <TEMPLATE URL> | grep -E '(autoscale/ltm/via-dns|autoscale/waf/via-dns)') ]]; then
    ((DEPLOYMENT_COUNT++))
else
    echo "Not autoscale DNS"
fi

CLOUD_COUNT=$(az deployment group list -g <RESOURCE GROUP> | jq '. | length')
SUCCEEDED=$(az deployment group list -g <RESOURCE GROUP> --query "[?properties.provisioningState=='Succeeded'].{Name:name}" | jq '. | length')

if [[ $CLOUD_COUNT != $DEPLOYMENT_COUNT ]]; then
    echo "womp womp"
fi

if [[ $SUCCEEDED == $DEPLOYMENT_COUNT ]]; then
    echo "too much winning"
fi