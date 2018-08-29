# Azure ARM Template Matrix

The following table contains all of the tagged releases of the F5 ARM templates for Azure, and the corresponding BIG-IP versions, license types and throughputs available for a specific tagged release.  To view a Tag, from the f5-azure-arm-templates repo (https://github.com/F5Networks/f5-azure-arm-templates/ or a sub directory), click the Branch < current branch > button, and then click the Tags tab.  You see a list of all of the F5 tagged releases.

**Note:** If using a BYOL (bring your own license) license the throughput available may be greater than what is described on the matrix.

| Release Tag | Template Family | BIG-IP Versions | BIG-IQ Versions | PAYG License Bundles and Throughput | BYOL/BIG-IQ Image options (v13.1.1 and later) |
| --- | --- | --- | --- | --- | --- |
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
| [v3.2.0.0](https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/3.2.0.0) | Standalone | BIG-IP v13.0.021, v12.1.24 | N/A | *Good/Better/Best*: 1Gbps, 200Mbps, 25Mbps | |
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
