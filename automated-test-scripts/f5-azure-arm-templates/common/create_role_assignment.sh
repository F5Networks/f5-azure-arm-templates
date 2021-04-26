#  expectValue = "Succeeded"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

PRINCIPAL_ID=$(az identity create -g <RESOURCE GROUP> -n <RESOURCE GROUP>id | jq -r .principalId)
echo "Principal ID: $PRINCIPAL_ID"

RESPONSE=$(az role assignment create --assignee-object-id ${PRINCIPAL_ID} --assignee-principal-type ServicePrincipal --role "Contributor" --resource-group <RESOURCE GROUP> | jq -r .resourceGroup)
echo "RESPONSE: $RESPONSE"

if [[ $RESPONSE == "<RESOURCE GROUP>" ]]; then
    echo "Succeeded"
else
    echo "Failed"
fi