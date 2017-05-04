# This script can be used to update some of the VM Scale Set Insight Settings since not available via the GUI
# The assumption is that no major changes have been made post-deployment of the ARM template, even then however this is just an example

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
  $notificationEmail = "None",

  [string]
  $autoScalingEnabled = "True"

)

Write-Host "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged." -foregroundcolor green
Start-Sleep -s 3

# Connect to Azure, right now it is only interactive login
try {
    Write-Host "Checking if already logged in!"
    Get-AzureRmSubscription | Out-Null
    Write-Host "Already logged in, continuing..."
    }
    Catch {
    Write-Host "Not logged in, please login..."
    Login-AzureRmAccount
  }

Write-Host "Connecting to vm scale set '$vmScaleSetName' in resource group '$resourceGroupName' with the action '$action' on the scale set insights"

# Get the current VM Scale Set Settings
$insights = Get-AzureRmResource -ResourceGroupName $resourceGroupName -ResourceType microsoft.insights/autoscalesettings -ResourceName autoscaleconfig
$insightsProperties = $insights.Properties

if ($action -eq "view") {
    # Display current VM Scale Set Settings
    Write-Output "-------Outputted as JSON-------"
    $jsoninsightsProperties = $insightsProperties | ConvertTo-Json -depth 5
    Write-Output ($jsoninsightsProperties)
}

if ($action -eq "modify") {
    # Manipulate User Params
    $email = @{}; $email.Add("sendToSubscriptionAdministrator", $false); $email.Add("sendToSubscriptionCoAdministrators", $false)
    $notifications = @{}; $notifications.Add("operation", "Scale"); $notifications.Add("webhooks", $null); $notifications.Add("email", $email); $notifications = @($notifications)
    if ($notificationEmail -eq "None" ) {
      $email.Add("customEmails", "")
    } else {
      $email.Add("customEmails", @($notificationEmail))
    }

    # Set Autoscale Settings
    $insightsProperties.enabled = $autoScalingEnabled
    $insightsProperties.profiles[0].capacity = @{minimum=$capacityMinimum; maximum=$capacityMaximum; default=$capacityMinimum}
    $insightsProperties.notifications = @($notifications)

    Set-AzureRmResource -PropertyObject $insightsProperties -ResourceGroupName $resourceGroupName -ResourceType microsoft.insights/autoscalesettings -ResourceName autoscaleconfig -Verbose -Force
}
