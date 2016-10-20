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

$timestamp = get-date -format g
Write-Host "[$timestamp] Starting Script "
Add-AzureRmAccount


New-AzureRmResourceGroup -Name $deploymentName -Location "$region"
Write-Host Resource Group $deploymentName created in $region


$pwd = ConvertTo-SecureString -String $f5pwd -AsPlainText -Force
$deployment = New-AzureRmResourceGroupDeployment -Name $deploymentName -ResourceGroupName $deploymentName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -adminPassword $pwd -dnsLabelPrefix $deploymentName -vmName "$vmName" -licenseToken1 "$licensetoken"

$deployment


#Send Email letting know if successfull or not
$status = $deployment.ProvisioningState
$type = "f5-arm-2nic"

$timestamp = get-date -format g
$EmailFrom = "discoveryeselabsauto@gmail.com"
$EmailTo = "j.sevedge@f5.com" 
$Subject = "[$timestamp] Notification for Azure Build Complete[$status]" 
$Body = "This is a notification for automated azure builds.. `n `n Testing template of type: $type " 
$SMTPServer = "smtp.gmail.com" 
$SMTPClient = New-Object Net.Mail.SmtpClient($SmtpServer, 587) 
$SMTPClient.EnableSsl = $true 
$SMTPClient.Credentials = New-Object System.Net.NetworkCredential("discoveryeselabsauto", "P4ssw0rd!azure"); 
$SMTPClient.Send($EmailFrom, $EmailTo, $Subject, $Body)

Write-Host "Email Has been Sent to $EmailTo at $timestamp"

Write-Host "[$timestamp] Ending Script"

