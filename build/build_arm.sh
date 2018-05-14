#/bin/bash

############################### Misc modifications during the build process ###############################
#### Right now only do the modifications if this (build) script includes release-prep as first arg
release_prep=""
if [[ $1 == "release-prep" ]]; then
    ## Update Exec bit on bash files if not set
    for f in `find .. -name '*.sh'`; do
        ( cd `dirname $f` && git update-index --chmod=+x `basename $f` )
    done
    ## Set build script release_prep flag
    release_prep="--release-prep"
fi

############################### Supported ###############################
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic), Cluster Failover-LB (1nic, 3nic), Cluster Failover-API
template_list="standalone/1nic standalone/2nic standalone/3nic standalone/n-nic cluster/failover-lb/1nic cluster/failover-lb/3nic cluster/failover-api"
for tmpl in $template_list; do
    loc=$tmpl
    if [[ $loc == *"standalone"* ]]; then
        tmpl="standalone_"`basename $loc`
    elif [[ $loc == *"failover-lb"* ]]; then
        tmpl="failover-lb_"`basename $loc`
    elif [[ $loc == *"failover-api"* ]]; then
        tmpl="failover-api"
    fi
    # Do not build production-stack for certain templates
    stack_list="new-stack existing-stack production-stack"
    if [[ $tmpl == *"failover-api"* ]] || [[ $tmpl == *"failover-lb_3nic"* ]]; then
        stack_list="new-stack existing-stack"
    fi
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type payg --stack-type $stack_type --template-location "../supported/$loc/$stack_type/payg/" --script-location "../supported/$loc/$stack_type/" $release_prep
        python -B '.\master_template.py' --template-name $tmpl --license-type byol --stack-type $stack_type --template-location "../supported/$loc/$stack_type/byol/" --script-location "../supported/$loc/$stack_type/" $release_prep
        # Don't build BIG-IQ template if stack type is production-stack
        if [[ $stack_type != *"production-stack"* ]]; then
            python -B '.\master_template.py' --template-name $tmpl --license-type bigiq --stack-type $stack_type --template-location "../supported/$loc/$stack_type/bigiq/" --script-location "../supported/$loc/$stack_type/" $release_prep
        fi
    done
done

## BIGIP ARM Templates - Solutions: autoscale/ltm, autoscale/waf
template_list="autoscale/ltm/via-lb autoscale/waf/via-lb"
for tmpl in $template_list; do
    loc=`echo $tmpl | sed 's/\/via-lb//g'|sed 's/\/via-dns//g'`
    if [[ $loc == *"autoscale"* ]]; then
        tmpl=`echo $tmpl | sed 's/\//_/g'`
    fi
    stack_list="new-stack existing-stack"
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type payg --stack-type $stack_type --template-location "../supported/$loc/$stack_type/payg/" --script-location "../supported/$loc/$stack_type/" --solution-location 'supported' $release_prep
        python -B '.\master_template.py' --template-name $tmpl --license-type bigiq --stack-type $stack_type --template-location "../supported/$loc/$stack_type/bigiq/" --script-location "../supported/$loc/$stack_type/" --solution-location 'supported' $release_prep
    done
done

############################### End Supported ###############################

############################### Experimental ###############################
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic), Cluster Failover-LB (1nic, 3nic), Cluster Failover-API
template_list="standalone/1nic standalone/2nic standalone/3nic standalone/n-nic cluster/failover-lb/1nic cluster/failover-lb/3nic cluster/failover-api"
for tmpl in $template_list; do
    loc=$tmpl
    if [[ $loc == *"standalone"* ]]; then
        tmpl="standalone_"`basename $loc`
    elif [[ $loc == *"failover-lb"* ]]; then 
        tmpl="failover-lb_"`basename $loc`
    elif [[ $loc == *"failover-api"* ]]; then
        tmpl="failover-api"
    fi
    # Do not build production-stack for certain templates
    stack_list="new-stack existing-stack production-stack"
    if [[ $tmpl == *"failover-api"* ]] || [[ $tmpl == *"failover-lb_3nic"* ]]; then
        stack_list="new-stack existing-stack"
    fi
    # Build learning-stack for certain templates
    if [[ $tmpl == *"standalone_3nic"* ]] || [[ $tmpl == *"failover-api"* ]]; then
        stack_list+=" learning-stack"
    fi
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type payg --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/payg/" --script-location "../experimental/$loc/$stack_type/" $release_prep
        python -B '.\master_template.py' --template-name $tmpl --license-type byol --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/byol/" --script-location "../experimental/$loc/$stack_type/" $release_prep
        # Don't build BIG-IQ template if stack type is production-stack
        if [[ $stack_type != *"production-stack"* ]]; then
            python -B '.\master_template.py' --template-name $tmpl --license-type bigiq --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/bigiq/" --script-location "../experimental/$loc/$stack_type/" $release_prep
        fi
    done
done

## BIGIP ARM Templates - Solutions: autoscale/ltm (via-dns, via-lb), autoscale/waf (via-dns, via-lb)
template_list="autoscale/ltm/via-lb autoscale/ltm/via-dns autoscale/waf/via-lb autoscale/waf/via-dns"
for tmpl in $template_list; do
    loc=$tmpl
    if [[ $loc == *"autoscale"* ]]; then
        tmpl=`echo $tmpl | sed 's/\//_/g'`
    fi
    stack_list="new-stack existing-stack"
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type payg --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/payg/" --script-location "../experimental/$loc/$stack_type/" --solution-location 'experimental' $release_prep
        python -B '.\master_template.py' --template-name $tmpl --license-type bigiq --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/bigiq/" --script-location "../experimental/$loc/$stack_type/" --solution-location 'experimental' $release_prep
        if [[ $tmpl == *"via-lb"* ]]; then
            python -B '.\master_template.py' --template-name $tmpl --license-type bigiq-payg --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/bigiq-payg/" --script-location "../experimental/$loc/$stack_type/" --solution-location 'experimental' $release_prep
        fi
    done
done

############################### End Experimental ###############################
