#  expectValue = "Command ran"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# download and use --template-file because --template-uri is limiting
curl -k https://s3.amazonaws.com/f5-cft/QA/azure-purge.json -o ${TMP_DIR}/<RESOURCE GROUP>-purge.json --create-dirs

if echo "<TEMPLATE URL>" | grep "bigiq/licenseManagement/cluster"; then
    # don't delete the resource group
    echo y | az deployment group create --verbose --mode Complete --no-wait --template-file ${TMP_DIR}/<RESOURCE GROUP>-purge.json -g <RESOURCE GROUP> -n <RESOURCE GROUP>
else
    az group delete --verbose --no-wait -n <RESOURCE GROUP> --yes
fi

# Clean up temp directory
rm -rf ${TMP_DIR}
