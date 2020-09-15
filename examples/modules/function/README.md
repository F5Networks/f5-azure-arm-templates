# Deploying Function Template

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/issues)


## Contents

- [Deploying Function Template](#deploying-function-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
  - [Resource Tree](#resource-tree)
  - [Getting Help](#getting-help)
    - [Filing Issues](#filing-issues)
  - [Copyright](#copyright)
  - [License](#license)
    - [Apache V2.0](#apache-v20)
    - [Contributor License Agreement](#contributor-license-agreement)
  - [Important Configuration Notes](#important-configuration-notes-1)
    - [Template Parameters](#template-parameters)
  - [Decision Tree](#decision-tree)
  - [Copyright](#copyright-1)
  - [License](#license-1)
    - [Apache V2.0](#apache-v20-1)
    - [Contributor License Agreement](#contributor-license-agreement-1)

## Introduction

This template creates the Azure function app, hosting plan, key vault, application insights, and storage account resources required for revoking licenses from a BIG-IQ system based on current Azure Virtual Machine Scale Set capacity. By default, the function app executes every 2 minutes; however, you can adjust this interval from the function app timer trigger configuration after deployment is complete.


## Prerequisites

- You must provide the Azure resource ID of a Virtual Machine Scale Set with BIG-IP instances licensed via BIG-IQ.
- You must provide the Azure resource ID of the Virtual Network where the BIG-IQ system used to license the BIG-IP instances is deployed.
- The licensing API of the BIG-IQ system used to license the BIG-IP instances must be accessible from the Azure function app.
- You must provide either the license pool name or utility licensing information used to license the BIG-IP instances.
- The function app name created by this template must be globally unique. Do not reuse the same functionAppName parameter value in multiple deployments.
- This template must be deployed in the same resource group as the Virtual Machine Scale Set resource.
- This template creates an Azure system-assigned Managed Identity and assigns the role of Contributor to it on the scope of the resource group where the template is deployed. You must have sufficient permissions to create the identity and role assignment.

## Important Configuration Notes

 - A sample template, 'sample_linked.json', has been included in this project. Use this example to see how to add function.json as a linked template into your templated solution.
 
 - BIG-IQ license class must use unreachable: Because the Azure function for license revocation filters license assignments based on the assignment tenant value, you must specify "reachable: false" in your F5 Declarative Onboarding license class declaration. See the F5 Declarative Onboarding [documentation](https://clouddocs.f5.com/products/extensions/f5-declarative-onboarding/latest/big-iq-licensing.html#license-class) for more information.

 - How to find outbound IP addresses for Azure function: If you specified a public IP address for the bigIqAddress parameter, you may need to configure the Azure network security group(s) for BIG-IQ management access to allow requests from the IP addresses allocated to the Azure function. In the Azure portal, you can find the list of function source IP addresses by clicking on the function app name, then clicking **Settings > Properties > Additional Outbound IP Addresses**. This list includes all possible source IP addresses used by the Azure function. 

- Disable SSL warnings in Azure function: By default, the Azure function is created with the F5_DISABLE_SSL_WARNINGS environment variable set to "False". When revoking licenses from a BIG-IQ License Manager device that is configured to use a self-signed certificate, you can set F5_DISABLE_SSL_WARNINGS to "True" to suppress insecure connection warning messages (this is not recommended for production deployments). You can configure this setting in the Azure portal by clicking on the function app name, then clicking Settings > Configuration > App Settings and changing the value for  F5_DISABLE_SSL_WARNINGS to "True".


### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| vmssId | Yes | Supply the fully-qualified resource ID of the Azure Virtual Machine Scale Set to be monitored. |
| bigIqAddress | Yes | The public or private IP address of the BIG-IQ to be used when revoking licenses from the BIG-IP.  Note: The Azure function will make a REST call to the BIG-IQ (already existing) to let it know a BIG-IP needs to be revoked. It will then revoke the license of the BIG-IP using the provided BIG-IQ credentials and license pool name/utility license info. |
| bigIqUsername | Yes | The BIG-IQ username to use during BIG-IP license revocation via BIG-IQ. |
| bigIqPassword | Yes | The BIG-IQ password to use during BIG-IP license revocation via BIG-IQ. This password will be securely stored in an Azure KeyVault secret. |
| bigIqTenant | No | The BIG-IQ tenant used during BIG-IP licensing via BIG-IQ. This limits the scope of licenses eligible for revocation to those that were licensed with the specified tenant value. |
| bigIqLicensePoolName | No | The BIG-IQ license pool used during BIG-IP licensing via BIG-IQ. |
| bigIqUtilityKey | No | The BIG-IQ utility license key used during BIG-IP licensing via BIG-IQ. ***Important***: This is only required when revoking a license from an ELA/subscription (utility) pool on the BIG-IQ, if not using this pool type leave the default of **Default**. |
| bigIqUtilityOffer | No | The BIG-IQ utility offer ID (UUID) used during BIG-IP licensing via BIG-IQ. ***Important***: This is only required when revoking a license from an ELA/subscription (utility) pool on the BIG-IQ, if you're not using this pool type, leave the default of **Default**. |
| functionAppName | Yes | Supply a name for the new function app. |
| functionAppSku | Yes | Supply a configuration for the function app server farm plan SKU (premium or appservice) in JSON format. Information about server farm plans is available [here](https://docs.microsoft.com/en-us/azure/templates/microsoft.web/2018-02-01/serverfarms). |
| functionAppVnetId | No | The fully-qualified resource ID of the Azure Virtual Network where BIG-IQ is deployed. This is required when connecting to BIG-IQ via a private IP address; the Azure function app will be granted ingress permission to the virtual network. When specifying an Azure public IP address for bigIqAddress, leave the default of **Default**. |
| tagValues| Yes | List of tags to add to created resources. |

### Template Outputs

| Name | Description | Required Resource | Type | 
| --- | --- | --- | --- |
| storageAccountId | Storage Account resource ID | Storage Account | string |
| hostingPlanId | Hosting Plan resource ID | Server Farm | string |
| functionAppId | Function App resource ID | Function App | string |
| keyVaultId | KeyVault resource ID | KeyVault | string |
| applicationInsightsId | Application Insights resource ID | Application Insights | string |
| roleAssignmentId | Role Assignment resource ID | Role Assignment | string |

## Resource Tree

Resource Creation Flow Chart
<br>
<br>
<br>
```mermaid
graph TD
  licPoolSpecified(["bigIqLicensePoolName: Specified"]);
  licPoolDefault(["bigIqLicensePoolName: Not Specified"]);
  utilityKey("bigIqUtilityKey<br>(Required)");
  utilityOffer("bigIqUtilityOffer<br>(Required)");
  functionApp("functionAppName");
  storageAccount{"Storage Account"};
  serverFarm{"Server Farm"};
  function{"Function App"};
  functionSettings{"Function App Settings"};
  keyVault{"KeyVault"};
  secret{"KeyVault Secret"};
  appInsights{"Application Insights"}
  subgraph Resources
    storageAccount-.-serverFarm-.-function-.-functionSettings-.-keyVault-.-secret-.-appInsights
  end
  subgraph License Type - Pool
    licPoolSpecified-.->functionApp;
  end
  subgraph License Type - Utility
    licPoolDefault-.->utilityKey.->utilityOffer-.->functionApp;
  end
```

<br>
<br>
<br>

## Getting Help

The example templates in this directory are intended to provide reference deployments of F5 BIG-IP Virtual Editions. Due to the heavy customization requirements of external cloud resources and BIG-IP configurations in these solutions, F5 does not provide technical support for deploying, customizing, or troubleshooting the templates themselves. However, the various underlying products and components used (for example: F5 BIG-IP Virtual Edition, Automation Toolchain extensions, and Cloud Failover Extension (CFE)) in the solutions located here are F5-supported and capable of being deployed with other orchestration tools. Read more about [Support Policies](https://www.f5.com/company/policies/support-policies). 

### Filing Issues

If you find an issue, we would love to hear about it.

## Copyright

Copyright 2014-2020 F5 Networks Inc.

## License

### Apache V2.0

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License [here](http://www.apache.org/licenses/LICENSE-2.0).

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

### Contributor License Agreement

Individuals or business entities who contribute to this project must have
completed and submitted the F5 Contributor License Agreement.
 system-assigned Managed Identity and assigns the role of Contributor to it on the scope of the resource group where the template is deployed. You must have sufficient permissions to create the identity and role assignment.
- Your BIG-IP instance license assignments must contain the tenant attribute. The value of this attribute is used to limit revocation to instances from a specific Azure VMSS deployment. If no value is specified for bigIqTenant when deploying this template, the tenant value defaults to the name of the Azure VMSS.

## Important Configuration Notes

 - A sample template, 'sample_linked.json', has been included in this project. Use this example to see how to add function.json as a linked template into your templated solution.

 - BIG-IQ license class must use unreachable: Because the Azure function for license revocation filters license assignments based on the assignment tenant value, you must specify "reachable: false" in your F5 Declarative Onboarding license class declaration. See the F5 Declarative Onboarding [documentation](https://clouddocs.f5.com/products/extensions/f5-declarative-onboarding/latest/big-iq-licensing.html#license-class) for more information.

- How to find outbound IP addresses for Azure function: If you specified a public IP address for the bigIqAddress parameter, you may need to configure the Azure network security group(s) for BIG-IQ management access to allow requests from the IP addresses allocated to the Azure function. In the Azure portal, you can find the list of function source IP addresses by clicking on the function app name, then clicking **Settings > Properties > Additional Outbound IP Addresses**. This list includes all possible source IP addresses used by the Azure function. 

- Disable SSL warnings in Azure function: By default, the Azure function is created with the F5_DISABLE_SSL_WARNINGS environment variable set to "False". When revoking licenses from a BIG-IQ License Manager device that is configured to use a self-signed certificate, you can set F5_DISABLE_SSL_WARNINGS to "True" to suppress insecure connection warning messages (this is not recommended for production deployments). You can configure this setting in the Azure portal by clicking on the function app name, then clicking Settings > Configuration > App Settings and changing the value for  F5_DISABLE_SSL_WARNINGS to "True".


### Template Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| vmssId | Yes | Supply the fully-qualified resource ID of the Azure Virtual Machine Scale Set to be monitored. |
| bigIqAddress | Yes | The public or private IP address of the BIG-IQ to be used when revoking licenses from the BIG-IP.  Note: The Azure function will make a REST call to the BIG-IQ (already existing) to let it know a BIG-IP needs to be revoked. It will then revoke the license of the BIG-IP using the provided BIG-IQ credentials and license pool name/utility license info. |
| bigIqUsername | Yes | The BIG-IQ username to use during BIG-IP license revocation via BIG-IQ. |
| bigIqPassword | Yes | The BIG-IQ password to use during BIG-IP license revocation via BIG-IQ. This password will be securely stored in an Azure KeyVault secret. |
| bigIqTenant | No | The BIG-IQ tenant used during BIG-IP licensing via BIG-IQ. This limits the scope of licenses eligible for revocation to those that were licensed with the specified tenant value. Leaving the default of **Default** will cause the function TENANT variable to be set to the Virtual Machine Scale Set name. |
| bigIqLicensePoolName | No | The BIG-IQ license pool used during BIG-IP licensing via BIG-IQ. |
| bigIqUtilityKey | No | The BIG-IQ utility license key used during BIG-IP licensing via BIG-IQ. ***Important***: This is only required when revoking a license from an ELA/subscription (utility) pool on the BIG-IQ; if you're not using this pool type, leave the default of **Default**. |
| bigIqUtilityOffer | No | The BIG-IQ utility offer ID (UUID) used during BIG-IP licensing via BIG-IQ. ***Important***: This is only required when revoking a license from an ELA/subscription (utility) pool on the BIG-IQ; if you're not using this pool type, leave the default of **Default**. |
| functionAppName | Yes | Supply a name for the new function app. |
| functionAppSku | Yes | Supply a configuration for the function app server farm plan SKU (premium or appservice) in JSON format. Information about server farm plans is available [here](https://docs.microsoft.com/en-us/azure/templates/microsoft.web/2018-02-01/serverfarms). |
| functionAppVnetId | No | The fully-qualified resource ID of the Azure Virtual Network where BIG-IQ is deployed. This is required when connecting to BIG-IQ via a private IP address; the Azure function app will be granted ingress permission to the virtual network. When specifying an Azure public IP address for bigIqAddress, leave the default of **Default**. |
| tagValues| Yes | List of tags to add to created resources. |

## Decision Tree

Resource Creation Flow Chart
<br>
<br>
<br>
```mermaid
graph TD
  licPoolSpecified(["bigIqLicensePoolName: Specified"]);
  licPoolDefault(["bigIqLicensePoolName: Not Specified"]);
  utilityKey("bigIqUtilityKey<br>(Required)");
  utilityOffer("bigIqUtilityOffer<br>(Required)");
  functionApp("functionAppName");
  storageAccount{"Storage Account"};
  serverFarm{"Server Farm"};
  function{"Function App"};
  functionSettings{"Function App Settings"};
  keyVault{"KeyVault"};
  secret{"KeyVault Secret"};
  appInsights{"Application Insights"}
  subgraph Resources
    storageAccount-.-serverFarm-.-function-.-functionSettings-.-keyVault-.-secret-.-appInsights
  end
  subgraph License Type - Pool
    licPoolSpecified-.->functionApp;
  end
  subgraph License Type - Utility
    licPoolDefault-.->utilityKey.->utilityOffer-.->functionApp;
  end
```

<br>
<br>
<br>


## Copyright

Copyright 2014-2020 F5 Networks Inc.

## License

### Apache V2.0

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License [here](http://www.apache.org/licenses/LICENSE-2.0).

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

### Contributor License Agreement

Individuals or business entities who contribute to this project must have
completed and submitted the F5 Contributor License Agreement.