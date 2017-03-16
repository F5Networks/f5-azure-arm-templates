# This script can be used to update some of the VM Scale Set Insight Settings since not available via the GUI

param(

  [Parameter(Mandatory=$True)]
  [string]
  $resourceGroupName,

  [Parameter(Mandatory=$True)]
  [string]
  $vmScaleSetName,

  [Parameter(Mandatory=$True)]
  [string]
  $action = "view",

  [string]
  $capacityMinimum,

  [string]
  $capacityMaximum,

  [string]
  $disableAutoScaling

)

Write-Host "Connecting to vm scale set '$vmScaleSetName' in resource group '$resourceGroupName' with the action '$action' on the scale set insights"

# Get the current VM Scale Set Settings
$insights = Get-AzureRmResource -ResourceGroupName $resourceGroupName -ResourceType microsoft.insights/autoscalesettings -ResourceName autoscaleconfig
$insightsProperties = $insights.Properties


# Display current VM Scale Set Settings
Write-Output "-------Insight Properties-------"
$insightsProperties
Write-Output "-------Insight Property Profiles-------"
$insightsProperties.profiles
Write-Output "-------Insight Property Notifications-------"
$insightsProperties.notifications
$insightsProperties.notifications.email
$insightsProperties.notifications.webhooks


if ($action -eq "modify") {
    # Set Autoscale Settings
    $insightsProperties.enabled = $disableAutoScaling
    $insightsProperties.profiles[0].capacity = @{minimum=$capacityMinimum; maximum=$capacityMaximum; default=$capacityMinimum}
    #$insightsProperties.notifications[0].email.sendToSubscriptionAdministrator = $false
    #$insightsProperties.notifications[0].email.customEmails = "j.sevedge@f5.com"
    Set-AzureRmResource -PropertyObject $insightsProperties -ResourceGroupName $resourceGroupName -ResourceType microsoft.insights/autoscalesettings -ResourceName autoscaleconfig -Force
}
