#!/bin/bash
function passwd() {
  echo | f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/decryptDataFromFile.js --data-file /config/cloud/.passwd | awk '{print $1}'
}

while getopts m:d:n:j:k:h:s:t:l:a:c:r:o:u: option
do case "$option"  in
        o) declarationUrl=$OPTARG;;
        m) mode=$OPTARG;;
        n) pool_member=$OPTARG;;
        j) vs_http_port=$OPTARG;;
        k) vs_https_port=$OPTARG;;
        h) pool_http_port=$OPTARG;;
        s) pool_https_port=$OPTARG;;
        t) type=$OPTARG;;
        l) level=$OPTARG;;
        a) policy=$OPTARG;;
        c) ssl_cert=$OPTARG;;
        r) ssl_passwd=$OPTARG;;
        u) user=$OPTARG;;
    esac
done

deployed="no"
file_loc="/config/cloud/custom_config"
dfl_mgmt_port=`tmsh list sys httpd ssl-port | grep ssl-port | sed 's/ssl-port //;s/ //g'`
url_regex="(http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$"

if [[ $declarationUrl =~ $url_regex ]]; then
    response_code=$(/usr/bin/curl -sk -w "%{http_code}" $declarationUrl -o $file_loc)
    if [[ $response_code == 200 ]]; then
         echo "Custom config download complete; checking for valid JSON."
         cat $file_loc | jq .class
         if [[ $? == 0 ]]; then
             response_code=$(/usr/bin/curl -skvvu $user:$(passwd) -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "Expect:" https://localhost:$dfl_mgmt_port/mgmt/shared/appsvcs/declare -d @$file_loc -o /dev/null)

             if [[ $response_code == 200 || $response_code == 502 ]]; then
                  echo "Deployment of application succeeded."
                  deployed="yes"
             else
                 echo "Failed to deploy application; continuing with response code '"$response_code"'"
             fi
         else
             echo "Custom config was not valid JSON, continuing"
         fi
    else
        echo "Failed to download custom config; continuing with response code '"$response_code"'"
    fi
else
     echo "Custom config was not a URL, continuing."
fi

if [[ $deployed == "no" && $declarationUrl == "NOT_SPECIFIED" ]]; then
    ip_regex='^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'
    dfl_mgmt_port=`tmsh list sys httpd ssl-port | grep ssl-port | sed 's/ssl-port //;s/ //g'`
    mode=`sed "s/-/_/g" <<<"$mode"`
    payload='{"class":"ADC","schemaVersion":"3.0.0","label":"autoscale_waf","id":"AUTOSCALE_WAF","remark":"Autoscale WAF","waf":{"class":"Tenant","Shared":{"class":"Application","template":"shared","serviceAddress":{"class":"Service_Address","virtualAddress":"0.0.0.0"},"policyWAF":{"class":"WAF_Policy","file":"/tmp/as30-linux-medium.xml"}},"http":{"class":"Application","template":"http","pool":{"class":"Pool","monitors":["http"],"members":[{"addressDiscovery":"fqdn","autoPopulate":true,"servicePort":80,"hostname":"www.example.com","serverAddresses":["255.255.255.254"]}]},"serviceMain":{"class":"Service_HTTP","virtualAddresses":[{"use":"/waf/Shared/serviceAddress"}],"virtualPort":80,"snat":"auto","securityLogProfiles":[{"bigip":"/Common/Log illegal requests"}],"pool":"pool","policyWAF":{"use":"/waf/Shared/policyWAF"}}},"https":{"class":"Application","template":"https","serverTLS":{"class":"TLS_Server","certificates":[{"certificate":"certServer"}],"authenticationTrustCA":{"bigip":"/Common/ca-bundle.crt"}},"certServer":{"class":"Certificate","certificate":{"bigip":"/Common/wafCert.crt"},"privateKey":{"bigip":"/Common/wafCert.key"}},"clientTLS":{"class":"TLS_Client"},"pool":{"class":"Pool","monitors":["https"],"members":[{"addressDiscovery":"fqdn","autoPopulate":true,"servicePort":443,"hostname":"www.example.com","serverAddresses":["255.255.255.254"]}]},"serviceMain":{"class":"Service_HTTPS","virtualAddresses":[{"use":"/waf/Shared/serviceAddress"}],"virtualPort":443,"serverTLS":"serverTLS","clientTLS":"clientTLS","redirect80":true,"snat":"auto","securityLogProfiles":[{"bigip":"/Common/Log illegal requests"}],"pool":"pool","policyWAF":{"use":"/waf/Shared/policyWAF"}}},"https_offload":{"class":"Application","template":"https","serverTLS":{"class":"TLS_Server","certificates":[{"certificate":"certServer"}],"authenticationTrustCA":{"bigip":"/Common/ca-bundle.crt"}},"certServer":{"class":"Certificate","certificate":{"bigip":"/Common/wafCert.crt"},"privateKey":{"bigip":"/Common/wafCert.key"}},"pool":{"class":"Pool","monitors":["http"],"members":[{"addressDiscovery":"fqdn","autoPopulate":true,"servicePort":80,"hostname":"www.example.com","serverAddresses":["255.255.255.254"]}]},"serviceMain":{"class":"Service_HTTPS","virtualAddresses":[{"use":"/waf/Shared/serviceAddress"}],"virtualPort":80,"serverTLS":"serverTLS","snat":"auto","securityLogProfiles":[{"bigip":"/Common/Log illegal requests"}],"pool":"pool","policyWAF":{"use":"/waf/Shared/policyWAF"}}}}}'

    # verify that the custom policy is a URL
    if [[ $level == "custom" ]]; then
         if [[ -n $policy && $policy != "NOT_SPECIFIED" ]]; then
             if [[ $policy =~ $url_regex ]]; then
                  custom_policy=$policy
                  /usr/bin/curl -sk $custom_policy --retry 3 -o /tmp/custom_policy.xml
                  asm_policy="/tmp/custom_policy.xml"
             else
                  echo "Custom policy was not a URL, defaulting to high"
                  asm_policy="/config/cloud/asm-policy-$type-high.xml"
             fi
         else
              echo "Custom policy was not specified, defaulting to high"
              asm_policy="/config/cloud/asm-policy-$type-high.xml"
         fi
    else
         asm_policy="/config/cloud/asm-policy-$type-$level.xml"
    fi

    if [[ $mode == "https" || $mode == "http_https" || $mode == "https_offload" ]]; then
         chain="/Common/ca-bundle.crt"

         echo "Starting Certificate download"

         certificate_location=$ssl_cert

         response_code=$(/usr/bin/curl -sk -u $user:$(passwd) -w "%{http_code}"  -X POST -H "Content-type: application/json" https://localhost:$dfl_mgmt_port/mgmt/tm/util/bash -d '{ "command":"run","utilCmdArgs":"-c \"curl -k -s -f --retry 5 --retry-delay 10 --retry-max-time 10 -o /config/tmp.pfx '$certificate_location'\"" }' -o /dev/null)

         if [[ $response_code == 200  ]]; then
              echo "Certificate download complete."
         else
             echo "Failed to download SSL cert; exiting with response code '"$response_code"'"
             exit 1
         fi

         response_code=$(/usr/bin/curl -sku $user:$(passwd) -w "%{http_code}" -X POST -H "Content-Type: application/json" https://localhost:$dfl_mgmt_port/mgmt/tm/sys/crypto/pkcs12 -d '{"command": "install","name": "wafCert","options": [ { "from-local-file": "/config/tmp.pfx" }, { "passphrase": "'"$ssl_passwd"'" } ] }' -o /dev/null)

         if [[ $response_code == 200  ]]; then
              echo "Certificate install complete."
         else
             echo "Failed to install SSL cert; exiting with response code '"$response_code"'"
             exit 1
         fi
    fi

    payload=$(echo $payload | jq -c --arg asm_policy $asm_policy ' .waf.Shared.policyWAF.file = $asm_policy')

    payload=$(echo $payload | jq -c --arg pool_http_port $pool_http_port --arg pool_https_port $pool_https_port --arg vs_http_port $vs_http_port --arg vs_https_port $vs_https_port ' .waf.http.pool.members[0].servicePort = ($pool_http_port | tonumber) | .waf.http.serviceMain.virtualPort = ($vs_http_port | tonumber) | .waf.https.pool.members[0].servicePort = ($pool_https_port | tonumber) | .waf.https.serviceMain.virtualPort = ($vs_https_port | tonumber) | .waf.https_offload.pool.members[0].servicePort = ($pool_http_port | tonumber) | .waf.https_offload.serviceMain.virtualPort = ($vs_https_port | tonumber)')

    if [[ $pool_member =~ $ip_regex ]]; then
         payload=$(echo $payload | jq -c 'del(.waf.http.pool.members[0].autoPopulate) | del(.waf.http.pool.members[0].hostname) | del(.waf.http.pool.members[0].addressDiscovery) |  del(.waf.https.pool.members[0].autoPopulate) | del(.waf.https.pool.members[0].hostname) | del(.waf.https.pool.members[0].addressDiscovery) | del(.waf.https_offload.pool.members[0].autoPopulate) | del(.waf.https_offload.pool.members[0].hostname) | del(.waf.https_offload.pool.members[0].addressDiscovery)')

         payload=$(echo $payload | jq -c --arg pool_member $pool_member '.waf.http.pool.members[0].serverAddresses[0] = $pool_member | .waf.https.pool.members[0].serverAddresses[0] = $pool_member | .waf.https_offload.pool.members[0].serverAddresses[0] = $pool_member')
    else
         payload=$(echo $payload | jq -c 'del(.waf.http.pool.members[0].serverAddresses) | del(.waf.https.pool.members[0].serverAddresses) | del(.waf.https_offload.pool.members[0].serverAddresses)')

         payload=$(echo $payload | jq -c --arg pool_member $pool_member '.waf.http.pool.members[0].hostname = $pool_member | .waf.https.pool.members[0].hostname = $pool_member | .waf.https_offload.pool.members[0].hostname = $pool_member')
    fi

    if [[ $mode == "http" ]]; then
        payload=$(echo $payload | jq -c 'del(.waf.https) | del(.waf.https_offload)')
    elif [[ $mode == "https" ]]; then
        payload=$(echo $payload | jq -c 'del(.waf.http) | del(.waf.https_offload) | .waf.https.certServer.certificate.bigip = "/Common/wafCert.crt" | .waf.https.certServer.privateKey.bigip = "/Common/wafCert.key"')
    elif [[ $mode == "http_https" ]]; then
        payload=$(echo $payload | jq -c 'del(.waf.https_offload) | .waf.https.serviceMain.redirect80 = false | .waf.https.certServer.certificate.bigip = "/Common/wafCert.crt" | .waf.https.certServer.privateKey.bigip = "/Common/wafCert.key"')
    else
        payload=$(echo $payload | jq -c 'del(.waf.http) | del(.waf.https) | .waf.https_offload.certServer.certificate.bigip = "/Common/wafCert.crt" | .waf.https_offload.certServer.privateKey.bigip = "/Common/wafCert.key"')
    fi

     response_code=$(/usr/bin/curl -skvvu $user:$(passwd) -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "Expect:" https://localhost:$dfl_mgmt_port/mgmt/shared/appsvcs/declare -d "$payload" -o /dev/null)

     if [[ $response_code == 200 || $response_code == 502  ]]; then
          echo "Deployment of application succeeded."
    else
         echo "Failed to deploy application; exiting with response code '"$response_code"'"
         exit 1
     fi
 fi

echo "Deployment complete."
exit