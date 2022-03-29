## Script parameters being asked for below match to parameters in the azuredeploy.json file, otherwise pointing to the ##
## azuredeploy.parameters.json file for values to use.  Some options below are mandatory, some (such as region) can    ##
## be supplied inline when running this script but if they aren't then the default will be used as specified below.    ##
## Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -authenticationType password -adminPasswordOrKey <value> -dnsLabel <value> -instanceType Standard_D2s_v3 -imageName AllTwoBootLocations -bigIqAddress <value> -bigIqUsername <value> -bigIqPassword <value> -bigIqLicensePoolName <value> -bigIqLicenseSkuKeyword1 OPTIONAL -bigIqLicenseUnitOfMeasure OPTIONAL -bigIpVersion 16.1.201000 -bigIpModules asm:nominal -vnetName <value> -vnetResourceGroupName <value> -mgmtSubnetName <value> -declarationUrl NOT_SPECIFIED -ntpServer 0.pool.ntp.org -timeZone UTC -customImageUrn OPTIONAL -customImage OPTIONAL -allowUsageAnalytics Yes -allowPhoneHome Yes -vmScaleSetMinCount 2 -vmScaleSetMaxCount 4 -appInsights CREATE_NEW -scaleOutCpuThreshold 80 -scaleInCpuThreshold 20 -scaleOutThroughputThreshold 20000000 -scaleInThroughputThreshold 10000000 -scaleOutTimeWindow 10 -scaleInTimeWindow 10 -notificationEmail OPTIONAL -mgmtNsgName OPTIONAL -externalLoadBalancerName OPTIONAL -internalLoadBalancerName OPTIONAL -useAvailabilityZones Yes -autoscaleTimeout 10 -provisionPublicIP Yes -applicationProtocols http-https -applicationAddress <value> -applicationPort 80 -applicationSecurePort 443 -sslCert NOT_SPECIFIED -sslPswd NOT_SPECIFIED -applicationType Linux -blockingLevel medium -customPolicy NOT_SPECIFIED -tenantId <value> -clientId <value> -servicePrincipalSecret <value> -resourceGroupName <value>

param(

  [string] [Parameter(Mandatory=$True)] $adminUsername,
  [string] [Parameter(Mandatory=$True)] $authenticationType,
  [string] [Parameter(Mandatory=$True)] $adminPasswordOrKey,
  [string] [Parameter(Mandatory=$True)] $dnsLabel,
  [string] [Parameter(Mandatory=$True)] $instanceType,
  [string] [Parameter(Mandatory=$True)] $imageName,
  [string] [Parameter(Mandatory=$True)] $bigIqAddress,
  [string] [Parameter(Mandatory=$True)] $bigIqUsername,
  [string] [Parameter(Mandatory=$True)] $bigIqPassword,
  [string] [Parameter(Mandatory=$True)] $bigIqLicensePoolName,
  [string] [Parameter(Mandatory=$True)] $bigIqLicenseSkuKeyword1,
  [string] [Parameter(Mandatory=$True)] $bigIqLicenseUnitOfMeasure,
  [string] [Parameter(Mandatory=$True)] $bigIpVersion,
  [string] [Parameter(Mandatory=$True)] $bigIpModules,
  [string] [Parameter(Mandatory=$True)] $vnetName,
  [string] [Parameter(Mandatory=$True)] $vnetResourceGroupName,
  [string] [Parameter(Mandatory=$True)] $mgmtSubnetName,
  [string] [Parameter(Mandatory=$True)] $declarationUrl,
  [string] [Parameter(Mandatory=$True)] $ntpServer,
  [string] [Parameter(Mandatory=$True)] $timeZone,
  [string] [Parameter(Mandatory=$True)] $customImageUrn,
  [string] [Parameter(Mandatory=$True)] $customImage,
  [string] $restrictedSrcAddress = "None",
  $tagValues = '{"application": "APP", "cost": "COST", "environment": "ENV", "group": "GROUP", "owner": "OWNER"}',
  [string] [Parameter(Mandatory=$True)] $allowUsageAnalytics,
  [string] [Parameter(Mandatory=$True)] $allowPhoneHome,
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
  [string] [Parameter(Mandatory=$True)] $mgmtNsgName,
  [string] [Parameter(Mandatory=$True)] $externalLoadBalancerName,
  [string] [Parameter(Mandatory=$True)] $internalLoadBalancerName,
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
$bigIqPasswordSecure = ConvertTo-SecureString -String $bigIqPassword -AsPlainText -Force
$sslPswdSecure = ConvertTo-SecureString -String $sslPswd -AsPlainText -Force
$servicePrincipalSecretSecure = ConvertTo-SecureString -String $servicePrincipalSecret -AsPlainText -Force

(ConvertFrom-Json $tagValues).psobject.properties | ForEach -Begin {$tagValues=@{}} -process {$tagValues."$($_.Name)" = $_.Value}

# Create Arm Deployment
$deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername $adminUsername -authenticationType $authenticationType -adminPasswordOrKey $adminPasswordOrKeySecure -dnsLabel $dnsLabel -instanceType $instanceType -imageName $imageName -bigIqAddress $bigIqAddress -bigIqUsername $bigIqUsername -bigIqPassword $bigIqPasswordSecure -bigIqLicensePoolName $bigIqLicensePoolName -bigIqLicenseSkuKeyword1 $bigIqLicenseSkuKeyword1 -bigIqLicenseUnitOfMeasure $bigIqLicenseUnitOfMeasure -bigIpVersion $bigIpVersion -bigIpModules $bigIpModules -vnetName $vnetName -vnetResourceGroupName $vnetResourceGroupName -mgmtSubnetName $mgmtSubnetName -declarationUrl $declarationUrl -ntpServer $ntpServer -timeZone $timeZone -customImageUrn $customImageUrn -customImage $customImage -restrictedSrcAddress $restrictedSrcAddress -tagValues $tagValues -allowUsageAnalytics $allowUsageAnalytics -allowPhoneHome $allowPhoneHome -vmScaleSetMinCount $vmScaleSetMinCount -vmScaleSetMaxCount $vmScaleSetMaxCount -appInsights $appInsights -scaleOutCpuThreshold $scaleOutCpuThreshold -scaleInCpuThreshold $scaleInCpuThreshold -scaleOutThroughputThreshold $scaleOutThroughputThreshold -scaleInThroughputThreshold $scaleInThroughputThreshold -scaleOutTimeWindow $scaleOutTimeWindow -scaleInTimeWindow $scaleInTimeWindow -notificationEmail $notificationEmail -mgmtNsgName $mgmtNsgName -externalLoadBalancerName $externalLoadBalancerName -internalLoadBalancerName $internalLoadBalancerName -useAvailabilityZones $useAvailabilityZones -autoscaleTimeout $autoscaleTimeout -provisionPublicIP $provisionPublicIP -applicationProtocols $applicationProtocols -applicationAddress $applicationAddress -applicationPort $applicationPort -applicationSecurePort $applicationSecurePort -sslCert $sslCert -sslPswd $sslPswdSecure -applicationType $applicationType -blockingLevel $blockingLevel -customPolicy $customPolicy -tenantId $tenantId -clientId $clientId -servicePrincipalSecret $servicePrincipalSecretSecure 

# Print Output of Deployment to Console
$deployment