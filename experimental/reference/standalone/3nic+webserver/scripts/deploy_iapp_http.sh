#!/bin/bash
export PATH="/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin/"
# Default MGMT and VS Port if not passed in as a script argument
mgmt_port=443
vs_http_port="80"

while getopts d:n:h:u:p:v:c:s: option
do	case "$option"  in
        d) deployment=$OPTARG;;
	    n) pool_member=$OPTARG;;
        h) pool_http_port=$OPTARG;;
        u) user=$OPTARG;;
        p) passwd=$OPTARG;;
		v) vs_ip=$OPTARG;;
		c) mgmt_port=$OPTARG;;
        s) vs_http_port=$OPTARG;;
    esac
done

IP_REGEX='^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'
device_group="none"
traffic_group="traffic-group-local-only"
pool_member_list=${pool_member//,/ }
cert="/Common/default.crt"
key="/Common/default.key"
chain="/Common/ca-bundle.crt"

sleep 30

# download iApp templates
template_location="http://cdn-prod-ore-f5.s3-website-us-west-2.amazonaws.com/product/blackbox/staging/azure"

# In a for loop to allow for adding additional template downloads
for template in f5.http.v1.2.0rc4.tmpl
do
     curl -k -s -f --retry 5 --retry-delay 10 --retry-max-time 10 -o /config/$template $template_location/$template
     response_code=$(curl -sku $user:$passwd -w "%{http_code}" -X POST -H "Content-Type: application/json" https://localhost:$mgmt_port/mgmt/tm/sys/config -d '{"command": "load","name": "merge","options": [ { "file": "/config/'"$template"'" } ] }' -o /dev/null)
     if [[ $response_code != 200  ]]; then
          echo "Failed to install iApp template; exiting with response code '"$response_code"'"
          exit
     fi
     sleep 10
done

# pre-create node
for unique_node in $pool_member_list
do
    if [[ $unique_node =~ $IP_REGEX ]]; then
        response_code=$(curl -sku $user:$passwd -w "%{http_code}" -X POST -H "Content-Type: application/json" https://localhost:$mgmt_port/mgmt/tm/ltm/node -d '{"name": "'"$unique_node"'","partition": "Common","address": "'"$unique_node"'"}' -o /dev/null)
    else
        response_code=$(curl -sku $user:$passwd -w "%{http_code}" -X POST -H "Content-Type: application/json" https://localhost:$mgmt_port/mgmt/tm/ltm/node -d '{"name": "'"$unique_node"'","partition": "Common","fqdn": {"autopopulate": "enabled","tmName": "'"$unique_node"'"}}' -o /dev/null)
    fi
    if [[ $response_code != 200  ]]; then
        echo "Failed to create node $unique_node; with response code '"$response_code"'"
    fi
done
sleep 10

# Create json blob of pool members
for unique_member in $pool_member_list
do
    pool_members_json+='{"row":["'"$unique_member"'","'"80"'","0"]},'
done


# deploy unencrypted application
if [[ $vs_http_port == "80"  ]]; then
     response_code=$(curl -sku $user:$passwd -w "%{http_code}" -X POST -H "Content-Type: application/json" https://localhost:$mgmt_port/mgmt/tm/sys/application/service/ -d '{"name":"'"$deployment"'-'"$vs_http_port"'","partition":"Common","deviceGroup":"'"$device_group"'","strictUpdates":"enabled","template":"/Common/f5.http.v1.2.0rc4","trafficGroup":"'"$traffic_group"'","tables":[{"name":"pool__hosts","columnNames":["name"],"rows":[{"row":["'"$deployment"'"]}]},{"name":"pool__members","columnNames":["addr","port","connection_limit"],"rows":['"${pool_members_json%,}"']},{"name":"server_pools__servers"}],"variables":[{"name":"monitor__monitor","encrypted":"no","value":"/Common/http"},{"name":"pool__addr","encrypted":"no","value":"'"$vs_ip"'"},{"name":"pool__mask","encrypted":"no","value":"255.255.255.255"},{"name":"pool__persist","encrypted":"no","value":"/#do_not_use#"},{"name":"pool__port","encrypted":"no","value":"'"$vs_http_port"'"},{"name":"ssl__mode","encrypted":"no","value":"no_ssl"},{"name":"client__standard_caching_without_wa","encrypted":"no","value":"/#do_not_use#"}]}' -o /dev/null)

     if [[ $response_code != 200  ]]; then
          echo "Failed to deploy unencrypted application; exiting with response code '"$response_code"'"
          exit
     fi
fi

# deploy encrypted(offload) application
if [[ $vs_http_port == "443"  ]]; then
     response_code=$(curl -sku $user:$passwd -w "%{http_code}" -X POST -H "Content-Type: application/json" https://localhost:$mgmt_port/mgmt/tm/sys/application/service/ -d '{"name":"'"$deployment"'-'"$vs_http_port"'","partition":"Common","deviceGroup":"'"$device_group"'","strictUpdates":"enabled","template":"/Common/f5.http.v1.2.0rc4","trafficGroup":"'"$traffic_group"'","tables":[{"name":"pool__hosts","columnNames":["name"],"rows":[{"row":["'"$deployment"'"]}]},{"name":"pool__members","columnNames":["addr","port","connection_limit"],"rows":['"${pool_members_json%,}"']},{"name":"server_pools__servers"}],"variables":[{"name":"monitor__monitor","encrypted":"no","value":"/Common/http"},{"name":"pool__addr","encrypted":"no","value":"'"$vs_ip"'"},{"name":"pool__mask","encrypted":"no","value":"255.255.255.255"},{"name":"pool__persist","encrypted":"no","value":"/#do_not_use#"},{"name":"pool__port_secure","encrypted":"no","value":"'"$vs_http_port"'"},{"name":"pool__redirect_to_https","encrypted":"no","value":"no"},{"name":"client__standard_caching_without_wa","encrypted":"no","value":"/#do_not_use#"},{"name":"ssl__cert","encrypted":"no","value":"'"$cert"'"},{"name":"ssl__key","encrypted":"no","value":"'"$key"'"},{"name":"ssl__mode","encrypted":"no","value":"client_ssl"},{"name":"ssl__use_chain_cert","encrypted":"no","value":"'"$chain"'"}]}' -o /dev/null)

     if [[ $response_code != 200  ]]; then
          echo "Failed to deploy encrypted(offload) application; exiting with response code '"$response_code"'"
          exit
     fi
fi

echo "Deployment complete, vs port $vs_http_port chosen."
exit