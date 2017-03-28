#/bin/bash

## BIGIP ARM Templates - Standalone (1nic, 2nic_limited)
# Experimental
python '.\master_template.py' --template-name 1nic --license-type PAYG --template-location '../experimental/standalone/1nic/PAYG/' --script-location '../experimental/standalone/1nic/'
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../experimental/standalone/1nic/BYOL/' --script-location '../experimental/standalone/1nic/'

python '.\master_template.py' --template-name 2nic_limited --license-type PAYG --template-location '../experimental/standalone/2nic_limited/PAYG/' --script-location '../experimental/standalone/2nic_limited/'
python '.\master_template.py' --template-name 2nic_limited --license-type BYOL --template-location '../experimental/standalone/2nic_limited/BYOL/' --script-location '../experimental/standalone/2nic_limited/'

python '.\master_template.py' --template-name 3_nic --license-type PAYG --template-location '../experimental/standalone/3_nic/PAYG/' --script-location '../experimental/standalone/3_nic/'
python '.\master_template.py' --template-name 3_nic --license-type BYOL --template-location '../experimental/standalone/3_nic/BYOL/' --script-location '../experimental/standalone/3_nic/'

# Supported
python '.\master_template.py' --template-name 1nic --license-type PAYG --template-location '../supported/standalone/1nic/PAYG/' --script-location '../supported/standalone/1nic/'
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../supported/standalone/1nic/BYOL/' --script-location '../supported/standalone/1nic/'

python '.\master_template.py' --template-name 2nic_limited --license-type PAYG --template-location '../supported/standalone/2nic_limited/PAYG/' --script-location '../supported/standalone/2nic_limited/'
python '.\master_template.py' --template-name 2nic_limited --license-type BYOL --template-location '../supported/standalone/2nic_limited/BYOL/' --script-location '../supported/standalone/2nic_limited/'

## BIGIP ARM Templates - Cluster (base)
# Experimental
python '.\master_template.py' --template-name cluster_base --license-type PAYG --template-location '../experimental/cluster/1nic/PAYG/' --script-location '../experimental/cluster/1nic/'
python '.\master_template.py' --template-name cluster_base --license-type BYOL --template-location '../experimental/cluster/1nic/BYOL/' --script-location '../experimental/cluster/1nic/'
# Supported
python '.\master_template.py' --template-name cluster_base --license-type PAYG --template-location '../supported/cluster/1nic/PAYG/' --script-location '../supported/cluster/1nic/'
python '.\master_template.py' --template-name cluster_base --license-type BYOL --template-location '../supported/cluster/1nic/BYOL/' --script-location '../supported/cluster/1nic/'

## BIGIP ARM Template - LTM AutoScale
# Experimental
python '.\master_template.py' --template-name ltm_autoscale --license-type PAYG --template-location '../experimental/autoscale/ltm/' --script-location '../experimental/autoscale/ltm/'

## BIGIP ARM Template - LTM AutoScale
# Experimental
python '.\master_template.py' --template-name waf_autoscale --license-type PAYG --template-location '../experimental/autoscale/waf/' --script-location '../experimental/autoscale/waf/' --solution-location 'experimental'