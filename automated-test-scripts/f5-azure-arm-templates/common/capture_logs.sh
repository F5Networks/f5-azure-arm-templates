#  expectValue = "good"
#  scriptTimeout = 2
#  replayEnabled = false
#  replayTimeout = 20

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

echo "--- Github Status ---"
github_response=`curl https://status.github.com/api/status.json?callback-apiStatus | jq .status --raw-output`
curl https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/master/dist/f5-cloud-libs.tar.gz -I

# get the private key from key vault via file
SSH_KEY=${TMP_DIR}/<RESOURCE GROUP>-private

case <CREATE PUBLIC IP> in
"No")
    BASTION_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bastionIp"].value' --raw-output | cut -d' ' -f1`
    echo "Verify bastion host: $BASTION_HOST" ;;
*)
    echo "Not production stack" ;;
esac

IP1=""
IP2=""
PORT1=22
PORT2=22

if [[ $(echo <TEMPLATE URL> | grep -E '(autoscale/ltm/via-lb|autoscale/waf/via-lb)') ]]; then
    echo "connecting via an ALB (new/existing stack)"
    IP1=$(az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["ssH-URL"].value' --raw-output | cut -d' ' -f1)
    PORTS=$(az network lb show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-ext-alb | jq '[.inboundNatRules[] | select(.backendPort==22) | .frontendPort]')
    PORT1=$(echo $PORTS | jq .[0])
    PORT2=$(echo $PORTS | jq .[1])
elif [[ $(echo <TEMPLATE URL> | grep -E '(via-lb/1nic)') ]]; then
    echo "connecting via an ALB to HA 1nic (new/existing stack/prod stack)"
    IP1=$(az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["ssH-URL"].value' --raw-output | cut -d' ' -f1)
    PORT1=8022
    PORT2=8023
elif [[ $(echo <TEMPLATE URL> | grep -E '(via-dns)') ]]; then
    echo "connecting directly via the mgmt IP of the first DNS autoscale instance (new/existing stack)"
    IP1=$(az vmss list-instance-public-ips --name <RESOURCE GROUP>-vmss --resource-group <RESOURCE GROUP> --output json | jq .[0].ipAddress --raw-output)
elif [[ $(echo <TEMPLATE URL> | grep -E '(failover)') ]]; then
    echo "connecting via the mgmt IP to HA 3nic (new/existing stack)"
    IP1=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-<MGMT PIP1> | jq .ipAddress | sed "s/\"//g")
    IP2=$(az network public-ip show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-<MGMT PIP2> | jq .ipAddress | sed "s/\"//g")
else
    echo "connecting via the mgmt IP to a standalone BIG-IP"
    IP1=$(az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["ssH-URL"].value' --raw-output | cut -d' ' -f1)
fi

echo "Verify IP1=$IP1"
echo "Verify IP2=$IP2"
echo "Verify PORT1=$PORT1"
echo "Verify PORT2=$PORT2"

# get deployment status
echo "--- Deployment Status ---"
STATUS=$(az deployment operation group list -g <RESOURCE GROUP> -n <RESOURCE GROUP>)
echo $STATUS | jq .

# build logs list
CUST_SCRIPT_LOC="/var/lib/waagent/custom-script/download/<SEQUENCE NUMBER>"
# Expected logs
AZURE_LOGS=($(echo '<SOLUTION LOGS>'| tr ';' ' '))
LOGS="$CUST_SCRIPT_LOC/stdout $CUST_SCRIPT_LOC/stderr /var/log/waagent.log"
for I in ${AZURE_LOGS[@]}; do
    LOGS+=" /var/log/cloud/azure/"$I
done

if [[ "<CREATE PUBLIC IP>" == "No" && -n "$IP1" ]]; then
  for LOG in $LOGS; do
    echo "------------------------LOG:$LOG ------------------------"
    filename=$(basename ${LOG})
    echo $filename
    sshpass -p '<AUTOFILL PASSWORD>' scp -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" -P $PORT1 admin@${IP1}:${base}${LOG} ${TMP_DIR}/${filename}-<REGION>
    cat ${TMP_DIR}/${filename}-<REGION> 2>/dev/null
    echo
  done
  ssh-keygen -R $IP 2>/dev/null
  ssh-keygen -R $BASTION_HOST 2>/dev/null
elif [[ "<CREATE PUBLIC IP>" == "Yes" && -n "$IP1" ]]; then
  for LOG in $LOGS; do
    echo "------------------------LOG:$LOG ------------------------"
    filename=$(basename ${LOG})
    echo $filename
    sshpass -p '<AUTOFILL PASSWORD>' scp -o "StrictHostKeyChecking no" -P $PORT1 admin@${IP1}:${base}${LOG} ${TMP_DIR}/${filename}-<REGION>
    cat ${TMP_DIR}/${filename}-<REGION> 2>/dev/null
    echo
  done
  ssh-keygen -R $IP 2>/dev/null
else
  echo "Nothing matched, logs not being collected"
fi

if [[ "<CREATE PUBLIC IP>" == "No" && -n "$IP2" ]]; then
  for LOG in $LOGS; do
    echo "------------------------LOG:$LOG ------------------------"
    filename=$(basename ${LOG})
    echo $filename
    sshpass -p '<AUTOFILL PASSWORD>' scp -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" -P $PORT2 admin@${IP2}:${base}${LOG} ${TMP_DIR}/${filename}-<REGION>
    cat ${TMP_DIR}/${filename}-<REGION> 2>/dev/null
    echo
  done
  ssh-keygen -R $IP2 2>/dev/null
  ssh-keygen -R $BASTION_HOST 2>/dev/null
elif [[ "<CREATE PUBLIC IP>" == "Yes" && -n "$IP2" ]]; then
  for LOG in $LOGS; do
    echo "------------------------LOG:$LOG ------------------------"
    filename=$(basename ${LOG})
    echo $filename
    sshpass -p '<AUTOFILL PASSWORD>' scp -o "StrictHostKeyChecking no" -P $PORT2 admin@${IP2}:${base}${LOG} ${TMP_DIR}/${filename}-<REGION>
    cat ${TMP_DIR}/${filename}-<REGION> 2>/dev/null
    echo
  done
  ssh-keygen -R $IP2 2>/dev/null
  ssh-keygen -R $BASTION_HOST 2>/dev/null
else
  echo "Second Big-IP Not Present"
fi

if [[ $github_response == "good" ]]; then
    echo "GitHub status is good"
fi
