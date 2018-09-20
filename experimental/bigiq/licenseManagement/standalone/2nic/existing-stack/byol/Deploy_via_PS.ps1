## Script parameters being asked for below match to parameters in the azuredeploy.json file, otherwise pointing to the ##
## azuredeploy.parameters.json file for values to use.  Some options below are mandatory, some (such as region) can    ##
## be supplied inline when running this script but if they aren't then the default will be used as specified below.    ##
## Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -authenticationType password -adminPasswordOrKey <value> -dnsLabel <value> -instanceName f5vm01 -instanceType Standard_DS2_v2 -bigIqVersion latest -bigIqLicenseKey1 <value> -licensePoolKeys <value> --regPoolKeys <value> -numberOfExternalIps 1 -vnetName <value> -vnetResourceGroupName <value> -mgmtSubnetName <value> -mgmtIpAddress <value> -externalSubnetName <value> -externalIpAddressRangeStart <value> -avSetChoice CREATE_NEW -ntpServer 0.pool.ntp.org -timeZone UTC -customImage OPTIONAL -allowUsageAnalytics Yes -resourceGroupName <value>

param(

  [string] [Parameter(Mandatory=$True)] $adminUsername,
  [string] [Parameter(Mandatory=$True)] $authenticationType,
  [string] [Parameter(Mandatory=$True)] $adminPasswordOrKey,
  [string] [Parameter(Mandatory=$True)] $dnsLabel,
  [string] [Parameter(Mandatory=$True)] $instanceName,
  [string] [Parameter(Mandatory=$True)] $instanceType,
  [string] [Parameter(Mandatory=$True)] $licensePoolKeys,
  [string] [Parameter(Mandatory=$True)] $regPoolKeys,
  [string] [Parameter(Mandatory=$True)] $bigIqVersion,
  [string] [Parameter(Mandatory=$True)] $bigIqLicenseKey1,
  [string] [Parameter(Mandatory=$True)] $numberOfExternalIps,
  [string] [Parameter(Mandatory=$True)] $vnetName,
  [string] [Parameter(Mandatory=$True)] $vnetResourceGroupName,
  [string] [Parameter(Mandatory=$True)] $mgmtSubnetName,
  [string] [Parameter(Mandatory=$True)] $mgmtIpAddress,
  [string] [Parameter(Mandatory=$True)] $internalSubnetName,
  [string] [Parameter(Mandatory=$True)] $internalIpAddressRangeStart,
  [string] [Parameter(Mandatory=$True)] $restrictedSrcAddress,
  [string] [Parameter(Mandatory=$True)] $restrictedSrcAddressApp,
  [string] [Parameter(Mandatory=$True)] $avSetChoice,
  [string] [Parameter(Mandatory=$True)] $ntpServer,
  [string] [Parameter(Mandatory=$True)] $timeZone,
  [string] [Parameter(Mandatory=$True)] $customImage,
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

$adminPasswordOrKeySecure = ConvertTo-SecureString -String $adminPasswordOrKey -AsPlainText -Force

(ConvertFrom-Json $tagValues).psobject.properties | ForEach -Begin {$tagValues=@{}} -process {$tagValues."$($_.Name)" = $_.Value}

# Create Arm Deployment
$deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername $adminUsername -authenticationType $authenticationType -adminPasswordOrKey $adminPasswordOrKeySecure -dnsLabel $dnsLabel -instanceName $instanceName -instanceType $instanceType -bigIqVersion $bigIqVersion -bigIqlicenseKey1 $bigIqLicenseKey1 -regPoolKeys $regPoolKeys -licensePoolKeys $licensePoolKeys -numberOfExternalIps $numberOfExternalIps -vnetName $vnetName -vnetResourceGroupName $vnetResourceGroupName -mgmtSubnetName $mgmtSubnetName -mgmtIpAddress $mgmtIpAddress -internalSubnetName $internalSubnetName -internalIpAddressRangeStart $internalIpAddressRangeStart -avSetChoice $avSetChoice -ntpServer $ntpServer -timeZone $timeZone -customImage $customImage -restrictedSrcAddress $restrictedSrcAddress -restrictedSrcAddressApp $restrictedSrcAddressApp -tagValues $tagValues -allowUsageAnalytics $allowUsageAnalytics 

# Print Output of Deployment to Console
$deployment