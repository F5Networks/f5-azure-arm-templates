## Script parameters being asked for below match to parameters in the azuredeploy.json file, otherwise pointing to the ##
## azuredeploy.parameters.json file for values to use.  Some options below are mandatory, some (such as region) can    ##
## be supplied inline when running this script but if they aren't then the default will be used as specified below.    ##
## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth 200m -vmScaleSetMinCount 2 -vmScaleSetMaxCount 4 -autoScaleMetric Host_Throughput -appInsights CREATE_NEW -calculatedBandwidth 200m -scaleOutThreshold 90 -scaleInThreshold 10 -scaleTimeWindow 10 -adminUsername azureuser -adminPassword <value> -dnsLabel <value> -instanceType Standard_DS2_v2 -imageName Good -bigIpVersion 13.1.0200 -vnetName <value> -vnetResourceGroupName <value> -mgmtSubnetName <value> -dnsMemberIpType private -dnsMemberPort 80 -dnsProviderHost <value> -dnsProviderPort 443 -dnsProviderUser <value> -dnsProviderPassword <value> -dnsProviderPool autoscale_pool -dnsProviderDataCenter azure_datacenter -tenantId <value> -clientId <value> -servicePrincipalSecret <value> -notificationEmail OPTIONAL -ntpServer 0.pool.ntp.org -timeZone UTC -allowUsageAnalytics Yes -resourceGroupName <value>

param(
  [string] [Parameter(Mandatory=$True)] $licenseType,
  [string] $licensedBandwidth = $(if($licenseType -eq "PAYG") { Read-Host -prompt "licensedBandwidth"}),
  [string] $bigIqLicenseHost = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicenseHost"}),
  [string] $bigIqLicenseUsername = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicenseUsername"}),
  [string] $bigIqLicensePassword = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicensePassword"}),
  [string] $bigIqLicensePool = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicensePool"}),

  [string] [Parameter(Mandatory=$True)] $vmScaleSetMinCount,
  [string] [Parameter(Mandatory=$True)] $vmScaleSetMaxCount,
  [string] [Parameter(Mandatory=$True)] $autoScaleMetric,
  [string] [Parameter(Mandatory=$True)] $appInsights,
  [string] [Parameter(Mandatory=$True)] $calculatedBandwidth,
  [string] [Parameter(Mandatory=$True)] $scaleOutThreshold,
  [string] [Parameter(Mandatory=$True)] $scaleInThreshold,
  [string] [Parameter(Mandatory=$True)] $scaleTimeWindow,
  [string] [Parameter(Mandatory=$True)] $adminUsername,
  [string] [Parameter(Mandatory=$True)] $adminPassword,
  [string] [Parameter(Mandatory=$True)] $dnsLabel,
  [string] [Parameter(Mandatory=$True)] $instanceType,
  [string] [Parameter(Mandatory=$True)] $imageName,
  [string] [Parameter(Mandatory=$True)] $bigIpVersion,
  [string] [Parameter(Mandatory=$True)] $vnetName,
  [string] [Parameter(Mandatory=$True)] $vnetResourceGroupName,
  [string] [Parameter(Mandatory=$True)] $mgmtSubnetName,
  [string] [Parameter(Mandatory=$True)] $dnsMemberIpType,
  [string] [Parameter(Mandatory=$True)] $dnsMemberPort,
  [string] [Parameter(Mandatory=$True)] $dnsProviderHost,
  [string] [Parameter(Mandatory=$True)] $dnsProviderPort,
  [string] [Parameter(Mandatory=$True)] $dnsProviderUser,
  [string] [Parameter(Mandatory=$True)] $dnsProviderPassword,
  [string] [Parameter(Mandatory=$True)] $dnsProviderPool,
  [string] [Parameter(Mandatory=$True)] $dnsProviderDataCenter,
  [string] [Parameter(Mandatory=$True)] $tenantId,
  [string] [Parameter(Mandatory=$True)] $clientId,
  [string] [Parameter(Mandatory=$True)] $servicePrincipalSecret,
  [string] [Parameter(Mandatory=$True)] $notificationEmail,
  [string] [Parameter(Mandatory=$True)] $ntpServer,
  [string] [Parameter(Mandatory=$True)] $timeZone,
  [string] $restrictedSrcAddress = "*",
  $tagValues = '{"application": "APP", "cost": "COST", "environment": "ENV", "group": "GROUP", "owner": "OWNER"}',
  [string] [Parameter(Mandatory=$True)] $allowUsageAnalytics,
  [string] [Parameter(Mandatory=$True)] $resourceGroupName,
  [string] $region = "West US",
  [string] $templateFilePath = "azuredeploy.json",
  [string] $parametersFilePath = "azuredeploy.parameters.json"
)

