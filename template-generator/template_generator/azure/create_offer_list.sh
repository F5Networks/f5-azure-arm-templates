#/bin/bash
## This script will create a YAML file with all the current Azure marketplace offers

az vm image list --output yaml --publisher f5-networks --all --query "[?!(contains(sku,'-po-'))]" | tee ../../../azure-offer-list.yaml ../../../azure-offer-list.yaml