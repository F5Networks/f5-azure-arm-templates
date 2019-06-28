## Stack Type
For each of the standalone templates, you must choose the type of stack into which you want to deploy the BIG-IP VE. See the individual README files for exact requirements.  Note that not all options are available for all templates. 


  - **Existing Stack** <br> These templates deploy BIG-IP instances into an existing cloud network.  This means that the Azure virtual network and subnets must be available prior to launching the template. If you choose "No" for the provisionPublicIP parameter, existing stack templates do not create or attach public IP addresses to the BIG-IP network interface(s). As BIG-IP VEs behind an Azure load balancer need external connectivity to download files for onboarding and access Cloud API services (autoscale only), these deployments will create a public front end IP configuration and load balancing rules on the external ALB.  If Internet access is to be provided via another public NAT service, firewall, etc., F5 recommends removing this public configuration after deployment completes.

  - **New Stack** <br> These templates deploy BIG-IP instances into a new cloud network.  The required Azure virtual network and subnets will be created along with the deployment, and public IP addresses are created on all external Azure network interfaces and load balancers by default. 

  - **Production Stack** <br> These templates have been deprecated.  Production stack templates are still available for deployment in f5-azure-arm-templates release v6.1.0 or earlier.