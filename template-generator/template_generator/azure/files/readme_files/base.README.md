# Deploying the BIG-IP VE in Azure - {{ TITLE_TXT }}

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
- [Service Discovery](#service-discovery)

## Introduction

{{ INTRO_TXT }}

For information on getting started using F5's ARM templates on GitHub, see [Microsoft Azure: Solutions 101](http://clouddocs.f5.com/cloud/public/v1/azure/Azure_solutions101.html).

**Networking Stack Type:** {{ STACK_TYPE_TXT }}

## Prerequisites

- **Important**: When you configure the admin password for the BIG-IP VE in the template, you cannot use the character **#**.  Additionally, there are a number of other special characters that you should avoid using for F5 product user accounts.  See [K2873](https://support.f5.com/csp/article/K2873) for details.
{{ EXTRA_PREREQS }}
## Important configuration notes

> **_CRITICAL:_**  As of Release 6.1.0.0, BIG-IP version 12.1 is no longer supported. If you require BIG-IP version 12.1, you can use a previously released ARM template.  To find a previously released template, from the **Branch** drop-down, click the **Tags** tab, and then select a tag of **v6.0.4.0** or earlier.

- F5 Azure ARM templates that create a new virtual network stack have been moved to the experimental folder.  You can find new-stack templates here: [Experimental Templates](https://github.com/F5Networks/f5-azure-arm-templates/tree/master/experimental)
- All F5 ARM templates include Application Services 3 Extension (AS3) v3.20.0 on the BIG-IP VE.  As of release 4.1.2, all supported templates give the option of including the URL of an AS3 declaration, which you can use to specify the BIG-IP configuration you want on your newly created BIG-IP VE(s).  In templates such as autoscale, where an F5-recommended configuration is deployed by default, specifying an AS3 declaration URL will override the default configuration with your declaration.   See the [AS3 documentation](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/) for details on how to use AS3.   
- There are new options for BIG-IP license bundles, including Per App VE LTM, Advanced WAF, and Per App VE Advanced WAF. See the [the version matrix](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/azure-bigip-version-matrix.md) for details and applicable templates.
- You have the option of using a password or SSH public key for authentication.  If you choose to use an SSH public key and want access to the BIG-IP web-based Configuration utility, you must first SSH into the BIG-IP VE using the SSH key you provided in the template.  You can then create a user account with admin-level permissions on the BIG-IP VE to allow access if necessary.
- See the important note about [optionally changing the BIG-IP Management port](#changing-the-big-ip-configuration-utility-gui-port).
- This template supports service discovery via the Application Services 3 Extension (AS3). See the [Service Discovery section](#service-discovery) for details.
- This template supports telemetry streaming via the F5 Telemetry Streaming extension. See [Telemetry Streaming](#telemetry-streaming) for details.
- This template can send non-identifiable statistical information to F5 Networks to help us improve our templates.  See [Sending statistical information to F5](#sending-statistical-information-to-f5).
- This template supports disabling the auto-phonehome system setting via the allowPhoneHome parameter. See [Overview of the Automatic Update Check and Automatic Phone Home features](https://support.f5.com/csp/article/K15000) for more information.
- This template can be used to create the BIG-IP(s) using a local VHD or Microsoft.Compute image, please see the **customImage** parameter description for more details.
- In order to pass traffic from your clients to the servers, after launching the template, you must create virtual server(s) on the BIG-IP VE.  See [Creating a virtual server](#creating-virtual-servers-on-the-big-ip-ve).
- F5 has created a matrix that contains all of the tagged releases of the F5 ARM templates for Microsoft Azure and the corresponding BIG-IP versions, license types and throughput levels available for a specific tagged release. See [azure-bigip-version-matrix](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/azure-bigip-version-matrix.md).
- F5 ARM templates now capture all deployment logs to the BIG-IP VE in **/var/log/cloud/azure**.  Depending on which template you are using, this includes deployment logs (stdout/stderr), f5-cloud-libs execution logs, recurring solution logs (failover, metrics, and so on), and more.
- Supported F5 ARM templates do not reconfigure existing Azure resources, such as network security groups.  Depending on your configuration, you may need to configure these resources to allow the BIG-IP VE(s) to receive traffic for your application.  Similarly, templates that deploy Azure load balancer(s) do not configure load balancing rules or probes on those resources to forward external traffic to the BIG-IP(s).  You must create these resources after the deployment has succeeded.
- See the **[Configuration Example](#configuration-example)** section for a configuration diagram and description for this solution.
{{ EXTRA_CONFIG_NOTES }}
## Security

This ARM template downloads helper code to configure the BIG-IP system. If you want to verify the integrity of the template, you can open the template and ensure the following lines are present. See [Security Detail](#security-details) for the exact code.
In the *variables* section:

- In the *verifyHash* variable: **script-signature** and then a hashed signature.
- In the *installCloudLibs* variable: **tmsh load sys config merge file /config/verifyHash**.
- In the *installCloudLibs* variable: ensure this includes **tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz**.

Additionally, F5 provides checksums for all of our supported templates. For instructions and the checksums to compare against, see [checksums-for-f5-supported-cft-and-arm-templates-on-github](https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014).

## Tested BIG-IP versions

The following table lists the versions of BIG-IP that have been tested and validated against F5 Azure ARM solution templates.

| Azure BIG-IP Image Version | BIG-IP Version | Build | Solution | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| 15.1.2.10000 | 15.1.2.1 | 0.0.10 | Standalone, Failover, Autoscale | Validated | |
| 14.1.300000 | 14.1.3 | 0.0.7 | Standalone, Failover, Autoscale | Validated | |
| 13.1.304000 | 13.1.3 | 0.0.4 | Standalone, Failover, Autoscale | Not Validated | F5 CFE requires BIG-IP 14.1 or later |
| 12.1.502000 | 12.1.5 | 0.0.2 | Standalone, Failover, Autoscale | Not Validated | F5 CFE requires BIG-IP 14.1 or later |


## Supported instance types and hypervisors

- For a list of supported Azure instance types for this solution, see the [Azure instances for BIG-IP VE](http://clouddocs.f5.com/cloud/public/v1/azure/Azure_singleNIC.html#azure-instances-for-big-ip-ve).

- For a list of versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and Microsoft Azure, see [supported-hypervisor-matrix](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html).

## Help

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

## Configuration Example

The following is an example configuration diagram for this solution deployment. {{ EXAMPLE_TEXT }}

![Configuration Example](../images/azure-example-diagram.png)

{% if nics != '1' and lb_method != 'api' -%}
## Post-Deployment Configuration

Use this section for optional configuration changes after you have deployed the template.

### Additional public IP addresses

This ARM template supports using up to 20 public IP addresses.  After you initially deployed the template, if you now want to include additional public IP addresses, use the following guidance.

#### Adding additional public IP addresses to the deployment

The deployment template supports creation of 1-20 external public IP addresses for application traffic (first one is used for external NIC Self IP).  Follow the steps below to add **additional** public IP addresses to the deployment:

- Create a new Azure public IP address resource in the deployment resource group
- Create a new, secondary IP configuration resource (for example: *myResourceGroupName-ext-ipconfig9*) in the properties of the external Azure network interface (for example: *myResourceGroupName-ext0*)

When you create virtual servers on the BIG-IP VE for these additional addresses, the BIG-IP network virtual server destination IP address should match the private IP addresses of both secondary Azure IP configurations assigned to the backend pool that is referenced by the application's Azure load balancing rule.
{% elif type == 'autoscale' %}
## Post-Deployment Configuration

This solution deploys an ARM template that fully configures BIG-IP VE(s) and handles clustering (DSC) and Azure creation of objects needed for management of those BIG-IP VEs.  However, once deployed the assumption is configuration will be performed on the BIG-IP VE(s) to create virtual servers, pools, and other objects used for processing application traffic.  An example of the steps required to add an application are listed [here](#post-deployment-application-configuration).

### Backup BIG-IP configuration for cluster recovery

The template now automatically saves a BIG-IP back up UCS file (into the **backup** container of the storage account ending in **data000** (it is a Blob container)) every night at 12am, and saves 7 days of back up UCS files.  If you make manual changes to the configuration, we recommend immediately making a backup of your BIG-IP configuration manually and storing the resulting UCS file in the backup container to ensure the master election process functions properly.  Note: If it is necessary to recover from this UCS backup, the system picks the backup file with the latest timestamp.

To manually save the BIG-IP configuration to a UCS file:

1. Backup your BIG-IP configuration (ideally the cluster primary) by creating a [UCS](https://support.f5.com/csp/article/K13132) archive.  Use the following syntax to save the backup UCS file:
    - From the CLI command: ```# tmsh save /sys ucs /var/tmp/original.ucs```
    - From the Configuration utility: **System > Archives > Create**
2. Upload the UCS into the **backup** container of the storage account ending in **data000** (it is a Blob container).

### Post-deployment application configuration

Note: Steps are for an example application on port 443 when behind an ALB (Azure Load Balancer)

1. Add a "Health Probe" to the ALB for port 443, you can choose TCP or HTTP depending on your needs.  This queries each BIG-IP at that port to determine if it is available for traffic.
2. Add a "Load Balancing Rule" to the ALB where the port is 443 and the backend port is also 443 (assuming you are using same port on the BIG-IP), make sure the backend pool is selected (there should only be one backend pool which was created and is managed by the VM Scale set)
3. Add an "Inbound Security Rule" to the Network Security Group (NSG) for port 443 as the NSG is added to the subnet where the BIG-IP VE(s) are deployed - You could optionally just remove the NSG from the subnet as the VM Scale Set is fronted by the ALB.

### Additional Optional Configuration Items

Here are some post-deployment options that are entirely optional but could be useful based on your needs.

#### BIG-IP Lifecycle Management

As new BIG-IP versions are released, existing VM scale sets can be upgraded to use those new images. In an existing implementation, we assume you have created different types of BIG-IP configuration objects (such as virtual servers, pools, and monitors), and you want to retain this BIG-IP configuration after an upgrade. This section describes the process of upgrading and retaining the configuration.

When this ARM template was initially deployed, a storage account was created in the same Resource Group as the VM scale set. This account name ends with **data000*** (the name of storage accounts have to be globally unique, so the prefix is a unique string). In this storage account, the template created a container named **backup**.  We use this backup container to hold backup [UCS](https://support.f5.com/csp/article/K13132) configuration files. Once the UCS is present in the container, you update the scale set "model" to use the newer BIG-IP version. Once the scale set is updated, you upgrade the BIG-IP VE(s). As a part of this upgrade, the provisioning checks the backup container for a UCS file and if one exists, it uploads the configuration (if more than one exists, it uses the latest).

#### To upgrade the BIG-IP VE Image

1. Ensure the configuration is backed up as outlined [here](#backup-big-ip-configuration-for-cluster-recovery)
2. Update the VM Scale Set Model to the new BIG-IP version
    - From PowerShell: Use the PowerShell script in the **scripts** folder in this directory
    - Using the Azure redeploy functionality: From the Resource Group where the ARM template was initially deployed, click the successful deployment and then select to redeploy the template. If necessary, re-select all the same variables, and **only change** the BIG-IP version to the latest.
3. Upgrade the Instances
    1. In Azure, navigate to the VM Scale Set instances pane and verify the *Latest model* does not say **Yes** (it should have a caution sign instead of the word Yes)
    2. Select either all instances at once or each instance one at a time (starting with instance ID 0 and working up).
    3. Click the **Upgrade** action button.

#### Configure Scale Event Notifications

**Note:** Email addresses for notification can now be specified within the solution and will be applied automatically, they can also be configured manually via the VM Scale Set configuration options available within the Azure Portal.

You can add notifications when scale up/down events happen, either in the form of email or webhooks. The following shows an example of adding an email address via the Azure Resources Explorer that receives an email from Azure whenever a scale up/down event occurs.

Log in to the [Azure Resource Explorer](https://resources.azure.com) and then navigate to the Auto Scale settings (**Subscriptions > Resource Groups >** *resource group where deployed* **> Providers > Microsoft.Insights > Autoscalesettings > autoscaleconfig**).  At the top of the screen click Read/Write, and then from the Auto Scale settings, click **Edit**.  Replace the current **notifications** json key with the example below, making sure to update the email address(es). Select PUT and notifications will be sent to the email addresses listed.

```json
    "notifications": [
      {
        "operation": "Scale",
        "email": {
          "sendToSubscriptionAdministrator": false,
          "sendToSubscriptionCoAdministrators": false,
          "customEmails": [
            "email@f5.com"
          ]
        },
        "webhooks": null
      }
    ]
```
{% elif type == 'failover' and nics != '1' and lb_method == 'api' %}
## Post-Deployment Configuration

Use this section for optional configuration changes after you have deployed the template.

### Additional Public IP Addresses - Failover

This ARM template supports using up to 20 public IP addresses for the external 'application' NIC to be used for passing traffic to BIG-IP virtual servers. Each virtual server should be configured with a destination address matching the private IP address value of the Azure IP configuration receiving traffic for the application. In the event the active BIG-IP VE becomes unavailable, the IP configuration(s) are migrated using network failover, seamlessly shifting application traffic to the current active BIG-IP VE (the template now supports [multiple traffic groups](#traffic-group-configuration)).  After you initially deployed the template, if you now want to include additional public IP addresses and/or if you want to add or remove the user-defined routes (UDRs) to be managed by the BIG-IP, use the following guidance.

#### Adding additional public IP addresses to the deployment

The deployment template supports creation of 1-20 external public IP addresses for application traffic (first one is used for external NIC Self IP). Use the following guidance to add **additional** public IP addresses to the deployment:

- Create a new Azure public IP address resource in the deployment resource group.
- Create a new, secondary IP configuration resource (for example: *myResourceGroupName-ext-ipconfig9*) in the properties of the external Azure network interface (for example: *myResourceGroupName-ext0*) of the **active** BIG-IP.
- Ensure a **Virtual Address** exists on the BIG-IP in the appropriate traffic group (such as traffic-group-1), and that the Virtual Address matches the private IP address of the secondary IP configuration you created.
  1. Note: A Virtual Address will automatically be created for each Virtual Server created (if it does not already exist).
  2. Note: This is what is matched on during a failover event to determine which NIC IP configurations to move.
  3. Note: F5 recommends creating the IP configuration on the network interface of the BIG-IP VE that is active for the traffic group assigned to the matching Virtual Address.

When you create virtual servers on the BIG-IP VE for these new additional addresses, the BIG-IP virtual server destination IP address should match the Azure Private IP Address of the IP configuration that corresponds to the Public IP address of your application. See the BIG-IP documentation for specific instructions on creating virtual servers.
{% endif %}

{% if type == 'failover' and lb_method == 'api' -%}
### Enabling Route Failover

This solution supports associating specific sets of self IP addresses with Azure Route Tables using the F5 Cloud Failover Extension.  However, because each environment's managed routes will be different, route failover is configured at deployment time, but disabled by default.  To enable route failover, you must POST an updated CFE declaration to the CFE endpoint (/mgmt/shared/cloud-failover/declare) on one of the BIG-IP devices.

The Cloud Failover Extension documentation describes route failover configuration here: https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/userguide/configuration.html#failover-routes

Below is an example of a declaration that enables route failover. The "resourceGroupName" value is a placeholder; replace that value with the name of the Azure resource group where the template was deployed. To verify that you are using the correct values, you can send a GET request to the CFE endpoint at /mgmt/shared/cloud-failover/declare:

# Initial declaration response (GET):
```json
{
    "class": "Cloud_Failover",
    "environment": "azure",
    "externalStorage": {
        "scopingTags": {
            "f5_cloud_failover_label": "resourceGroupName"
        }
    },
    "failoverAddresses": {
        "scopingTags": {
            "f5_cloud_failover_label": "resourceGroupName"
        }
    },
    "failoverRoutes": {
        "enabled": false,
        "scopingTags": {
            "f5_cloud_failover_label": "resourceGroupName"
        },
        "scopingAddressRanges": [
            {
                "range": "192.168.0.0/32"
            }
        ],
        "defaultNextHopAddresses": {
            "discoveryType": "static",
            "items": [
                "192.168.0.4",
                "192.168.0.5"
            ]
        }
    }
}
```

Replace the scopingAddressRanges array with a list of range objects that includes one range object per user-defined route that this deployment will manage.  Replace the defaultNextHopAddresses.items array with a list of the BIG-IP self IP addresses configured on the devices in this deployment:

# Example declaration enabling route failover (POST):
```json
{
    "class": "Cloud_Failover",
    "environment": "azure",
    "externalStorage": {
        "scopingTags": {
            "f5_cloud_failover_label": "resourceGroupName"
        }
    },
    "failoverAddresses": {
        "scopingTags": {
            "f5_cloud_failover_label": "resourceGroupName"
        }
    },
    "failoverRoutes": {
        "enabled": true,
        "scopingTags": {
            "f5_cloud_failover_label": "resourceGroupName"
        },
        "scopingAddressRanges": [
            {
                "range": "192.168.3.0/24"
            }
        ],
        "defaultNextHopAddresses": {
            "discoveryType": "static",
            "items": [
                "192.168.2.4",
                "192.168.2.5"
            ]
        }
    }
}
```

Next, use the following examples steps to add the required Azure tags to the route table resource:

  - Azure route table: myRouteTable
    - Add tag with key: "f5_cloud_failover_label", value: "resourceGroupName"

In this case, on failover, the routes in the Azure route table ***myRouteTable*** tagged with ***f5_cloud_failover_label: resourceGroupName*** and including user-defined routes matching the **scopingAddressRanges** array are updated to use either 192.168.2.4 or 192.168.2.5(depending on which BIG-IP VE device is active for traffic-group-1) as the next hop virtual appliance.
{% endif -%}

## Documentation

For more information on F5 solutions for Azure, including manual configuration procedures for some deployment scenarios, see the Azure section of [Public Cloud Docs](http://clouddocs.f5.com/cloud/public/v1/).

{% if (type == 'autoscale') %}
### How this solution works

  - **Primary Election Process**<br>
    In the event of a failure or scale-in event that deallocates the primary instance, a new primary instance is elected by the autoscale script based on the following criteria:
    - Last backup time: If only one device has a running configuration, that device is promoted to primary. This is determined based on the lastBackup timestamp, which is set to the beginning of epoch time by default; this date gets updated with sync cluster creation.
    - Lowest management IP address (private): If ***both*** devices have lastBackup set to either a) the default value or b) a non-default value, the device with the lowest private management IP address will be promoted to primary.
  - **Restore From UCS**<br>
    The template now automatically saves a BIG-IP back up UCS file (to the **/backup** directory in the S3 bucket created by the template) every night at 12am, and saves 7 days of back up UCS files. In the event the system needs to restore from a backup UCS file, the UCS with the latest timestamp will be restored when the following conditions are met:
    - No device present has a running configuration. Any device with a running configuration will be promoted to primary before UCS will be restored.
  - **Autoscale Timing**<br>
    This section describes the different autoscale timing intervals and how to override them.
    - Autoscale script execution interval: This interval can be overridden by specifying the clusterUpdateInterval when invoking autoscale.sh.
      - Azure default: 180 seconds. 
        - Usage example (from [Azure Autoscale template](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/supported/autoscale/ltm/via-lb/1nic/existing-stack/payg/azuredeploy.json)): (/usr/bin/f5-rest-node $CLOUD_LIB_DIR/f5-cloud-libs/scripts/runScript.js --output /var/log/cloud/azure/autoscale.log --log-level info --file $CLOUD_LIB_DIR/f5-cloud-libs-azure/scripts/autoscale.sh --shell /bin/bash --cl-args \"**--clusterUpdateInterval 180** --deploymentType ltm --logLevel info --backupUcs 7 --resourceGroup ', resourceGroup().name, ' --vmssName ', variables('vmssName'), ' --userName svc_user --password /config/cloud/.passwd --azureSecretFile /config/cloud/.azCredentials --managementPort ', variables('bigIpMgmtPort'), ' --ntpServer ', parameters('ntpServer'), ' --autoscaleTimeout ', parameters('autoscaleTimeout'), ' --as3Build ', variables('f5AS3Build'), ' --timeZone ', parameters('timeZone'), ' --bigIpModules ', parameters('bigIpModules'), variables('allowUsageAnalytics')[parameters('allowUsageAnalytics')].metricsCmd, ' --appScriptArgs \\\"', variables('commandArgs'), '\\\"', ' --appInsightsKey ', reference(resourceId(variables('appInsightsNameArray')[1], 'Microsoft.Insights/components', variables('appInsightsNameArray')[0]), variables('appInsightsComponentsApiVersion')).InstrumentationKey, '\" --signal AUTOSCALE_SCRIPT_DONE)
    - Primary instance expiration timeout default: 3 minutes. Expiration of this interval causes the re-election of a new primary device, and can be overridden by passing the following parameter to autoscale.js:
      - --primary-disconnected-time (milliseconds)
      - Usage example: **f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/autoscale.js --cloud azure --primary-disconnected-time 90000**. See [f5-cloud-libs usage](https://github.com/F5Networks/f5-cloud-libs/blob/master/USAGE.md) for complete usage information.
    - Autoscale script execution timeout default: 10 minutes. Expiration of this interval causes the autoscale script execution to terminate, and can be overridden by passing the following parameter to autoscale.js:
      - --autoscale-timeout (minutes)
      - Usage example: **f5-rest-node /config/cloud/azure/node_modules/@f5devcentral/f5-cloud-libs/scripts/autoscale.js --cloud azure --autoscale-timeout 5**. See [f5-cloud-libs usage](https://github.com/F5Networks/f5-cloud-libs/blob/master/USAGE.md) for complete usage information.

### Service Principal Authentication

This solution requires access to the Azure API to correctly configure both the BIG-IP VE(s) as well as the Azure resources managed by the solution.  The most efficient and security-conscious way to handle this is to utilize Azure service principal authentication, for all the typical security reasons.  The following information describes the initial configuration of an Azure service principal application for use with this solution.

**Minimum Required Access:** The service principal account must have read/write permissions to the following objects and it is *recommended* to apply the built-in **Contributor** role to the account being used. If applying a custom role, it must have *read/write* permissions to the following resources:

- Microsoft.Network/*
- Microsoft.Storage/*
{% elif type == 'autoscale' %}
**Minimum Required Access:** The service principal account must have read permissions to the following objects and it is *recommended* to apply the built-in **Reader** role to the account being used. If applying a custom role, it must have at least *read* permissions to the following resources:

- Microsoft.Compute/*
- Microsoft.Network/*
- Microsoft.Storage/*
{%- endif %}
{% if (type == 'autoscale') %}
**NOTE:** Service principal information is stored locally in the **/config/cloud/.azCredentials** file.  If for any reason you need to update the service principal information, you must manually edit the .azCredentials file on all BIG-IP systems.

#### 1. Azure Portal

Follow the steps outlined in the [Azure Portal documentation](https://azure.microsoft.com/en-us/documentation/articles/resource-group-create-service-principal-portal/) to generate the service principal.

#### 2. Azure CLI

This method can be used with either the [Azure CLI v2.0 (Python)](https://github.com/Azure/azure-cli) or the [Azure Cross-Platform CLI (npm module)](https://github.com/Azure/azure-xplat-cli).

##### Using the Python Azure CLI v2.0 - requires just one step

```shell
az ad sp create-for-rbac
```

##### Using the Node.js cross-platform CLI - requires additional steps for setting up

[Link](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-authenticate-service-principal-cli)

#### 3. Azure PowerShell

Follow the steps outlined in the [Azure Powershell documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-authenticate-service-principal) to generate the service principal.

After creating the service principal application in the same subscription where the template will be deployed, you should be in possession of the client ID (sometimes called the application ID), tenant ID, and service principal secret required in the template parameters.  Ensuring this is correctly configured prior to deploying this ARM template will reduce post-deployment troubleshooting.
{%- endif -%}
{%- if (type == 'standalone') or (type == 'autoscale') %}
## Creating virtual servers on the BIG-IP VE

In order to pass traffic from your clients to the servers through the BIG-IP system, you must create a virtual server on the BIG-IP VE. To create a BIG-IP virtual server you need to know the private IP address of the IP configuration(s) for each BIG-IP VE network interface created by the template. If you need additional virtual servers for your applications/servers, you can add more secondary IP configurations on the Azure network interface, and corresponding virtual servers on the BIG-IP system. See [virtual-network-multiple-ip-addresses-portal](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-network-multiple-ip-addresses-portal) for information on multiple IP addresses.

### To create virtual servers on the BIG-IP system

1. Once your BIG-IP VE has launched, open the BIG-IP VE Configuration utility.
2. On the Main tab, click **Local Traffic > Virtual Servers** and then click the **Create** button.
3. In the **Name** field, give the Virtual Server a unique name.
4. In the **Destination/Mask** field, type the Azure secondary private IP address. **Note**: *For 1 NIC BIG-IP VEs, the virtual server configuration uses a wildcard destination address (example: 0.0.0.0/0) and should use different ports (if behind an ALB) or hostnames to differentiate services.*
5. In the **Service Port** field, type the appropriate port.
6. Configure the rest of the virtual server as appropriate.
7. In the Resources section, from the **Default Pool** list, select the name of the pool you want to use.
8. Click the **Finished** button.
9. Repeat as necessary.
{% elif type == 'failover' and nics != '1' and lb_method == 'api' %}
## Creating virtual servers on the BIG-IP VE

In order to pass traffic from your clients to the servers through the BIG-IP system, you must create a virtual server on the BIG-IP VE. To create a BIG-IP virtual server you need to know the private IP address of the secondary IP configuration(s) for each BIG-IP VE network interface created by the template. If you need additional virtual servers for your applications/servers, you can add more secondary IP configurations on the Azure network interface, and corresponding virtual servers on the BIG-IP system. See [virtual-network-multiple-ip-addresses-portal](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-network-multiple-ip-addresses-portal) for information on multiple IP addresses.

In this template, each Azure public IP address is associated with a secondary IP configuration attached to the external network interface of the BIG-IP VE. Because this IP configuration will be moved to the active BIG-IP device, you need to create a single virtual server in **traffic-group-1** that corresponds to the private IP address of that IP configuration.

1. Once your BIG-IP VE has launched, open the BIG-IP VE Configuration utility.
2. On the Main tab, click **Local Traffic > Virtual Servers** and then click the **Create** button.
3. In the **Name** field, give the Virtual Server a unique name.
4. In the **Destination/Mask** field, type the private IP address of the secondary IP configuration associated with the Azure public IP address for your application (for example: 10.0.1.10/32).
5. In the **Service Port** field, type the appropriate port.
6. Configure the rest of the virtual server as appropriate.
7. In the Resources section, from the **Default Pool** list, select the name of the pool you want to use.
8. Click the **Finished** button.
9. Repeat as necessary.

When you have completed the virtual server configuration, you may modify the virtual addresses to use an alternative Traffic Group using the following guidance.

1. On the Main tab, click **Local Traffic > Virtual Servers**.
2. On the Menu bar, click the **Virtual Address List** tab.
3. Click the address of one of the virtual servers you just created.
4. From the **Traffic Group** list, select **traffic-group-2** (or the additional traffic group you created previously).
5. Click **Update**.
6. Repeat for each virtual server.

{% elif type == 'failover' and lb_method == 'via-lb' and nics == '3' %}
## Creating virtual servers on the BIG-IP VE

In order to pass traffic from your clients to the servers through the BIG-IP system, you must create a virtual server on the BIG-IP VE. To create a BIG-IP virtual server you need to know the private IP address of the secondary IP configuration(s) for each BIG-IP VE network interface created by the template. If you need additional virtual servers for your applications/servers, you can add more secondary IP configurations on the Azure network interface, and corresponding virtual servers on the BIG-IP system. See [virtual-network-multiple-ip-addresses-portal](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-network-multiple-ip-addresses-portal) for information on multiple IP addresses.

In this template, the Azure public IP address is associated with an Azure Load Balancer that forwards traffic to a backend pool that includes secondary IP configurations for *each* BIG-IP network interface.  You must create a single virtual server with a destination that matches both private IP addresses in the Azure Load Balancer's backend pool.  In this example, the backend pool private IP addresses are 10.0.1.36 and 10.0.1.37.

1. Once your BIG-IP VE has launched, open the BIG-IP VE Configuration utility.
2. On the Main tab, click **Local Traffic > Virtual Servers** and then click the **Create** button.
3. In the **Name** field, give the Virtual Server a unique name.
4. In the **Destination/Mask** field, type the destination address (for example: 10.0.1.32/27).
5. In the **Service Port** field, type the appropriate port.
6. Configure the rest of the virtual server as appropriate.
7. In the Resources section, from the **Default Pool** list, select the name of the pool you want to use.
8. Click the **Finished** button.
9. Repeat as necessary.

If network failover is disabled (default), when you have completed the virtual server configuration, you must modify the virtual addresses to use Traffic Group None using the following guidance.

1. On the Main tab, click **Local Traffic > Virtual Servers**.
2. On the Menu bar, click the **Virtual Address List** tab.
3. Click the address of one of the virtual servers you just created.
4. From the **Traffic Group** list, select **None**.
5. Click **Update**.
6. Repeat for each virtual server.

If network failover is enabled (if, for example, you have deployed the HA Cluster 3 NIC template, or manually enabled network failover with traffic groups), when you have completed the virtual server configuration, you may modify the virtual addresses to use an alternative Traffic Group using the following guidance.

1. On the Main tab, click **Local Traffic > Virtual Servers**.
2. On the Menu bar, click the **Virtual Address List** tab.
3. Click the address of one of the virtual servers you just created.
4. From the **Traffic Group** list, select **traffic-group-2** (or the additional traffic group you created previously).
5. Click **Update**.
6. Repeat for each virtual server.

{% elif type == 'failover' and lb_method == 'via-lb' and nics == '1' %}

## Creating virtual servers on the BIG-IP VE

In order to pass traffic from your clients to the servers through the BIG-IP system, you must create a virtual server on the BIG-IP VE.

In this template, the Azure public IP address is associated with an Azure Load Balancer that forwards traffic to a backend pool that includes the primary (self) IP configurations for *each* BIG-IP network interface.  Because traffic is destined for the self IP addresses of the BIG-IP VEs, you must create a single virtual server with a wildcard destination in Traffic Group **None**.

1. Once your BIG-IP VE has launched, open the BIG-IP VE Configuration utility.
2. On the Main tab, click **Local Traffic > Virtual Servers** and then click the **Create** button.
3. In the **Name** field, give the Virtual Server a unique name.
4. In the **Destination/Mask** field, type the destination address ( for example: 0.0.0.0/0).
5. In the **Service Port** field, type the appropriate port.
6. Configure the rest of the virtual server as appropriate.
7. In the Resources section, from the **Default Pool** list, select the name of the pool you want to use.
8. Click the **Finished** button.
9. Repeat as necessary.

When you have completed the virtual server configuration, you must modify the virtual addresses to use Traffic Group None using the following guidance.

1. On the Main tab, click **Local Traffic > Virtual Servers**.
2. On the Menu bar, click the **Virtual Address List** tab.
3. Click the address of one of the virtual servers you just created.
4. From the **Traffic Group** list, select **None**.
5. Click **Update**.
6. Repeat for each virtual server.
{%- endif -%}
{% if type == 'failover' and lb_method == 'api' %}
### Traffic Group Configuration

This template supports associating Azure NIC IP Configurations and Route Table resources with up to two BIG-IP traffic groups, allowing each BIG-IP VE device to process traffic for applications associated with the traffic group for which the device is active.  Use the following guidance to configure multiple traffic groups.  Note you must create the **f5_tg** on any route tables with routes that will be managed by BIG-IP VE. At a minimum, these route tables must be tagged with a default value of **traffic-group-1**.

1. Select the route table you want to associate with the second traffic group (in our example, the second traffic group name is **traffic-group-2**).
2. From the route table Tags blade, select the **f5_tg** tag.
3. Modify the tag value to **traffic-group-2** and then save the tag.
4. From the BIG-IP VE management Configuration utility, click **Device Management > Traffic Groups > Create**, and then complete the following.
    - *Name*: **traffic-group-2**
    - *Failover Order*: Select the preferred order of the devices for this traffic group; F5 recommends setting the current standby device as the preferred device for this second traffic group, so that each traffic group has a different preferred device (device will become active after creating the traffic group).
    - Click **Create Traffic Group**.
5. Ensure the BIG-IP **Virtual Address** corresponding with the created virtual servers is in the desired traffic group.
    - Note: NIC IP Configurations are mapped to a specific traffic group by the Virtual Address configuration of the BIG-IP.
    - Note: You can find the Virtual Address list by browsing to Local Traffic->Virtual Servers->Virtual Address List.
{% endif %}

### Deploying Custom Configuration to the BIG-IP (Azure Virtual Machine)

Once the solution has been deployed there may be a need to perform some additional configuration of the BIG-IP.  This can be accomplished via traditional methods such as via the GUI, logging into the CLI or using the REST API.  However, depending on the requirements it might be preferred to perform this custom configuration as a part of the initial deployment of the solution.  This can be accomplished in the below manner.

Within the Azure Resource Manager (ARM) template there is a variable called **customConfig**, this contains text similar to "### START (INPUT) CUSTOM CONFIGURATION", that can be replaced with custom shell scripting to perform additional configuration of the BIG-IP.  An example of what it would look like to configure the f5.ip_forwarding iApp is included below.

Warning: F5 does not support the template if you change anything other than the **customConfig** ARM template variable.

```json
"variables": {
    "customConfig": "### START (INPUT) CUSTOM CONFIGURATION HERE\ntmsh create sys application service my_deployment { device-group none template f5.ip_forwarding traffic-group none variables replace-all-with { basic__addr { value 0.0.0.0 } basic__forward_all { value No } basic__mask { value 0.0.0.0 } basic__port { value 0 } basic__vlan_listening { value default } options__advanced { value no }options__display_help { value hide } } }"
}
```

### Changing the BIG-IP Configuration utility (GUI) port

Depending on the deployment requirements, the default management port for the BIG-IP may need to be changed. To change the Management port, see [Changing the Configuration utility port](https://clouddocs.f5.com/cloud/public/v1/azure/Azure_singleNIC.html#azureconfigport) for instructions.

***Important***: The default port provisioned is dependent on 1) which BIG-IP version you choose to deploy as well as 2) how many interfaces (NICs) are configured on that BIG-IP. BIG-IP v13.x and later in a single-NIC configuration uses port 8443. All prior BIG-IP versions default to 443 on the MGMT interface.

***Important***: If you perform the procedure to change the port, you must check the Azure Network Security Group associated with the interface on the BIG-IP that was deployed and adjust the ports accordingly.

### Service Discovery

This template previously supported configuring service discovery using the f5.service_discovery iApp template.  That iApp has been deprecated and removed from this template.  You can now configure service discovery using the F5 AS3 extension, which is installed by all ARM templates by default.  See the official AS3 [documentation](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/service-discovery.html) and the iApp migration [guide](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/iapp-migration.md) for more information and examples.

### Telemetry Streaming

This template previously supported configuring device telemetry using the f5.cloud_logger iApp template.  That iApp has been deprecated and removed from this template.  You can now configure telemetry streaming using the F5 Telemetry Streaming extension.  See the official TS [documentation](https://clouddocs.f5.com/products/extensions/f5-telemetry-streaming/latest/) and the iApp migration [guide](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/iapp-migration.md) for installation steps and examples.

### Sending statistical information to F5

All of the F5 templates now have an option to send anonymous statistical data to F5 Networks to help us improve future templates.
None of the information we collect is personally identifiable, and only includes:

- Customer ID: this is a hash of the customer ID, not the actual ID
- Deployment ID: hash of stack ID
- F5 template name
- F5 template version
- Cloud Name
- Azure region
- BIG-IP version
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
    "verifyHash": "[concat(variables('singleQuote'), 'cli script /Common/verifyHash {\nproc script::run {} {\n        if {[catch {\n            set hashes(f5-cloud-libs.tar.gz) db8cb32226babb7557c05884987fb4542498cfc90b0117fcc5ec9de203caab18f1e12ec09161151696872f12ca342f2fa2259dd9dfd76906621b65345c76b5b2\n            set hashes(f5-cloud-libs-aws.tar.gz) 076c969cbfff12efacce0879820262b7787c98645f1105667cc4927d4acfe2466ed64c777b6d35957f6df7ae266937dde42fef4c8b1f870020a366f7f910ffb5\n            set hashes(f5-cloud-libs-azure.tar.gz) 9037203b1af31288ba6993204a2abf3bd660f62e7dfb2d5825909dd69133ce5b4f5c725afabd7d2acaa693669c878daa04a6375314d985ba07c8a36dccc61c5a\n            set hashes(f5-cloud-libs-gce.tar.gz) 1677835e69967fd9882ead03cbdd24b426627133b8db9e41f6de5a26fef99c2d7b695978ac189f00f61c0737e6dbb638d42dea43a867ef4c01d9507d0ee1fb2f\n            set hashes(f5-cloud-libs-openstack.tar.gz) 5c83fe6a93a6fceb5a2e8437b5ed8cc9faf4c1621bfc9e6a0779f6c2137b45eab8ae0e7ed745c8cf821b9371245ca29749ca0b7e5663949d77496b8728f4b0f9\n            set hashes(f5-cloud-libs-consul.tar.gz) a32aab397073df92cbbba5067e5823e9b5fafca862a258b60b6b40aa0975c3989d1e110f706177b2ffbe4dde65305a260a5856594ce7ad4ef0c47b694ae4a513\n            set hashes(asm-policy-linux.tar.gz) 63b5c2a51ca09c43bd89af3773bbab87c71a6e7f6ad9410b229b4e0a1c483d46f1a9fff39d9944041b02ee9260724027414de592e99f4c2475415323e18a72e0\n            set hashes(f5.http.v1.2.0rc4.tmpl) 47c19a83ebfc7bd1e9e9c35f3424945ef8694aa437eedd17b6a387788d4db1396fefe445199b497064d76967b0d50238154190ca0bd73941298fc257df4dc034\n            set hashes(f5.http.v1.2.0rc6.tmpl) 811b14bffaab5ed0365f0106bb5ce5e4ec22385655ea3ac04de2a39bd9944f51e3714619dae7ca43662c956b5212228858f0592672a2579d4a87769186e2cbfe\n            set hashes(f5.http.v1.2.0rc7.tmpl) 21f413342e9a7a281a0f0e1301e745aa86af21a697d2e6fdc21dd279734936631e92f34bf1c2d2504c201f56ccd75c5c13baa2fe7653213689ec3c9e27dff77d\n            set hashes(f5.aws_advanced_ha.v1.3.0rc1.tmpl) 9e55149c010c1d395abdae3c3d2cb83ec13d31ed39424695e88680cf3ed5a013d626b326711d3d40ef2df46b72d414b4cb8e4f445ea0738dcbd25c4c843ac39d\n            set hashes(f5.aws_advanced_ha.v1.4.0rc1.tmpl) de068455257412a949f1eadccaee8506347e04fd69bfb645001b76f200127668e4a06be2bbb94e10fefc215cfc3665b07945e6d733cbe1a4fa1b88e881590396\n            set hashes(f5.aws_advanced_ha.v1.4.0rc2.tmpl) 6ab0bffc426df7d31913f9a474b1a07860435e366b07d77b32064acfb2952c1f207beaed77013a15e44d80d74f3253e7cf9fbbe12a90ec7128de6facd097d68f\n            set hashes(f5.aws_advanced_ha.v1.4.0rc3.tmpl) 2f2339b4bc3a23c9cfd42aae2a6de39ba0658366f25985de2ea53410a745f0f18eedc491b20f4a8dba8db48970096e2efdca7b8efffa1a83a78e5aadf218b134\n            set hashes(f5.aws_advanced_ha.v1.4.0rc4.tmpl) 2418ac8b1f1884c5c096cbac6a94d4059aaaf05927a6a4508fd1f25b8cc6077498839fbdda8176d2cf2d274a27e6a1dae2a1e3a0a9991bc65fc74fc0d02ce963\n            set hashes(f5.aws_advanced_ha.v1.4.0rc5.tmpl) 5e582187ae1a6323e095d41eddd41151d6bd38eb83c634410d4527a3d0e246a8fc62685ab0849de2ade62b0275f51264d2deaccbc16b773417f847a4a1ea9bc4\n            set hashes(asm-policy.tar.gz) 2d39ec60d006d05d8a1567a1d8aae722419e8b062ad77d6d9a31652971e5e67bc4043d81671ba2a8b12dd229ea46d205144f75374ed4cae58cefa8f9ab6533e6\n            set hashes(deploy_waf.sh) 1a3a3c6274ab08a7dc2cb73aedc8d2b2a23cd9e0eb06a2e1534b3632f250f1d897056f219d5b35d3eed1207026e89989f754840fd92969c515ae4d829214fb74\n            set hashes(f5.policy_creator.tmpl) 06539e08d115efafe55aa507ecb4e443e83bdb1f5825a9514954ef6ca56d240ed00c7b5d67bd8f67b815ee9dd46451984701d058c89dae2434c89715d375a620\n            set hashes(f5.service_discovery.tmpl) 4811a95372d1dbdbb4f62f8bcc48d4bc919fa492cda012c81e3a2fe63d7966cc36ba8677ed049a814a930473234f300d3f8bced2b0db63176d52ac99640ce81b\n            set hashes(f5.cloud_logger.v1.0.0.tmpl) 64a0ed3b5e32a037ba4e71d460385fe8b5e1aecc27dc0e8514b511863952e419a89f4a2a43326abb543bba9bc34376afa114ceda950d2c3bd08dab735ff5ad20\n            set hashes(f5-appsvcs-3.18.0-4.noarch.rpm) ba71c6e1c52d0c7077cdb25a58709b8fb7c37b34418a8338bbf67668339676d208c1a4fef4e5470c152aac84020b4ccb8074ce387de24be339711256c0fa78c8\n\n            set file_path [lindex $tmsh::argv 1]\n            set file_name [file tail $file_path]\n\n            if {![info exists hashes($file_name)]} {\n                tmsh::log err \"No hash found for $file_name\"\n                exit 1\n            }\n\n            set expected_hash $hashes($file_name)\n            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n            if { $expected_hash eq $computed_hash } {\n                exit 0\n            }\n            tmsh::log err \"Hash does not match for $file_path\"\n            exit 1\n        }]} {\n            tmsh::log err {Unexpected error in verifyHash}\n            exit 1\n        }\n    }\n    script-signature U6njo2bmHHJ86qS/a1+7+QFIIOV9VJzaRnoVoOsB9KjHkWiWYChAT+QQWtyAFgMSG9il8Ol4pShWlIJVc5ldJMp37K3K+CDYBjeNVai4FQQvekjsurl+L1CFrwd6drMYSxbjSxGWCHcZlkZFrskaSej6xzo+scB4aeD7z3M2om7Iov8nq4x3S9tTgNHFI9XnLGGh0pe+I5CamnB/fvrHYStYcdnI36BLynggB6O8/hYocXfmGKjY5Td9gA+ziq6OQHoxtzjzguyeptHa8WsCB66gxg7TIOLDK9DfoSpQbIKyNs+BNL91Q6RqygfQdUrrAYrtN2RYtKkmK8XRs77Vlg==\n    signing-key /Common/f5-irule\n}', variables('singleQuote'))]",
    "installCloudLibs": "[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit 1\nfi\necho loaded verifyHash\n\nconfig_loc=\"/config/cloud/\"\nhashed_file_list=\"${config_loc}f5-cloud-libs.tar.gz {{ f5_as3_latest_build }} ${config_loc}f5-cloud-libs-azure.tar.gz\"\nfor file in $hashed_file_list; do\necho \"verifying $file\"\n/usr/bin/tmsh run cli script verifyHash $file\nif [ $? != 0 ]; then\necho \"$file is not valid\"\nexit 1\nfi\necho \"verified $file\"\ndone\necho \"expanding $hashed_file_list\"\ntar xfz /config/cloud/f5-cloud-libs.tar.gz --warning=no-unknown-keyword -C /config/cloud/azure/node_modules/@f5devcentral\ntar xfz /config/cloud/f5-cloud-libs-azure.tar.gz --warning=no-unknown-keyword -C /config/cloud/azure/node_modules/@f5devcentral\ntouch /config/cloud/cloudLibsReady', variables('singleQuote'))]",
```
{% if type == 'failover' and lb_method == 'api' %}
### Updating encrypted files

This template stores certain sensitive information in encrypted file(s) on the BIG-IP.  If that information needs to be updated after initial deployment, follow the below steps.

Note: The following example will update **/config/cloud/.azCredentials**.

- Login to the BIG-IP(s).
- Locate the file to update: **/config/cloud/.azCredentials**
- Decrypt the contents of the file (Note: --symmetric is **required**  if using symmetric encryption):

  ``` bash
  /usr/bin/f5-rest-node /config/cloud/azure/node_modules/\@f5devcentral/f5-cloud-libs/scripts/decryptDataFromFile.js --data-file /config/cloud/.azCredentials --symmetric
  >> output <<
  ```

- Edit contents as required (can save to file, etc.)
- Encrypt updated contents (Note: --data can also be used if updated contents are not in a file):

  ```bash
  f5-rest-node /config/cloud/azure/node_modules/\@f5devcentral/f5-cloud-libs/scripts/encryptDataToFile.js --data-file <file> --out-file /config/cloud/.azCredentials --symmetric
  ```

- Delete any temporary files created (if necessary)
{% endif %}
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