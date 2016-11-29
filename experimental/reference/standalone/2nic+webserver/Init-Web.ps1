# PowerShell Script to Initialize Webserver for 2nic+webserver Demo

# Sleep for 30 seconds to allow network initialization before intalling Web Server Role
Start-Sleep 30

$webinstall = Install-WindowsFeature -Name "Web-Server" -IncludeAllSubFeature
Write-Host "Result of Installing: $webinstall"

# Download Web Page(s) to display, IIS by default will accept Default.htm in directory specificed below as the file to serve
$sourcehtml = "https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/master/experimental/reference/standalone/2nic%2Bwebserver/Default.htm"
$destinationhtml = "C:\inetpub\wwwroot\Default.htm"

$downloadhtml = Invoke-WebRequest $sourcehtml -OutFile $destinationhtml
Write-Host "Download Result: $downloadhtml"

# Replace Hostname with real host name
$webserver = hostname
(Get-Content $destinationhtml | ForEach-Object { $_ -replace "Hostname", "$webserver" } ) | Set-Content $destinationhtml