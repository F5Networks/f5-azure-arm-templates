# Params below match to parameteres in the azuredeploy.json that are gen-unique, otherwsie pointing to
# the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
# can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
# Example Command: .\Deploy_via_PS.ps1 -dnsLabelPrefix f52nicauto01 -vmName f52nic -licenseToken XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -EmailTo user@f5.com

param(
  [Parameter(Mandatory=$True)]
  [string]
  $dnsLabelPrefix,

  [Parameter(Mandatory=$True)]
  [string]
  $vmName,

  [Parameter(Mandatory=$True)]
  [string]
  $licenseToken,

  [Parameter(Mandatory=$True)]
  [string]
  $EmailTo,

  [string]
  $adminPassword = "P4ssw0rd!azure",

  [string]
  $deploymentName = $dnsLabelPrefix,

  [string]
  $region = "West US",

  [string]
  $templateFilePath = "azuredeploy.json",

  [string]
  $parametersFilePath = "azuredeploy.parameters.json"
)

$timestamp = get-date -format g
Write-Host "[$timestamp] Starting Script "

# Connect to Azure, right now it is only interactive login
Add-AzureRmAccount

# Create Resource Group for ARM Deployment
New-AzureRmResourceGroup -Name $deploymentName -Location "$region"

# Create Arm Deployment
$pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force
$deployment = New-AzureRmResourceGroupDeployment -Name $deploymentName -ResourceGroupName $deploymentName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -adminPassword $pwd -dnsLabelPrefix $dnsLabelPrefix -vmName "$vmName" -licenseToken1 "$licensetoken"

# Print Output of Deployment to Console
$deployment

# Send Email letting deployer know if successful or not, placeholder utilizing arbitrary gmail account
$status = $deployment.ProvisioningState
$type = "f5-arm-2nic"

$timestamp = get-date -format g
$EmailFrom = "discoveryeselabsauto@gmail.com"
$Subject = "[$timestamp] Notification for Azure Build Complete[$status]"
$Body = "This is a notification for automated azure builds.. `n `n Testing template of type: $type "
$SMTPServer = "smtp.gmail.com"
$SMTPClient = New-Object Net.Mail.SmtpClient($SmtpServer, 587)
$SMTPClient.EnableSsl = $true
$SMTPClient.Credentials = New-Object System.Net.NetworkCredential("discoveryeselabsauto", "P4ssw0rd!azure");
$SMTPClient.Send($EmailFrom, $EmailTo, $Subject, $Body)

Write-Host "Email Has been Sent to $EmailTo at $timestamp"
Write-Host "[$timestamp] Ending Script"
