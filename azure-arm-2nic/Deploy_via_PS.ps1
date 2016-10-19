#Start

param(
  [Parameter(Mandatory=$True)]
  [string]
  $deploymentName,

  [Parameter(Mandatory=$True)]
  [string]
  $vmName,

  [Parameter(Mandatory=$True)]
  [string]
  $licenseToken,

  [string]
  $f5pwd = "P4ssw0rd!azure",

  [string]
  $region = "West US",

  [string]
  $templateFilePath = "azuredeploy.json",

  [string]
  $parametersFilePath = "azuredeploy.parameters.json"
)


Write-Host Logging in...
Add-AzureRmAccount


New-AzureRmResourceGroup -Name $deploymentName -Location "$region"
Write-Host Resource Group $deploymentName created in $region


$pwd = ConvertTo-SecureString -String $f5pwd -AsPlainText -Force
$deployment = New-AzureRmResourceGroupDeployment -Name $deploymentName -ResourceGroupName $deploymentName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -adminPassword $pwd -dnsLabelPrefix $deploymentName -vmName "$vmName" -licenseToken1 "$licensetoken"

$deployment

