# Params below match to parameteres in the azuredeploy.json that are gen-unique, otherwsie pointing to
# the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
# can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
# Example Command: .\Deploy_via_PS.ps1 -solutionDeploymentName deploynamestring -numberOfInstances 2 -adminUsername azureuser -adminPassword password
# -dnsLabel dnslabestring -licenseKey1 XXXX-XXXX-XXXX-XXXX -licenseKey2 XXXX-XXXX-XXXX-XXXX -applicationProtocols https -applicationAddress web01.discovery.com -applicationPort OPTIONAL
# -applicationSecurePort 443 -vaultName keyvault -vaultResourceGroup keyvaultresourcegroup -secretUrl https://secreturl -certThumbprint XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX -templateFilePath .\templates\https\azuredeploy.json
# -resourceGroupName rgname -parametersFilePath .\templates\https\azuredeploy.parameters.json

param(
  [Parameter(Mandatory=$True)]
  [string]
  $solutionDeploymentName,

  [Parameter(Mandatory=$True)]
  [ValidateSet("2")]
  [string]
  $numberOfInstances,

  [string]
  $instanceType = "Standard_D2_v2",

  [string]
  $imageName = "Best",

  [Parameter(Mandatory=$True)]
  [string]
  $adminUsername,

  [Parameter(Mandatory=$True)]
  [string]
  $adminPassword,

  [Parameter(Mandatory=$True)]
  [string]
  $dnsLabel,

  [Parameter(Mandatory=$True)]
  [string]
  $licenseKey1,

  [Parameter(Mandatory=$True)]
  [string]
  $licenseKey2,

  [Parameter(Mandatory=$True)]
  [ValidateSet("http","https","https-offload")]
  [string]
  $applicationProtocols,

  [Parameter(Mandatory=$True)]
  [string]
  $applicationAddress,

  [string]
  $applicationPort = $(if($applicationProtocols -ne "https") { Read-Host -prompt "applicationPort"}),

  [string]
  $applicationSecurePort = $(if($applicationProtocols -ne "http") { Read-Host -prompt "applicationSecurePort"}),

  [string]
  $vaultName = $(if($applicationProtocols -ne "http") { Read-Host -prompt "vaultName"}),

  [string]
  $vaultResourceGroup = $(if($applicationProtocols -ne "http") { Read-Host -prompt "vaultResourceGroup"}),

  [string]
  $secretUrl = $(if($applicationProtocols -ne "http") { Read-Host -prompt "secretUrl"}),

  [string]
  $certThumbprint = $(if($applicationProtocols -ne "http") { Read-Host -prompt "certThumbprint"}),

  [string]
  $restrictedSrcAddress  = "*",

  [Parameter(Mandatory=$True)]
  [string]
  $resourceGroupName,

  [string]
  $region = "West US",

  [string]
  $templateFilePath = "azuredeploy.json",

  [string]
  $parametersFilePath = "azuredeploy.parameters.json"
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

# Create Resource Group for ARM Deployment
New-AzureRmResourceGroup -Name $resourceGroupName -Location "$region"

# Create Arm Deployment
$pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force

# Need to change parameters based on mode, also defaulting relative path if not specifically included in script execution
if ($applicationProtocols -eq "http") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\http\azuredeploy.json"; $parametersFilePath = ".\http\azuredeploy.parameters.json" }
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -solutionDeploymentName "$solutionDeploymentName" -numberOfInstances "$numberOfInstances" -instanceType "$instanceType" -imageName "$imageName" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2" -applicationProtocols "$applicationProtocols" -applicationAddress "$applicationAddress" -restrictedSrcAddress "$restrictedSrcAddress"
} elseif ($applicationProtocols -eq "https-offload") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\https-offload\azuredeploy.json"; $parametersFilePath = ".\https-offload\azuredeploy.parameters.json" }
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -solutionDeploymentName "$solutionDeploymentName" -numberOfInstances "$numberOfInstances" -instanceType "$instanceType" -imageName "$imageName" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2" -applicationProtocols "$applicationProtocols" -applicationAddress "$applicationAddress" -applicationSecurePort "$applicationSecurePort" -vaultName "$vaultName" -vaultResourceGroup "$vaultResourceGroup" -secretUrl "$secretUrl" -certThumbprint "$certThumbprint" -restrictedSrcAddress "$restrictedSrcAddress"
} elseif ($applicationProtocols -eq "https") {
  if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\https\azuredeploy.json"; $parametersFilePath = ".\https\azuredeploy.parameters.json" }
  $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -solutionDeploymentName "$solutionDeploymentName" -numberOfInstances "$numberOfInstances" -instanceType "$instanceType" -imageName "$imageName" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2" -applicationProtocols "$applicationProtocols" -applicationAddress "$applicationAddress" -applicationSecurePort "$applicationSecurePort" -vaultName "$vaultName" -vaultResourceGroup "$vaultResourceGroup" -secretUrl "$secretUrl" -certThumbprint "$certThumbprint" -restrictedSrcAddress "$restrictedSrcAddress"
} else {
  Write-Host "Uh oh, shouldn't get here as validating applicationProtocols variable in params!"
  exit
}

# Print Output of Deployment to Console
$deployment