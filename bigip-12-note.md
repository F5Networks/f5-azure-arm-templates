# BIG-IP 12.1.3 removed from Azure Marketplace 

Microsoft Azure has removed Azure BIG-IP image version 12.1.30300 (BIG-IP version 12.1.3.3 Build 0.0.4) from the Marketplace.  For new deployments using F5 Azure ARM templates as of release 6.1.0.0, only Latest, BIG-IP v14.003000, BIG-IP v13.1.100000 are available options from the ARM templates. 

While this change won't affect most users, if you have deployed templates as part of an automated process that updates Azure resources, you may need to modify the template itself to remove some of the template code as described on this page.

**Important Notes**

  - If you have an existing deployment using version 12.1.30300, you can continue to use this version with no modifications.  

  - If you attempt to use an older version of an F5 ARM template (using GitHub tag 6.0.4.0 or earlier), the option to use 12.1.30300 will appear in the templates, but you will not be able to deploy this version of the BIG-IP, as the image is not longer available.  

  - If you have F5 ARM templates as part of an automated process (such as a CI/CD pipeline), and have standardized on BIG-IP image version 12.1.30300 and are not able to upgrade to a newer version, you must modify the template code to remove references to the BIG-IP image so that the template does not attempt to validate the virtual machine resource using the image that no longer exists.  See the following section for instructions.


## Modifying a template

Use this section to modify a template file so that it does not attempt to validate the BIG-IP virtual machine resource using version 12.1.30300.  This guidance is not applicable to F5 Autoscale ARM templates; to update the Azure VM scale set model, you must update the imageReference property of the scale set model to reference a valid F5 marketplace image.  Follow the instructions here:  https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-upgrade-scale-set to upgrade the VM scale set model.

  1. Go to the appropriate GitHub page for the template you are using.   
  In this example, we reference the failover via-lb existing stack BYOL template: https://github.com/F5Networks/f5-azure-arm-templates/tree/master/supported/failover/same-net/via-lb/3nic/existing-stack/byol.  
  For standalone templates, there will only be one virtual machine resource and one custom script extension resource.

  2. Click the **azuredeploy.json** file.

  3. Click the **Raw** button.

  4. Right-click the page, and then click **Save As** to save the file in an accessible location.

  5. Open the **azuredeploy.json** file in a text editor.

  6. There are two virtual machine resources you must remove from the failover template:  
  
     1. Search the template file for the following line:   
      ```"type": "Microsoft.Compute/virtualMachines"```
    
     2. Completely remove the all resources from the ARM template that **end** with this line.  

  7. There are two custom script extension resources you must remove from the failover template:  
     
     1. Search the template file for the following line:   
      ```"type": "Microsoft.Compute/virtualMachines/extensions"```
    
     2. Completely remove all resources from the ARM template that **end** with this line.  

  8.  After ensuring there are no errors in the code from missing brackets or missing/extra commas, save the file with the same name (**azuredeploy.json**). 

  9.  Deploy the template using your typical method.


### Example template

You can compare the difference between an existing template file and our modified version to see the changes described above.

For example, compare the Failover via-LB 3 NIC existing stack template: https://github.com/F5Networks/f5-azure-arm-templates/blob/master/supported/failover/same-net/via-lb/3nic/existing-stack/byol/azuredeploy.json

With our modified template: https://github.com/F5Networks/f5-azure-arm-templates/tree/master/experimental/reference/example-image-removed/azuredeploy.json.


