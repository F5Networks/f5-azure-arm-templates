#  expectValue = "false"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 60

# Limit output, only report errors

if echo "<TEMPLATE URL>" | grep "bigiq/licenseManagement/cluster"; then
    # don't delete the resource group
    echo "could not be found"
else
    result=$(az group exists -g <RESOURCE GROUP>)
    if echo $result | grep false; then
    echo $result
    else
        echo $result
        echo "sleeping for 2 minutes before retry"
        sleep 120
    fi
fi