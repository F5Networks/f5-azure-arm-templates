#  expectValue = "Succeeded"
#  scriptTimeout = 6
#  replayEnabled = true
#  replayTimeout = 30

if [[ $(echo <STACK PARAM> | grep -E '(DYNAMIC)') ]] || [[ $(echo <VNET PARAM> | grep -E '(DYNAMIC)') ]]; then
    allocation='Dynamic'
else
    allocation='Static'
fi
echo "Allocation: $allocation"

if [[ $(echo <TEMPLATE URL> | grep -E '(failover)') ]]; then
    nic_suffix='0'
else
    nic_suffix=''
fi

mgmt_nic=<RESOURCE GROUP>-mgmt${nic_suffix}
ext_nic=<RESOURCE GROUP>-ext${nic_suffix}
int_nic=<RESOURCE GROUP>-int${nic_suffix}

case <NIC COUNT> in
"3")
    mgmt_response=$(az network nic ip-config list -g <RESOURCE GROUP> --nic-name ${mgmt_nic} | jq -r .[0].privateIpAllocationMethod)
    ext_response=$(az network nic ip-config list -g <RESOURCE GROUP> --nic-name ${ext_nic} | jq -r .[0].privateIpAllocationMethod)
    int_response=$(az network nic ip-config list -g <RESOURCE GROUP> --nic-name ${int_nic} | jq -r .[0].privateIpAllocationMethod)
    ;;
"2")
    mgmt_response=$(az network nic ip-config list -g <RESOURCE GROUP> --nic-name ${mgmt_nic} | jq -r .[0].privateIpAllocationMethod)
    ext_response=$(az network nic ip-config list -g <RESOURCE GROUP> --nic-name ${ext_nic} | jq -r .[0].privateIpAllocationMethod)
    int_response=$allocation
    ;;
"1")
    mgmt_response=$(az network nic ip-config list -g <RESOURCE GROUP> --nic-name ${mgmt_nic} | jq -r .[0].privateIpAllocationMethod)
    ext_response=$allocation
    int_response=$allocation
    ;;
esac

if [[ $mgmt_response == $allocation && $ext_response == $allocation && $int_response == $allocation ]]; then
    echo "Succeeded"
else
    echo "Failed"
fi