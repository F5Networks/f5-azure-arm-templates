#!/usr/bin/env bash
#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

## Account for it possibly being autoscale DNS
if [[ $(echo <TEMPLATE URL> | grep -E '(via-dns)') ]]; then
    HOST=https://`az vmss list-instance-public-ips --name <RESOURCE GROUP>-vmss --resource-group <RESOURCE GROUP> --output json | jq .[0].ipAddress --raw-output`:8443
else
    HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["guI-URL"].value' --raw-output | cut -d' ' -f1`
fi
echo "Verify Host: $HOST"

# Getting Requested modules
IFS=',' read -ra ADDR <<< $(echo <BIGIP MODULES>)
for i in "${ADDR[@]}"; do
    provisioned_list+=($i)
done

echo "REQUESTED MODULES: ${provisioned_list[@]}"

function verify_provisioned_modules(){
    #Getting Provisioned Modules
    for module in ${provisioned_list[@]};
    do
        module_name=$(echo ${module} | sed 's/:.*//')
        module_level=$(echo ${module} | sed 's/.*://')

        if [ "<TOKEN AUTH>" = "Yes" ]; then
        # BIG-IQ uses Token Auth
            token=$(curl -k -H 'Content-Type: application/json' -X POST $HOST/mgmt/shared/authn/login -d '{"username":"<ADMIN USER>", "password":"<AUTOFILL PASSWORD>"}' | jq -r .token.token)
            response=$(curl -k -H "X-F5-Auth-Token: $token" --connect-timeout 10 $HOST/mgmt/tm/sys/provision/${module_name})
        fi

        case <CREATE PUBLIC IP> in
        "No")
            BASTION_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bastionIp"].value' --raw-output | cut -d' ' -f1`
            echo "Verify bastion host: $BASTION_HOST"
            response=$(ssh -o "StrictHostKeyChecking no" -i $SSH_KEY dewpoint@${BASTION_HOST} "curl -ku dewpoint:'<AUTOFILL PASSWORD>' ${HOST}/mgmt/tm/sys/provision/${module_name}") ;;
        *)
            response=$(curl -ku dewpoint:'<AUTOFILL PASSWORD>' --connect-timeout 10 ${HOST}/mgmt/tm/sys/provision/${module_name}) ;;
        esac

        echo "RESPONSE: $response"

        if [[ $(echo ${response} | jq '.kind') == '"tm:sys:provision:provisionstate"' ]]; then
            if [[ $(echo ${response} | jq '.name') == \"${module_name}\" ]]; then
                if [[ $(echo ${response} | jq '.level') == \"${module_level}\" ]]; then
                    echo "PASSED: $module_name CORRECTLY PROVISIONED WITH LEVEL: $module_level"
                    flag=1
                else
                    echo "FAILED: MODULE LEVEL IS INCORRECT; EXPECTED VALUE ${module_level}; RECIEVED VALUE $(echo ${response} | jq '.level')"
                    flag=0
                    break
                fi
            else
                echo "FAILED: MODULE NAME IS INCORRECT; EXPECTED VALUE ${module_name}; RECIEVED VALUE $(echo ${response} | jq '.name')"
                flag=0
                break
            fi
        else
            echo "FAILED: INVALID RESPONSE FOR PROVISIONSTATE REQUEST; RESPONSE $response"
            flag=0
            break
        fi
    done
}

flag=0

verify_provisioned_modules $HOST

if [[ ${flag} == 1 ]]; then
    echo "SUCCESS"
else
    echo "FAILED"
fi

echo "COMPLETED: VERIFY_PROVISIONED_MODULES"
