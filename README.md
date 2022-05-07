# F5 Azure ARM templates

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/issues)
  

## F5 Azure ARM Templates 1.0

| :eyes:    | ***Notice***: These legacy templates are now in maintenance mode and are being replaced by our next-generation templates available in the [Cloud Templates 2.0 GitHub repo](https://github.com/F5Networks/f5-azure-arm-templates-v2). We recommend you adopt the next-generation templates as soon as is feasible. |
|---------------|:------------------------|  

| :warning: | ***Warning***: Due to vulnerabilities related to [CVE-2022-1388](https://support.f5.com/csp/article/K23605346), do not use templates unless using a custom image (template parameter = customImage or customImageUrn). Updated images are pending publication to Marketplace. For existing deployments, F5 recommends [upgrading to a patched software version](https://support.f5.com/csp/article/K84205182). Production should never expose the BIG-IP Management interface to the Internet. Always ensure `restrictedSrcAddress` has been set to a trusted source network. Please see [K23605346: BIG-IP iControl REST vulnerability CVE-2022-1388](https://support.f5.com/csp/article/K23605346) for more information and latest updates.|
|---------------|:------------------------|

## Introduction

Welcome to the GitHub repository for F5's ARM templates for Azure deployments. All of the templates in this repository have been developed by F5 Networks engineers. This repository contains one main directory: *supported*.

- **supported**<br>
  The supported directory contains our legacy Azure ARM templates that have been created and fully tested by F5 Networks. These legacy cloud solution templates (CST1) are fully supported by F5, meaning you can get assistance if necessary from F5 Technical Support via your typical methods. These legacy templates are now in maintenance mode and are being replaced by our next-generation cloud solution templates (CST2) available at https://github.com/F5Networks/f5-azure-arm-templates-v2. We recommend you adopt the next-generation templates as soon as is feasible.
  
  - Maintenance mode does NOT mean we are removing nor disabling legacy templates.
  - Customers are free to continue using legacy cloud templates.
  - Legacy cloud templates are officially in sustaining/maintenance mode.
  - Package updates and critical bug fixes will be considered for maintenance mode cloud templates.
  - TMOS 16.1 is the final TMOS version for which legacy cloud verification testing will take place.
  - No new features nor legacy cloud templates will be developed.


## Template information

Descriptions for each template are contained at the top of each template in the *Description* key.
For additional information, including how the templates are generated, and assistance in deploying a template, see the individual README.md file in the individual template directory.

### Matrix for tagged releases

F5 has created a matrix that contains all of the tagged releases of the F5 ARM templates for Microsoft Azure and the corresponding BIG-IP versions, license types and throughput levels available for a specific tagged release. See https://github.com/F5Networks/f5-azure-arm-templates/blob/main/azure-bigip-version-matrix.md

## List of F5 ARM templates for Azure deployments

To see a list of all of our supported Azure ARM templates, see the **[Azure Supported Template index](https://github.com/F5Networks/f5-azure-arm-templates/blob/main/template-index.md)**. See the **experimental** directory for experimental templates.
Note that many of the solutions now include the *provisionPublicIP* option.  This means that the templates deploy without creating or attaching any public IP addresses to the BIG-IP VEs, see the individual README files for more information.
Standalone and HA production stack templates have been deprecated.

### Known Issues
All known issues are on GitHub for better tracking and visibility. See issues with a label of **Known Issues** at https://github.com/f5networks/f5-azure-arm-templates/issues.


---



### Copyright

Copyright 2014-2022 F5 Networks Inc.

### License

#### Apache V2.0

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

#### Contributor License Agreement

Individuals or business entities who contribute to this project must have
completed and submitted the F5 Contributor License Agreement.
