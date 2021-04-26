#  expectValue = "SUCCESS"
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
    response=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' ${HOST}/mgmt/tm/net/vlan | jq .items[].name --raw-output") ;;
*)
    response=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 $HOST/mgmt/tm/net/vlan | jq .items[].name --raw-output) ;;
esac

## validate all items in list are in response
list=($(echo '<BASE VLAN NAME>' | tr ';' ' '))
list+=($(echo '<ADDITIONAL NIC LOCATION>' | sed -e 's#optional##i' | tr ';' ' '))

matched_list=()
for vlan in ${list[@]}; do
	echo "Checking for vlan: $vlan"
	for i in $response; do
		# grep -w for exact match as internal is substring of internal2
		if echo $i | grep -w "$vlan" --silent; then
			echo "match: $i"
			matched_list+=("$vlan")
		fi
	done
done

i_length=${#list[@]}
m_length=${#matched_list[@]}
echo "i_length: $i_length m_length: $m_length"
if (( "$m_length" >= "$i_length" )); then
	echo "SUCCESS"
fi
