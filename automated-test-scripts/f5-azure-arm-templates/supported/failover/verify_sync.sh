#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private
if [ <NIC COUNT> = 1 ]; then
    PORT0=8443
    PORT1=8444
else
    PORT0=$(az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["guI-URL"].value' --raw-output | cut -d' ' -f2 | cut -d':' -f3)
    PORT1=$(az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["guI-URL"].value' --raw-output | cut -d' ' -f2 | cut -d':' -f3)
fi
echo "PORT:$PORT0"
echo "PORT:$PORT1"
case <CREATE PUBLIC IP> in
"No")
    HOST0=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt0 | jq .ipConfigurations[0].privateIpAddress -r)
    HOST1=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt1 | jq .ipConfigurations[0].privateIpAddress -r)
    BASTION_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bastionIp"].value' --raw-output | cut -d' ' -f1`
    echo "BASTION HOST: $BASTION_HOST"
    echo "HOST0:$HOST0"
    echo "HOST1:$HOST1"
    response=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST0}:${PORT0}/mgmt/tm/cm/sync-status | jq .")
    response2=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST1}:${PORT0}/mgmt/tm/cm/sync-status | jq .") ;;
*)
    if [ <NIC COUNT> = 1 ]; then
        HOST0=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip | jq .ipAddress -r)
        HOST1=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip | jq .ipAddress -r)
    else    
        HOST0=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip0 | jq .ipAddress -r)
        HOST1=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip1 | jq .ipAddress -r)
    fi
    echo "HOST0:$HOST0"
    echo "HOST1:$HOST1"
    response=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST0}:${PORT0}/mgmt/tm/cm/sync-status | jq .)
    response2=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST1}:${PORT1}/mgmt/tm/cm/sync-status | jq .) ;;
esac

if echo $response | grep "high-availability" && echo $response2 | grep "high-availability" && echo $response | grep "All devices in the device group are in sync" && echo $response2 | grep "All devices in the device group are in sync"; then
    echo "SUCCESS"
else
    echo "FAILED"
fi