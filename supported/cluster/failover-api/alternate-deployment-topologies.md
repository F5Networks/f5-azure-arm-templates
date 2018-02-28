## Alternate Deployment Topologies - failover-lb

This page contains some alternate deployment topology diagrams for the F5 Cluster Failover-LB ARM template which can assist in your deployment planning.

**Contents**
  - [failover-lb alternate topology 1](#failover-lb-alternate-topology-1)
  - [failover-lb alternate topology 2](#failover-lb-alternate-topology-2)

### failover-lb alternate topology 1
In this example, a Node.js failover script moves the Azure IP configuration for an application to the active BIG-IP VE for traffic-group-1 via the Azure REST API.  

An external Azure load balancer forwards application traffic from the Internet to host destination virtual servers on BIG-IP VE.


![Configuration Example alternate deployment 1](images/azure-failover-lb-alternate-diagram1.png)

---
<br>
### failover-lb alternate topology 2
In this example, a Node.js failover script moves the Azure IP configuration for a second application to the active BIG-IP VE for traffic-group-2 via the Azure REST API.  

An external Azure load balancer forwards application traffic from the Internet to host destination virtual servers on BIG-IP VE.



![Configuration Example alternate deployment 2](images/azure-failover-lb-alternate-diagram2.png)

---





