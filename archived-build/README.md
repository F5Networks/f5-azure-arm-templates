# F5-Azure-Arm-Templates Build Directory

This directory contains all the files and scripts necessary to build the ARM templates and additional components within this repository. It is meant to be used by the maintainers of this project and not meant for end-users. It's purpose is to ensure that the solutions contained in this repository are organized and created in a reliable and deterministic manner.

## master_template.py

The primary build script that is used to declare the ARM template sections. - It utilizes helper modules (master_helper.py, readme_generator.py) in the same directory to complete the full build for each solution.

Note: Run ```pip install -r requirements.txt``` to pull in any modules necessary for the build process.

## build.sh

A bash wrapper script that contains the list of solutions to be built by **master-template.py**.

## /Files directory

The files directory contains both base elements for the ARM templates as well as base script files.  It also contains the files used to auto-generate the README's for each solution.