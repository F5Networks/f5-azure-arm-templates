## Script parameters being asked for below match to parameters in the azuredeploy.json file, otherwise pointing to the ##
## azuredeploy.parameters.json file for values to use.  Some options below are mandatory, some (such as region) can    ##
## be supplied inline when running this script but if they aren't then the default will be used as specified below.    ##
## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth 200m -adminUsername azureuser -adminPassword <value> -dnsLabel <value> -instanceName f5vm01 -instanceType Standard_DS2_v2 -imageName Good -bigIpVersion 13.1.0200 -numberOfExternalIps 1 -vnetAddressPrefix 10.0 -ntpServer 0.pool.ntp.org -timeZone UTC -allowUsageAnalytics Yes -resourceGroupName <value>

param(
  [string] [Parameter(Mandatory=$True)] $licenseType,
  [string] $licensedBandwidth = $(if($licenseType -eq "PAYG") { Read-Host -prompt "licensedBandwidth"}),
  [string] $licenseKey1 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey1"}),
  [string] $bigIqAddress = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqAddress"}),
  [string] $bigIqUsername = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqUsername"}),
  [string] $bigIqPassword = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqPassword"}),
  [string] $bigIqLicensePoolName = $(if($licenseType -eq "BIGIQ") { Read-Host -prompt "bigIqLicensePoolName"}),

  [string] [Parameter(Mandatory=$True)] $adminUsername,
  [string] [Parameter(Mandatory=$True)] $adminPassword,
  [string] [Parameter(Mandatory=$True)] $dnsLabel,
  [string] [Parameter(Mandatory=$True)] $instanceName,
  [string] [Parameter(Mandatory=$True)] $instanceType,
  [string] [Parameter(Mandatory=$True)] $imageName,
  [string] [Parameter(Mandatory=$True)] $bigIpVersion,
  [string] [Parameter(Mandatory=$True)] $numberOfExternalIps,
  [string] [Parameter(Mandatory=$True)] $vnetAddressPrefix,
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
(ConvertFrom-Json $tagValues).psobject.properties | ForEach -Begin {$tagValues=@{}} -process {$tagValues."$($_.Name)" = $_.Value}

# Create Arm Deployment
if ($licenseType -eq "BYOL") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BYOL\azuredeploy.json"; $parametersFilePath = ".\BYOL\azuredeploy.parameters.json" }
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername $adminUsername -adminPassword $pwd -dnsLabel $dnsLabel -instanceName $instanceName -instanceType $instanceType -imageName $imageName -bigIpVersion $bigIpVersion -numberOfExternalIps $numberOfExternalIps -vnetAddressPrefix $vnetAddressPrefix -ntpServer $ntpServer -timeZone $timeZone -restrictedSrcAddress $restrictedSrcAddress -tagValues $tagValues -allowUsageAnalytics $allowUsageAnalytics  -licenseKey1 "$licenseKey1"
} elseif ($licenseType -eq "PAYG") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\azuredeploy.json"; $parametersFilePath = ".\PAYG\azuredeploy.parameters.json" }
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername $adminUsername -adminPassword $pwd -dnsLabel $dnsLabel -instanceName $instanceName -instanceType $instanceType -imageName $imageName -bigIpVersion $bigIpVersion -numberOfExternalIps $numberOfExternalIps -vnetAddressPrefix $vnetAddressPrefix -ntpServer $ntpServer -timeZone $timeZone -restrictedSrcAddress $restrictedSrcAddress -tagValues $tagValues -allowUsageAnalytics $allowUsageAnalytics  -licensedBandwidth "$licensedBandwidth"
} elseif ($licenseType -eq "BIGIQ") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BIGIQ\azuredeploy.json"; $parametersFilePath = ".\BIGIQ\azuredeploy.parameters.json" }
  $bigiq_pwd = ConvertTo-SecureString -String $bigIqPassword -AsPlainText -Force
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername $adminUsername -adminPassword $pwd -dnsLabel $dnsLabel -instanceName $instanceName -instanceType $instanceType -imageName $imageName -bigIpVersion $bigIpVersion -numberOfExternalIps $numberOfExternalIps -vnetAddressPrefix $vnetAddressPrefix -ntpServer $ntpServer -timeZone $timeZone -restrictedSrcAddress $restrictedSrcAddress -tagValues $tagValues -allowUsageAnalytics $allowUsageAnalytics  -bigIqAddress "$bigIqAddress" -bigIqUsername "$bigIqUsername" -bigIqPassword $bigiq_pwd -bigIqLicensePoolName "$bigIqLicensePoolName"
} else {
  Write-Error -Message "Please select a valid license type of PAYG, BYOL or BIGIQ."
}

# Print Output of Deployment to Console
$deployment