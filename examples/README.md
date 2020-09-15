
# Example Templates

- [Example Templates](#example-templates)
  - [Introduction](#introduction)
  - [Template Types](#template-types)
  - [Deployment Example](#deployment-example)
  - [Getting Help](#getting-help)
    - [Filing Issues](#filing-issues)
  - [Copyright](#copyright)
  - [License](#license)
    - [Apache V2.0](#apache-v20)
    - [Contributor License Agreement](#contributor-license-agreement)

## Introduction

The examples here leverage the modular [linked templates](https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/linked-templates) design to provide maximum flexibility when authoring solutions using F5 BIG-IP.  

Example deployments use parent templates to deploy child templates (or modules) to facilitate quickly standing up entire stacks (complete with **example** network, application, and BIG-IP tiers). 

As a basic framework, an example full stack deployment may consist of: 

- **(Parent) Solution Template** (ex. Quickstart or Autoscale)
  -  **(Child) Network Template** - which creates virtual networks, subnets, and network security groups. 
  -  **(Child) Application Template** - which creates a generic application, based on the f5-demo-app container, for demonstrating live traffic through the BIG-IP.
  -  **(Child) DAG/Ingress Template** -  which creates resources required to get traffic to the BIG-IP.
  -  **(Child) Access Template** - which creates Identity and Acccess related resources, like a secret in cloud vault that can be referenced by F5 BIG-IP.
  -  **(Child) Function Template** - which creates an Azure function to manage licenses for an Azure Virtual Machine Scale Set of BIG-IP instances licensed with BIG-IQ.
  -  **(Child) BIG-IP Template** *(existing-stack)* - which creates BIG-IP instance(s).

***Disclaimer:** F5 does not require or have any recommendations on leveraging linked stacks in production. They are used here simply to provide useful tested/validated examples and illustrate various solutions' resource dependencies, configurations, etc., which you may need or want to customize, regardless of the deployment method used.* 

## Template Types
Templates are grouped into the following categories:

  - **Quickstart** <br> *Coming Soon*: These parent templates deploy a collection of linked child templates to create a standalone BIG-IP VE in an example full-stack. Standalone BIG-IP VEs are primarily used for Dev/Test/Staging, replacing/upgrading individual instances in traditional failover clusters, and/or manually scaling out. <br>

  - **Autoscale** <br> These parent templates deploy a collection of linked child templates to create a Virtual Machine Scale Set (VMSS) of BIG-IP VE instances that scale in and out based on thresholds you configure in the template, as well as the full stack of resources required by the solution. The BIG-IP VEs are "All Active" and are primarily used to scale an L7 service on a single wildcard virtual (although you can add additional services using ports).<br> Unlike previous solutions, this solution leverages the more traditional autoscale configuration management pattern where each instance is created with an identical configuration as defined in the Scale Set's "model". Scale Set sizes are no longer restricted to the smaller limitations of the BIG-IP's cluster. The BIG-IP's configuration, now defined in a single convenient yaml-based [F5 BIG-IP Runtime Init](https://github.com/f5devcentral/f5-bigip-runtime-init) *(IN PREVIEW)* configuration file, leverages [F5 Automation Tool Chain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) declarations which are easier to author, validate and maintain as code. For instance, if you need to change the configuration on the instances in the deployment, you update the the "model" by passing the new config version via the template's *runtimeConfig* input parameter. The Scale Set provider will update the instances to the new model according to its rolling update policy. Web Application Firewall (WAF) functionality is provisioned using Declarative Onboarding declaration and configured via a Application Services declaration. Example F5 BIG-IP Runtime Init configurations and Automation Toolchain component declarations are available in the Autoscale examples folder. 


  - **Modules** <br> These child templates create the Azure resources that compose a full stack deployment. They are referenced as linked deployment resources from the parent templates (Quickstart, Autoscale, etc).<br>
  The parent templates manage passing inputs to the child templates and using their outputs as inputs to other child templates.<br>

    #### Module Types:
      - **Network**: Use this template to create a reference network stack. This template creates virtual networks, subnets, and network security groups. 
      - **Application**: Use this template to deploy an example application. This template creates a generic application, based on the f5-demo-app container, for demonstrating live traffic through the BIG-IP. You can specify a different container or application to use when deploying the example template.
      - **Disaggregation/Ingress** (DAG): Use these templates to create resources required to get or distribute traffic to the BIG-IP instance(s). For example: Azure Public IP Addresses, internal/external Load Balancers, and accompanying resources such as load balancing rules, NAT rules, and probes.
      - **Access**: Use these templates to create a Identity and Access related resources required for the solution.  These templates create an Azure Managed User Identity, KeyVault, and secret that can be referenced in the F5 BIG-IP Runtime Init configuration file. The secret can store sensitive information such as the BIG-IP password, BIG-IQ password, or Azure service principal access key for use in service discovery. 
      - **Function**: Use these templates to create an Azure function, hosting plan, and other resources required to automatically revoke a BIG-IP license assignment from BIG-IQ when the capacity of the Virtual Machine Scale Set is reduced due to deallocation of a BIG-IP instance.
      - **BIG-IP**: Use these templates to create the BIG-IP Virtual Machine instance(s). For example, a standalone VM or a Virtual Machine Scale Set. The BIG-IP module can be used independently from the linked stack examples here (ex. in an "existing-stack").<br><br> In the Autoscale example, the required Autoscale Settings and Application Insights resources are also created.
          

## Deployment Example
Autoscale PAYG example template shown

![Deployment](https://gitswarm.f5net.com/cloudsolutions/f5-cloud-factory/-/raw/develop2.0/f5-azure-arm-templates/examples/images/azure-autoscale-example-diagram.png)



## Getting Help

The example templates in this directory are intended to provide reference deployments of F5 BIG-IP Virtual Editions. Due to the heavy customization requirements of external cloud resources and BIG-IP configurations in these solutions, F5 does not provide technical support for deploying, customizing, or troubleshooting the templates themselves. However, the various underlying products and components used (for example: F5 BIG-IP Virtual Edition, Automation Toolchain extensions, and Cloud Failover Extension (CFE)) in the solutions located here are F5-supported and capable of being deployed with other orchestration tools. Read more about [Support Policies](https://www.f5.com/company/policies/support-policies). 

### Filing Issues

If you find an issue, we would love to hear about it.

- Use the **Issues** link on the GitHub menu bar in this repository for items such as enhancement or feature requests and non-urgent bug fixes. Tell us as much as you can about what you found and how you found it.


## Copyright

Copyright 2014-2020 F5 Networks Inc.

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


