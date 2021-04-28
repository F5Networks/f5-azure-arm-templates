#  expectValue = "PASS"
#  scriptTimeout = 1
#  replayEnabled = true
#  replayTimeout = 5
PASS_MSG="Test Result: PASS"

# Only via-dns
if [[ "<RESOURCE GROUP>" != *"via-dns"* ]]; then
    echo "Skipping: $PASS_MSG"
    exit
fi

HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["gtmGui"].value' --raw-output | cut -d' ' -f1`
echo "Host: $HOST"

response=`curl -ku <DNS PROVIDER USER>:'<DNS PROVIDER PASSWORD>' --connect-timeout 10 $HOST/mgmt/tm/gtm/pool/a/<RESOURCE GROUP>/members`
#echo "DEBUG - Response: $response"

length=$(echo $response | jq '.items | length')
echo "Debug - Length: $length"
if [[ $length -ge 1 ]] ; then
    echo $PASS_MSG
fi
