#!/usr/bin/env bash

echo "Starting Template Generation"

build/prepare_execution_enviroment.sh

echo "Executing Template Generator for cloud(s)" $@

python3 template_generator/main.py $@

echo "Execution has been completed."