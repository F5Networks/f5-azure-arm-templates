#  expectValue = "logs exist"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

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
    response=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -sku dewpoint:'<AUTOFILL PASSWORD>' -H \"Content-Type:application/json\" -X POST $HOST/mgmt/tm/util/bash -d \"{\\\"command\\\":\\\"run\\\",\\\"utilCmdArgs\\\":\\\"-c 'ls /var/log/cloud/azure'\\\"}\" | jq .commandResult --raw-output") ;;
*)
    response=$(curl -sku dewpoint:'<AUTOFILL PASSWORD>' -H "Content-Type:application/json" -X POST $HOST/mgmt/tm/util/bash -d "{\"command\":\"run\",\"utilCmdArgs\":\"-c 'ls /var/log/cloud/azure'\"}" | jq .commandResult --raw-output) ;;
esac

echo "Response: $response"

## Validate all items in logs are in response
logs=($(echo '<SOLUTION LOGS>'| tr ';' ' '))

matched_list=()
for log in ${logs[@]}; do
	echo "Checking for log: $log"
	for i in $response; do
		# grep -w for exact match as internal is substring of internal2
		if echo $i | grep "$log" --silent; then
			echo "Match: $i"
			matched_list+=("$log")
		fi
	done
done

i_length=${#logs[@]}
m_length=${#matched_list[@]}
echo "i_length: $i_length m_length: $m_length"
if (( "$m_length" == "$i_length" )); then
	echo "logs exist"
fi
