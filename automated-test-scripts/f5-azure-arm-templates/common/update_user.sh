#  expectValue = "User Updated"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 10

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

## Account for it possibly being autoscale DNS
if [[ $(echo <TEMPLATE URL> | grep -E '(via-dns)') ]]; then
    IP=`az vmss list-instance-public-ips --resource-group <RESOURCE GROUP> --name <RESOURCE GROUP>-vmss | jq .[0].ipAddress --raw-output`
    PORT=22
else
    IP=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["ssH-URL"].value' --raw-output | cut -d' ' -f1`
    PORT=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["ssH-URL"].value' --raw-output | cut -d' ' -f2`
fi
echo "Verify IP: $IP Verify PORT: $PORT"



# Update dewpoint user password
# Note: will sync to other boxes if in a cluster so only need to update the first one
if echo <PASSWORD TYPE> | grep -iq "sshPublicKey"; then
    case <CREATE PUBLIC IP> in
    "No")
        BASTION_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bastionIp"].value' --raw-output | cut -d' ' -f1`
        echo "Verify bastion host: $BASTION_HOST"
        ssh-keygen -R $BASTION_HOST 2>/dev/null
        ssh -o "StrictHostKeyChecking no" -i $SSH_KEY -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" admin@"$IP" 'modify auth user dewpoint password <AUTOFILL PASSWORD>' ;;
    *)
        ssh-keygen -R $IP 2>/dev/null
        ssh -o "StrictHostKeyChecking no" -i $SSH_KEY admin@${IP} -p $PORT 'modify auth user dewpoint password <AUTOFILL PASSWORD>' ;;
    esac
    if [ $? -eq 0 ]; then
        echo "User Updated"
    fi
else
    echo "No need to update user, sending success message: User Updated"
fi
