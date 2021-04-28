#  expectValue = "Succeeded"
#  expectFailValue = "failed"
#  scriptTimeout = 15
#  replayEnabled = true
#  replayTimeout = 3

echo "sleep for 3 minutes to wait for onboarding to fully complete"
sleep 180
echo "starting test"
shutdown=""
response=$(az vm list -g <RESOURCE GROUP> | jq -r .[].name)
for item in $response
do
    if echo $item | grep 'bastion'; then
        echo "bastion host, not stoppping"
    else
        stop=$(az vm stop -g <RESOURCE GROUP> -n $item)
        status=$(az vm get-instance-view -g <RESOURCE GROUP> -n $item --query instanceView.statuses[1] | jq .displayStatus)
        if echo $status | grep "stopped"; then
            echo "$item has powered off: $status" 
        else
            echo "$item is not powered off: $status"
            shutdown="$shutdown failed"
        fi
    fi
done
startup=""
for item in $response
do
    if echo $item | grep 'bastion'; then
        echo "bastion host, not starting"
    else
        start=$(az vm start -g <RESOURCE GROUP> -n $item)
        status=$(az vm get-instance-view -g <RESOURCE GROUP> -n $item --query instanceView.statuses[1] | jq .displayStatus)
        if echo $status | grep "running"; then
            echo "$item has powered on"
        else
            echo "$item is not powered on: $status"
            startup="$startup failed"
        fi
    fi
done

if echo $shutdown | grep "failed" || echo $startup | grep "failed"; then
    echo "system reboot failed"
else
    echo "Succeeded"
fi

echo "sleep for 3 minutes to wait for system to complete startup"
sleep 180