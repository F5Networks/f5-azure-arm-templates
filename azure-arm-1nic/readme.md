**f5-azure-arm-1nic**
================

Introduction
------------

This project implements an ARM Template to deploy a base example of F5 in a 1 nic deployment.

Documentation
-------------
Please see the project documentation - This is still being created

Installation
------------

Deploy via Azure deploy button below or via CLI Tools

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fsupported%2Fazure-arm-1nic%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>


Powershell Usage
-----
    # Params below match to parameteres in the azuredeploy.json that are gen-unique, otherwsie pointing to
    # the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
    # can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments

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



Design Patterns
------------
----------

The goal is for the design patterns for all the iterative examples of F5 being deployed via ARM templates to closely match as much as possible.

List of Patterns For Contributing Developers
--------------------------------------------
----------


 1. Still working on patterns to use

Filing Issues
-------------
----------


See the Issues section of `Contributing <CONTRIBUTING.md>`__.

Contributing
------------
----------


See `Contributing <CONTRIBUTING.md>`__

Test
----
----------

Before you open a pull request, your code must have passed a deployment into Azure with the intended result

Unit Tests
----
----------
Simply deploying the ARM template and completing use case fullfils a functional test



Copyright
---------
Copyright 2014-2016 F5 Networks Inc.


License
-------

Apache V2.0
~~~~~~~~~~~
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

Contributor License Agreement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Individuals or business entities who contribute to this project must have
completed and submitted the `F5 Contributor License Agreement`