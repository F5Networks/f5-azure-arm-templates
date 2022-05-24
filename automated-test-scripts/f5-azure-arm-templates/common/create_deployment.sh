#  expectValue = "Template validation succeeded"
#  expectFailValue = "failed"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

if [[ <CREATE PUBLIC IP> == "Yes" ]]; then
  source_cidr=$(curl ifconfig.me)/32
else
  source_cidr='0.0.0.0/0'
fi
echo "source_cidr=$source_cidr"

# download and use --template-file because --template-uri is limiting
TEMPLATE_FILE=${TMP_DIR}/<RESOURCE GROUP>.json
curl -k <TEMPLATE URL> -o ${TEMPLATE_FILE}
echo "TEMPLATE URI: <TEMPLATE URL>"

case <PASSWORD TYPE> in
password)
    PASSWORD='<AUTOFILL PASSWORD>'
    echo "Autofill password: $PASSWORD" ;;
sshPublicKey)
    PASSWORD=$(az keyvault secret show --vault-name dewdropKeyVault -n dewpt-public | jq .value --raw-output) ;;
esac

LICENSE_PARAM='<LICENSE PARAM>'
DNS_PROVIDER_HOST_PARAM=''
PUBLIC_IP_PARAM=''
EXISTENT_LB_PARAM=''
USER_IDENTITY_PARAM=''

case <LICENSE TYPE> in
bigiq)
    bigiq_address=''
    bigiq_password=''
    if [ -f "${TMP_DIR}/bigiq_info.json" ]; then
      echo "Found existing BIG-IQ"
      cat ${TMP_DIR}/bigiq_info.json
      bigiq_address=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_address)
      bigiq_password=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_password)
    else
        echo "failed - No BIG-IQ found"
    fi
    LICENSE_PARAM=',"bigIqAddress":{"value":"'"${bigiq_address}"'"},"bigIqUsername":{"value":"admin"},"bigIqPassword":{"value":"'"${bigiq_password}"'"},"bigIqLicensePoolName":{"value":"production"},"bigIqLicenseSkuKeyword1":{"value":"F5-BIG-MSP-BT-1G"},"bigIqLicenseUnitOfMeasure":{"value":"yearly"}' ;;
*)
    echo "Not licensed with BIG-IQ" ;;
esac

if [[ $(echo <TEMPLATE URL> | grep -E '(autoscale/ltm/via-dns|autoscale/waf/via-dns)') ]]; then
    DNS_PROVIDER_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["gtmIp"].value' --raw-output | cut -d' ' -f1`
    DNS_PROVIDER_HOST_PARAM=',"dnsProviderHost":{"value":"'"${DNS_PROVIDER_HOST}"'"}'
else
    echo "Not autoscale DNS"
fi

# CREATE PUBLIC IP: 'null' or non-existent will result in this parameter not being added
if [[ <CREATE PUBLIC IP> == "Yes" || <CREATE PUBLIC IP> == "No" ]]; then
    PUBLIC_IP_PARAM=',"provisionPublicIP":{"value":"<CREATE PUBLIC IP>"}'
fi

if [[ -z $(echo <TEMPLATE URL> | grep -E '(failover/same-net/via-api/)') ]]; then
    # CREATE PUBLIC IP APP: 'null' or non-existent will result in this parameter not being added
    if [[ <CREATE PUBLIC IP APP> == "Yes" || <CREATE PUBLIC IP APP> == "No" ]]; then
        PUBLIC_IP_APP_PARAM=',"provisionPublicIPApp":{"value":"<CREATE PUBLIC IP APP>"}'
    fi
fi

# CREATE INTERNAL LOAD BALANCER: 'null' or non-existent will result in this parameter not being added
if [[ <PROVISION INT LB> == "Yes" || <PROVISION INT LB> == "No" ]]; then
    PROVISION_INT_LB_PARAM=',"provisionInternalLoadBalancer":{"value":"<PROVISION INT LB>"}'
fi

if [[ <TEMPLATE URL> == *"existing-stack"* && <CREATE PUBLIC IP> == "Yes" && <EXT ALB EXISTS> == "Yes"  ]]; then
    EXISTENT_LB_PARAM=',"externalLoadBalancerName":{"value":"<RESOURCE GROUP>-existing-lb"}'
fi

if [[ $(echo <TEMPLATE URL> | grep -E '(failover/same-net/via-api/)') ]]; then
    USER_IDENTITY_PARAM=',"userAssignedManagedIdentity":{"value":"<USER IDENTITY>"}'
fi

DEPLOY_PARAMS='{"authenticationType":{"value":"<PASSWORD TYPE>"},"adminPasswordOrKey":{"value":"'"${PASSWORD}"'"},"adminUsername":{"value":"dewpoint"},"instanceType":{"value":"<INSTANCE TYPE>"},"bigIpVersion":{"value":"<BIGIP VERSION>"},"bigIpModules":{"value":"<BIGIP MODULES>"},"imageName":{"value":"<IMAGE NAME>"},"ntpServer":{"value":"<NTP SERVER>"},"declarationUrl":{"value":"<DECLARATION URL>"},"timeZone":{"value":"<TIMEZONE>"},"customImage":{"value":"<CUSTOM IMAGE PARAM>"},"customImageUrn":{"value":"<IMAGE URN>"},"restrictedSrcAddress":{"value":"'"${source_cidr}"'"},"allowUsageAnalytics":{"value":"<USAGE ANALYTICS CHOICE>"},"allowPhoneHome":{"value":"<PHONEHOME>"}<DNS LABEL><NETWORK PARAM><STACK PARAM><VNET PARAM><ADDTL NIC PARAM>'${LICENSE_PARAM}''${DNS_PROVIDER_HOST_PARAM}''${PUBLIC_IP_PARAM}''${PUBLIC_IP_APP_PARAM}''${PROVISION_INT_LB_PARAM}''${EXISTENT_LB_PARAM}''${ROUTE_TABLE_NAME}''${USER_IDENTITY_PARAM}'}'
DEPLOY_PARAMS_FILE=${TMP_DIR}/deploy_params.json

# save deployment parameters to a file, to avoid weird parameter parsing errors with certain values
# when passing as a variable. I.E. when providing an sshPublicKey
echo ${DEPLOY_PARAMS} > ${DEPLOY_PARAMS_FILE}

echo "DEBUG: DEPLOY PARAMS"
echo ${DEPLOY_PARAMS}

VALIDATE_RESPONSE=$(az deployment group validate --resource-group <RESOURCE GROUP> --template-file ${TEMPLATE_FILE} --parameters @${DEPLOY_PARAMS_FILE})
VALIDATION=$(echo ${VALIDATE_RESPONSE} | jq .properties.provisioningState)
if [[ $VALIDATION == \"Succeeded\" ]]; then
    az deployment group create --verbose --no-wait --template-file ${TEMPLATE_FILE} -g <RESOURCE GROUP> -n <RESOURCE GROUP> --parameters @${DEPLOY_PARAMS_FILE}
    echo "Template validation succeeded"
else
    echo "Template validation failed: ${VALIDATE_RESPONSE}"
fi
