#  expectValue = "Failover State and Peer Failover State: ACTIVE"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 15

HOST=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-<MGMT PIP1> | jq -r .ipAddress)
echo "Verify host: $HOST"

# BIG-IQ uses Token Auth
token=$(curl -k -H 'Content-Type: application/json' -X POST https://$HOST/mgmt/shared/authn/login -d '{"username":"<ADMIN USER>", "password":"<AUTOFILL PASSWORD>"}' | jq -r .token.token)
FAILOVER_STATE=$(curl -k -H "X-F5-Auth-Token: $token" --connect-timeout 10 https://$HOST/mgmt/shared/failover-state | jq -r '"\(.systemMode) \(.nodeRole) \(.haStatus.peerAvailable)"')

echo "FAILOVER_STATE: $FAILOVER_STATE"
if [ "$FAILOVER_STATE" = "HA PRIMARY true" ]; then
    echo "Failover State and Peer Failover State: ACTIVE"
fi