#  expectValue = "valid permissions"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10

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
# This command will list all files in /config/cloud with permisisons in octal format
# response=`curl -sku dewpoint:'<AUTOFILL PASSWORD>' -H "Content-Type:application/json" -X POST $HOST/mgmt/tm/util/bash -d "{\"command\":\"run\",\"utilCmdArgs\":\"-c 'ls -la /config/cloud'\"}" | jq .commandResult --raw-output | awk '{k=0;for(i=0;i<=8;i++)k+=((substr($1,i+2,1)~/[rwx]/)*2^(8-i));if(k)printf(" %0o ",k);print $NF}'`
# The following command will get permission of each file
# response=`curl -sku dewpoint:'<AUTOFILL PASSWORD>' -H "Content-Type:application/json" -X POST $HOST/mgmt/tm/util/bash -d '{"command":"run","utilCmdArgs":"-c \"stat  -c '\''%a %n'\'' /config/cloud/.passwd\""}' | jq .commandResult --raw-output`

## Validate all configuration files have valid permisison
CONF_FILES=($(echo '<CONFIG FILES>'| tr ';' ' '))
BIGIQ_CONF_FILE=($(echo '<BIGIQ CONFIG FILE>'))
CONF_FILES+=" "$BIGIQ_CONF_FILE

valid_permission="400"
result="valid permissions"

case <CREATE PUBLIC IP> in
"No")
    BASTION_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bastionIp"].value' --raw-output | cut -d' ' -f1`
    echo "Verify bastion host: $BASTION_HOST" ;;
*)
    echo "Not production stack"
esac

for file in ${CONF_FILES[@]}; do
    echo "Checking permission for file: $file"
    case <CREATE PUBLIC IP> in
"No")
        response=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -sku dewpoint:'<AUTOFILL PASSWORD>' -H \"Content-Type:application/json\" -X POST $HOST/mgmt/tm/util/bash -d \"{\\\"command\\\":\\\"run\\\",\\\"utilCmdArgs\\\":\\\"-c 'stat -c %a /config/cloud/${file}'\\\"}\" | jq .commandResult --raw-output") ;;
    *)
        response=$(curl -sku dewpoint:'<AUTOFILL PASSWORD>' -H "Content-Type:application/json" -X POST $HOST/mgmt/tm/util/bash -d '{"command":"run","utilCmdArgs":"-c \"stat  -c '\''%a'\'' /config/cloud/'$file'\""}' | jq .commandResult --raw-output) ;;
    esac
    echo "Response: $response"

	if [ "$response" != "$valid_permission" ]; then
		result="wrong permissions"
		break
	fi
done

echo "$result"
