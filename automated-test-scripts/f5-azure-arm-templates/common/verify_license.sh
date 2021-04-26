#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 5

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

## Account for it possibly being autoscale DNS
if [[ $(echo <TEMPLATE URL> | grep -E '(via-dns)') ]]; then
    HOST=https://`az vmss list-instance-public-ips --name <RESOURCE GROUP>-vmss --resource-group <RESOURCE GROUP> --output json | jq .[0].ipAddress --raw-output`:8443
else
    HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["guI-URL"].value' --raw-output | cut -d' ' -f1`
fi
echo "Verify Host: $HOST"

case <CREATE PUBLIC IP> in
"No")
    BASTION_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bastionIp"].value' --raw-output | cut -d' ' -f1`
    echo "Verify bastion host: $BASTION_HOST"
    response=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' ${HOST}/mgmt/tm/sys/license") ;;
*)
    response=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 ${HOST}/mgmt/tm/sys/license) ;;
esac

# evaluate response
if echo $response | grep 'registrationKey'; then
    echo "SUCCESS"
else
    echo "FAILED"
fi
