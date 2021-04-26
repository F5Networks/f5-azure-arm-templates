#!/bin/bash
function passwd() {
  echo | f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/decryptDataFromFile.js --data-file /config/cloud/.passwd | awk '{print $1}'
}

while getopts o:u:f: option
do case "$option"  in
        o) declarationUrl=$OPTARG;;
        u) user=$OPTARG;;
        f) isAs3=$OPTARG;;
    esac
done

deployed="no"
file_loc="/config/cloud/custom_config"
dfl_mgmt_port=`tmsh list sys httpd ssl-port | grep ssl-port | sed 's/ssl-port //;s/ //g'`
url_regex="(http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$"

if [[ $declarationUrl =~ $url_regx && $isAs3 =~ "do_as" ]]; then
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

if [[ $deployed == "no" && $declarationUrl == "NOT_SPECIFIED" &&  $2 != 'skip_as3' ]]; then
    echo "Application deployment failed or custom URL was not specified."
fi

cfe_file_loc=/config/cloud/azure/cfe-init.cfg
cfe_response_code=$(/usr/bin/curl -skvvu $user:$(passwd) -w "%{http_code}" -X POST -H "Content-Type:application/json" https://localhost:443/mgmt/shared/cloud-failover/declare -d @$cfe_file_loc)

if [[ $cfe_response_code == 200 || $cfe_response_code == 502 ]]; then
    echo "Deployment of CFE application succeeded."
else
    echo "Failed to deploy CFE application with response code '"$cfe_response_code"'"
fi

echo "Deployment complete."
exit
