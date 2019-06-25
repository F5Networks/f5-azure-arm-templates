## Stack Type
For each of the standalone templates, you must choose the type of stack into which you want to deploy the BIG-IP VE. See the individual README files for exact requirements.  Note that not all options are available for all templates. 


  - **Existing Stack** <br> These templates deploy into an existing cloud network.  This means that all of the cloud networking infrastructure must be available prior to launching the template. By default, the template will create and attach Public IP Address(es) to the BIG-IP interface(s). However, this can be managed by setting the **provisionPublicIP** parameter to 'No', which will not create Public IP Address(es) these deployments assume Internet access is provided via another Public NAT service, Firewall, etc.  In most cases, there is no public IP assigned to the IP addresses on the external interfaces (Virtual Servers, Self IP addresses, etc).

  - **New Stack** <br>This solution deploys into a new cloud network, this means that all of the cloud networking infrastructure required will be created along with the deployment. 
