# F5 Azure ARM templates
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

## Introduction

Welcome to the GitHub repository for F5's ARM templates for Azure deployments.  All of the templates in this repository have been developed by F5 Networks engineers. Across all branches in this repository, there are two directories: *f5_supported* and *experimental*

  - **f5_supported**<br>
  The f5_supported directory contains Azure ARM templates that have been created and fully tested by F5 Networks. These templates are fully supported by F5, meaning you can get assistance if necesary from F5 Technical Support via your typical methods.

  - **experimental**<br>
  The expermimental directory also contains ARM templates that have been created by F5 Networks. However, these templates have not completed full testing and are subject to change. F5 Networks does not offer technical support for templates in the experimental diretory, so use these templates with caution.

## Template information
Descriptions for each template are contained at the top of each template in the *Description* key.
For additional information, including how the templates are generated, and assistance in deploying a template, see the individual README.md file in the **build/** directory.


## List of F5 ARM templates for Azure deployments
The following is a list of the current *supported* F5 ARM templates:
  - [Deploying the BIG-IP VE in Azure - Single NIC](https://github.com/F5Networks/f5-azure-arm-templates/tree/master/supported/standalone/1nic)<br>
  <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fsupported%2Fstandalone%2F1nic%2Fazuredeploy.json" target="_blank">
  <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>

  - [Deploying the BIG-IP VE in Azure - 2 NICs](https://github.com/F5Networks/f5-azure-arm-templates/tree/master/supported/standalone/2nic)<br>
  <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fsupported%2Fstandalone%2F2nic_limited%2Fazuredeploy.json" target="_blank">
  <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>

  - [Deploying the BIG-IP VE in Azure - Single NIC (Cluster)](https://github.com/F5Networks/f5-azure-arm-templates/tree/master/supported/cluster/1nic)<br>
  <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fsupported%2Fcluster%2F1nic%2Fazuredeploy.json" target="_blank">
  <img src="http://azuredeploy.net/deploybutton.png"/></a>


### Copyright

Copyright 2014-2017 F5 Networks Inc.


### License


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
