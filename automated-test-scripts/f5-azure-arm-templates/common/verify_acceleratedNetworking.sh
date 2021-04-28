#  expectValue = "Succeeded"
#  expectFailValue = "Failed"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10

testStatus='Failed'
counter=0
additionalNics="<NUMBER OF ADDITIONAL NICS>"
nicCount=0

if [[ ! $additionalNics =~  *"<NUMBER OF ADDITIONAL NICS>"* ]]; then
    nicCount=$((<NIC COUNT> + additionalNics))
else
    nicCount=<NIC COUNT>
fi

if [[ <NIC COUNT> -ne 1 && ! <BIGIP VERSION> =~ .*"14.1.200000".* ]]; then
    response=`az network nic list -g <RESOURCE GROUP> | jq '.[].enableAcceleratedNetworking'`
    for item in $response
    do
        if [[ $item = true ]]; then
            (( counter++ ))
        fi
    done

    if [[ <TEMPLATE URL> == *"failover"* ]]; then
         counter=$(( counter/2 ))
    fi
    echo "Counter: $counter"
    echo "NIC Count: $nicCount"
    if [[ $((nicCount-1)) == $counter ]]; then
        testStatus='Succeeded'
    fi
else
    testStatus='Succeeded'
fi

echo $testStatus

