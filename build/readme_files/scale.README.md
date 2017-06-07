### Post-Deployment Azure Configuration
This solution deploys an ARM template that fully configures BIG-IP VE(s) and handles clustering (DSC) and Azure creation of objects needed for management of those BIG-IP VEs.  However, once deployed the assumption is configuration will be performed on the BIG-IP VE(s) to create virtual servers, pools, and other objects used for processing application traffic.  Because that information is unknown at deployment time, ensure the following tasks are done for each unique service to allow traffic to reach the BIG-IP(s) in the VM Scale Set.

# Post-deployment tasks(example application on port 443)
  1. Add a "Health Probe" to the ALB(Azure Load Balancer) for port 443, you can choose TCP or HTTP depending on your needs.  This queries each BIG-IP at that port to determine if it is available for traffic.
  2. Add a "Load Balancing Rule" to the ALB where the port is 443 and the backend port is also 443 (assuming you are using same port on the BIG-IP), make sure the backend pool is selected (there should only be one backend pool which was created and is managed by the VM Scale set)
  3. Add an "Inbound Security Rule" to the Network Security Group(NSG) for port 443 as the NSG is added to the subnet where the BIG-IP VE(s) are deployed - You could optionally just remove the NSG from the subnet as the VM Scale Set is fronted by the ALB.

## Additional Optional Configuration Items
Here are some post-deployment options that are entirely optional but could be useful based on your needs.

### BIG-IP Lifecycle Management
As new BIG-IP versions are released, existing VM scale sets can be upgraded to use those new images. In an existing implementation, we assume you have created different types of BIG-IP configuration objects (such as virtual servers, pools, and monitors), and you want to retain this BIG-IP configuration after an upgrade. This section describes the process of upgrading and retaining the configuration.

When this ARM template was initially deployed, a storage account was created in the same Resource Group as the VM scale set. This account name ends with **data000*** (the name of storage accounts have to be globally unique, so the prefix is a unique string). In this storage account, the template created a container named **backup**.  We use this backup container to hold backup [UCS](https://support.f5.com/csp/article/K13132) configuration files. Once the UCS is present in the container, you update the scale set "model" to use the newer BIG-IP version. Once the scale set is updated, you upgrade the BIG-IP VE(s). As a part of this upgrade, the provisioning checks the backup container for a UCS file and if one exists, it uploads the configuration (if more than one exists, it uses the latest).

**To upgrade the BIG-IP VE Image**
  1. Save a UCS backup file of the current BIG-IP configuration (cluster or standalone)
     - From the CLI command: ```# tmsh save /sys ucs /var/tmp/original.ucs```
     - From the Configuration utility: **System > Archives > Create**
  2. Upload the UCS into the **backup** container of the storage account ending in **data000** (it is a Blob container)
  3. Update the VM Scale Set Model to the new BIG-IP version
     - From PowerShell: Use the PowerShell script in the **scripts** folder in this directory
     - Using the Azure redeploy functionality: From the Resource Group where the ARM template was initially deployed, click the successful deployment and then select to redeploy the template. If necessary, re-select all the same variables, and **only change** the BIG-IP version to the latest.
  4. Upgrade the Instances
     1. In Azure, navigate to the VM Scale Set instances pane and verify the *Latest model* does not say **Yes** (it should have a caution sign instead of the word Yes)
     2. Select either all instances at once or each instance one at a time (starting with instance ID 0 and working up).
     3. Click the **Upgrade** action button.

### Configure Scale Event Notifications
You can add notifications when scale up/down events happen, either in the form of email or webhooks. The following shows an example of adding an email address that receives an email from Azure whenever a scale up/down event occurs.

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