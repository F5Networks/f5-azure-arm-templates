#  expectValue = "Licenses deleted"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

# This test is to be used to revoke licenses from specified
# BIG-IQ's and pools
# Tested with BIG-IQ 5.3, 5.2
HOSTS="<LICENSE HOSTS>"
USER="admin"
POOLS="<LICENSE POOLS>"
# Loop through HOST and then POOL attempting to delete licenses
for HOST in $HOSTS; do
    if [[ $HOST = *"10.146"* ]]; then
        PSWD='B@giq2017'
    else
        PSWD='B!giq2017'
    fi
    printf "\nHost: $HOST Password: $PSWD"
    # Version Check as API's are different
    bigiq_version=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/shared/resolver/device-groups/cm-shared-all-big-iqs/devices | jq -r .items[].version`
    printf "\nBIG-IQ Version: $bigiq_version"
    if [[ $bigiq_version == "5.3"* ]]; then
        for POOL in $POOLS; do
            if [ $POOL != "clpv2" ]; then
                POOLID=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses | jq -r '.items[] | select(.name == "'${POOL}'") | .id'`
                printf "\nPool ID for $POOL is $POOLID"
                # for each license key in the pool, get the regKey:
                LICS=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses/${POOLID}/offerings | jq -r .items[].regKey`
                printf "\nLicense Keys: $LICS"
                # For each regKey do "stuff"
                for LIC in $LICS; do
                    printf "\nGetting info on $LIC"
                    LICINFO=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses/${POOLID}/offerings/${LIC}`
                    ##### echo $LICINFO | jq .status
                    MBRINFO=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses/${POOLID}/offerings/${LIC}/members`
                    ##### echo $MBRINFO | jq .items[]
                    # Deleting
                    MBRID=`echo $MBRINFO | jq -r .items[0].id`
                    if [[ $MBRID != "null" ]]; then
                        echo "Deleting device..."
                        curl -sku ${USER}:"${PSWD}" -H "Content-Type: application/json" -X DELETE https://${HOST}/mgmt/cm/device/licensing/pool/regkey/licenses/${POOLID}/offerings/${LIC}/members/${MBRID} -d '{"username":"admin","password":"admin","id":"'${MBRID}'"}'
                    fi
                done
            else
                printf "\n Unable to process utility pools. It is a TO DO ITEM in this script for version 5.3"
            fi
        done    
    else
    # Assume v5.3 or later and use newer API's
        LICS=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/assignments |jq -r '.items[].deviceAddress'`
        if [ -n "$LICS" ]; then
            for POOL in $POOLS; do
                for LIC in $LICS; do
                    LIC_DETAILS=`curl -sku ${USER}:"${PSWD}" https://${HOST}/mgmt/cm/device/licensing/assignments |jq -r '.items[] | select(.deviceAddress | contains ("'${LIC}'")) |(.)'`
                    LIC_ASSIGN_TYPE=`echo $LIC_DETAILS | jq .assignmentType --raw-output`
                    printf "\nRevoke lic for ip $LIC assignmentType: $LIC_ASSIGN_TYPE"
                    if [[ $LIC_ASSIGN_TYPE == *"UNREACHABLE"* ]]; then
                        LIC_MAC=`echo $LIC_DETAILS | jq .macAddress --raw-output | head -n1`
                        printf "\nRevoking unreachable device, MAC: $LIC_MAC"
                        curl -sku ${USER}:"${PSWD}" -d "{\"licensePoolName\": \"${POOL}\", \"command\": \"revoke\", \"address\": \"${LIC}\", \"assignmentType\": \"UNREACHABLE\", \"macAddress\": \"${LIC_MAC}\"}" -H "Content-Type: application/json" -X POST https://${HOST}/mgmt/cm/device/tasks/licensing/pool/member-management
                    else
                        curl -sku ${USER}:"${PSWD}" -d "{\"licensePoolName\": \"${POOL}\", \"command\": \"revoke\", \"address\": \"${LIC}\", \"user\": \"admin\", \"password\": \"admin\"}" -H "Content-Type: application/json" -X POST https://${HOST}/mgmt/cm/device/tasks/licensing/pool/member-management
                    fi
                done
            done
        else
            printf "\nServer: $HOST returned no licenses to process."
        fi
    fi    
done
printf "\nLicenses deleted"