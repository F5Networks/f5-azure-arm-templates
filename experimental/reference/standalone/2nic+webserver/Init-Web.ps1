# PowerShell Script to Initialize Webserver for 2nic+webserver Demo

$webinstall = Install-WindowsFeature -Name "Web-Server" -IncludeAllSubFeature
Write-Host "Result of Installing: $webinstall"

# Download DWeb Page(s) to display, windows by default will accept Default.htm in directory specificed as the file to server
$sourcehtml = "https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/master/experimental/reference/standalone/2nic%2Bwebserver/Default.htm"
$destinationhtml = "C:\inetpub\wwwroot\Default.htm"

$downloadhtml = Invoke-WebRequest $sourcehtml -OutFile $destinationhtml
Write-Host "Download Result: $downloadhtml"