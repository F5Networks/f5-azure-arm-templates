#  expectValue = "Service deployments finished"
#  expectFailValue = "Template validation failed"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

case <LICENSE TYPE> in
bigiq)
    # download and use --template-file because --template-uri is limiting
    curl -k https://s3.amazonaws.com/f5-cft/QA/azure-bigiq-standalone.json -o ${TMP_DIR}/azure-bigiq-standalone.json

    # validate the template
    VALIDATION=$(az deployment group validate --resource-group <RESOURCE GROUP> --template-file ${TMP_DIR}/azure-bigiq-standalone.json --parameters '{"adminPassword":{"value":"B!giq2017"},"dnsLabel":{"value":"<RESOURCE GROUP>-bigiq"},"bigIqLicenseKey1":{"value":"<AUTOFILL BIGIQ LICENSE KEY>"},"vnetResourceGroupName":{"value":"<RESOURCE GROUP>"},"licensePoolKeys":{"value":"clpv2:<AUTOFILL CLPV2 LICENSE KEY>"}}' | jq .properties.provisioningState)

    if [[ $VALIDATION == \"Succeeded\" ]]; then
        az deployment group create --verbose --no-wait --template-file ${TMP_DIR}/azure-bigiq-standalone.json -g <RESOURCE GROUP> -n <RESOURCE GROUP>-bigiq --parameters '{"adminPassword":{"value":"B!giq2017"},"dnsLabel":{"value":"<RESOURCE GROUP>-bigiq"},"bigIqLicenseKey1":{"value":"<AUTOFILL BIGIQ LICENSE KEY>"},"vnetResourceGroupName":{"value":"<RESOURCE GROUP>"},"licensePoolKeys":{"value":"clpv2:<AUTOFILL CLPV2 LICENSE KEY>"}}'
    else
        echo "Template validation failed"
    fi
    echo "Deployed BIG-IQ" ;;
*)
    echo "Not deploying BIG-IQ" ;;
esac

if [[ $(echo <TEMPLATE URL> | grep -E '(autoscale/ltm/via-dns|autoscale/waf/via-dns)') ]]; then
    # download and use --template-file because --template-uri is limiting
    curl -k https://s3.amazonaws.com/f5-cft/QA/azure-gtm.json -o ${TMP_DIR}/azure-gtm.json

    # validate the template
    VALIDATION=$(az deployment group validate --resource-group <RESOURCE GROUP> --template-file ${TMP_DIR}/azure-gtm.json --parameters '{"adminPasswordOrKey":{"value":"B!gdns2017"},"dnsLabel":{"value":"<RESOURCE GROUP>-dns"},"licenseKey1":{"value":"<AUTOFILL EVAL LICENSE KEY>"},"vnetResourceGroupName":{"value":"<RESOURCE GROUP>"}}' | jq .properties.provisioningState)

    if [[ $VALIDATION == \"Succeeded\" ]]; then
        az deployment group create --verbose --no-wait --template-file ${TMP_DIR}/azure-gtm.json -g <RESOURCE GROUP> -n <RESOURCE GROUP>-dns --parameters '{"adminPasswordOrKey":{"value":"B!gdns2017"},"dnsLabel":{"value":"<RESOURCE GROUP>-dns"},"licenseKey1":{"value":"<AUTOFILL EVAL LICENSE KEY>"},"vnetResourceGroupName":{"value":"<RESOURCE GROUP>"}}'
    else
        echo "Template validation failed"
    fi
else
    echo "Not deploying DNS provider"
fi

echo "Service deployments finished"