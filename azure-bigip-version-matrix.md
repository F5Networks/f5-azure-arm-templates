# Azure ARM Template Matrix

The following table contains all of the tagged releases of the F5 ARM templates for Azure, and the corresponding BIG-IP versions, license types and throughputs available for a specific tagged release.  To view a Tag, from the f5-azure-arm-templates repo (https://github.com/F5Networks/f5-azure-arm-templates/ or a sub directory), click the Branch < current branch > button, and then click the Tags tab.  You see a list of all of the F5 tagged releases.

**Note:** If using a BYOL (Bring Your Own License) some versions of BIG-IP only have two boot locations available, even though the option for one boot location may appear in the template. See the BIG-IP version table in the individual README file for details.

> **_CRITICAL:_**  As of F5 ARM template GitHub release 6.1.0.0, BIG-IP version 12.1 is no longer supported, and Microsoft Azure has removed Azure BIG-IP image version 12.1.30300 (BIG-IP version 12.1.3.3 Build 0.0.4) from the Marketplace. While this change won't affect most users, if you have deployed templates as part of an automated process that updates Azure resources, see https://github.com/F5Networks/f5-azure-arm-templates/blob/master/bigip-12-note.md.  

| Release Tag | Template Family | BIG-IP Versions | BIG-IQ Versions | PAYG License Bundles and Throughput | BYOL/BIG-IQ Image options |
| --- | --- | --- | --- | --- | --- |
| [v7.1.1.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v7.1.1.0) | Standalone | Latest, BIG-IP v14.1.2.0, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.1.0 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v7.1.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v7.1.0.0) | Standalone | Latest, BIG-IP v14.1.2.0, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.1.0 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v7.0.3.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v7.0.3.0) | Standalone | Latest, BIG-IP v15.0.1, BIG-IP v14.1.2.0, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.1.0 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v7.0.2.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v7.0.2.0) | Standalone | Latest, BIG-IP v14.1.2.0, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.1.0 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v7.0.1.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v7.0.1.0) | Standalone | Latest, BIG-IP v14.1.2.0, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.1.0 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v14.1.200000, BIG-IP v13.1.300000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v7.0.0.2](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v7.0.0.0) | Standalone | Latest, BIG-IP v14.1.0.3, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.1.0 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v7.0.0.1](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v7.0.0.1) | Standalone | Latest, BIG-IP v14.1.0.3, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.1.0 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v7.0.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v7.0.0.0) | Standalone | Latest, BIG-IP v14.1.0.3, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.1.0 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v6.1.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v6.1.0.0) | Standalone | Latest, BIG-IP v14.1.0.3, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v14.1.003000, BIG-IP v13.1.100000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v6.0.4.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v6.0.4.0) | Standalone | Latest, BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | Latest, BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | Latest, BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | Latest, BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | Latest, BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v6.0.3.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v6.0.3.0) | Standalone | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v6.0.2.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v6.0.2.0) | Standalone | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v6.0.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v6.0.0.0) | Standalone | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v5.5.1.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v5.5.1.0) | Standalone | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale LTM | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v5.5.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v5.5.0.0) | Standalone | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps<br>Per App VE LTM: 25Mbps, 200Mbps<br>Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllTwoBootLocations, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps <br>BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps | AllTwoBootLocations, LTMTwoBootLocations |
|  | Auto Scale WAF | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps<br> BIG-IP v13.1+:<br> Advanced WAF: 25Mbps, 200Mbps, 1Gbps <br> Per App VE Advanced WAF: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations |
|  | Auto Scale LTM | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps<br>v13.1+:  Per App VE LTM: 25Mbps, 200Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | BIG-IQ | N/A | 6.0.1 | N/A | Best |
| [v5.4.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v5.4.0.0) | Standalone | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps |AllOneBootLocation, AllTwoBootLocations |
|  | Auto Scale LTM | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
| [v5.3.2.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v5.3.2.0) | Standalone | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps |AllOneBootLocation, AllTwoBootLocations |
|  | Auto Scale LTM | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
| [v5.3.1.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v5.3.1.0) | Standalone | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps |AllOneBootLocation, AllTwoBootLocations |
|  | Auto Scale LTM | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
| [v5.3.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v5.3.0.0) | Standalone | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-API) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Cluster (Failover-LB) | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
|  | Auto Scale WAF | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Best*: 1Gbps, 200Mbps, 25Mbps |AllOneBootLocation, AllTwoBootLocations |
|  | Auto Scale LTM | BIG-IP v13.1.100000, 12.1.303000 | BIG-IQ v5.4, v6.0.1 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | AllOneBootLocation, AllTwoBootLocations, LTMOneBootLocation, LTMTwoBootLocations |
| [v5.2.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v5.2.0.0) | Standalone | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps |
|  | Cluster (Failover-API) | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster (Failover-LB) | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v5.1.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v5.1.0.0) | Standalone | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster (Failover-API) | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster (Failover-LB) | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.3, 5.4 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v5.0.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v5.0.0.0) | Standalone | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster (Failover-API) | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster (Failover-LB) | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.0-5.3 | *Best*: 1Gbps, 200Mbps, 25Mbps | | 
|  | Auto Scale LTM | BIG-IP v13.1.0200, 12.1.303000 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v4.4.0.1](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v4.4.0.1) | Standalone | BIG-IP v13.1.0200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.1.0200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.1.0200 | BIG-IQ v5.0-5.3 | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.1.0200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.1.0200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v4.4.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v4.4.0.0) | Standalone | BIG-IP v13.1.0200, v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.1.0200, BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.1.0200, BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.1.0200, BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.1.0200, BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v4.3.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v4.3.0.0) | Standalone | BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM |BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v4.2.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v4.2.0.0) | Standalone | BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.0300, v12.1.2200 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM |BIG-IP v13.0.0300, v12.1.2200 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.0.0300, v12.1.2200 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v4.1.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v4.1.0.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.021, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v4.0.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v4.0.0.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.021, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.3.2.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.3.2.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.021, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.3.1.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.3.1.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.021, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.3.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.3.0.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.021, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.0.021, v12.1.24 | BIG-IQ v5.0-5.3 | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.2.1.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.2.1.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.021, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.2.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.2.0.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.021, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | HA-AVSET | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.1.4.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.1.4.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.021, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.1.3.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.1.3.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.021, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.1.2.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.1.2.0) | Standalone | BIG-IP v13.0.020, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.020, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.020, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.1.1.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.1.1.0) | Standalone | BIG-IP v13.0.020, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.020, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.020, v12.1.24 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.1.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.1.0.0) | Standalone | BIG-IP v13.0.020, v12.1.21 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.020, v12.1.21 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.020, v12.1.21 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v3.0.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v3.0.0.0) | Standalone | BIG-IP v13.0.000, v12.1.21 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.000, v12.1.21 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale WAF | BIG-IP v13.0.000, v12.1.21 | N/A | *Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Auto Scale LTM | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v2.0.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v2.0.0.0) | Standalone | BIG-IP v13.0.000, v12.1.21 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v13.0.000, v12.1.21 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v1.1.2.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v1.1.2.0) | Standalone | BIG-IP v12.1.21 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | v12.1.21 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps |
| [v1.1.1.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v1.1.1.0) | Standalone | BIG-IP v12.1<br> ('latest' was only option) | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | BIG-IP v12.1 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v1.1.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v1.1.0.0) | Standalone | BIG-IP v12.1 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | v12.1 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v1.0.1](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v1.0.1) | Standalone | BIG-IP v12.1 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | v12.1 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
| [v1.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v1.0.0) | Standalone | BIG-IP v12.1 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
|  | Cluster | v12.1 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
