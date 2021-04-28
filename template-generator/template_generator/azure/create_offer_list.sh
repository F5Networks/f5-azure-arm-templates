#/bin/bash
## This script will create a YAML file with all the current Azure marketplace offers

az vm image list --output yaml --publisher f5-networks --all --query "[?!(contains(sku,'-po-'))]" | tee ../../../../f5-azure-arm-templates/azure-offer-list.yaml ../../../../f5-azure-arm-templates-v2/azure-offer-list.yaml