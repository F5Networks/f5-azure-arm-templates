# Deploying the BIG-IQ VE License Manager in Azure - {{ TITLE_TXT }}

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

{{ INTRO_TXT }}

For information on getting started using F5's ARM templates on GitHub, see [Microsoft Azure: Solutions 101](http://clouddocs.f5.com/cloud/public/v1/azure/Azure_solutions101.html).

**Networking Stack Type:** {{ STACK_TYPE_TXT }}

## Prerequisites

- **Important**: When you configure the admin password for the BIG-IP VE in the template, you cannot use the character **#**.  Additionally, there are a number of other special characters that you should avoid using for F5 product user accounts.  See [K2873](https://support.f5.com/csp/article/K2873) for details.
{{ EXTRA_PREREQS }}
## Important configuration notes

- This template creates Azure Security Groups as a part of the deployment. For the internal Security Group, this includes a port for accessing BIG-IQ on port 443.
- This solution uses the SSH key to enable access to the BIG-IQ system. If you want access to the BIG-IQ web-based Configuration utility, you must first SSH into the BIG-IQ VE using the SSH key you provided in the template.  You can then create a user account with admin-level permissions on the BIG-IQ VE to allow access if necessary.
- This solution uses SKU with BIG-IQ v6.0.1 or later.
- After deploying the template, if you need to change your BIG-IQ VE password, there are a number of special characters that you should avoid using for F5 product user accounts.  See https://support.f5.com/csp/article/K2873 for details.
- This template can send non-identifiable statistical information to F5 Networks to help us improve our templates.  See [Sending statistical information to F5](#sending-statistical-information-to-f5).
- F5 has created a matrix that contains all of the tagged releases of the F5 ARM Templates for Microsoft Azure ARM, and the corresponding BIG-IQ versions, license types and throughput levels available for a specific tagged release. See https://github.com/F5Networks/f5-azure-arm-templates/blob/master/azure-bigip-version-matrix.md.
- These ARM templates incorporate an existing Virtual Network (VNet).
- F5 Azure ARM templates now capture all deployment logs to the BIG-IQ VE in /var/log/cloud/azure. Depending on which template you are using, this includes deployment logs (stdout/stderr), Cloud Libs execution logs, recurring solution logs (metrics, failover, and so on), and more.
{{ EXTRA_CONFIG_NOTES }}
## Security

This ARM template downloads helper code to configure the BIG-IQ system. If you want to verify the integrity of the template, you can open the template and ensure the following lines are present. See [Security Detail](#security-details) for the exact code.
In the *variables* section:

- In the *verifyHash* variable: **script-signature** and then a hashed signature.
- In the *installCloudLibs* variable: **tmsh load sys config merge file /config/verifyHash**.
- In the *installCloudLibs* variable: ensure this includes **tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz**.

Additionally, F5 provides checksums for all of our supported templates. For instructions and the checksums to compare against, see [checksums-for-f5-supported-cft-and-arm-templates-on-github](https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014).

## Supported BIG-IP versions

The following is a map that shows the available options for the template parameter **bigIqVersion** as it corresponds to the BIG-IQ version itself. Only the latest version of BIG-IQ VE is posted in the Azure Marketplace. For older versions, see downloads.f5.com.


## Supported instance types and hypervisors

- For a list of recommended Azure instance types for the BIG-IQ VE, see https://support.f5.com/kb/en-us/products/big-iq-centralized-mgmt/manuals/product/bigiq-ve-supported-hypervisors-matrix.html.

## Getting Help

{{ HELP_TEXT }}

### Community Help

We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 ARM templates. There are F5 employees who are members of this community who typically monitor the channel Monday-Friday 9-5 PST and will offer best-effort assistance. This slack channel community support should **not** be considered a substitute for F5 Technical Support for supported templates. See the [Slack Channel Statement](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/slack-channel-statement.md) for guidelines on using this channel.

## Installation

You have three options for deploying this solution:

- Using the Azure deploy buttons
- Using [PowerShell](#powershell-script-example)
- Using [CLI Tools](#azure-cli-10-script-example)

### Azure deploy buttons

Use the appropriate button below to deploy:

{{ DEPLOY_LINKS }}
### Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
{{ EXAMPLE_PARAMS }}
### Programmatic deployments

As an alternative to deploying through the Azure Portal (GUI) each solution provides example scripts to deploy the ARM template.  The example commands can be found below along with the name of the script file, which exists in the current directory.

#### PowerShell Script Example

```powershell
{{ PS_SCRIPT }}
```

=======

#### Azure CLI (1.0) Script Example

```bash
{{ BASH_SCRIPT }}
```

## Documentation
- For more information on BIG-IQ VE, see https://support.f5.com/csp/knowledge-center/software/BIG-IQ?module=BIG-IQ%20Centralized%20Management&version=6.1.0 and https://support.f5.com/csp/knowledge-center/cloud/Public%20Cloud/Amazon%20Web%20Services
- For more information on F5 solutions for Azure, including manual configuration procedures for some deployment scenarios, see the Azure section of [Public Cloud Docs](http://clouddocs.f5.com/cloud/public/v1/).

{% if type == 'bigiq' and bigiq_solution == 'cluster' and stack == 'existing-stack' -%}
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
{% endif %}

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

{{ SECRET_UPDATE_TXT }}

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