Write-Host "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged." -foregroundcolor green
Start-Sleep -s 3

# Connect to Azure, right now it is only interactive login
try {
    Write-Host "Checking if already logged in!"
    Get-AzureRmSubscription | Out-Null
    Write-Host "Already logged in, continuing..."
    }
    catch {
      Write-Host "Not logged in, please login..."
      Login-AzureRmAccount
    }

# Create Resource Group for ARM Deployment
New-AzureRmResourceGroup -Name $resourceGroupName -Location "$region"

$pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force
$sps = ConvertTo-SecureString -String $servicePrincipalSecret -AsPlainText -Force
$dnsProviderPasswordSecure = ConvertTo-SecureString -String $dnsProviderPassword -AsPlainText -Force
(ConvertFrom-Json $tagValues).psobject.properties | ForEach -Begin {$tagValues=@{}} -process {$tagValues."$($_.Name)" = $_.Value}

# Create Arm Deployment
if ($licenseType -eq "PAYG") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\azuredeploy.json"; $parametersFilePath = ".\PAYG\azuredeploy.parameters.json" }
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -vmScaleSetMinCount $vmScaleSetMinCount -vmScaleSetMaxCount $vmScaleSetMaxCount -autoScaleMetric $autoScaleMetric -appInsights $appInsights -calculatedBandwidth $calculatedBandwidth -scaleOutThreshold $scaleOutThreshold -scaleInThreshold $scaleInThreshold -scaleTimeWindow $scaleTimeWindow -adminUsername $adminUsername -adminPassword $pwd -dnsLabel $dnsLabel -instanceType $instanceType -imageName $imageName -bigIpVersion $bigIpVersion -vnetName $vnetName -vnetResourceGroupName $vnetResourceGroupName -mgmtSubnetName $mgmtSubnetName -dnsMemberIpType $dnsMemberIpType -dnsMemberPort $dnsMemberPort -dnsProviderHost $dnsProviderHost -dnsProviderPort $dnsProviderPort -dnsProviderUser $dnsProviderUser -dnsProviderPassword $dnsProviderPasswordSecure -dnsProviderPool $dnsProviderPool -dnsProviderDataCenter $dnsProviderDataCenter -tenantId $tenantId -clientId $clientId -servicePrincipalSecret $sps -notificationEmail $notificationEmail -ntpServer $ntpServer -timeZone $timeZone -restrictedSrcAddress $restrictedSrcAddress -tagValues $tagValues -allowUsageAnalytics $allowUsageAnalytics  -licensedBandwidth "$licensedBandwidth"
} elseif ($licenseType -eq "BIGIQ") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BIGIQ\azuredeploy.json"; $parametersFilePath = ".\BIGIQ\azuredeploy.parameters.json" }
  $bigiq_pwd = ConvertTo-SecureString -String $bigIqLicensePassword -AsPlainText -Force
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -vmScaleSetMinCount $vmScaleSetMinCount -vmScaleSetMaxCount $vmScaleSetMaxCount -autoScaleMetric $autoScaleMetric -appInsights $appInsights -calculatedBandwidth $calculatedBandwidth -scaleOutThreshold $scaleOutThreshold -scaleInThreshold $scaleInThreshold -scaleTimeWindow $scaleTimeWindow -adminUsername $adminUsername -adminPassword $pwd -dnsLabel $dnsLabel -instanceType $instanceType -imageName $imageName -bigIpVersion $bigIpVersion -vnetName $vnetName -vnetResourceGroupName $vnetResourceGroupName -mgmtSubnetName $mgmtSubnetName -dnsMemberIpType $dnsMemberIpType -dnsMemberPort $dnsMemberPort -dnsProviderHost $dnsProviderHost -dnsProviderPort $dnsProviderPort -dnsProviderUser $dnsProviderUser -dnsProviderPassword $dnsProviderPasswordSecure -dnsProviderPool $dnsProviderPool -dnsProviderDataCenter $dnsProviderDataCenter -tenantId $tenantId -clientId $clientId -servicePrincipalSecret $sps -notificationEmail $notificationEmail -ntpServer $ntpServer -timeZone $timeZone -restrictedSrcAddress $restrictedSrcAddress -tagValues $tagValues -allowUsageAnalytics $allowUsageAnalytics  -bigIqLicenseHost "$bigIqLicenseHost" -bigIqLicenseUsername "$bigIqLicenseUsername" -bigIqLicensePassword $bigiq_pwd -bigIqLicensePool "$bigIqLicensePool"
} else {
  Write-Error -Message "Please select a valid license type of PAYG or BIGIQ."
}

# Print Output of Deployment to Console
$deployment