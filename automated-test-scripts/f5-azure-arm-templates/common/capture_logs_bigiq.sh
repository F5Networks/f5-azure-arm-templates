#  expectValue = "good"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 10

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

echo "--- Github Status ---"
github_response=`curl https://www.githubstatus.com/api/v2/status.json | jq .status.description --raw-output`
curl https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/master/dist/f5-cloud-libs.tar.gz -I
# Get BIG-IQ management IP address
if [[ "<CLUSTER>" == "Yes" ]]; then
    IP=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip0 | jq .ipAddress --raw-output)
    IP2=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-mgmt-pip1 | jq .ipAddress --raw-output)
else
    IP=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-<MGMT PIP1> | jq .ipAddress --raw-output)
fi
echo "Verify BIG-IQ: $IP"

CUST_SCRIPT_LOC="/var/lib/waagent/custom-script/download/<SEQUENCE NUMBER>"
# Expected logs
AZURE_LOGS=($(echo '<SOLUTION LOGS>'| tr ';' ' '))
LOGS="$CUST_SCRIPT_LOC/stdout $CUST_SCRIPT_LOC/stderr /var/log/waagent.log"
for I in ${AZURE_LOGS[@]}; do
    LOGS+=" /var/log/cloud/azure/"$I
done

if [ -n "$IP" ]; then
    for LOG in $LOGS; do
        echo "---------- Capturing BIG-IQ $LOG ----------"
        LOG_NAME=`basename $LOG`
        if echo <PASSWORD TYPE> | grep -iq "sshPublicKey"; then
            ssh-keygen -R $IP 2>/dev/null
            scp -o "StrictHostKeyChecking no" -i $SSH_KEY -p <SSH PORT> <ADMIN USER>@${IP}:${LOG} ${TMP_DIR}/<RESOURCE GROUP>-${LOG_NAME}
        else
            sshpass -p '<AUTOFILL PASSWORD>' scp -P <SSH PORT> -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP}:${LOG} ${TMP_DIR}/<RESOURCE GROUP>-${LOG_NAME}
        fi
        cat ${TMP_DIR}/<RESOURCE GROUP>-${LOG_NAME} 2>/dev/null
        rm -f ${TMP_DIR}/<RESOURCE GROUP>-${LOG_NAME}
    done
else
    echo "Azure mgmt public IP $IP not found in resource group <RESOURCE GROUP>"
fi
if [ -n "$IP2" ]; then
    for LOG in $LOGS; do
        echo "---------- Capturing BIG-IQ2 $LOG ----------"
        LOG_NAME=`basename $LOG`
        if echo <PASSWORD TYPE> | grep -iq "sshPublicKey"; then
            ssh-keygen -R $IP2 2>/dev/null
            scp -o "StrictHostKeyChecking no" -i $SSH_KEY -p <SSH PORT> <ADMIN USER>@${IP2}:${LOG} ${TMP_DIR}/<RESOURCE GROUP>-${LOG_NAME}
        else
            sshpass -p '<AUTOFILL PASSWORD>' scp -P <SSH PORT> -o "StrictHostKeyChecking=no" <ADMIN USER>@${IP2}:${LOG} ${TMP_DIR}/<RESOURCE GROUP>-${LOG_NAME}
        fi
        cat ${TMP_DIR}/<RESOURCE GROUP>-${LOG_NAME} 2>/dev/null
    done
else
    echo "Azure mgmt public IP $IP2 not found in resource group <RESOURCE GROUP>"
fi

if [[ $github_response == "All Systems Operational" ]]; then
    echo "GitHub status is good"
fi