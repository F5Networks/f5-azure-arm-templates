# Deploying the BIG-IQ VE License Manager in Azure - Cluster 2-NIC

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/issues)

## Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Important Configuration Notes](#important-configuration-notes)
- [Security](#security)
- [Getting Help](#help)
- [Installation](#installation)
- [Configuration Example](#configuration-example)

## Introduction

This solution uses an experimental ARM Template to launch and configure two BIG-IQ 2-NIC VEs in a clustered, hot-standby configuration, using BYOL (bring your own license) licensing.

IIn a 2-NIC implementation, one interface is for management and one is for data-plane traffic, each with a unique public/private IP.

You can choose one or both of these types of license pools on your BIG-IQ devices for licensing your BIG-IP VE devices:
- A License (Purchase) Pool, which can either be a registration key with a particular number of licenses, or an ELA/subscription pool, which enables self-licensing of BIG-IP virtual editions (VEs).
- A Registration Key Pool, which is a pool of single standalone BIG-IP VE registration keys for one or more BIG-IP services. This enables the ability to revoke and reassign a license to BIG-IP VE systems without having to contact F5 to allow the license to be moved.

See the [BIG-IQ documentation](https://support.f5.com/kb/en-us/products/big-iq-centralized-mgmt/manuals/product/big-iq-centralized-management-device-6-0-1/04.html) for more information on these pool types.

For information on getting started using F5's ARM templates on GitHub, see [Microsoft Azure: Solutions 101](http://clouddocs.f5.com/cloud/public/v1/azure/Azure_solutions101.html).

**Networking Stack Type:** This template deploys into an existing networking stack; so the networking infrastructure MUST be available prior to deploying. See the [Template Parameters Section](#template-parameters) for required networking objects.

## Prerequisites

- **Important**: When you configure the admin password for the BIG-IP VE in the template, you cannot use the character **#**.  Additionally, there are a number of other special characters that you should avoid using for F5 product user accounts.  See [K2873](https://support.f5.com/csp/article/K2873) for details.
- Before deploying this template,  you must create a managed identity to allow BIG-IQ to migrate IP configurations to the network interface of the active device on failover.  You must also create a **Contributor** role assignment for this identity with a scope that includes the resource group where the existing stack virtual network is configured. When deploying the template, use the identity name from these examples for the **userAssignedIdentityName** input parameter.

Click one of the following links for guidance on creating the managed identity:
	- [Azure Portal](#creating-a-managed-user-identity-from-the-azure-portal)
	- [Azure CLI](#creating-a-managed-user-identity-from-the-azure-cli)

- The following are prerequisites and notes for the F5 2-NIC ARM Template:

- Management subnet: the subnet for the management network requires a route and access to the Internet for the initial configuration to download the BIG-IP cloud library.
- Internal subnet.

- Since you are deploying the BYOL template, you must have a valid BIG-IP license token.
- The master-key (the passphrase used to establish trust between a future HA pair) for this deployment.

## Important configuration notes

- This template creates Azure Security Groups as a part of the deployment. For the internal Security Group, this includes a port for accessing BIG-IQ on port 443.
- This solution uses the SSH key to enable access to the BIG-IQ system. If you want access to the BIG-IQ web-based Configuration utility, you must first SSH into the BIG-IQ VE using the SSH key you provided in the template.  You can then create a user account with admin-level permissions on the BIG-IQ VE to allow access if necessary.
- This solution uses SKU with BIG-IQ v6.0.1 or later.
- After deploying the template, if you need to change your BIG-IQ VE password, there are a number of special characters that you should avoid using for F5 product user accounts.  See https://support.f5.com/csp/article/K2873 for details.
- This template can send non-identifiable statistical information to F5 Networks to help us improve our templates.  See [Sending statistical information to F5](#sending-statistical-information-to-f5).
- F5 has created a matrix that contains all of the tagged releases of the F5 ARM Templates for Microsoft Azure ARM, and the corresponding BIG-IQ versions, license types and throughput levels available for a specific tagged release. See https://github.com/F5Networks/f5-azure-arm-templates/blob/master/azure-bigip-version-matrix.md.
- These ARM templates incorporate an existing Virtual Network (VNet).
- F5 Azure ARM templates now capture all deployment logs to the BIG-IQ VE in /var/log/cloud/azure. Depending on which template you are using, this includes deployment logs (stdout/stderr), Cloud Libs execution logs, recurring solution logs (metrics, failover, and so on), and more.

## Security

This ARM template downloads helper code to configure the BIG-IQ system. If you want to verify the integrity of the template, you can open the template and ensure the following lines are present. See [Security Detail](#security-details) for the exact code.
In the *variables* section:

- In the *verifyHash* variable: **script-signature** and then a hashed signature.
- In the *installCloudLibs* variable: **tmsh load sys config merge file /config/verifyHash**.
- In the *installCloudLibs* variable: ensure this includes **tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz**.

Additionally, F5 provides checksums for all of our supported templates. For instructions and the checksums to compare against, see [checksums-for-f5-supported-cft-and-arm-templates-on-github](https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014).

## Supported BIG-IP versions

The following is a map that shows the available options for the template parameter **bigIqVersion** as it corresponds to the BIG-IQ version itself. Only the latest version of BIG-IQ VE is posted in the Azure Marketplace. For older versions, see downloads.f5.com.

| Azure BIG-IQ Image Version | BIG-IQ Version |
| --- | --- |
| 6.1.000000 | BIG-IQ 6.1.0 |


## Supported instance types and hypervisors

- For a list of recommended Azure instance types for the BIG-IQ VE, see https://support.f5.com/kb/en-us/products/big-iq-centralized-mgmt/manuals/product/bigiq-ve-supported-hypervisors-matrix.html.

## Getting Help

While this template has been created by F5 Networks, it is in the **experimental** directory and therefore has not completed full testing and is subject to change.  F5 Networks does not offer technical support for templates in the experimental directory. For supported templates, see the templates in the **supported** directory.

### Community Help

We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 ARM templates. There are F5 employees who are members of this community who typically monitor the channel Monday-Friday 9-5 PST and will offer best-effort assistance. This slack channel community support should **not** be considered a substitute for F5 Technical Support for supported templates. See the [Slack Channel Statement](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/slack-channel-statement.md) for guidelines on using this channel.

## Installation

You have three options for deploying this solution:

- Using the Azure deploy buttons
- Using [PowerShell](#powershell-script-example)
- Using [CLI Tools](#azure-cli-10-script-example)

### Azure deploy buttons

Use the appropriate button below to deploy:

- **BYOL** (bring your own license): This allows you to use an existing BIG-IP license.

  [![Deploy to Azure](http://azuredeploy.net/deploybutton.png)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv7.2.0.0%2Fexperimental%2Fbigiq%2FlicenseManagement%2Fcluster%2F2nic%2Fexisting-stack%2Fbyol%2Fazuredeploy.json)

### Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| adminUsername | Yes | User name for the Virtual Machine. |
| adminPassword | Yes | Password to login to the Virtual Machine. Note: There are a number of special characters that you should avoid using for F5 product user accounts.  See [K2873](https://support.f5.com/csp/article/K2873) for details. |
| masterKey | Yes | Specify BIG-IQ master Key. |
| dnsLabel | Yes | Unique DNS Name for the Public IP address used to access the Virtual Machine. |
| instanceName | Yes | Name of the Virtual Machine. |
| instanceType | Yes | Instance size of the Virtual Machine. |
| bigIqVersion | Yes | F5 BIG-IQ version you want to use. |
| bigIqLicenseKey1 | Yes | F5 BYOL BIG-IQ License Manager registration key. |
| bigIqLicenseKey2 | Yes | The license token for the F5 BIG-IQ VE (BYOL). This field is required when deploying two or more devices. |
| licensePoolKeys | Yes | Enter a pool name and registration key using the format of name:key. Leave Do_Not_Create if you do not want to create a licensing pool on BIG-IQ at this time. |
| regPoolKeys | Yes | Enter a pool name and a list of individual BIG-IP registration keys in the format of name:key,key,key. Leave Do_Not_Create if you do not want to create a reg key pool on BIG-IQ at this time. |
| vnetName | Yes | The name of the existing virtual network to which you want to connect the BIG-IP VEs. |
| vnetResourceGroupName | Yes | The name of the resource group that contains the Virtual Network where the BIG-IP VE will be placed. |
| userAssignedIdentityResourceGroupName | Yes | The name of the resource group that contains the User Assigned Identity. |
| userAssignedIdentityName | Yes | The name of the existing User Assigned Identity that has access to the existing resource group with the Virtual Network |
| mgmtSubnetName | Yes | Name of the existing mgmt subnet - with external access to the Internet. **Important**: The subnet you provide for the mgmt NIC **must** be unique. |
| mgmtIpAddressRangeStart | Yes | The static private IP address you want to assign to the management self IP of the first BIG-IQ. The next contiguous address will be used for the second BIG-IQ device. |
| internalSubnetName | Yes | Name of the existing internal subnet. **Important**: The subnet you provide for the internal NIC **must** be unique. |
| internalIpSelfAddressRangeStart | Yes | The static private IP address you want to assign to the internal self IP (primary) of the first BIG-IQ VE. The next contiguous address will be used for the second BIG-IQ device. |
| internalIpAddressRangeStart | Yes | The static private IP address you would like to assign to the internal self IP of the first BIG-IQ VE. The next contiguous address will be used for the second BIG-IQ device. |
| ntpServer | Yes | Leave the default NTP server the BIG-IQ uses, or replace the default NTP server with the one you want to use. |
| timeZone | Yes | If you would like to change the time zone the BIG-IQ uses, enter the time zone you want to use. This is based on the tz database found in /usr/share/zoneinfo (see the full list [here](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/azure-timezone-list.md)). Example values: UTC, US/Pacific, US/Eastern, Europe/London or Asia/Singapore. |
| customImage | Yes | If you would like to deploy using a local BIG-IQ image, provide either the full URL to the VHD in Azure storage **or** the full resource ID to an existing Microsoft.Compute image resource.  **Note**: Unless specifically required, leave the default of **OPTIONAL**. |
| restrictedSrcAddress | Yes | This field restricts management access to a specific network or address. Enter an IP address or address range in CIDR notation, or asterisk for all sources |
| tagValues | Yes | Default key/value resource tags will be added to the resources in this deployment, if you would like the values to be unique adjust them as needed for each key. |
| allowUsageAnalytics | Yes | This deployment can send anonymous statistics to F5 to help us determine how to improve our solutions. If you select **No** statistics are not sent. |

### Programmatic deployments

As an alternative to deploying through the Azure Portal (GUI) each solution provides example scripts to deploy the ARM template.  The example commands can be found below along with the name of the script file, which exists in the current directory.

#### PowerShell Script Example

```powershell
## Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -adminPassword <value> -masterKey <value> -dnsLabel <value> -instanceName f5vm01 -instanceType Standard_D4s_v3 -bigIqVersion 6.1.000000 -bigIqLicenseKey1 <value> -bigIqLicenseKey2 <value> -licensePoolKeys Do_Not_Create -regPoolKeys Do_Not_Create -vnetName <value> -vnetResourceGroupName <value> -userAssignedIdentityResourceGroupName <value> -userAssignedIdentityName <value> -mgmtSubnetName <value> -mgmtIpAddressRangeStart <value> -internalSubnetName <value> -internalIpSelfAddressRangeStart <value> -internalIpAddressRangeStart <value> -ntpServer 0.pool.ntp.org -timeZone UTC -customImage OPTIONAL -allowUsageAnalytics Yes -resourceGroupName <value>
```

=======

#### Azure CLI (1.0) Script Example

```bash
## Example Command: ./deploy_via_bash.sh --adminUsername azureuser --adminPassword <value> --masterKey <value> --dnsLabel <value> --instanceName f5vm01 --instanceType Standard_D4s_v3 --bigIqVersion 6.1.000000 --bigIqLicenseKey1 <value> --bigIqLicenseKey2 <value> --licensePoolKeys Do_Not_Create --regPoolKeys Do_Not_Create --vnetName <value> --vnetResourceGroupName <value> --userAssignedIdentityResourceGroupName <value> --userAssignedIdentityName <value> --mgmtSubnetName <value> --mgmtIpAddressRangeStart <value> --internalSubnetName <value> --internalIpSelfAddressRangeStart <value> --internalIpAddressRangeStart <value> --ntpServer 0.pool.ntp.org --timeZone UTC --customImage OPTIONAL --allowUsageAnalytics Yes --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>
```

## Documentation
- For more information on BIG-IQ VE, see https://support.f5.com/kb/en-us/products/big-iq-centralized-mgmt/manuals/product/big-iq-centralized-management-device-6-0-1.html and https://support.f5.com/kb/en-us/products/big-iq-centralized-mgmt/manuals/product/big-iq-centralized-management-and-amazon-web-services-setup-6-0-0.html
- For more information on F5 solutions for Azure, including manual configuration procedures for some deployment scenarios, see the Azure section of [Public Cloud Docs](http://clouddocs.f5.com/cloud/public/v1/).

## Creating a managed user identity
Use one of the following procedures to create a managed user identity.


### Creating a managed user identity from the Azure Portal
Use the following procedure if you want to create the managed user identity from the Azure Portal.

1.	Click the Azure Resource Group where you want to add the Managed User Identity.
2.	Click **Add**.
3.	Type **User Assigned Managed Identity** in the search bar.
4.	Click **User Assigned Managed Identity** and then click **Create**.
5.	Specify a name for the resource and choose a Resource Group where it will be created, and then click **Create**.
6.	Click the Azure Resource Group containing your existing Azure virtual network.
7.	Click **Access Control (IAM)**.
8.	Click **Role Assignments**.
9.	Click **Add > Role Assignment**.
10.	Under **Role**, select the **Contributor** role.
11.	Under **Assign access to**, select **User assigned managed identity**.
12.	Select the User assigned managed identity you created previously, and click **Save**
13. Repeat steps 6-12 for the Resource Group where you deployed the ARM template

The BIG-IQ system now has access to move Azure IP configurations to the active device.

### Creating a managed user identity from the Azure CLI
Use the following procedure if you want to create the managed user identity from the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/?view=azure-cli-latest).

- To create a managed identity, use the following command syntax from the Azure CLI:
```az identity create -n <identity_name> -g <deployment_resource_group>```
- To get the object ID of the identity (the object ID is the "value" property (GUID) of the returned JSON object), use the following command syntax from the Azure CLI:
```az identity show -g <deployment_resource_group> --name <identity_name> --output json```
- To create a role assignment for the identity on the existing stack resource group, use the following command syntax from the Azure CLI:
    ```az role assignment create --resource-group <existing_stack_resource_group> <identity_object_ID> --roleName "Contributor"```


### Sending statistical information to F5

All of the F5 templates now have an option to send anonymous statistical data to F5 Networks to help us improve future templates.
None of the information we collect is personally identifiable, and only includes:

- Customer ID: this is a hash of the customer ID, not the actual ID
- Deployment ID: hash of stack ID
- F5 template name
- F5 template version
- Cloud Name
- Azure region
- BIG-IQ version
- F5 license type
- F5 Cloud libs version
- F5 script name

This information is critical to the future improvements of templates, but should you decide to select **No**, information will not be sent to F5.

## Security Details

This section has the code snippet for each the lines you should ensure are present in your template file if you want to verify the integrity of the helper code in the template.

Note the hashed script-signature may be different in your template.

```json
"variables": {
    "apiVersion": "2015-06-15",
    "location": "[resourceGroup().location]",
    "singleQuote": "'",
    "f5CloudLibsTag": "release-2.0.0",
    "expectedHash": "8bb8ca730dce21dff6ec129a84bdb1689d703dc2b0227adcbd16757d5eeddd767fbe7d8d54cc147521ff2232bd42eebe78259069594d159eceb86a88ea137b73",
    "verifyHash": "[concat(variables('singleQuote'), 'cli script /Common/verifyHash {\nproc script::run {} {\n        if {[catch {\n            set file_path [lindex $tmsh::argv 1]\n            set expected_hash ', variables('expectedHash'), '\n            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n            if { $expected_hash eq $computed_hash } {\n                exit 0\n            }\n            tmsh::log err {Hash does not match}\n            exit 1\n        }]} {\n            tmsh::log err {Unexpected error in verifyHash}\n            exit 1\n        }\n    }\n    script-signature fc3P5jEvm5pd4qgKzkpOFr9bNGzZFjo9pK0diwqe/LgXwpLlNbpuqoFG6kMSRnzlpL54nrnVKREf6EsBwFoz6WbfDMD3QYZ4k3zkY7aiLzOdOcJh2wECZM5z1Yve/9Vjhmpp4zXo4varPVUkHBYzzr8FPQiR6E7Nv5xOJM2ocUv7E6/2nRfJs42J70bWmGL2ZEmk0xd6gt4tRdksU3LOXhsipuEZbPxJGOPMUZL7o5xNqzU3PvnqZrLFk37bOYMTrZxte51jP/gr3+TIsWNfQEX47nxUcSGN2HYY2Fu+aHDZtdnkYgn5WogQdUAjVVBXYlB38JpX1PFHt1AMrtSIFg==\n}', variables('singleQuote'))]",
    "installCloudLibs": "[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit\nfi\necho loaded verifyHash\necho verifying f5-cloud-libs.targ.gz\n/usr/bin/tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz\nif [ $? != 0 ]; then\necho f5-cloud-libs.tar.gz is not valid\nexit\nfi\necho verified f5-cloud-libs.tar.gz\necho expanding f5-cloud-libs.tar.gz\ntar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud\ntouch /config/cloud/cloudLibsReady', variables('singleQuote'))]",
```



## Filing Issues

If you find an issue, we would love to hear about it.
You have a choice when it comes to filing issues:

- Use the **Issues** link on the GitHub menu bar in this repository for items such as enhancement or feature requests and non-urgent bug fixes. Tell us as much as you can about what you found and how you found it.
- Contact us at [solutionsfeedback@f5.com](mailto:solutionsfeedback@f5.com?subject=GitHub%20Feedback) for general feedback or enhancement requests.
- Use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 cloud templates.  There are F5 employees who are members of this community who typically monitor the channel Monday-Friday 9-5 PST and will offer best-effort assistance.
- For templates in the **supported** directory, contact F5 Technical support via your typical method for more time sensitive changes and other issues requiring immediate support.

## Copyright

Copyright 2014-2019 F5 Networks Inc.

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