#!/usr/bin/env bash
#  expectValue = "good"
#  scriptTimeout = 2
#  replayEnabled = false
#  replayTimeout = 20


echo "--- Deployment Status ---"
STATUS=$(az deployment operation group list -g <RESOURCE GROUP> -n <RESOURCE GROUP>)
echo $STATUS | jq .


if [[ ! -z $STATUS ]]; then
    echo "good"
fi