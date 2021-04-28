#  expectValue = "Succeeded"
#  expectFailValue = "Failed"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

SCALE_DOWN=$(az monitor autoscale update -g <RESOURCE GROUP> -n <RESOURCE GROUP>-autoscaleconfig --min-count 2 --count 2 | jq .name)

if [[ $SCALE_DOWN == \"<RESOURCE GROUP>-autoscaleconfig\" ]]; then
    echo "Succeeded"
else
    echo "Failed"
fi
