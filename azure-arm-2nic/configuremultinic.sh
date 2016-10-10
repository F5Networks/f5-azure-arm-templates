#!/bin/bash

# This script will setup the multi-nic configuration of an F5 device in Azure
# Parameter 1: MGMT IP
# Parameter 2: Default GW
# Parameter 3: List of Additional IP's
# Example for 3 nic: ./configurenic.sh 10.0.1.5 10.0.1.1 "10.0.2.5 10.0.3.5"

    echo "$(date +%c): Starting NIC Configuration for multi-NIC Deployment"
## Set DB Variables to allow for multi nic
    tmsh modify sys db provision.1nic value forced_enable
    tmsh modify sys db provision.1nicautoconfig value disable
    bigstart restart
## Check bigstart tmm status in a while loop before moving on 
    sleep 10
    while [[ $(bigstart status tmm) == *down* ]]
        do
            echo "$(date +%c): TMM Down..."
            sleep 20
        done
    echo "$(date +%c): TMM Back UP"
## Create MGMT VLAN, IP and GW
    tmsh create net vlan vlan_mgmt interfaces add { 1.0 { untagged } }
    tmsh create net self self_mgmt address $1/24 vlan vlan_mgmt allow-service default
    tmsh create net route default gw $2
## Create Traffic VLAN(s) and IP(s)
    int=1
    for nic in $3
        do
            tmsh create net vlan vlan_$int interfaces add { 1.$int { untagged } }
            tmsh create net self self_$int address $nic/24 vlan vlan_$int allow-service default
            int=$((int+1))
        done 

    tmsh save sys config
    #reboot , is this needed?
    echo "$(date +%c): Ending NIC Configuration for multi-NIC Deployment"
    exit