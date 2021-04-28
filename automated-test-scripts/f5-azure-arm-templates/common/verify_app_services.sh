#  expectValue = "Declaration succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

## Account for it possibly being autoscale DNS
if [[ $(echo <TEMPLATE URL> | grep -E '(via-dns)') ]]; then
    HOST=https://`az vmss list-instance-public-ips --name <RESOURCE GROUP>-vmss --resource-group <RESOURCE GROUP> --output json | jq .[0].ipAddress --raw-output`:8443
else
    HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["guI-URL"].value' --raw-output | cut -d' ' -f1`
fi
echo "Verify Host: $HOST"

response=`curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 $HOST/mgmt/shared/appsvcs/declare  | jq .class`
echo "Response: $response"

if echo $response | grep 'ADC'; then
    echo "Declaration succeeded"
else
    echo "Declaration failure"
fi
