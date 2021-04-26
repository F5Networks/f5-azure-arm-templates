#  expectValue = "Succeeded"
#  expectFailValue = "Failed"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

SCALE_UP=$(az monitor autoscale update -g <RESOURCE GROUP> -n <RESOURCE GROUP>-autoscaleconfig --min-count 3 --count 3 | jq .name)

if [[ $SCALE_UP == \"<RESOURCE GROUP>-autoscaleconfig\" ]]; then
    echo "Succeeded"
else
    echo "Failed"
fi