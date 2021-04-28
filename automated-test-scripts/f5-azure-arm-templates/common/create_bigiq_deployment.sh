#  expectValue = "Template validation succeeded"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# download and use --template-file because --template-uri is limiting
TEMPLATE_FILE=${TMP_DIR}/<RESOURCE GROUP>.json
curl -k <TEMPLATE URL> -o ${TEMPLATE_FILE}
echo "TEMPLATE URI: <TEMPLATE URL>"

## Standalone Parameters
parameters="{"
parameters+='"adminUsername":{"value":"<ADMIN USER>"},"instanceType":{"value":"<INSTANCE TYPE>"},"instanceName":{"value":"<INSTANCE NAME>"},"bigIqVersion":{"value":"<BIGIQ VERSION>"},"ntpServer":{"value":"<NTP SERVER>"},"timeZone":{"value":"<TIMEZONE>"},"customImage":{"value":"<CUSTOM IMAGE PARAM>"},"restrictedSrcAddress":{"value":"*"},"allowUsageAnalytics":{"value":"<USAGE ANALYTICS CHOICE>"}<LICENSE PARAM><LIC POOL PARAM><REG POOL PARAM><NETWORK PARAM><STACK PARAM><ADDTL NIC PARAM><VNET PARAM><DNS LABEL>'

## Add cluster parameters if cluster template
if [[ "<CLUSTER>" == "Yes" ]]; then
    parameters+=',"adminPassword":{"value":"<AUTOFILL PASSWORD>"},"masterKey":{"value":"34jkcvni389#494kcx@dfkdi9H"}<SUBNET PARAM SELF>'
    if [[ $(echo <TEMPLATE URL> | grep -E '(existing-stack)') ]]; then
        parameters+=',"userAssignedIdentityName":{"value":"myUserIdentity"}'
        parameters+=',"userAssignedIdentityResourceGroupName":{"value":"myResourceGroupName"}'
    fi
else
    parameters+=',"adminPassword":{"value":"<AUTOFILL PASSWORD>"},"masterKey":{"value":"34jkcvni389#494kcx@dfkdi9H"}'
fi
parameters+="}"

DEPLOY_PARAMS=${parameters}
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