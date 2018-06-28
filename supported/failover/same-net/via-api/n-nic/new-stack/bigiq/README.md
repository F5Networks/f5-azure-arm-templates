# Deploying the BIG-IP VE in Azure - HA Cluster (Active/Standby)

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

This solution uses an ARM template to launch two BIG-IP VEs in an Active/Standby configuration with network failover enabled (the template now supports [multiple traffic groups](#traffic-group-configuration) which enables active/active deployments). Each pair of BIG-IP VEs is deployed in an Azure Availability Set, and can therefore be spread across different update and fault domains. Each BIG-IP VE has 3 network interfaces (NICs), one for management, one for external traffic, and one for internal traffic.

Traffic flows from the client through BIG-IP VE to the application servers. This is the standard 'on-premise-like' cloud design where the  BIG-IP VE instance is running with a management interface, a front-end application traffic (external) interface, and back-end application (internal) interface. This template is a result of Azure now supporting multiple public-to-private IP address mappings per NIC.

This template supports creating up to 20 additional public/private IP address configurations for the external 'application' NIC to be used for passing traffic to BIG-IP virtual servers.

The template also supports updating the next hop of Azure User-Defined Routes (UDRs) to use the active BIG-IP VEs internal self IP address.

The BIG-IP VEs have the [Local Traffic Manager (LTM)](https://f5.com/products/big-ip/local-traffic-manager-ltm) module enabled to provide advanced traffic management functionality. This means you can also configure the BIG-IP VE to enable F5's L4/L7 security features, access control, and intelligent traffic management.

For information on getting started using F5's ARM templates on GitHub, see [Microsoft Azure: Solutions 101](http://clouddocs.f5.com/cloud/public/v1/azure/Azure_solutions101.html).

**Networking Stack Type:** This solution deploys into a new networking stack, which is created along with the solution.

## Prerequisites

- **Important**: When you configure the admin password for the BIG-IP VE in the template, you cannot use the character **#**.  Additionally, there are a number of other special characters that you should avoid using for F5 product user accounts.  See [K2873](https://support.f5.com/csp/article/K2873) for details.
- This template requires a service principal.  See the [Service Principal Setup section](#service-principal-authentication) for details, including required permissions.
- To indicate that the next hop of a user-defined route (UDR) should be updated during failover, you must configure each UDR's parent route table resource with an Azure tag with the key name **f5_ha** and the value of **self_2nic** (this is the default self IP name created by the template; if necessary, this can be the name of a different self IP address onfigured on the the BIG-IP VE).  You must also create an Azure tag with the key **f5_tg** and value of **traffic-group-1** (or the name of a different traffic group you have configured on the BIG-IP VE).  For details, see [Customizing the Next Hop of Azure User-Defined Routes](#customizing-the-next-hop-of-azure-user-defined-routes).
- This solution uses calls to the Azure REST API to read and update Azure resources such as storage accounts, network interfaces, and route tables.  For the solution to function correctly, you must ensure that the BIG-IP(s) can connect to the Azure REST API on port 443.
- This solution uses calls to the Azure REST API to read and update Azure resources, this has specifically been tested in Azure Commercial Cloud.  Additional cloud environments such as Azure Goverment, Azure Germany and Azure China cloud have not yet been tested.
- You must have a [BIG-IQ device](https://f5.com/products/big-iq-centralized-management) with a pool of BIG-IP BYOL licenses to use this template (see the PAYG and BYOL templates for other options). This solution supports the two most recent versions of BIG-IQ (see the [Version Matrix](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/azure-bigip-version-matrix.md) for specific versions), and your BIG-IQ system must have at least 2 NICs.

## Important configuration notes

- You have the option of using a password or SSH public key for authentication.  If you choose to use an SSH public key and want access to the BIG-IP web-based Configuration utility, you must first SSH into the BIG-IP VE using the SSH key you provided in the template.  You can then create a user account with admin-level permissions on the BIG-IP VE to allow access if necessary.
- See the important note about [optionally changing the BIG-IP Management port](#changing-the-big-ip-configuration-utility-gui-port).
- This template supports service discovery.  See the [Service Discovery section](#service-discovery) for details.
- F5 has created an iApp for configuring logging for BIG-IP modules to be sent to a specific set of cloud analytics solutions.  See [Logging iApp](#logging-iapp).
- This template can send non-identifiable statistical information to F5 Networks to help us improve our templates.  See [Sending statistical information to F5](#sending-statistical-information-to-f5).
- This template can be used to create the BIG-IP(s) using a local VHD or Microsoft.Compute image, please see the **customImage** parameter description for more details.
- In order to pass traffic from your clients to the servers, after launching the template, you must create virtual server(s) on the BIG-IP VE.  See [Creating a virtual server](#creating-virtual-servers-on-the-big-ip-ve).
- F5 has created a matrix that contains all of the tagged releases of the F5 ARM templates for Microsoft Azure and the corresponding BIG-IP versions, license types and throughputs available for a specific tagged release. See [azure-bigip-version-matrix](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/azure-bigip-version-matrix.md).
- F5 ARM templates now capture all deployment logs to the BIG-IP VE in **/var/log/cloud/azure**.  Depending on which template you are using, this includes deployment logs (stdout/stderr), f5-cloud-libs execution logs, recurring solution logs (failover, metrics, and so on), and more.
- Supported F5 ARM templates do not reconfigure existing Azure resources, such as network security groups.  Depending on your configuration, you may need to configure these resources to allow the BIG-IP VE(s) to receive traffic for your application.  Similarly, templates that deploy Azure load balancer(s) do not configure load balancing rules or probes on those resources to forward external traffic to the BIG-IP(s).  You must create these resources after the deployment has succeeded.
- See the **[Configuration Example](#configuration-example)** section for a configuration diagram and description for this solution.
- This template has some optional post-deployment configuration.  See the [Post-Deployment Configuration section](#post-deployment-configuration) for details.
- This template now supports associating Azure NIC IP configurations with up to two BIG-IP traffic groups, allowing each BIG-IP VE device to process traffic for applications associated with the traffic group for which the device is active.  See [Traffic Group Configuration](#traffic-group-configuration) for instructions.
- Persistence and connection mirroring are now supported in this template.  It also supports mirroring of APM sessions.
- The BIG-IP VE failover log can be found at **/var/log/cloud/azure/azureFailover.log**.
- When configuring the template, you have the option of selecting 0 (zero) public IP addresses.  If you select 0 public IP addresses, the BIG-IP systems **will not** create any additional IP configurations on the Azure network interfaces; however, failover of UDR next hop is still supported.  If you create IP configurations post-deployment and would like them to failover, see the [Post-Deployment Configuration section](#post-deployment-configuration) for details.
- This template may deploy additional NICs using the parameter **numberOfAdditionalNics**, if doing so it will preconfigure the BIG-IP VLAN(s) and place the interfaces into the corresponding VLAN based on the subnet name(s) provided in the parameter **additionalNicLocation**.  Be aware that after the template deploys, the BIG-IP self IP address(es) need to be created that correspond to the Azure IP Config object for that NIC.  You must also set the IP Config object to a **static** address instead of **dynamic** to ensure it does not change on reboot.
- Adding additional NIC's post-deployment is possible, it requires creating an additional NIC, powering off the VM and adding the network interface to the VM. See Microsoft documentation for more details on adding a NIC to an existing VM. **Important**: For failover to occur, each set of additional NIC's created must be named exactly the same except for the last character, such as **additionalnic0** and **additionalnic1**.
- The templates now support BIG-IQ licensing using an [ELA](https://www.f5.com/pdf/licensing/big-ip-virtual-edition-enterprise-licensing-agreement-overview.pdf)/subscription pool, which enables self-licensing of BIG-IP virtual editions (VEs).

## Security

This ARM template downloads helper code to configure the BIG-IP system. If you want to verify the integrity of the template, you can open the template and ensure the following lines are present. See [Security Detail](#security-details) for the exact code.
In the *variables* section:

- In the *verifyHash* variable: **script-signature** and then a hashed signature.
- In the *installCloudLibs* variable: **tmsh load sys config merge file /config/verifyHash**.
- In the *installCloudLibs* variable: ensure this includes **tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz**.

Additionally, F5 provides checksums for all of our supported templates. For instructions and the checksums to compare against, see [checksums-for-f5-supported-cft-and-arm-templates-on-github](https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014).

## Supported BIG-IP versions

The following is a map that shows the available options for the template parameter **bigIpVersion** as it corresponds to the BIG-IP version itself. Only the latest version of BIG-IP VE is posted in the Azure Marketplace. For older versions, see downloads.f5.com.

| Azure BIG-IP Image Version | BIG-IP Version |
| --- | --- |
| 13.1.0200 | 13.1.0 Build 0.0.6 |
| 12.1.303000 | 12.1.3.3 Build 0.0.1 |
| latest | This will select the latest BIG-IP version available |

## Supported instance types and hypervisors

- For a list of supported Azure instance types for this solution, see the [Azure instances for BIG-IP VE](http://clouddocs.f5.com/cloud/public/v1/azure/Azure_singleNIC.html#azure-instances-for-big-ip-ve).

- For a list of versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and Microsoft Azure, see [supported-hypervisor-matrix](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html).

## Help

Because this template has been created and fully tested by F5 Networks, it is fully supported by F5. This means you can get assistance if necessary from [F5 Technical Support](https://support.f5.com/csp/article/K40701984).

### Community Help

We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 ARM templates. There are F5 employees who are members of this community who typically monitor the channel Monday-Friday 9-5 PST and will offer best-effort assistance. This slack channel community support should **not** be considered a substitute for F5 Technical Support for supported templates. See the [Slack Channel Statement](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/slack-channel-statement.md) for guidelines on using this channel.

## Installation

You have three options for deploying this solution:

- Using the Azure deploy buttons
- Using [PowerShell](#powershell-script-example)
- Using [CLI Tools](#azure-cli-10-script-example)

### Azure deploy buttons

Use the appropriate button below to deploy:

- **BIGIQ**: This allows you to launch the template using an existing BIG-IQ device with a pool of licenses to license the BIG-IP VE(s).

  [![Deploy to Azure](http://azuredeploy.net/deploybutton.png)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.2.0.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-api%2Fn-nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json)

### Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| adminUsername | Yes | User name for the Virtual Machine. |
| authenticationType | Yes | Type of authentication to use on the Virtual Machine, password based authentication or key based authentication. |
| adminPasswordOrKey | Yes | Password or SSH public key to login to the Virtual Machine. Note: There are a number of special characters that you should avoid using for F5 product user accounts.  See [K2873](https://support.f5.com/csp/article/K2873) for details. Note: If using key-based authentication, this should be the public key as a string, typically starting with **---- BEGIN SSH2 PUBLIC KEY ----** and ending with **---- END SSH2 PUBLIC KEY ----**. |
| dnsLabel | Yes | Unique DNS Name for the Public IP address used to access the Virtual Machine. |
| instanceName | Yes | Name of the Virtual Machine. |
| instanceType | Yes | Instance size of the Virtual Machine. |
| imageName | Yes | F5 SKU (image) to you want to deploy. Note: The disk size of the VM will be determined based on the option you select.  **Important**: If intending to provision multiple modules, ensure the appropriate value is selected, such as **Best** instead of **Good**. |
| bigIpVersion | Yes | F5 BIG-IP version you want to use. |
| bigIqAddress | Yes | The IP address (or hostname) for the BIG-IQ to be used when licensing the BIG-IP.  Note: The BIG-IP will make a REST call to the BIG-IQ (already existing) to let it know a BIG-IP needs to be licensed. It will then license the BIG-IP using the provided BIG-IQ credentials and license pool. |
| bigIqUsername | Yes | The BIG-IQ username to use during BIG-IP licensing via BIG-IQ. |
| bigIqPassword | Yes | The BIG-IQ password to use during BIG-IP licensing via BIG-IQ. |
| bigIqLicensePoolName | Yes | The BIG-IQ license pool to use during BIG-IP licensing via BIG-IQ. |
| bigIqLicenseSkuKeyword1 | Yes | The BIG-IQ license filter (based on SKU keyword) you want to use for licensing the BIG-IPs from the BIG-IQ, for example **F5-BIG-MSP-LTM-25M**, **F5-BIG-MSP-BR-200M**, **F5-BIG-MSP-BT-1G** or **F5-BIG-MSP-ASM-1G**. ***Important***: This is only required when licensing with an ELA/subscription (utility) pool on the BIG-IQ, if not using this pool type leave the default of **OPTIONAL**. |
| bigIqLicenseUnitOfMeasure | Yes | The BIG-IQ license unit of measure to use during BIG-IP licensing via BIG-IQ, for example **yearly**, **monthly**, **daily** or **hourly**. ***Important***: This is only required when licensing with an ELA/subscription (utility) pool on the BIG-IQ, if not using this pool type leave the default of **OPTIONAL**. |
| numberOfAdditionalNics | Yes | By default this solution deploys the BIG-IP(s) in a 3 NIC configuration, however additional NICs can be added to the BIG-IP(s) using this parameter.  **Note**: The default value is 0, additional NICs will only be created if 1 or higher is specified. |
| additionalNicLocation | Yes | This parameter specifies where the additional NICs go, use the default value of **OPTIONAL** if **0** was selected for the parameter **numberOfAdditionalNics**.  Otherwise this value must be a semi-colon delimited string of subnets, equal to the number of additional NICs being deployed.  For example, for 2 additional NICs you would use: **subnet01;subnet02**. **Note**: Ensure there are no spaces and the correct number of subnets are provided based on the value selected in **numberOfAdditionalNics**. **Important**: The subnet you provide for each additional NIC **must** be unique. |
| numberOfExternalIps | Yes | The number of public/private IP addresses you want to deploy for the application traffic (external) NIC on the BIG-IP VE to be used for virtual servers. |
| vnetAddressPrefix | Yes | The start of the CIDR block the BIG-IP VEs use when creating the Vnet and subnets.  You MUST type just the first two octets of the /16 virtual network that will be created, for example '10.0', '10.100', 192.168'. |
| tenantId | Yes | Your Azure service principal application tenant ID. |
| clientId | Yes | Your Azure service principal application client ID. |
| servicePrincipalSecret | Yes | Your Azure service principal application secret. |
| managedRoutes | Yes | A comma-delimited list of route destinations to be managed by this cluster.  For example: 0.0.0.0/0,192.168.1.0/24. Specifying a comma-delimited list of managedRoutes and creating f5_ha and f5_tg tags on the Azure Route Table defines the UDRs to be updated. To have the UDRs managed by BIG-IP, you will need to create an Azure tag with key **f5_ha** and value **self_2nic**, or the name of a different self IP address configured on the BIG-IP VE. All UDRs with destinations matching managedRoutes and configured in Azure Route Tables tagged with 'f5_ha:' will use the corresponding self IP address on the active BIG-IP VE as the next hop for those routes. You must also associate the route table with a traffic group by creating an Azure tag with key **f5_tg** and value **traffic-group-1**, or the name of a different traffic group configured on the BIG-IP VE. |
| ntpServer | Yes | Leave the default NTP server the BIG-IP uses, or replace the default NTP server with the one you want to use. |
| timeZone | Yes | If you would like to change the time zone the BIG-IP uses, enter the time zone you want to use. This is based on the tz database found in /usr/share/zoneinfo (see the full list [here](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/azure-timezone-list.md)). Example values: UTC, US/Pacific, US/Eastern, Europe/London or Asia/Singapore. |
| customImage | Yes | If you would like to deploy using a local BIG-IP image, provide either the full URL to the VHD in Azure storage **or** the full resource ID to an existing Microsoft.Compute image resource.  **Note**: Unless specifically required, leave the default of **OPTIONAL**. |
| restrictedSrcAddress | Yes | This field restricts management access to a specific network or address. Enter an IP address or address range in CIDR notation, or asterisk for all sources |
| tagValues | Yes | Default key/value resource tags will be added to the resources in this deployment, if you would like the values to be unique adjust them as needed for each key. |
| allowUsageAnalytics | Yes | This deployment can send anonymous statistics to F5 to help us determine how to improve our solutions. If you select **No** statistics are not sent. |

### Programmatic deployments

As an alternative to deploying through the Azure Portal (GUI) each solution provides example scripts to deploy the ARM template.  The example commands can be found below along with the name of the script file, which exists in the current directory.

#### PowerShell Script Example

```powershell
## Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -authenticationType password -adminPasswordOrKey <value> -dnsLabel <value> -instanceName f5vm01 -instanceType Standard_DS3_v2 -imageName Best -bigIpVersion 13.1.0200 -bigIqAddress <value> -bigIqUsername <value> -bigIqPassword <value> -bigIqLicensePoolName <value> -bigIqLicenseSkuKeyword1 OPTIONAL -bigIqLicenseUnitOfMeasure OPTIONAL -numberOfAdditionalNics 0 -additionalNicLocation OPTIONAL -numberOfExternalIps 1 -vnetAddressPrefix 10.0 -tenantId <value> -clientId <value> -servicePrincipalSecret <value> -managedRoutes NOT_SPECIFIED -ntpServer 0.pool.ntp.org -timeZone UTC -customImage OPTIONAL -allowUsageAnalytics Yes -resourceGroupName <value>
```

=======

#### Azure CLI (1.0) Script Example

```bash
## Example Command: ./deploy_via_bash.sh --adminUsername azureuser --authenticationType password --adminPasswordOrKey <value> --dnsLabel <value> --instanceName f5vm01 --instanceType Standard_DS3_v2 --imageName Best --bigIpVersion 13.1.0200 --bigIqAddress <value> --bigIqUsername <value> --bigIqPassword <value> --bigIqLicensePoolName <value> --bigIqLicenseSkuKeyword1 OPTIONAL --bigIqLicenseUnitOfMeasure OPTIONAL --numberOfAdditionalNics 0 --additionalNicLocation OPTIONAL --numberOfExternalIps 1 --vnetAddressPrefix 10.0 --tenantId <value> --clientId <value> --servicePrincipalSecret <value> --managedRoutes NOT_SPECIFIED --ntpServer 0.pool.ntp.org --timeZone UTC --customImage OPTIONAL --allowUsageAnalytics Yes --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>
```

## Configuration Example

The following is an example configuration diagram for this solution deployment. In this scenario, each BIG-IP has one NIC for management, one NIC for external traffic and one NIC for internal traffic.  This is the traditional BIG-IP deployment model where data-plane, management and internal traffic is separate. The IP addresses in this example may be different in your implementation.

![Configuration Example](../images/azure-example-diagram.png)

## Post-Deployment Configuration

Use this section for optional configuration changes after you have deployed the template.

### Additional Public IP Addresses - Failover

This ARM template supports using up to 20 public IP addresses for the external 'application' NIC to be used for passing traffic to BIG-IP virtual servers. Each virtual server should be configured with a destination address matching the private IP address value of the Azure IP configuration receiving traffic for the application. In the event the active BIG-IP VE becomes unavailable, the IP configuration(s) are migrated using network failover, seamlessly shifting application traffic to the current active BIG-IP VE (the template now supports [multiple traffic groups](#traffic-group-configuration) which enables active/active deployments).  After you initially deployed the template, if you now want to include additional public IP addresses and/or if you want to add or remove the user-defined routes (UDRs) to be managed by the BIG-IP, use the following guidance.

#### Adding additional public IP addresses to the deployment

The deployment template supports creation of 1-20 external public IP addresses for application traffic (first one is used for external NIC Self IP). Use the following guidance to add **additional** public IP addresses to the deployment:

- Create a new Azure public IP address resource in the deployment resource group.
- Create a new, secondary IP configuration resource (for example: *myResourceGroupName-ext-ipconfig9*) in the properties of the external Azure network interface (for example: *myResourceGroupName-ext0*) of the **active** BIG-IP.
- Ensure a **Virtual Address** exists on the BIG-IP in the appropriate traffic group (such as traffic-group-1), and that the Virtual Address matches the private IP address of the secondary IP configuration you created.
  1. Note: A Virtual Address will automatically be created for each Virtual Server created (if it does not already exist).
  2. Note: This is what is matched on during a failover event to determine which NIC IP configurations to move.
  3. Note: F5 recommends creating the IP configuration on the network interface of the BIG-IP VE that is active for the traffic group assigned to the matching Virtual Address.

When you create virtual servers on the BIG-IP VE for these new additional addresses, the BIG-IP virtual server destination IP address should match the Azure Private IP Address of the IP configuration that corresponds to the Public IP address of your application. See the BIG-IP documentation for specific instructions on creating virtual servers.

### Configuring additional routes

If you want to configure additional routes to use the active BIG-IP VE as the next hop virtual appliance, you must edit the **/config/cloud/managedRoutes** file on each BIG-IP VE device.

The managedRoutes file is a comma-separated list of route destinations. For example, if you entered **192.168.0.0/24,192.168.1.0/24** in the **managedRoutes** parameter of the ARM template deployment, and want to set the active BIG-IP VE device as the next hop for the routes 192.168.2.0/24 and 0.0.0.0/0, log in via SSH to each device and manually edit the **/config/cloud/managedRoutes** file to: **192.168.0.0/24,192.168.1.0/24, 192.168.2.0/24,0.0.0.0/0**

### Customizing the Next Hop of Azure User-Defined Routes

This template supports associating specific sets of self IP addresses with Azure Route Tables.  Each route table that references routes that use the active BIG-IP VE as the next hop must be configured in Azure with both **f5_ha** and **f5_tg** tags.  The **f5_ha** tag value specifies the set of self IP addresses to which traffic will be forwarded, while the **f5_tg** tag associates the route table with a traffic group on the BIG-IP VE cluster. For example, if you want the routes specified in the **managedRoutes** parameter to use the default internal self IP address in **traffic-group-1** as the virtual appliance next hop, configure these Azure tags on the route table:

  - Key: "f5_ha", value: "self_2nic"
  - Key: "f5_tg", value: "traffic-group-1"

If you have the same route destinations (a wildcard destination of 0.0.0.0/0, for example) in multiple route tables, with each destination targeting a different interface of the BIG-IP VEs, we recommend creating a new set of self IP addresses and their corresponding IP configurations in Azure, and then tagging the route table appropriately.  

To find the self IP address from the BIG-IP VE Configuration utility, on the Main tab, click **Network > Self IPs**.

Use the following examples steps to create a secondary set of self IP addresses and corresponding Azure IP configurations, and add the required Azure tags to the route table resource:

  - Add: Azure IP configuration (internal NIC0)
    - Type: Secondary
    - Private IP address allocation: Static
    - Private IP address: 10.1.3.50 

  - Add: BIG-IP VE self IP address (BIG-IP VE0)
    - Name: internal_2_self
    - IP Address: 10.1.3.50
    - VLAN: external
    - Traffic Group: traffic-group-local-only

  - Add: Azure IP configuration (internal NIC1)
    - Type: Secondary
    - Private IP address allocation: Static
    - Private IP address: 10.1.3.51 

  - Add: BIG-IP VE self IP address (BIG-IP VE1)
    - Name: internal_2_self
    - IP Address: 10.1.3.51
    - VLAN: external
    - Traffic Group: traffic-group-local-only

  - Azure route table: myRouteTable
    - Add tag with key: "f5_ha", value: "internal_2_self"
    - Add tag with key: "f5_tg", value: "traffic-group-1"

In this case, on failover, the routes in **myRouteTable** with destinations matching the **managedRoutes** template parameter are updated to use either 10.1.3.50 or 10.1.3.51 (depending on which BIG-IP VE device is active for traffic-group-1) as the next hop virtual appliance.

## Documentation

For more information on F5 solutions for Azure, including manual configuration procedures for some deployment scenarios, see the Azure section of [Public Cloud Docs](http://clouddocs.f5.com/cloud/public/v1/).

### Service Discovery

Once you launch your BIG-IP instance using the ARM template, you can use the Service Discovery iApp template on the BIG-IP VE to automatically update pool members based on auto-scaled cloud application hosts.  In the iApp template, you enter information about your cloud environment, including the tag key and tag value for the pool members you want to include, and then the BIG-IP VE programmatically discovers (or removes) members using those tags.  See our [Service Discovery video](https://www.youtube.com/watch?v=ig_pQ_tqvsI) to see this feature in action.

#### Tagging

In Microsoft Azure, you have three options for tagging objects that the Service Discovery iApp uses. Note that you select public or private IP addresses within the iApp.

- *Tag a VM resource*

The BIG-IP VE will discover the primary public or private IP addresses for the primary NIC configured for the tagged VM.

- *Tag a NIC resource*

The BIG-IP VE will discover the primary public or private IP addresses for the tagged NIC.  Use this option if you want to use the secondary NIC of a VM in the pool.

- *Tag a Virtual Machine Scale Set resource*

The BIG-IP VE will discover the primary private IP address for the primary NIC configured for each Scale Set instance.  Note you must select Private IP addresses in the iApp template if you are tagging a Scale Set.

The iApp first looks for NIC resources with the tags you specify.  If it finds NICs with the proper tags, it does not look for VM resources. If it does not find NIC resources, it looks for VM resources with the proper tags. In either case, it then looks for Scale Set resources with the proper tags.

**Important**: Make sure the tags and IP addresses you use are unique. You should not tag multiple Azure nodes with the same key/tag combination if those nodes use the same IP address.

To launch the template:

1. From the BIG-IP VE web-based Configuration utility, on the Main tab, click **iApps > Application Services > Create**.
2. In the **Name** field, give the template a unique name.
3. From the **Template** list, select **f5.service_discovery**.  The template opens.
4. Complete the template with information from your environment.  For assistance, from the Do you want to see inline help? question, select Yes, show inline help.
5. When you are done, click the **Finished** button.

### Service Principal Authentication

This solution requires access to the Azure API to correctly configure both the BIG-IP VE(s) as well as the Azure resources managed by the solution.  The most efficient and security-conscious way to handle this is to utilize Azure service principal authentication, for all the typical security reasons.  The following information describes the initial configuration of an Azure service principal application for use with this solution.

_However you decide to create the the service principal application, prior to deploying this template you must verify that it has the minimum required access based on the solution requirements._

**Minimum Required Access:** The service principal account must have read/write permissions to the following objects and it is *recommended* to apply the built-in **Contributor** role to the account being used. If applying a custom role, it must have *read/write* permissions to the following resources:

- Microsoft.Network/*
- Microsoft.Storage/*

**NOTE:** Service principal information is stored locally in the **/config/cloud/.azCredentials file.  If for any reason you need to update the service principal information, you must manually edit the .azCredentials file on all BIG-IP systems.

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

## Creating virtual servers on the BIG-IP VE

In order to pass traffic from your clients to the servers through the BIG-IP system, you must create a virtual server on the BIG-IP VE. To create a BIG-IP virtual server you need to know the private IP address of the secondary IP configuration(s) for each BIG-IP VE network interface created by the template. If you need additional virtual servers for your applications/servers, you can add more secondary IP configurations on the Azure network interface, and corresponding virtual servers on the BIG-IP system. See [virtual-network-multiple-ip-addresses-portal](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-network-multiple-ip-addresses-portal) for information on multiple IP addresses.

In this template, each Azure public IP address is associated with a secondary IP configuration attached to the external network interface of the BIG-IP VE. Because this IP configuration will be moved to the active BIG-IP device, you need to create a single virtual server in **traffic-group-1** that corresponds to the private IP address of that IP configuration.

1. Once your BIG-IP VE has launched, open the BIG-IP VE Configuration utility.
2. On the Main tab, click **Local Traffic > Virtual Servers** and then click the **Create** button.
3. In the **Name** field, give the Virtual Server a unique name.
4. In the **Destination/Mask** field, type the private IP address of the secondary IP configuration associated with the Azure public IP address for your application (for example: 10.0.1.10/32).
5. In the **Service Port** field, type the appropriate port.
6. Configure the rest of the virtual server as appropriate.
7. If you used the Service Discovery iApp template: In the Resources section, from the **Default Pool** list, select the name of the pool created by the iApp.
8. Click the **Finished** button.
9. Repeat as necessary.

When you have completed the virtual server configuration, you may modify the virtual addresses to use an alternative Traffic Group using the following guidance.

1. On the Main tab, click **Local Traffic > Virtual Servers**.
2. On the Menu bar, click the **Virtual Address List** tab.
3. Click the address of one of the virtual servers you just created.
4. From the **Traffic Group** list, select **traffic-group-2** (or the additional traffic group you created previously).
5. Click **Update**.
6. Repeat for each virtual server.

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

### Deploying Custom Configuration to the BIG-IP (Azure Virtual Machine)

Once the solution has been deployed there may be a need to perform some additional configuration of the BIG-IP.  This can be accomplished via traditional methods such as via the GUI, logging into the CLI or using the REST API.  However, depending on the requirements it might be preferred to perform this custom configuration as a part of the initial deployment of the solution.  This can be accomplished in the below manner.

Within the Azure Resource Manager (ARM) template there is a variable called **customConfig**, this contains text similar to "### START(INPUT) CUSTOM CONFIGURATION", that can be replaced with custom shell scripting to perform additional configuration of the BIG-IP.  An example of what it would look like to configure the f5.ip_forwarding iApp is included below.

Warning: F5 does not support the template if you change anything other than the **customConfig** ARM template variable.

```json
"variables": {
    "customConfig": "### START (INPUT) CUSTOM CONFIGURATION HERE\ntmsh create sys application service my_deployment { device-group none template f5.ip_forwarding traffic-group none variables replace-all-with { basic__addr { value 0.0.0.0 } basic__forward_all { value No } basic__mask { value 0.0.0.0 } basic__port { value 0 } basic__vlan_listening { value default } options__advanced { value no }options__display_help { value hide } } }"
}
```

### Changing the BIG-IP Configuration utility (GUI) port

Depending on the deployment requirements, the default management port for the BIG-IP may need to be changed. To change the Management port, see [Changing the Configuration utility port](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-0-0/2.html#GUID-3E6920CD-A8CD-456C-AC40-33469DA6922E) for instructions.

***Important***: The default port provisioned is dependent on 1) which BIG-IP version you choose to deploy as well as 2) how many interfaces (NICs) are configured on that BIG-IP. BIG-IP v13.x and later in a single-NIC configuration uses port 8443. All prior BIG-IP versions default to 443 on the MGMT interface.

***Important***: If you perform the procedure to change the port, you must check the Azure Network Security Group associated with the interface on the BIG-IP that was deployed and adjust the ports accordingly.

### Logging iApp

F5 has created an iApp for configuring logging for BIG-IP modules to be sent to a specific set of cloud analytics solutions. The iApp creates logging profiles which can be attached to the appropriate objects (virtual servers, APM policy, and so on) which results in logs being sent to the selected cloud analytics solution, Azure in this case.

We recommend you watch the [Viewing ASM Data in Azure Analytics video](https://www.youtube.com/watch?v=X3B_TOG5ZpA&feature=youtu.be) that shows this iApp in action, everything from downloading and importing the iApp, to configuring it, to a demo of an attack on an application and the resulting ASM violation log that is sent to ASM Analytics.

**Important**: Be aware that this may (depending on the level of logging required) affect performance of the BIG-IP as a result of the processing to construct and send the log messages over HTTP to the cloud analytics solution.
It is also important to note this cloud logging iApp template is a *different solution and iApp template* than the F5 Analytics iApp template described [here](https://f5.com/solutions/deployment-guides/analytics-big-ip-v114-v1212-ltm-apm-aam-asm-afm).

Use the following guidance using the iApp template (the iApp now is present on the BIG-IP VE image as a part of the templates).

1. Log on to the BIG-IP VE Configuration utility.
2. On the Main tab, from the **iApp** menu, click **Application Services > Applications > Create**.
3. From the **Template** list, select f5.cloud_logger.v1.0.0.tmpl (or later version if applicable).

For assistance running the iApp template, once you open the iApp, from the *Do you want to see inline help?* question, select **Yes, show inline help**.

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

Copyright 2014-2018 F5 Networks Inc.

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