#  expectValue = "Objects deleted"
#  scriptTimeout = 1
#  replayEnabled = true
#  replayTimeout = 5

# Continue if not DNS templates
if ! echo "<RESOURCE GROUP>" | grep "via-dns"; then
    echo "Skipping: Objects deleted"
    exit
fi

HOST=https://<DNS PROVIDER HOST>
echo "Host: $HOST"

# Cleanup GSLB pool
curl -ku <DNS PROVIDER USER>:'<DNS PROVIDER PASSWORD>'  $HOST/mgmt/tm/gtm/pool/a/<RESOURCE GROUP> -X DELETE
# Cleanup GSLB server
curl -ku <DNS PROVIDER USER>:'<DNS PROVIDER PASSWORD>'  $HOST/mgmt/tm/gtm/server/<RESOURCE GROUP>-vmss -X DELETE
echo "Objects deleted"
