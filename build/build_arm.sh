#/bin/bash

# BIGIP ARM Templates - Standalone (1nic, 2nic_limited)

# Experimental
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../experimental/standalone/1nic/'

python '.\master_template.py' --template-name 2nic_limited --license-type BYOL --template-location '../experimental/standalone/2nic_limited/'
# Supported
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../supported/standalone/1nic/'

python '.\master_template.py' --template-name 2nic_limited --license-type BYOL --template-location '../supported/standalone/2nic_limited/'