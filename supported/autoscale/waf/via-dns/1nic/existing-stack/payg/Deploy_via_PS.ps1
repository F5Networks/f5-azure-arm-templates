## Script parameters being asked for below match to parameters in the azuredeploy.json file, otherwise pointing to the ##
## azuredeploy.parameters.json file for values to use.  Some options below are mandatory, some (such as region) can    ##
## be supplied inline when running this script but if they aren't then the default will be used as specified below.    ##
## Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -authenticationType password -adminPasswordOrKey <value> -dnsLabel <value> -instanceType Standard_DS2_v2 -imageName Best1Gbps -bigIpVersion 15.0.100000 -bigIpModules asm:nominal -vnetName <value> -vnetResourceGroupName <value> -mgmtSubnetName <value> -declarationUrl NOT_SPECIFIED -ntpServer 0.pool.ntp.org -timeZone UTC -customImage OPTIONAL -allowUsageAnalytics Yes -vmScaleSetMinCount 2 -vmScaleSetMaxCount 4 -appInsights CREATE_NEW -scaleOutCpuThreshold 80 -scaleInCpuThreshold 20 -scaleOutThroughputThreshold 20000000 -scaleInThroughputThreshold 10000000 -scaleOutTimeWindow 10 -scaleInTimeWindow 10 -notificationEmail OPTIONAL -useAvailabilityZones Yes -autoscaleTimeout 10 -provisionPublicIP Yes -applicationProtocols http-https -applicationAddress <value> -applicationPort 80 -applicationSecurePort 443 -sslCert NOT_SPECIFIED -sslPswd NOT_SPECIFIED -applicationType Linux -blockingLevel medium -customPolicy NOT_SPECIFIED -dnsMemberIpType private -dnsMemberPort 80 -dnsProviderHost <value> -dnsProviderPort 443 -dnsProviderUser <value> -dnsProviderPassword <value> -dnsProviderPool autoscale_pool -dnsProviderDataCenter azure_datacenter -tenantId <value> -clientId <value> -servicePrincipalSecret <value> -resourceGroupName <value>

