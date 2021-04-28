# Deploying Additional Applications to the F5 WAF

You can use the [**deploy_waf_application_autoscale.sh**](deploy_waf_application_autoscale.sh) script in this repo to deploy additional applications to your F5 WAF devices.  The script configures the required security policy, profiles, and virtual server objects to receive application traffic. After you run the script, you must manually configure the Azure Load Balancer and Network Security Group to pass traffic for the application to the WAF device. The script does not configure Azure resources. For more information on configuring Azure objects, see the Azure documentation.

You need to provide a list of parameters when deploying the script (you will be prompted for the WAF password).

Example usage:  
```bash
bash -x .\deploy_waf_application.sh -m http-https -d mydeployment -p 1.2.3.4 -v 881 -s 8446 -o 80 -l 443 -t linux -e custom -i https://example.com/my_security_policy.xml -c https://example.com/my_ssl_archive.pfx -a Ih3@rtF5! -r myapp.example.com -u azureuser -h 1.1.1.1 -g 50101
```

| Flag | Name | Description | Example values | Notes |
| --- | --- | --- | --- | --- |
| -m | Application Protocols | The protocol(s) used by clients to access your application. | http, http-https, https, https-offload | 
| -d | Solution Deployment Name | A unique name for the deployment. | mydeployment | Must be unique for each deployment. |
| -p | Application Address | The IP address or FQDN of the application or App Service Environment. | 1.2.3.4, app1.example.com | |   
| -v | Virtual Server Port | The unique port used for unencrypted traffic on WAF for this application. | 881 | Must be unique for each deployment. |
| -s | Virtual Server Secure Port | The unique port used for encrypted traffic on the WAF for this application. | 8446 | Must be unique for each deployment. |
| -o | Application Port | The unencrypted port clients use to access your application. | 80 | |  
| -l | Application Secure Port | The encrypted port clients use to access your application. | 443 | | 
| -t | Application Type | The OS type of the application server(s). | linux, windows | | 
| -e | Blocking Level | The blocking level of the ASM security policy. | high, medium, low, off, custom | |  
| -i | Custom Security Policy | The URL of a custom ASM security policy to apply to the deployment. | https://example.com/my_policy.xml, NOT_SPECIFIED | Enter a URL here when Custom Security Policy is **custom**; otherwise, use **NOT_SPECIFIED**. |
| -c | SSL Archive File  | The URL of a .pfx archive that is accessible to this WAF device https://example.com/my_archive.pfx, NOT_SPECIFIED | Enter a URL here when Application Protocols is **http-https**, **https**, or **https-offload**; otherwise, use **NOT_SPECIFIED** |
| -a | SSL Archive Password | The password for the specified .pfx archive. | Ih3@rtF5! | | 
| -r | Application Service FQDN |  The FQDN of your application, if not the same as pool_member. | myapp.example.com, NOT_SPECIFIED | When the application is an Azure App Service or App Service Environment, enter the FQDN that clients use to access the application; otherwise, use **NOT_SPECIFIED**. |
| -u | WAF Username | The user name for the account create at provisioning time. | azureuser | |  
| -h | WAF Host IP | The management IP address of the WAF device | 1.1.1.1 | The host IP address can be accessed in the outputs of the Azure template deployment, or from Azure Security Center. |
| -g | WAF Management Port | The management port of the WAF device. | 50101 | The management port can be accessed in the outputs of the Azure template deployment, or from Azure Security Center. |
