# This script can be used to update the VM Scale Set to a newer big ip version, I.E. to go from 12.1.22 to 13.0.000
# NOTE: Another alternative would be to simply "re-deploy" the ARM template using all the same variables except the BIG-IP version
# parameter. That will update the version used and Azure Load Balancer/NSG rules(if needed), then simply updating each instance
# to the latest model will be all that is required to utilize the latest BIG-IP version selected.

param(

  [Parameter(Mandatory=$True)]
  [string]
  $resourceGroupName,

  [Parameter(Mandatory=$True)]
  [string]
  $vmScaleSetName,

  [Parameter(Mandatory=$True)]
  [string]
  $oldBigIpVersion,

  [Parameter(Mandatory=$True)]
  [string]
  $newBigIpVersion

)

# Get the current VM Scale Set Settings
$vmss = Get-AzureRmVmss -ResourceGroupName $resourceGroupName -VMScaleSetName $vmScaleSetName
$vmss

if ($oldBigIpVersion -eq $vmss.virtualMachineProfile.storageProfile.imageReference.version ) {
    Write-Output "Confirmed version upgrading from is $oldBigIpVersion"
} else {
    Write-Error "Uh oh, are you sure you are upgrading the right VM Scale Set?"
    exit 1
}

# Set the new BIG-IP version to use
$vmss.virtualMachineProfile.storageProfile.imageReference.version = $newBigIpVersion

# update the VMSS model
Update-AzureRmVmss -ResourceGroupName $resourceGroupName -Name $vmScaleSetName -VirtualMachineScaleSet $vmss

Write-Output "VM Scale Set new version is $newBigIpVersion"
