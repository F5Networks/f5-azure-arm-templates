#  expectValue = "Failover task started"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 15

HOST=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-<MGMT PIP2> | jq -r .ipAddress)
echo "Verify host: $HOST"

# BIG-IQ uses Token Auth
token=$(curl -k -H 'Content-Type: application/json' -X POST https://$HOST/mgmt/shared/authn/login -d '{"username":"<ADMIN USER>", "password":"<AUTOFILL PASSWORD>"}' | jq -r .token.token)

failover_status=$(curl -k -H "X-F5-Auth-Token: $token" https://$HOST/mgmt/shared/ha/promote-task -d '{"0":0}' | jq -r .status)

echo "Failover Status: $failover_status"
if [ "$failover_status" = 'STARTED' ]; then
    echo "Failover task started"
fi