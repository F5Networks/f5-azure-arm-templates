#  expectValue = "BIG-IP was not found"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 15

# This test is to be used to verify BIG-IQ license revocation happens
# when a device is scaled down and using BYOL via BIG-IQ
# Tested with BIG-IQ 5.3, API should be the same for 5.2
HOST="<LICENSE HOST>"
USER="admin"
PSWD='B!giq2017'
POOL="production"

# Set to true if intending to clean out a pool, otherwise the intent is simply to check if a BIG-IP exists in the pool (by hostname)
DELETE_ALL="false"
BIGIP_NAME="vmss_2."

if [[ "<LICENSE TYPE>" == "BIGIQ"]]; then
	# Get ID for specific BIG-IQ pool
	POOLID=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses | jq '.items[] | select(.name == "'${POOL}'") | .id' --raw-output`
	echo "Pool ID for $POOL is $POOLID"
	# for each license key in the pool, get the regKey:
	LICS=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses/${POOLID}/offerings | jq .items[].regKey --raw-output`
	echo "License Keys: $LICS"
	# For each regKey do "stuff"
	for LIC in $LICS; do
		echo "Getting info on $LIC"
		LICINFO=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses/${POOLID}/offerings/${LIC}`
		echo $LICINFO | jq .status
		echo "Checking for BIG-IP members for $LIC"
		MBRINFO=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses/${POOLID}/offerings/${LIC}/members`
		echo $MBRINFO | jq .items[]
		# Check if deleting or not
		if [[ $DELETE_ALL == "true" ]]; then
			MBRID=`echo $MBRINFO | jq .items[0].id --raw-output`
			if [[ $MBRID != "null" ]]; then
				echo "Deleting device..."
				curl -sku ${USER}:"${PSWD}" -H "Content-Type: application/json" -X DELETE https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses/${POOLID}/offerings/${LIC}/members/${MBRID} -d '{"username":"admin","password":"admin","id":"'${MBRID}'"}'
			fi
		else
			# Checking for the existence of a device instead
			echo "Checking if $BIGIP_NAME exists in the pool"
			if echo $MBRINFO | grep $BIGIP_NAME -q; then
				echo "BIG-IP exists!"
				EXISTS_FLAG=true
			fi
		fi
	done
	# Let DP know that the BIG-IP was not found
	if [[ -z $EXISTS_FLAG ]]; then
		echo "BIG-IP was not found"
	fi
else
	echo "BIG-IP was not found"
fi