#!/bin/bash

### Configure default values
log_level="info"
help=false
skip_verify=false
script_dir=$(dirname $0)


TMSH=/usr/bin/tmsh
CURL=/usr/bin/curl
NODE=/usr/bin/node
MKDIR=/bin/mkdir
MOUNT=/bin/mount
RMDIR=/bin/rmdir
UMOUNT=/bin/umount

### Functions - These should go into seperate file(s)
# usage: log message
function log() {
    echo "$(date '+%Y-%m-%dT%H:%M:%SZ'): $1"
}
# usage: get_version
function get_version() {
    ret=$($TMSH show sys version | grep -i product | awk '{print $2}')
    echo ${ret,,}
}
# usage: jsonify key:value,key1:value1
function jsonify() {
    list=$(echo $1 | tr ',' ' ')
    json='{}'
    for i in $list ; do
        kv=($(echo $i | tr ':' ' '))
        json=$(echo $json | jq --arg k ${kv[0]} --arg v ${kv[1]} '. | .[$k]=$v')
    done
    echo $json
}
# usage: get_val json_object key
function get_val() {
    ret=$(echo $1 | jq .$2 -r)
    echo $ret
}
# usage: make sure there is internet connection to GitHub
function check_internet_connection {
    echo "--- Checking Github status ---"
    checks=0
    github_response="bad"
    while [ $checks -lt 120 ] ; do
        github_response=`curl https://www.githubstatus.com/api/v2/status.json | jq .status.description --raw-output`
        if [ "$github_response" == "All Systems Operational" ]; then
            log "GitHub is ready"
            break
        fi
        log "GitHub not ready: $checks"
        let checks=checks+1
        sleep 5
    done
    if [ "$github_response" == "bad" ]; then
        log "No GitHub internet connection."
        exit
    fi
}
# usage: mcp_running
function mcp_running {
    checks=0
    while [ $checks -lt 120 ] ; do
        $TMSH -a show sys mcp-state field-fmt | grep -q running
        if [ $? == 0 ]; then
            log "MCPD ready"
            break
        fi
        log "MCPD not ready: $checks"
        let checks=checks+1
        sleep 5
    done
}
# usage: Download from Github until successful
#
# $1: output file name
# $2: URL
function safe_download {
    checks=0
    while [ $checks -lt 120 ] ; do
        $CURL --fail --retry 20 --retry-delay 5 --retry-max-time 240 -o $1 $2 && break
        let checks=checks+1
        sleep 5
    done
}
# usage: base_config_available - resolves issue found in 6.0.0 versions of big-iq
function base_config_available {
    checks=0
    while [ $checks -lt 120 ] ; do
        $TMSH -a show sys mcp-state field-fmt | grep -q running
        if [ -f /config/bigip_base.conf ]; then
            log "Base Config file present; saving config"
            tmsh save sys config
            cat /config/bigip_base.conf
            break
        fi
        log "Base config file not yet present: $checks"
        let checks=checks+1
        sleep 5
    done
}
# usage: get_net_info eth0 ns|gw include_cidr
function get_net_info() {
    RET=""
    CIDR_BLOCK=""
    if [[ $cloud == "azure" ]]; then
        add_int=1
        IF_MAC=$(ifconfig $1 | grep -i hwaddr | awk '{print $5}' | sed 's/://g')
        IF_INFO=$(curl -sf --retry 20 curl -H Metadata:true "http://169.254.169.254/metadata/instance/network/interface?api-version=2017-08-01" | jq '.[] | select(.macAddress=="'${IF_MAC}'")')
        CIDR_BLOCK=$(echo ${IF_INFO} | jq .ipv4.subnet[0].address --raw-output)
        CIDR_BLOCK+="/"
        CIDR_BLOCK+=$(echo ${IF_INFO} | jq .ipv4.subnet[0].prefix --raw-output)
    elif [[ $cloud == "aws" ]]; then
        cidr_block_uri="vpc-ipv4-cidr-block"
        add_int=2
        # If getting gateway, update necessary vars
        if [[ $2 == "gw" ]] ; then cidr_block_uri="subnet-ipv4-cidr-block" ; add_int=1 ; fi
        IF_MAC=$(ifconfig $1 | grep -i hwaddr | awk '{print tolower($5)}')
        CIDR_BLOCK=$(curl -sf --retry 20 http://169.254.169.254/latest/meta-data/network/interfaces/macs/${IF_MAC}/${cidr_block_uri})
    fi
    RET=$(echo ${CIDR_BLOCK%/*} | awk -F. '{ printf "%d.%d.%d.%d", $1, $2, $3, $4+'${add_int}' }')
    # Include mask in response if requested
    if [[ -n "$3" ]] ; then echo ${RET}/${CIDR_BLOCK#*/} ; else echo $RET ; fi
}
# creates a directory for in-memory files
# usage: create_temp_dir name size
function create_temp_dir() {
    $MKDIR "$1"
    $MOUNT -t tmpfs -o size="$2",mode=1700 tmpfs "$1"
}
# usage: remove_temp_dir name
function remove_temp_dir() {
    $UMOUNT "$1"
    $RMDIR "$1"
}
# usage: wipe_temp_dir name
function wipe_temp_dir() {
    FILES=$(ls -1 "$1")

    for f in $FILES; do
        shred --remove "${1}/${f}"
    done

    remove_temp_dir "$1"
}

read -r -d '' USAGE << EOM
    Usage: $0
        --help                      Print usage message and exit
        --log-level <string>        Level of logging desired: error, warn, info, debug
        --cloud <string>            Cloud environment executed against: aws
        --skip-verify <string>      Skip verification of dependencies
        --license <string>          License for the device
        --ntp <string>              NTP for the device
        --timezone <string>         Timezone for the device
        --data-interface <string>   Primary interface to use for data-plane
        --vlan <string>             VLAN(s) to create on the device (; for multiple) 'n:ext,nic:1.1'
        --self-ip <string>          Self IP(s) to create on the device (; for multiple): 'n:ext,a:x.x.x.x,v:ext,i:eth1'
        --usage-analytics <string>  Usage analytics to send: 'cN:val,r:val,cI:val,dI:val,lT:val,bIV:val,tN:val,tV:val,send:yes'
        --create-license-pool       Creates license pool, send: name:reg_key
        --create-reg-key-pool       Creates a regkey pool, send: name:reg_key_list
        --fcl-tag                   F5 cloud lib tag to download f5-cloud-libs.tar.gz
        --fcl-cloud-tag             F5 specified cloud tag to download f5-cloud-libs-<cloud>.tar.gz
        --big-iq-password           Bigiq password, used to onboard bigiq clusters
        --big-iq-master-key         Big-IQ masterkey used during inititial configuraiton
        --big-iq-password-data-uri  URI to the location that contains BIG-IQ admin user password
        --primary                   Indicates that this instance is master (used in BIG-IQ clustering) use with --big-iq-failover-peer-ip option
        --big-iq-failover-peer-ip   This is the private IP address for the secondary BIG-IQ
        --tag-value                 The tag value to add to the Elastic virtual IP address
        --vip-allocation-id         Allocation ID of the Elastic virtual IP address
        --private-ip                Private IP address associated with the Elastic virtual IP address
        --associate-eni             ENI of the network interface to associate the Elastic virtual IP address with in AWS
        --associate-intf            Name of the network interface to associate the virtual IP address with in Azure
        --dissociate-intf           Name of the network interface to dissociate the virtual IP address from in Azure


EOM

### Parse command line arguments
while [[ $# -gt 0 ]] ; do
    case "$1" in
        --help)
            help=true
            shift ;;
        --log-level)
            log_level="$2"
            shift 2 ;;
        --cloud)
            cloud="$2"
            shift 2 ;;
        --skip-verify)
            skip_verify=true
            shift ;;
        --license)
            license="$2"
            shift 2 ;;
        --ntp)
            ntp="$2"
            shift 2 ;;
        --timezone)
            timezone="$2"
            shift 2 ;;
        --data-interface)
            data_interface="$2"
            shift 2 ;;
        --usage-analytics)
            usage_analytics="$2"
            shift ;;
        --vlan)
            vlan="$2"
            shift 2 ;;
        --self-ip)
            self_ip="$2"
            shift 2 ;;
        --discovery-address)
            discovery_address="$2"
            shift 2 ;;
        --create-license-pool)
            license_pool="$2"
            shift 2 ;;
        --create-reg-key-pool)
            reg_key_pool="$2"
            shift 2 ;;
        --fcl-tag)
            fcl_tag="$2"
            shift 2 ;;
        --fcl-cloud-tag)
            fcl_cloud_tag="$2"
            shift 2 ;;
        --big-iq-password)
            bigiq_password="$2"
            shift 2 ;;
        --big-iq-master-key)
            bigiq_master_key="$2"
            shift 2 ;;
        --big-iq-password-data-uri)
            password_data_uri="$2"
            shift 2 ;;
        --primary)
            primary=true
            shift ;;
        --big-iq-failover-peer-ip)
            big_iq_failover_peer_ip="$2"
            shift 2 ;;
        --tag-value)
            tag_value="$2"
            shift 2 ;;
        --vip-allocation-id)
            vip_allocation_id="$2"
            shift 2 ;;
        --private-ip)
            private_ip="$2"
            shift 2 ;;
        --associate-eni)
            associate_eni="$2"
            shift 2 ;;
        --associate-intf)
            associate_intf="$2"
            shift 2 ;;
        --dissociate-intf)
            dissociate_intf="$2"
            shift 2 ;;
        *|--)
            shift
            break ;;
    esac
