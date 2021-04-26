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
    response=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' ${HOST}/mgmt/tm/sys/application/template | jq .items[].name --raw-output") ;;
*)
    response=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 ${HOST}/mgmt/tm/sys/application/template | jq .items[].name --raw-output) ;;
esac

## validate all items in list are in response
iapp_list=("f5.service_discovery" "f5.cloud_logger")

matched_list=()
for iapp in ${iapp_list[@]}; do
	echo "Checking for iapp: $iapp"
	for i in $response; do
		if echo $i | grep "$iapp" --silent; then
			echo "match: $i"
			matched_list+=("$iapp")
		fi
	done
done

i_length=${#iapp_list[@]}
r_length=${#matched_list[@]}
echo "i_length: $i_length r_length: $r_length"
if (( "$r_length" >= "$i_length" )); then
	echo "SUCCESS"
fi
