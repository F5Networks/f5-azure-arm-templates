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
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic), Cluster (1nic, 3nic), HA-AVSET
template_list="standalone/1nic standalone/2nic standalone/3nic standalone/n-nic cluster/1nic cluster/3nic ha-avset"
for tmpl in $template_list; do
    loc=$tmpl
    if [[ $loc == *"standalone"* ]]; then
        tmpl="standalone_"`basename $loc`
    elif [[ $loc == *"cluster"* ]]; then
        tmpl="cluster_"`basename $loc`
    fi
    # Do not build prod_stack for certain templates
    stack_list="new_stack existing_stack prod_stack"
    if [[ $tmpl == *"ha-avset"* ]] || [[ $tmpl == *"cluster_"* ]]; then
        stack_list="new_stack existing_stack"
    fi
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type PAYG --stack-type $stack_type --template-location "../supported/$loc/$stack_type/PAYG/" --script-location "../supported/$loc/$stack_type/" $release_prep
        python -B '.\master_template.py' --template-name $tmpl --license-type BYOL --stack-type $stack_type --template-location "../supported/$loc/$stack_type/BYOL/" --script-location "../supported/$loc/$stack_type/" $release_prep
        # Don't build BIG-IQ template if stack type is prod_stack
        if [[ $stack_type != *"prod_stack"* ]]; then
            python -B '.\master_template.py' --template-name $tmpl --license-type BIGIQ --stack-type $stack_type --template-location "../supported/$loc/$stack_type/BIGIQ/" --script-location "../supported/$loc/$stack_type/" $release_prep
        fi
    done
done

## BIGIP ARM Templates - Solutions (autoscale/ltm, autoscale/waf)
template_list="autoscale/ltm autoscale/waf"
for tmpl in $template_list; do
    loc=$tmpl
    if [[ $loc == *"autoscale"* ]]; then
        tmpl=`basename $loc`"_autoscale"
    fi
    stack_list="new_stack existing_stack"
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type PAYG --stack-type $stack_type --template-location "../supported/solutions/$loc/$stack_type/PAYG/" --script-location "../supported/solutions/$loc/$stack_type/" --solution-location 'supported' $release_prep
        python -B '.\master_template.py' --template-name $tmpl --license-type BIGIQ --stack-type $stack_type --template-location "../supported/solutions/$loc/$stack_type/BIGIQ/" --script-location "../supported/solutions/$loc/$stack_type/" --solution-location 'supported' $release_prep
    done
done

############################### End Supported ###############################

############################### Experimental ###############################
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic), Cluster (1nic, 3nic), HA-AVSET
template_list="standalone/1nic standalone/2nic standalone/3nic standalone/n-nic cluster/1nic cluster/3nic ha-avset"
for tmpl in $template_list; do
    loc=$tmpl
    if [[ $loc == *"standalone"* ]]; then
        tmpl="standalone_"`basename $loc`
    elif [[ $loc == *"cluster"* ]]; then
        tmpl="cluster_"`basename $loc`
    fi
    # Do not build prod_stack for certain templates
    stack_list="new_stack existing_stack prod_stack"
    if [[ $tmpl == *"ha-avset"* ]] || [[ $tmpl == *"cluster_3nic"* ]]; then
        stack_list="new_stack existing_stack"
    fi
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type PAYG --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/PAYG/" --script-location "../experimental/$loc/$stack_type/" $release_prep
        python -B '.\master_template.py' --template-name $tmpl --license-type BYOL --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/BYOL/" --script-location "../experimental/$loc/$stack_type/" $release_prep
        # Don't build BIG-IQ template if stack type is prod_stack
        if [[ $stack_type != *"prod_stack"* ]]; then
            python -B '.\master_template.py' --template-name $tmpl --license-type BIGIQ --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/BIGIQ/" --script-location "../experimental/$loc/$stack_type/" $release_prep
        fi
    done
done

## BIGIP ARM Templates - Solutions (autoscale/ltm, autoscale/waf)
template_list="autoscale/ltm autoscale/waf"
for tmpl in $template_list; do
    loc=$tmpl
    if [[ $loc == *"autoscale"* ]]; then
        tmpl=`basename $loc`"_autoscale"
    fi
    stack_list="new_stack existing_stack"
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type PAYG --stack-type $stack_type --template-location "../experimental/solutions/$loc/$stack_type/PAYG/" --script-location "../experimental/solutions/$loc/$stack_type/" --solution-location 'experimental' $release_prep
        python -B '.\master_template.py' --template-name $tmpl --license-type BIGIQ --stack-type $stack_type --template-location "../experimental/solutions/$loc/$stack_type/BIGIQ/" --script-location "../experimental/solutions/$loc/$stack_type/" --solution-location 'experimental' $release_prep
    done
done

############################### End Experimental ###############################