done

if $help ; then
    echo "$USAGE"
    exit
fi

# Verify required parameters
required=("cloud")
for i in ${required[@]} ; do
    if [ -z ${!i} ] ; then
        log "A required parameter is missing: $i"
        exit
    fi
done

config_params="--help $help --log-level $log_level --cloud $cloud --skip-verify $skip_verify --license $license --ntp $ntp --timezone $timezone  --data-interface $data_interface --usage-analytics $usage_analytics --vlan $vlan --self-ip $self_ip --discovery-address $discovery_address --create-license-pool $license_pool --create-reg-key-pool $reg_key_pool --fcl-tag $fcl_tag --fcl-cloud-tag $fcl_cloud_tag "

# Check for empty vars; add to config_parms is not empty
[[ ! -z "$primary" ]] && config_params+=" --primary $primary "
[[ ! -z "$bigiq_master_key" ]] && config_params+=" --big-iq-master-key $bigiq_master_key "
[[ ! -z "$password_data_uri" ]] && config_params+=" --big-iq-password-data-uri $password_data_uri "
[[ ! -z "$big_iq_failover_peer_ip" ]] && config_params+=" --big-iq-failover-peer-ip $big_iq_failover_peer_ip "
echo "Configuration parameters: ${config_params/$bigiq_master_key/Obfuscated}"
# Check for "Do Not Create" in create pool parmeters
shopt -s nocasematch
if [[ $license_pool == "Do_Not_Create" ]] ; then
    log "Setting licensing pool to null as 'Do_Not_Create' has been specified: $licensing_pool"
    license_pool=""
