# Params below match to parameteres in the azuredeploy.json that are gen-unique, otherwsie pointing to
# the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
# can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
# Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -adminPassword yourpassword -dnsLabelPrefix f52nicdeploy01 -vmName f52nic -licenseToken XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -resourceGroupName f52nicdeploy01 -EmailTo user@f5.com

param(
  [Parameter(Mandatory=$True)]
  [string]
  $adminUsername,

  [Parameter(Mandatory=$True)]
  [string]
  $adminPassword,

  [Parameter(Mandatory=$True)]
  [string]
  $dnsLabelPrefix,

  [Parameter(Mandatory=$True)]
  [string]
  $vmName,

  [string]
  $vmSize = "Standard_D2_v2",

  [Parameter(Mandatory=$True)]
  [string]
  $licenseToken,

  [Parameter(Mandatory=$True)]
  [string]
  $resourceGroupName,

  [string]
  $region = "West US",

  [string]
  $templateFilePath = "azuredeploy.json",

  [string]
  $parametersFilePath = "azuredeploy.parameters.json",

  [Parameter(Mandatory=$True)]
  [string]
  $EmailTo
)

# Connect to Azure, right now it is only interactive login
Login-AzureRmAccount

# Create Resource Group for ARM Deployment
New-AzureRmResourceGroup -Name $resourceGroupName -Location "$region"

# Create Arm Deployment
$pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force
$deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabelPrefix "$dnsLabelPrefix" -vmName "$vmName" -vmSize "$vmSize" -licenseToken1 "$licensetoken"

# Print Output of Deployment to Console
$deployment



#### Internal Addition for F5 developer deployments
# Send Email letting deployer know if successful or not, placeholder utilizing arbitrary gmail account for sending from
$status = $deployment.ProvisioningState
$type = "f5-arm-2nic"

$EmailFrom = "discoveryeselabsauto@gmail.com"
$Subject = "[$(get-date -format g)] Notification for Azure Build Complete[$status]"
$Body = "This is a notification for automated azure builds.. `n `n Testing template of type: $type "
$SMTPServer = "smtp.gmail.com"
$SMTPClient = New-Object Net.Mail.SmtpClient($SmtpServer, 587)
$SMTPClient.EnableSsl = $true
$SMTPClient.Credentials = New-Object System.Net.NetworkCredential("discoveryeselabsauto", "P4ssw0rd!azure");
$SMTPClient.Send($EmailFrom, $EmailTo, $Subject, $Body)
#### End Internal Addition