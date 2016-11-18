# PowerShell Script to Initialize Webserver for 2nic+webserver Demo

Write-Host "Installing Web Server Role"
$webinstall = Install-WindowsFeature -Name "Web-Server" -IncludeAllSubFeature

Write-Host "Result of Installing: $webinstall"