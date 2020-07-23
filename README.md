# F5 Azure ARM templates

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/issues)

## Introduction

Welcome to the GitHub repository for F5's ARM templates for Azure deployments.  All of the templates in this repository have been developed by F5 Networks engineers. Across all branches in this repository, there are two directories: *f5_supported* and *experimental*

  - **supported**<br>
  The supported directory contains Azure ARM templates that have been created and fully tested by F5 Networks. These templates are fully supported by F5, meaning you can get assistance if necessary from F5 Technical Support via your typical methods.

  - **experimental**<br>
  The experimental directory also contains ARM templates that have been created by F5 Networks. However, these templates have not completed full testing and are subject to change. F5 Networks does not offer technical support for templates in the experimental directory, so use these templates with caution.

## Template information

Descriptions for each template are contained at the top of each template in the *Description* key.
For additional information, including how the templates are generated, and assistance in deploying a template, see the individual README.md file in the individual template directory.

### Matrix for tagged releases

F5 has created a matrix that contains all of the tagged releases of the F5 ARM templates for Microsoft Azure and the corresponding BIG-IP versions, license types and throughput levels available for a specific tagged release. See https://github.com/F5Networks/f5-azure-arm-templates/blob/v7.0.0.0/azure-bigip-version-matrix.md

## List of F5 ARM templates for Azure deployments

To see a list of all of our supported Azure ARM templates, see the **[Azure Supported Template index](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/template-index.md)**. See the **experimental** directory for experimental templates.
Note that many of the solutions now include the *provisionPublicIP* option.  This means that the templates deploy without creating or attaching any public IP addresses to the BIG-IP VEs, see the individual README files for more information.
Standalone and HA production stack templates have been deprecated.

### Known Issues
All known issues are on GitHub for better tracking and visibility. See issues with a label of **Known Issues** at https://github.com/f5networks/f5-azure-arm-templates/issues.


---



### Copyright

Copyright 2014-2019 F5 Networks Inc.

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
