#  expectValue = "NETWORK_DONE"
#  expectFailValue = "CLOUD_LIBS_ERROR"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 60

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

if [[ "<CLUSTER>" == "Yes" ]]; then
    IP=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip0 | jq .ipAddress --raw-output)
    IP2=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip1 | jq .ipAddress --raw-output)
else
    IP=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-<MGMT PIP1> | jq .ipAddress --raw-output)
fi
PORT=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["ssH-URL"].value' --raw-output | cut -d' ' -f2`

echo "Verify IP: $IP Verify PORT: $PORT"
if echo <PASSWORD TYPE> | grep -iq "sshPublicKey"; then
    ssh-keygen -R $IP 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP} -p $PORT 'modify auth user <ADMIN USER> shell bash'
    ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP} -p $PORT 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/azure'
    ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP} -p $PORT 'tmsh modify auth user admin password <AUTOFILL PASSWORD>'
    ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP} -p $PORT 'set-basic-auth on'
else
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP} -p $PORT 'modify auth user <ADMIN USER> shell bash'
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP} -p $PORT 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/azure'
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP} -p $PORT 'tmsh modify auth user admin password <AUTOFILL PASSWORD>'
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP} -p $PORT 'set-basic-auth on'
fi

if [[ "<CLUSTER>" == "Yes" ]]; then
    echo "Verify IP: $IP2 Verify PORT: $PORT"
    if echo <PASSWORD TYPE> | grep -iq "sshPublicKey"; then
        ssh-keygen -R $IP2 2>/dev/null
        ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP2} -p $PORT 'modify auth user <ADMIN USER> shell bash'
        ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP2} -p $PORT 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/azure'
        ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP2} -p $PORT 'tmsh modify auth user admin password <AUTOFILL PASSWORD>'
        ssh -o "StrictHostKeyChecking no" -i $SSH_KEY <ADMIN USER>@${IP2} -p $PORT 'set-basic-auth on'
    else
        sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP2} -p $PORT 'modify auth user <ADMIN USER> shell bash'
        sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP2} -p $PORT 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/azure'
        sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP2} -p $PORT 'tmsh modify auth user admin password <AUTOFILL PASSWORD>'
        sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP2} -p $PORT 'set-basic-auth on'
    fi
fi