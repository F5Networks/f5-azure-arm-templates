#!/usr/bin/env bash

echo "Preparing python virtual enviroment"

python3 -m venv venv
. venv/bin/activate


pip3 install -r requirements.txt

echo "Created virtualenv environment in ./venv."
echo "Installed all dependencies into the virtualenv."

