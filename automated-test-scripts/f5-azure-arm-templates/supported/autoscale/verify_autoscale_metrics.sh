#  expectValue = "PASS"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

PASS_MSG="Test Result: PASS"

profile=$(az monitor autoscale show --resource-group <RESOURCE GROUP> --name <RESOURCE GROUP>-autoscaleconfig)
base_profile=$(echo $profile | jq -r '.profiles[] | select (.name=="Profile1")')

# Check that there are 4 rules, 2 for scale up and 2 for scale down
rules_count=$(echo $base_profile | jq '.rules | length')
echo "DEBUG - Rules count: $rules_count"
if [ "$rules_count" == 4 ] ; then
    echo $PASS_MSG
fi

# TODO: Could also check that that the threshold for the rules matches the input given