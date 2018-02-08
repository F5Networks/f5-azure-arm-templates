## Alternate Deployment Topologies - HA-AVSET

This page contains some alternate deployment topology diagrams for the F5 HA-AVSET ARM templates which can assist in your deployment planning using an F5 HA-AVSET ARM template.

**Contents**
  - [HA-AVSET alternate topology 1](#ha-avset-alternate-topology-1) 
  - [HA-AVSET alternate topology 2](#ha-avset-alternate-topology-2) 

### HA-AVSET alternate topology 1 
In this example, a Node.js failover script moves the Azure IP configuration for an application to the active BIG-IP VE for traffic-group-1 via the Azure REST API.  

An external Azure load balancer forwards application traffic from the Internet to host destination virtual servers on BIG-IP VE.


![Configuration Example alternate deployment 1](images/azure-ha-avset-alternate-diagram1.png)

---
<br>
### HA-AVSET alternate topology 2  
In this example, a Node.js failover script moves the Azure IP configuration for a second application to the active BIG-IP VE for traffic-group-2 via the Azure REST API.  

An external Azure load balancer forwards application traffic from the Internet to host destination virtual servers on BIG-IP VE.



![Configuration Example alternate deployment 2](images/azure-ha-avset-alternate-diagram2.png)

---





