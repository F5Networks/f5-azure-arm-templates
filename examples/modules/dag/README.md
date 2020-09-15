
# Deploying Dag/Ingress Template

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/issues)


## Contents

- [Deploying Dag/Ingress Template](#deploying-dagingress-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
  - [Resource Tree](#resource-tree)
  - [Getting Help](#getting-help)
    - [Filing Issues](#filing-issues)
  - [Copyright](#copyright)
  - [License](#license)
    - [Apache V2.0](#apache-v20)
    - [Contributor License Agreement](#contributor-license-agreement)

## Introduction

This template creates various cloud resources to get traffic to BIG-IP solutions, including; Public IPs (for accessing management and dataplane/VIP addresses), load balancers (for example, a standard sku external load balancer and/or a standard SKU internal load balancer) to distribute or disaggregate traffic, etc.

## Prerequisites

 - Existing subnet required for internal load balancer creation.
 
## Important Configuration Notes

 - A sample template, 'sample_linked.json', has been included in this project. Use this example to see how to add a template as a linked template into your templated solution.


### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| numberPublicMgmtIPAddresses | Yes | Enter the number of public mgmt IP addresses to create. |
| numberPublicAppIPAddresses | Yes | Enter the number of public IP addresses to create. At least one is required to build ELB. |
| dnsLabel | Yes | Unique DNS Name for the Public IP address used to access the Virtual Machine. |
| externalLoadBalancerName | Yes | Valid values include 'None', or an external load balancer name. A value of 'None' will not create an external load balancer. Specifying a name creates an external load balancer with the name specified. |
| loadBalancerRulePorts | Yes | Valid values include valid TCP ports. Enter an array of ports that your applications use. For example: '[80,443,445]' |
| internalLoadBalancerName | Yes | Valid values include 'None', or an internal load balancer name. A value of 'None' will not create an internal load balancer. Specifying a name creates an internal load balancer with the name specified. |
| internalSubnetId | Yes | Enter the subnet ID to use for frontend internal load balancer configuration. If you specify 'None' for provision internal load balancer, this setting has no effect. |
| internalLoadBalancerProbePort | Yes | Specify a TCP port for the internal load balancer to monitor. If you specify 'None' for provision internal load balancer, this setting has no effect. |
| tagValues| Yes | List of tags to add to created resources. |

### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| appIpIds | Application Public IP Address resource IDs | Application Public IP Address | array |
| appIps | Application Public IP Addresses | Application Public IP Address | array |
| externalBackEndLoadBalancerID | Application Back End Address Pool resource ID | External Load Balancer | string |
| externalBackEndMgmtLoadBalancerID | Management Back End Address Pool resource ID | External Load Balancer | string |
| externalFrontEndLoadBalancerID | Application Front End resource IDs | External Load Balancer | array |
| externalFrontEndMgmtLoadBalancerID | Management Front End resource ID | External Load Balancer | string |
| externalLoadBalancer | External Load Balancer resource ID | External Load Balancer | string |
| externalLoadBalancerProbesID | External Load Balancer Probe resource IDs | External Load Balancer | array |
| externalLoadBalancerRulesID | External Load Balancing Rules resource IDs | External Load Balancer | array |
| inboundMgmtNatPool | Management NAT Pool resource ID | Management Public IP Address | string |
| inboundSshNatPool | SSH NAT Pool resource ID | Management Public IP Address | string |
| internalBackEndLoadBalancerID | Internal Back End Address Pool resource ID | Internal Load Balancer | string |
| internalFrontEndLoadBalancerIP | Internal Front End resource ID | Internal Load Balancer | string |
| internalLoadBalancerProbeID | Internal Load Balancer Probe ID | Internal Load Balancer | string |
| internalLoadBalancer | Internal Load Balancer resource ID | Internal Load Balancer | string |
| mgmtIpIds | Management Public IP Address resource IDs | Management Public IP Address | array |
| mgmtIps | Management Public IP Addresses | Management Public IP Address | array |


## Resource Tree 

Resource Creation Flow Chart
<br>
<br>
<br>
```mermaid
graph TD
  elb(["[externalLoadBalancerName](string)"]);
  noelb("External load Balancer<br>is not created.");
  yeselb("External load Balancer<br>is created using specified name.");
  ilb(["[internalLoadBalancerName](string)"]);
  noilb("Internal load Balancer<br>is not created.");
  yesilb("Internal load Balancer<br>is created using specified name.");
  mgmtip(["[numberPublicMgmtIPAddresses](int)"]);
  nomgmtip("No management public ip created");
  yesmgmtip("Public IP address created<br>Naming pattern:<br>(dns)-mgmt-pip(x)<br>dns=[dnsLabel](string)<br>x begins at 0 and increments by 1 to<br>[numberPublicMgmtIPAddresses](int)");
  appip(["[numberPublicAppIPAddresses](int)"]);
  noappip("No application public ip created");
  yesappip("Public IP address created<br>Naming pattern:<br>(dns)-app-pip(x)<br>dns=[dnsLabel](string)<br>x begins at 0 and increments by 1 to<br>[numberPublicMgmtIPAddresses](int)");
  ilbname("myILB");
  ilbbackend("backendAddressPool(loadBalancerBackend)");
  ilbfrontend("frontendIPConfigurations(loadBalancerFrontEnd)<br>IP(Dynamic)<br>Subnet[internalSubnetId](string)");
  ilbrules("loadBalancingRules(allProtocolRule)<br>Allows all traffic.");
  ilbprobes("probe(tcp-probe-[internalLoadBalancerProbePort](int))<br>Probes members of <br>backendAddressPool(loadBalancerBacked)<br>Using TCP port specified");
  elbname["myELB"];
  elbbackend("backendAddressPool(loadBalancerBackend)");
  elbmgmtbackend("backendAddressPool(loadBalancerMgmtBackend)");
  elbfrontend("frontendIPConfigurations(loadBalancerFrontEnd(x))<br>uses public IP:[dnsLabel](string)-app-pip(x)<br>x begins at 0 and increments by 1 to<br>[numberPublicAppIPAddresses](int)");
  elbmgmtfrontend("frontendIPConfigurations(loadBalancerMgmtFrontEnd)<br>uses public IP:[dnsLabel](string)-mgmt-pip0");
  elbmgmtoutbound("outboundRules(outboundRuleForInit)<br>allows all outbound traffic from<br>backendAddressPool(loadBalancerMgmtBacked) through<br>frontendIPConfigurations(loadBalancerMgmtFrontEnd)");
  elbrules("creates a rule for each port specified in<br>[loadBalancerRulePorts](array)<br>x equals port specified for each item in array<br>loadBalancingRules(app-x)<br>frontendIPConfigurations(loadBalancerFrontEnd0)<br>backendAddressPool(loadBalancerBacked)<br>port(x)<br>backEndPort(x)<br>probe(tcp_probe_(x))");
  elbprobes("probe(tcp-probe-[internalLoadBalancerProbePort](int))<br>Probes members of <br>backendAddressPool(loadBalancerBacked)<br>Using TCP port specified");  
  elbinboundnat("Creates 2 inbound nat pools<br>Range 50001-50100 used for SSH<br>Range 50101-50200 used for management GUI - port 8443<br>Associated to  frontendIpConfigurations(loadBalancerMgmtFrontEnd)");  
  legendtxt("[template parameter noted in square brackets]<br>(example value or type noted in parentheses)");
  subgraph legend
  legendtxt;
  end
  subgraph Public IP Creation
  mgmtip-. "(0)" .->nomgmtip;
  mgmtip-. "(>0)" .->yesmgmtip;
  appip-. "(0)" .->noappip;
  appip-. "(>0)" .->yesappip;
  end
  subgraph LB Decisions
  ilb-. "string(myILB)" .-yesilb;
  ilb-. "(None)" .->noilb;
  yesappip-. "(>0)<br>One application public<br>ip required to create elb" .-elb;
  elb-. "(None)" .->noelb;
  elb-. "string(myELB)" .-yeselb;
  end
  subgraph ILB Properties
  yesilb-. "Create internal lb" .->ilbname;
  ilbname-.-ilbbackend;
  ilbbackend-.-ilbfrontend-.-ilbrules-.-ilbprobes;
  end
  subgraph ELB Properties
  yeselb-. "Create external lb<br>requires [numberPublicAppIPAddresses](int) > 0" .->elbname;
  elbname-. "[numberPublicMgmtIPAddresses](int) > 0<br>AND<br>[numberPublicAppIPAddresses](int) > 0" .-elbinboundnat;
  elbname-. "[numberPublicAppIPAddresses](int) > 0" .-elbbackend;
  elbname-. "[numberPublicMgmtIPAddresses](int) > 0" .-elbmgmtbackend;
  elbmgmtbackend-.-elbmgmtfrontend;
  elbmgmtfrontend-.-elbmgmtoutbound;
  elbbackend-.-elbfrontend;
  elbfrontend-.-elbprobes;
  elbprobes-.-elbrules;
  end
```

<br>
<br>
<br>

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
