#  expectValue = "PASS"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

PASS_MSG="Test Result: PASS"

# Only bigiq-payg
if [[ "<LICENSE TYPE>" != *"bigiq-payg"* ]] ; then
    echo "Skipping: $PASS_MSG"
    exit
fi

# Check that the sku name for the static VMSS contains byol
vmss=$(az vmss show --resource-group <RESOURCE GROUP> --name <RESOURCE GROUP>-vmss-static)
sku=$(echo $vmss | jq .virtualMachineProfile.storageProfile.imageReference.sku --raw-output)
echo "DEBUG - Sku Name: $sku"
if [[ "$sku" == *"byol"* ]] ; then
    echo $PASS_MSG
fi
