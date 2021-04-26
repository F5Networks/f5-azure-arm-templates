#  expectValue = "SUCCESS"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

# grab bastion ip address
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

# grab autoscale ip address
if [[ $(echo <TEMPLATE URL> | grep -E '(autoscale/ltm/via-lb|autoscale/waf/via-lb)') ]]; then
    echo "connecting via an ALB (new/existing stack)"
    IP1=$(az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP> | jq '.properties.outputs["ssH-URL"].value' --raw-output | cut -d' ' -f1)
    PORTS=$(az network lb show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-ext-alb | jq '[.inboundNatRules[] | select(.backendPort==22) | .frontendPort]')
    PORT1=$(echo $PORTS | jq .[0])
    PORT2=$(echo $PORTS | jq .[1])
elif [[ $(echo <TEMPLATE URL> | grep -E '(via-dns)') ]]; then
    echo "connecting directly via the mgmt IP of the first DNS autoscale instance (new/existing stack)"
    IP1=$(az vmss list-instance-public-ips --name <RESOURCE GROUP>-vmss --resource-group <RESOURCE GROUP> --output json | jq .[0].ipAddress --raw-output)
else
    echo "Unable to locate autoscale mgmt addrees"
fi

echo "Verify IP1=$IP1"
echo "Verify PORT1=$PORT1"
echo "Verify PORT2=$PORT2"


if [[ "<CREATE PUBLIC IP>" == "No" && -n "$IP1" ]]; then
    # upload test.ucs file. Contains example bigip.conf, bigip_base.conf, BigDb.dat, and SPEC_Manifest files to use for diff.
    sshpass -p '<AUTOFILL PASSWORD>' scp -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" -P $PORT1 $PWD/cloud-tools/automated-test-scripts/common/test_azure.ucs admin@${IP1}:/config/test.ucs
    # create directories and copy test.ucs to /shared/tmp/ucs/ucsOriginal.ucs to mirror autoscale.js behavior when restoring bigip via ucs
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP1} -p $PORT1 'modify auth user admin shell bash'
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP1} -p $PORT1 'mkdir -p /shared/tmp/ucs/old; mkdir -p /shared/tmp/ucs/new; mkdir -p /shared/tmp/ucs/ucsRestore; cp /config/test.ucs /shared/tmp/ucs/ucsOriginal.ucs'
    # run update_autoscale_ucs.py using same args as autoscale.js
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP1} -p $PORT1 'python /config/cloud/azure/node_modules/\@f5devcentral/f5-cloud-libs/scripts/update_autoscale_ucs.py --original-ucs "/shared/tmp/ucs/ucsOriginal.ucs" --updated-ucs "/shared/tmp/ucs/ucsUpdated.ucs" --cloud-provider "azure" --extract-directory "/shared/tmp/ucs/ucsRestore"'
    # unzip original ucs and updated ucs for comparison
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP1} -p $PORT1 'tar -C /shared/tmp/ucs/new -xvf /shared/tmp/ucs/ucsUpdated.ucs; tar -C /shared/tmp/ucs/old -xvf /shared/tmp/ucs/ucsOriginal.ucs'
    # capture diffs
    bigip_diff=$(sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP1} -p $PORT1 'diff /var/tmp/ucs/old/config/bigip.conf /var/tmp/ucs/new/config/bigip.conf')
    bigip_base_diff=$(sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP1} -p $PORT1 'diff /var/tmp/ucs/old/config/bigip_base.conf /var/tmp/ucs/new/config/bigip_base.conf')
    bigip_dat_diff=$(sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP1} -p $PORT1 'diff /var/tmp/ucs/old/config/BigDB.dat /var/tmp/ucs/new/config/BigDB.dat')
    manifest_diff=$(sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i $SSH_KEY -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP1} -p $PORT1 'diff /var/tmp/ucs/old/SPEC-Manifest /var/tmp/ucs/new/SPEC-Manifest')
    ssh-keygen -R $IP1 2>/dev/null
    ssh-keygen -R $BASTION_HOST 2>/dev/null
elif [[ "<CREATE PUBLIC IP>" == "Yes" && -n "$IP1" ]]; then
    # upload test.ucs file. Contains example bigip.conf, bigip_base.conf, BigDb.dat, and SPEC_Manifest files to use for diff.
    sshpass -p '<AUTOFILL PASSWORD>' scp -o "StrictHostKeyChecking no" -P $PORT1 $PWD/cloud-tools/automated-test-scripts/common/test_azure.ucs admin@${IP1}:/config/test.ucs
    # create directories and copy test.ucs to /shared/tmp/ucs/ucsOriginal.ucs to mirror autoscale.js behavior when restoring bigip via ucs
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" admin@${IP1} -p $PORT1 'modify auth user admin shell bash'
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" admin@${IP1} -p $PORT1 'mkdir -p /shared/tmp/ucs/old; mkdir -p /shared/tmp/ucs/new; mkdir -p /shared/tmp/ucs/ucsRestore; cp /config/test.ucs /shared/tmp/ucs/ucsOriginal.ucs'
    # run update_autoscale_ucs.py using same args as autoscale.js
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" admin@${IP1} -p $PORT1 'python /config/cloud/azure/node_modules/\@f5devcentral/f5-cloud-libs/scripts/update_autoscale_ucs.py --original-ucs "/shared/tmp/ucs/ucsOriginal.ucs" --updated-ucs "/shared/tmp/ucs/ucsUpdated.ucs" --cloud-provider "azure" --extract-directory "/shared/tmp/ucs/ucsRestore"'
    # unzip original ucs and updated ucs for comparison
    sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" admin@${IP1} -p $PORT1 'tar -C /shared/tmp/ucs/new -xvf /shared/tmp/ucs/ucsUpdated.ucs; tar -C /shared/tmp/ucs/old -xvf /shared/tmp/ucs/ucsOriginal.ucs'
    # capture diffs
    bigip_diff=$(sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" admin@${IP1} -p $PORT1 'diff /var/tmp/ucs/old/config/bigip.conf /var/tmp/ucs/new/config/bigip.conf')
    bigip_base_diff=$(sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" admin@${IP1} -p $PORT1 'diff /var/tmp/ucs/old/config/bigip_base.conf /var/tmp/ucs/new/config/bigip_base.conf')
    bigip_dat_diff=$(sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" admin@${IP1} -p $PORT1 'diff /var/tmp/ucs/old/config/BigDB.dat /var/tmp/ucs/new/config/BigDB.dat')
    manifest_diff=$(sshpass -p '<AUTOFILL PASSWORD>' ssh -o "StrictHostKeyChecking no" admin@${IP1} -p $PORT1 'diff /var/tmp/ucs/old/SPEC-Manifest /var/tmp/ucs/new/SPEC-Manifest')
    ssh-keygen -R $IP1 2>/dev/null
else
  echo "Nothing matched, unable to load test.ucs to bigip"
fi

# evaluate diffs
echo "$bigip_diff"
echo "--------------------"
echo "$bigip_base_diff"
echo "--------------------"
echo "$bigip_dat_diff"
echo "--------------------"
echo "$manifest_diff"

# diff should at a min contain original > ip and new < hostname
if echo $bigip_base_diff | grep -q '<RESOURCE GROUP>-vmss_';then
    echo "SUCCESS"
else
    echo "FAILED"
fi