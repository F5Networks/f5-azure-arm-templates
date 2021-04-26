#  expectValue = "IP is associated with device and Route NextHop is set to External on vm"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 40

TMP_DIR='/tmp/<DEWPOINT JOB ID>'
# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

case <CREATE PUBLIC IP> in
"No")
    HOST0=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt0 | jq .ipConfigurations[0].privateIpAddress -r)
    HOST1=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt1 | jq .ipConfigurations[0].privateIpAddress -r)
    BASTION_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bastionIp"].value' --raw-output | cut -d' ' -f1`
    echo "BASTION HOST: $BASTION_HOST"
    ;;
*)
    HOST0=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip0 | jq .ipAddress -r)
    HOST1=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip1 | jq .ipAddress -r)
esac

echo "HOST0: ${HOST0}"
echo "HOST1: ${HOST1}"


case <CREATE PUBLIC IP> in
"No")
    HOST0=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt0 | jq .ipConfigurations[0].privateIpAddress -r)
    HOST1=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt1 | jq .ipConfigurations[0].privateIpAddress -r)

    STATE0=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST0}/mgmt/tm/sys/failover -H 'Content-Type: application/json'" | jq .apiRawValues.apiAnonymous)
    STATE1=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST1}/mgmt/tm/sys/failover -H 'Content-Type: application/json'" | jq .apiRawValues.apiAnonymous);;
*)
     STATE0=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST0}/mgmt/tm/sys/failover -H 'Content-Type: application/json' | jq .apiRawValues.apiAnonymous)
     STATE1=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 https://${HOST1}/mgmt/tm/sys/failover -H 'Content-Type: application/json' | jq .apiRawValues.apiAnonymous)
esac

echo "STATE0: ${STATE0}"
echo "STATE1: ${STATE1}"


INDEX=0
if echo $STATE0 | grep 'active' && echo $STATE1 | grep 'standby'; then
   echo "HOST0 is in active state. Index is set to ${INDEX}"
elif echo $STATE0 | grep 'standby' && echo $STATE1 | grep 'active'; then
   INDEX=1
   echo "HOST1 is in active state. Index is set to ${INDEX}"
else
   echo "FAILED - Failover Cluster is incorrect state"
fi

ROUTE_NEXT_HOP=$(az network route-table route list -g <VNET RESOURCE GROUP> --route-table-name <RESOURCE GROUP>-rt | jq .[].nextHopIpAddress)
EXTERNAL=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-ext${INDEX} | jq .ipConfigurations[0].privateIpAddress)
case <CREATE PUBLIC IP> in
"No")
    IPCONFIG_NAME=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-ext${INDEX} | jq .ipConfigurations[1].name)
    PROVISIONING_STATE=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-ext${INDEX} | jq .provisioningState)
    echo "IPCONFIG_NAME: $IPCONFIG_NAME"
    echo "EXTERNAL PRIVATE IP: $EXTERNAL"
    echo "PROVISIONING STATE: $PROVISIONING_STATE"
    echo "ROUTE_NEXT_HOP: $ROUTE_NEXT_HOP"
    if echo $IPCONFIG_NAME | grep -i <RESOURCE GROUP>-ext-ipconfig0 && echo $PROVISIONING_STATE | grep -i "Succeeded" && echo $EXTERNAL | grep -i $ROUTE_NEXT_HOP; then
     echo "IP is associated with device and Route NextHop is set to External on vm"
    fi ;;
*)
    IPCONFIG_ID=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-ext-pip0 | jq .ipConfiguration.id)
    PROVISIONING_STATE=$(az network nic show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-ext${INDEX} | jq .provisioningState)
    echo "IPCONFIG_ID: $IPCONFIG_ID"
    echo "EXTERNAL PRIVATE IP: $EXTERNAL"
    echo "PROVISIONING STATE: $PROVISIONING_STATE"
    echo "ROUTE_NEXT_HOP: $ROUTE_NEXT_HOP"
    if echo $IPCONFIG_ID | grep -i <RESOURCE GROUP>-ext${INDEX} && echo $PROVISIONING_STATE | grep -i "Succeeded" && echo $EXTERNAL | grep -i $ROUTE_NEXT_HOP; then
        echo "IP is associated with device and Route NextHop is set to External on vm"
    fi ;;
esac

sleep 60