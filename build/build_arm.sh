#/bin/bash

#### Experimental ####
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic)
python '.\master_template.py' --template-name 1nic --license-type PAYG --template-location '../experimental/standalone/1nic/PAYG/' --script-location '../experimental/standalone/1nic/'
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../experimental/standalone/1nic/BYOL/' --script-location '../experimental/standalone/1nic/'

python '.\master_template.py' --template-name 2nic --license-type PAYG --stack-type 'new' --template-location '../experimental/standalone/2nic/new_stack/PAYG/' --script-location '../experimental/standalone/2nic/new_stack/'
python '.\master_template.py' --template-name 2nic --license-type BYOL --stack-type 'new' --template-location '../experimental/standalone/2nic/new_stack/BYOL/' --script-location '../experimental/standalone/2nic/new_stack/'
python '.\master_template.py' --template-name 2nic --license-type PAYG --stack-type 'existing' --template-location '../experimental/standalone/2nic/existing_stack/PAYG/' --script-location '../experimental/standalone/2nic/existing_stack/'
python '.\master_template.py' --template-name 2nic --license-type BYOL --stack-type 'existing' --template-location '../experimental/standalone/2nic/existing_stack/BYOL/' --script-location '../experimental/standalone/2nic/existing_stack/'

python '.\master_template.py' --template-name 3nic --license-type PAYG --stack-type 'new' --template-location '../experimental/standalone/3nic/new_stack/PAYG/' --script-location '../experimental/standalone/3nic/new_stack/'
python '.\master_template.py' --template-name 3nic --license-type BYOL --stack-type 'new' --template-location '../experimental/standalone/3nic/new_stack/BYOL/' --script-location '../experimental/standalone/3nic/new_stack/'
python '.\master_template.py' --template-name 3nic --license-type PAYG --stack-type 'existing' --template-location '../experimental/standalone/3nic/existing_stack/PAYG/' --script-location '../experimental/standalone/3nic/existing_stack/'
python '.\master_template.py' --template-name 3nic --license-type BYOL --stack-type 'existing' --template-location '../experimental/standalone/3nic/existing_stack/BYOL/' --script-location '../experimental/standalone/3nic/existing_stack/'

## BIGIP ARM Templates - Cluster (base)
python '.\master_template.py' --template-name cluster_base --license-type PAYG --template-location '../experimental/cluster/1nic/PAYG/' --script-location '../experimental/cluster/1nic/'
python '.\master_template.py' --template-name cluster_base --license-type BYOL --template-location '../experimental/cluster/1nic/BYOL/' --script-location '../experimental/cluster/1nic/'

## BIGIP ARM Template - LTM AutoScale
python '.\master_template.py' --template-name ltm_autoscale --license-type PAYG --template-location '../experimental/autoscale/ltm/' --script-location '../experimental/autoscale/ltm/' --solution-location 'experimental'

## BIGIP ARM Template - WAF AutoScale
python '.\master_template.py' --template-name waf_autoscale --license-type PAYG --template-location '../experimental/autoscale/waf/' --script-location '../experimental/autoscale/waf/' --solution-location 'experimental'

#### End Experimental ####


#### Supported ####
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic)
python '.\master_template.py' --template-name 1nic --license-type PAYG --template-location '../supported/standalone/1nic/PAYG/' --script-location '../supported/standalone/1nic/'
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../supported/standalone/1nic/BYOL/' --script-location '../supported/standalone/1nic/'

python '.\master_template.py' --template-name 2nic --license-type PAYG --template-location '../supported/standalone/2nic/PAYG/' --script-location '../supported/standalone/2nic/'
python '.\master_template.py' --template-name 2nic --license-type BYOL --template-location '../supported/standalone/2nic/BYOL/' --script-location '../supported/standalone/2nic/'

python '.\master_template.py' --template-name 3nic --license-type PAYG --template-location '../supported/standalone/3nic/PAYG/' --script-location '../supported/standalone/3nic/'
python '.\master_template.py' --template-name 3nic --license-type BYOL --template-location '../supported/standalone/3nic/BYOL/' --script-location '../supported/standalone/3nic/'

## BIGIP ARM Templates - Cluster (base)
python '.\master_template.py' --template-name cluster_base --license-type PAYG --template-location '../supported/cluster/1nic/PAYG/' --script-location '../supported/cluster/1nic/'
python '.\master_template.py' --template-name cluster_base --license-type BYOL --template-location '../supported/cluster/1nic/BYOL/' --script-location '../supported/cluster/1nic/'

#### End Supported ####