fi
if [[ $reg_key_pool == "Do_Not_Create" ]] ; then
    log "Setting reg key pool to null as 'Do_Not_Create' has been specified: $licensing_pool"
    reg_key_pool=""
fi
shopt -u nocasematch

### Install dependencies ###
## There must be GitHub internet connection
check_internet_connection

base_url="https://cdn.f5.com/product/cloudsolutions"
base_dir="/config/cloud"
base_log_dir="/var/log/cloud/${cloud}"
base_dependency_dir="${base_dir}/${cloud}/node_modules/@f5devcentral"

## Download
dependencies=("${base_url}/f5-cloud-libs/${fcl_tag}/f5-cloud-libs.tar.gz")
dependencies+=("${base_url}/f5-cloud-libs-${cloud}/${fcl_cloud_tag}/f5-cloud-libs-${cloud}.tar.gz")
dependencies+=("${base_url}/f5-cloud-libs/${fcl_tag}/verifyHash")

for i in ${dependencies[@]} ; do
    log "Downloading dependency: $i"
    f=$(basename $i)
    safe_download ${base_dir}/$f $i
    # $CURL -ksf --retry 10 --retry-delay 5 --retry-max-time 240 -o ${base_dir}/$f $i
done

## Verify
# MCP must be running first
mcp_running
base_config_available

if ! $skip_verify ; then
    verify_script="${base_dir}/verifyHash"
    if ! $TMSH load sys config merge file $verify_script ; then
        log "CLI verification script is not valid: $verify_script"
        exit 1
    fi

    for i in ${dependencies[@]} ; do
        f=$(basename $i)
        if [[ $f != "verifyHash" ]] ; then
            log "Verifying dependency: $f"
            if ! $TMSH run cli script verifyHash "/config/cloud/$f" ; then
                log "Dependency is not valid: $f"
                exit 1
            fi
        fi
    done
else
    log "Warning: Skipping dependency verification"
fi

## Install
mkdir -p $base_dependency_dir
for i in ${dependencies[@]} ; do
    f=$(basename $i)
    log "Installing dependency: $f"
    if [[ $f == *".tar"* ]] ; then
        tar xfz ${base_dir}/${f} -C $base_dependency_dir
    fi
done

## Signal
touch "${base_dir}/cloudLibsReady"

