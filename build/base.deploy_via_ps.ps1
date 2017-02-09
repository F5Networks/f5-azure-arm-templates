# Params below match to parameters in the azuredeploy.json that are gen-unique, otherwise pointing to
# the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
# can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
# Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -adminPassword yourpassword -dnsLabel f5dnslabel01 -instanceName f5vm01 -licenseType BYOL -licenseKey1 XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -resourceGroupName f5rg01

param(
<DYNAMIC_PARAMETERS>

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
<DEPLOYMENT_CREATE>

# Print Output of Deployment to Console
$deployment