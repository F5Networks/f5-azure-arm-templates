#  expectValue = "Template validation succeeded"
#  expectFailValue = "Template validation failed"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# download and use --template-file because --template-uri is limiting
TEMPLATE_FILE=${TMP_DIR}/<RESOURCE GROUP>.json
curl -k <TEMPLATE URL> -o ${TEMPLATE_FILE}
echo "TEMPLATE URI: <TEMPLATE URL>"

VALIDATION=$(az deployment group validate --resource-group <RESOURCE GROUP> --template-file ${TEMPLATE_FILE} --parameters '{"adminUsername":{"value":"dewpoint"},"instanceType":{"value":"<INSTANCE TYPE>"},"bigIpVersion":{"value":"<BIGIP VERSION>"},"imageName":{"value":"<IMAGE NAME>"},"staticImageName":{"value":"<STATIC IMAGE NAME>"},"ntpServer":{"value":"<NTP SERVER>"},"timeZone":{"value":"<TIMEZONE>"},"customImage":{"value":"<CUSTOM IMAGE PARAM>"},"restrictedSrcAddress":{"value":"*"},"allowUsageAnalytics":{"value":"<USAGE ANALYTICS CHOICE>"}<PASSWORD PARAM><DNS LABEL><LICENSE PARAM><NETWORK PARAM><STACK PARAM><VNET PARAM><ADDTL NIC PARAM>}' | jq .properties.provisioningState)

if [[ $VALIDATION == \"Succeeded\" ]]; then
    az deployment group create --verbose --no-wait --template-file ${TEMPLATE_FILE} -g <RESOURCE GROUP> -n <RESOURCE GROUP> --parameters '{"adminUsername":{"value":"dewpoint"},"instanceType":{"value":"<INSTANCE TYPE>"},"bigIpVersion":{"value":"<BIGIP VERSION>"},"imageName":{"value":"<IMAGE NAME>"},"staticImageName":{"value":"<STATIC IMAGE NAME>"},"ntpServer":{"value":"<NTP SERVER>"},"timeZone":{"value":"<TIMEZONE>"},"customImage":{"value":"<CUSTOM IMAGE PARAM>"},"restrictedSrcAddress":{"value":"*"},"allowUsageAnalytics":{"value":"<USAGE ANALYTICS CHOICE>"}<PASSWORD PARAM><DNS LABEL><LICENSE PARAM><NETWORK PARAM><STACK PARAM><VNET PARAM><ADDTL NIC PARAM>}'
    echo "Template validation succeeded"
else
    echo "Template validation failed"
fi