# Create tmp big-iq password file. Required for Azure big-iq clustering.
if [ -n "$bigiq_password" ] ; then
    echo 'Creating bigiq temporary password file.'
    tmp_file='/mnt/cloudTmp/.bigiq_pass'
    tmp_dir=$(dirname $tmp_file)
    create_temp_dir $tmp_dir
    echo "{ \"masterPassphrase\": \"${bigiq_master_key}\",\"root\": \"${bigiq_password}\",\"admin\": \"${bigiq_password}\" }" > $tmp_file
fi
### Provision Device ###
mkdir -p $base_log_dir
hostname=""
if [[ $cloud == "aws" ]]; then
    hostname=$($CURL -sf --retry 20 http://169.254.169.254/latest/meta-data/hostname)
elif [[ $cloud == "azure" ]]; then
    metadata=$($CURL -H Metadata:true "http://169.254.169.254/metadata/instance/compute?api-version=2017-12-01")
    hostname=$(echo ${metadata} | jq .name --raw-output)
    hostname+="."
    hostname+=$(echo ${metadata} | jq .location --raw-output)
    hostname+=".cloudapp.azure.com"
fi
host="localhost"
separator=";"

# Could use a generic --onboard|--network|etc for optional arguments
# instead, at least for now implement the additional abstraction

## Onboard
onboard_args=""
if [ -n "$cloud" ] ; then onboard_args+="--cloud ${cloud} " ; fi
if [ -n "$license" ] ; then onboard_args+="--license ${license} " ; fi
if [ -n "$ntp" ] ; then onboard_args+="--ntp ${ntp} " ; fi
if [ -n "$timezone" ] ; then onboard_args+="--tz ${timezone} " ; fi
if [ -n "$license_pool" ] ; then
    # Check for mulitiple license pools
    OIFS=$IFS
    IFS=",";
    licenseArray=($license_pool);
    for i in ${licenseArray[@]}; do
        flag=' --create-license-pool '
        cat_args="${cat_args}${flag}$i"
    done
    IFS=$OIFS;
    onboard_args+="${cat_args} " ; fi

if [ -n "$reg_key_pool" ] ; then onboard_args+="--create-reg-key-pool ${reg_key_pool} " ; fi

if [[ $cloud == "aws" ]]; then
    if [ -n "$data_interface" ] ; then onboard_args+="--dns $(get_net_info $data_interface ns) " ; fi
elif [[ $cloud == "azure" ]]; then
    if [ -n "$data_interface" ] ; then onboard_args+="--dns 168.63.129.16 " ; fi
fi

if [[ "$(get_version)" == "big-iq" && -n "$password_data_uri" ]]; then
    onboard_args+="--big-iq-password-data-uri ${password_data_uri} "
elif [[ "$(get_version)" == "big-iq" ]]; then
    onboard_args+="--set-master-key "
fi

if [ -n "$usage_analytics" ] ; then
    o=$(jsonify $usage_analytics)
    # Obfuscate sensitive information
    cI=$(echo $(get_val "$o" cI) | sha512sum | cut -d " " -f 1)
    dI=$(echo $(get_val "$o" dI) | sha512sum | cut -d " " -f 1)
    metrics+="cloudName:$(get_val "$o" cN),region:$(get_val "$o" r),customerId:${cI}"
    metrics+=",deploymentId:${dI},licenseType:$(get_val "$o" lT),bigIpVersion:$(get_val "$o" bIV)"
    metrics+=",templateName:$(get_val "$o" tN),templateVersion:$(get_val "$o" tV) "
    send_analytics=$(get_val "$o" send)
    if [[ "${send_analytics,,}" == "yes" ]] ; then onboard_args+="--metrics $metrics " ; fi
fi

$NODE "${base_dependency_dir}/f5-cloud-libs/scripts/onboard.js" --host $host --log-level $log_level \
    --output "${base_log_dir}/onboard.log" --signal ONBOARD_DONE --hostname $hostname $onboard_args &>> ${base_log_dir}/install.log

# TODO: Race condition between onboard/network - Using auth token results in 403 "not authorized"
# if network call immediately follows onboard.  Use following placeholder until fixed in f5-cloud-libs
# adding --wait-for signal for network call.
wait_time=30
log "Waiting: $wait_time"
sleep $wait_time

## Network
echo "Configuring network..."
network_args=""
if [ -n "$data_interface" ] ; then network_args+="--default-gw $(get_net_info $data_interface gw) " ; fi
if [ -n "$vlan" ] ; then
    for i in $(echo $vlan | tr "$separator" ' ') ; do
        o=$(jsonify $i)
        network_args+="--vlan name:$(get_val "$o" n),nic:$(get_val "$o" nic) "
    done
fi
if [ -n "$self_ip" ] ; then
    for i in $(echo $self_ip | tr "$separator" ' ') ; do
        o=$(jsonify $i)
        gw=$(get_net_info $(get_val "$o" i) gw cidr)
        network_args+="--self-ip name:$(get_val "$o" n),address:$(get_val "$o" a)/${gw#*/},vlan:$(get_val "$o" v) "
    done
fi
if [ -n "$discovery_address" ] ; then
    network_args+="--discovery-address ${discovery_address}"
fi
$NODE "${base_dependency_dir}/f5-cloud-libs/scripts/network.js" --host $host --log-level $log_level \
    --output "${base_log_dir}/network.log" --wait-for ONBOARD_DONE --signal NETWORK_DONE $network_args &>> ${base_log_dir}/install.log

## Add route to Instance Metadata service
# Allow system to use IPv4 link-local addresses in network routes
tmsh modify sys db config.allow.rfc3927 value enable

# Add route to Metadata service
gateway=$(tmsh list sys management-route gateway | grep gateway | head -n 1 | awk '{print $2}')
tmsh create sys management-route metadata network 169.254.169.254/32 gateway $gateway

## Cluster
if [[ -n "$primary" && -n "$big_iq_failover_peer_ip" ]] ; then
    echo "Configuring cluster..."
    cluster_args="--cloud $cloud --primary --big-iq-failover-peer-ip $big_iq_failover_peer_ip"
    if [ -n "$password_data_uri" ] ; then
        cluster_args+=" --big-iq-password-data-uri $password_data_uri "
    fi
    $NODE "${base_dependency_dir}/f5-cloud-libs/scripts/cluster.js" --host $host --log-level $log_level \
        --output "${base_log_dir}/cluster.log" --user admin $cluster_args &>> ${base_log_dir}/install.log
fi

# Failover
# Only perform failover for cluster solution
if [[ -n "$tag_value" ]] ; then
    failover_args="--log-level $log_level --log-file /var/log/cloud/$cloud/failover.log --tag-key f5_deployment "
    failover_args+="--tag-value $tag_value "

    if [[ $cloud == "aws" ]]; then
        if [ -n "$vip_allocation_id" ] ; then
        failover_args+="--vip-allocation-id $vip_allocation_id "
        fi

        if [ -n "$private_ip" ] ; then
            failover_args+="--private-ip $private_ip "
        fi

        if [ -n "$associate_eni" ] ; then
            failover_args+="--associate-eni $associate_eni "
        fi

        if [ -n "$password_data_uri" ] ; then
            failover_args+="--password-uri $password_data_uri "
        fi
    fi

    # Azure needs extra cares: after clustering is done, bigiq tmp password file will be deleted, we need bigiq password
    # to perform failover
    if [[ $cloud == "azure" ]]; then
        if [ -n "$bigiq_password" ] ; then
            ## If created, remove bigiq tmp password file
            tmp_file='/mnt/cloudTmp/.bigiq_pass'
            tmp_dir=$(dirname $tmp_file)
            wipe_temp_dir $tmp_dir
            echo 'Deleting bigiq temporary password file.'
            # Use bigiq password for failover script
            failover_args+="--password-data $bigiq_password "
        fi
        if [ -n "$associate_intf" ] ; then
        failover_args+="--associate-intf $associate_intf "
        fi

        if [ -n "$dissociate_intf" ] ; then
            failover_args+="--dissociate-intf $dissociate_intf "
        fi
    fi

    ## Make sure the secondary private IP address is a Self IP
    tmsh list net self | grep "$private_ip"
    if [[ $? != 0 ]]; then
        tmsh create net self lic_manager vlan internal allow-service default address ${private_ip}/32
    else
        echo "Appears $private_ip is already a Self IP"
    fi

    ## Create iCall script and handler to handle failover
    failover_script_loc="/config/cloud/${cloud}/node_modules/@f5devcentral/f5-cloud-libs-${cloud}/scripts/failover.js"
    icall_handler_name="FailoverHandler"
    icall_script_name="FailoverCollector"
    ## First check if iCall already exists
    tmsh list sys icall handler | grep $icall_handler_name
    if [[ $? != 0 ]]; then
        tmsh create sys icall script $icall_script_name definition { if { [catch {set is_failover_running [exec pgrep -f  "$failover_script_loc"]}] } { exec node $failover_script_loc $failover_args } else { puts "$icall_script_name is already running with PID $is_failover_running" } }
        tmsh create sys icall handler periodic /Common/$icall_handler_name { first-occurrence now interval 60 script /Common/$icall_script_name }
    else
        echo "Appears the $icall_handler_name icall already exists!"
    fi
fi

tmsh save sys config