param(

  [string] [Parameter(Mandatory=$True)] $adminUsername,
  [string] [Parameter(Mandatory=$True)] $authenticationType,
  [string] [Parameter(Mandatory=$True)] $adminPasswordOrKey,
  [string] [Parameter(Mandatory=$True)] $dnsLabel,
  [string] [Parameter(Mandatory=$True)] $instanceType,
  [string] [Parameter(Mandatory=$True)] $imageName,
  [string] [Parameter(Mandatory=$True)] $bigIpVersion,
  [string] [Parameter(Mandatory=$True)] $bigIpModules,
  [string] [Parameter(Mandatory=$True)] $vnetName,
  [string] [Parameter(Mandatory=$True)] $vnetResourceGroupName,
  [string] [Parameter(Mandatory=$True)] $mgmtSubnetName,
  [string] [Parameter(Mandatory=$True)] $declarationUrl,
  [string] [Parameter(Mandatory=$True)] $ntpServer,
  [string] [Parameter(Mandatory=$True)] $timeZone,
  [string] [Parameter(Mandatory=$True)] $customImage,
  [string] $restrictedSrcAddress = "*",
  $tagValues = '{"application": "APP", "cost": "COST", "environment": "ENV", "group": "GROUP", "owner": "OWNER"}',
  [string] [Parameter(Mandatory=$True)] $allowUsageAnalytics,
  [string] [Parameter(Mandatory=$True)] $vmScaleSetMinCount,
  [string] [Parameter(Mandatory=$True)] $vmScaleSetMaxCount,
  [string] [Parameter(Mandatory=$True)] $appInsights,
  [string] [Parameter(Mandatory=$True)] $scaleOutCpuThreshold,
  [string] [Parameter(Mandatory=$True)] $scaleInCpuThreshold,
  [string] [Parameter(Mandatory=$True)] $scaleOutThroughputThreshold,
  [string] [Parameter(Mandatory=$True)] $scaleInThroughputThreshold,
  [string] [Parameter(Mandatory=$True)] $scaleOutTimeWindow,
  [string] [Parameter(Mandatory=$True)] $scaleInTimeWindow,
  [string] [Parameter(Mandatory=$True)] $notificationEmail,
  [string] [Parameter(Mandatory=$True)] $useAvailabilityZones,
  [string] [Parameter(Mandatory=$True)] $autoscaleTimeout,
  [string] [Parameter(Mandatory=$True)] $provisionPublicIP,
  [string] [Parameter(Mandatory=$True)] $applicationProtocols,
  [string] [Parameter(Mandatory=$True)] $applicationAddress,
  [string] [Parameter(Mandatory=$True)] $applicationPort,
  [string] [Parameter(Mandatory=$True)] $applicationSecurePort,
  [string] [Parameter(Mandatory=$True)] $sslCert,
  [string] [Parameter(Mandatory=$True)] $sslPswd,
  [string] [Parameter(Mandatory=$True)] $applicationType,
  [string] [Parameter(Mandatory=$True)] $blockingLevel,
  [string] [Parameter(Mandatory=$True)] $customPolicy,
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
$sslPswdSecure = ConvertTo-SecureString -String $sslPswd -AsPlainText -Force
$dnsProviderPasswordSecure = ConvertTo-SecureString -String $dnsProviderPassword -AsPlainText -Force
$servicePrincipalSecretSecure = ConvertTo-SecureString -String $servicePrincipalSecret -AsPlainText -Force

(ConvertFrom-Json $tagValues).psobject.properties | ForEach -Begin {$tagValues=@{}} -process {$tagValues."$($_.Name)" = $_.Value}

# Create Arm Deployment
$deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername $adminUsername -authenticationType $authenticationType -adminPasswordOrKey $adminPasswordOrKeySecure -dnsLabel $dnsLabel -instanceType $instanceType -imageName $imageName -bigIpVersion $bigIpVersion -bigIpModules $bigIpModules -vnetName $vnetName -vnetResourceGroupName $vnetResourceGroupName -mgmtSubnetName $mgmtSubnetName -declarationUrl $declarationUrl -ntpServer $ntpServer -timeZone $timeZone -customImage $customImage -restrictedSrcAddress $restrictedSrcAddress -tagValues $tagValues -allowUsageAnalytics $allowUsageAnalytics -vmScaleSetMinCount $vmScaleSetMinCount -vmScaleSetMaxCount $vmScaleSetMaxCount -appInsights $appInsights -scaleOutCpuThreshold $scaleOutCpuThreshold -scaleInCpuThreshold $scaleInCpuThreshold -scaleOutThroughputThreshold $scaleOutThroughputThreshold -scaleInThroughputThreshold $scaleInThroughputThreshold -scaleOutTimeWindow $scaleOutTimeWindow -scaleInTimeWindow $scaleInTimeWindow -notificationEmail $notificationEmail -useAvailabilityZones $useAvailabilityZones -autoscaleTimeout $autoscaleTimeout -provisionPublicIP $provisionPublicIP -applicationProtocols $applicationProtocols -applicationAddress $applicationAddress -applicationPort $applicationPort -applicationSecurePort $applicationSecurePort -sslCert $sslCert -sslPswd $sslPswdSecure -applicationType $applicationType -blockingLevel $blockingLevel -customPolicy $customPolicy -dnsMemberIpType $dnsMemberIpType -dnsMemberPort $dnsMemberPort -dnsProviderHost $dnsProviderHost -dnsProviderPort $dnsProviderPort -dnsProviderUser $dnsProviderUser -dnsProviderPassword $dnsProviderPasswordSecure -dnsProviderPool $dnsProviderPool -dnsProviderDataCenter $dnsProviderDataCenter -tenantId $tenantId -clientId $clientId -servicePrincipalSecret $servicePrincipalSecretSecure 

# Print Output of Deployment to Console
$deployment