# Params below match to parameteres in the azuredeploy.json that are gen-unique, otherwsie pointing to
# the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
# can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
# Example Command: .\Deploy_via_PS.ps1 -dnsLabelPrefix f52nicauto01 -vmName f52nic -licenseToken 1 -EmailTo user@f5.com

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
### Start Prep Work ###
Write-Host "[$(get-date -format g)] Starting Script "

# Connect to Azure, using service principal
    # Specify Service Principal Information
    $accountId = "aa91d779-a3e6-4912-9bef-b7283b05db6e"
    $login = $AccountId.ToString()+"@discoveryeselabs.com"

    # Create Credentials, using password from service principal
    $pass = ConvertTo-SecureString "P4ssw0rd!azure" -AsPlainText –Force 
    $cred = New-Object -TypeName pscredential –ArgumentList $login, $pass
 
    # Login
    Login-AzureRmAccount -Credential $cred -ServicePrincipal –TenantId "949978da-9adb-4fb1-b24d-bd236f9b5d81"

# Modify variables as required for automation, grab license key as well
    $dnsLabelPrefix = $dnsLabelPrefix + $(Get-Random)
    $deploymentName = $deploymentName + $(Get-Random)
    $licenseoutflag = $false
    $logfile = "logger.log"
    Write-Output "Starting..." | Out-File -FilePath $logfile 

# Grabbing license from csv file
    $location = "C:\Licensing\LicenseFile.csv"
    $licensefile = Import-Csv $location
    $license = "empty"

    foreach ($_ in $licensefile) {
        if ($_.Status -eq 'Free') {
            $license = $_.LicenseToken
            $_.Status = 'Used'
            break
        }
    }

    if ($license -eq 'empty') {
        Write-Host "Uh oh... Need to add more licenses to $location"
        $licenseoutflag = $true
    } else {
        $licenseToken = $license
        Write-Host "License Token: $licenseToken was used"
    }

    $licensefile | Export-Csv $location -NoTypeInformation

### Finish Prep Work ###

# Create Resource Group for ARM Deployment
New-AzureRmResourceGroup -Name $deploymentName -Location "$region"    

# Create Arm Deployment
    $pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force
    $deployment = New-AzureRmResourceGroupDeployment -Name $deploymentName -ResourceGroupName $deploymentName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminPassword $pwd -dnsLabelPrefix $dnsLabelPrefix -vmName "$vmName" -licenseToken1 "$licensetoken"

# Print Output of Deployment to Console
   $deployment
   Add-Content $logfile "$deployment"

# Send Email letting deployer know if successful or not, placeholder utilizing arbitrary gmail account
    $status = $deployment.ProvisioningState
    $type = "f5-arm-2nic"

    $EmailFrom = "discoveryeselabsauto@gmail.com"
    $Subject = "[$(get-date -format g)] Notification for Azure Build Complete[$status]"
    $Body = "This is a notification for automated azure builds.. `n`n Testing template of type: $type `n`n License Tokens out? $licenseoutflag"
    $SMTPServer = "smtp.gmail.com"
    $SMTPClient = New-Object Net.Mail.SmtpClient($SmtpServer, 587)
    $SMTPClient.EnableSsl = $true
    $SMTPClient.Credentials = New-Object System.Net.NetworkCredential("discoveryeselabsauto", "P4ssw0rd!azure");
    $SMTPClient.Send($EmailFrom, $EmailTo, $Subject, $Body)

    Write-Host "Email Has been Sent to $EmailTo at $(get-date -format g)"
    Add-Content $logfile "Email Has been Sent to $EmailTo at $(get-date -format g)"


#Delete Objects Created
    Start-Sleep -m 1

    $removearmgroup = Remove-AzureRmResourceGroup -Name $deploymentName -Force

    Write-Host "[$(get-date -format g)] ARM Group $deploymentName Removed: $removearmgroup"
    Add-Content $logfile "[$(get-date -format g)] ARM Group $deploymentName Removed: $removearmgroup"

    Write-Host "[$(get-date -format g)] Ending Script"
