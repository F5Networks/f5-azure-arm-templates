#/bin/bash

# BIGIP ARM Templates - Standalone (1nic, 2nic_limited)

# Experimental
python '.\master_template.py' --template-name 1nic --license-type PAYG --template-location '../experimental/standalone/1nic/PAYG/'
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../experimental/standalone/1nic/BYOL/'

python '.\master_template.py' --template-name 2nic_limited --license-type PAYG --template-location '../experimental/standalone/2nic_limited/PAYG/'
python '.\master_template.py' --template-name 2nic_limited --license-type BYOL --template-location '../experimental/standalone/2nic_limited/BYOL/'

# Supported
python '.\master_template.py' --template-name 1nic --license-type PAYG --template-location '../supported/standalone/1nic/PAYG/'
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../supported/standalone/1nic/BYOL/'

python '.\master_template.py' --template-name 2nic_limited --license-type PAYG --template-location '../supported/standalone/2nic_limited/PAYG/'
python '.\master_template.py' --template-name 2nic_limited --license-type BYOL --template-location '../supported/standalone/2nic_limited/BYOL/'

# BIGIP ARM Templates - Cluster (base)
# Test Location
python '.\master_template.py' --template-name cluster_base --license-type BYOL --template-location './testing_built_templates/cluster/1nic/'