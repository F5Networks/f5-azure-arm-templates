#  expectValue = "Succeeded"
#  expectFailValue = "Failed"
#  scriptTimeout = 20
#  replayEnabled = true
#  replayTimeout = 30

if [[ <TEMPLATE URL> == *"existing-stack"* && (<CREATE PUBLIC IP> == "Yes") ]]; then
        STACK_TYPE='existing-stack'
        if [[ $(echo <TEMPLATE URL> | grep -E '(autoscale/ltm/via-lb|autoscale/waf/via-lb)') ]]; then
            if [[ <EXT ALB EXISTS> == "Yes" ]]; then
                # creating public ip which will used on existent LB
                echo 'Creating Public IP'
                echo $(az network public-ip create --resource-group <RESOURCE GROUP> --name <RESOURCE GROUP>-mgmt-pip --allocation-method Static --dns-name <RESOURCE GROUP>  --sku Standard)
                # creating loadbalancer to use as exitent resource for deployment
                echo 'Creating loadbalancer'
                echo $(az network lb create --resource-group <RESOURCE GROUP> --name <RESOURCE GROUP>-existing-lb --public-ip-address <RESOURCE GROUP>-mgmt-pip --frontend-ip-name loadBalancerFrontEnd  --backend-pool-name loadBalancerBackEnd --sku Standard)
                echo 'Creating inbound ssh nat pool'
                echo $(az network lb inbound-nat-pool create -g <RESOURCE GROUP> --lb-name <RESOURCE GROUP>-existing-lb -n sshnatpool --protocol Tcp --frontend-port-range-start 50001 --frontend-port-range-end 50100 --backend-port 22 --frontend-ip-name loadBalancerFrontEnd)
                echo 'Creating inbound mgmtnatpool nat pool'
                echo $(az network lb inbound-nat-pool create -g <RESOURCE GROUP> --lb-name <RESOURCE GROUP>-existing-lb -n mgmtnatpool --protocol Tcp --frontend-port-range-start 50101 --frontend-port-range-end 50200 --backend-port 8443 --frontend-ip-name loadBalancerFrontEnd)
                echo 'Creating LB Probes'
                echo $(az network lb probe create -g <RESOURCE GROUP> --lb-name <RESOURCE GROUP>-existing-lb -n tcp_probe_http --protocol tcp --port 80 --interval 15  --threshold 3)
                echo $(az network lb probe create -g <RESOURCE GROUP> --lb-name <RESOURCE GROUP>-existing-lb -n tcp_probe_https --protocol tcp --port 443 --interval 15  --threshold 3)
                echo 'Creating loadbalancing rules'
                echo $(az network lb rule create -g <RESOURCE GROUP> --lb-name <RESOURCE GROUP>-existing-lb -n app-http --protocol Tcp --frontend-ip-name loadBalancerFrontEnd --frontend-port 80 --backend-pool-name loadBalancerBackEnd --backend-port 80 --probe-name tcp_probe_http)
                echo $(az network lb rule create -g <RESOURCE GROUP> --lb-name <RESOURCE GROUP>-existing-lb -n app-https --protocol Tcp --frontend-ip-name loadBalancerFrontEnd --frontend-port 443 --backend-pool-name loadBalancerBackEnd --backend-port 443 --probe-name tcp_probe_https)
            fi
        fi
fi

echo "Succeeded"