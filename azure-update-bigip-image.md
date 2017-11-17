## Changing the BIG-IP VE image in an F5 ARM template
The following procedure describes how to update an F5 ARM template to use a different BIG-IP image than the one referenced in the template.  This is useful if your organization has standardized on a particular version of a template, and a vulnerability is discovered in the BIG-IP image used by the template.  

Refer to the [Azure ARM Template Matrix](https://github.com/F5Networks/f5-azure-arm-templates/blob/master/azure-bigip-version-matrix.md) to ensure proper compatibility of BIG-IP versions for particular releases.  The BIG-IP version must be in the same family (for example, if you deployed using a v13 image, you use any v13.x image in the template).

*Important*  This procedure is only necessary if you need to modify a template that was contained in a previous tagged release.  If you do not need to use an older template, we recommend using the latest templates.

**To change the BIG-IP VE image in a template**
1.  Determine the F5 ARM template you want to deploy (for example, standalone, 1-NIC).
2.  Select the release Tag that corresponds to the template.  To select the release tag:

    a.  Go to the F5 ARM Template main page (https://github.com/F5Networks/f5-azure-arm-templates).  
    b.  From the **Branch** list, click the arrow, and then click the **Tags** tab.  ![Finding tagged releases](images/tag-location.png)<br>  
    c.  Select the Tagged version that contains the template you want to update.  
    d.  Browse to the template file (**azuredeploy.json**) which contains the BIG-IP image you want to replace.  For example, for a 1-NIC, new stack, PAYG template, we click **supported > standalone > 1nic > new_stack > PAYG > azuredeploy.json**.  
    e. Search for the BIG-IP version (image SKU) you want to replace (for example, **13.0.021**).  Replace this number everywhere it appears in the file.
    ```
    "bigIpVersion": {
            "allowedValues": [
                "13.0.021", 
                "12.1.24", 
                "latest"
            ], 
            "defaultValue": "13.0.021", 
            "metadata": {
                "description": "F5 BIG-IP version you want to use."
            }, 
            "type": "string"
    ```
    f.  Save the new file.. and (need guidance from james on what to do after).

