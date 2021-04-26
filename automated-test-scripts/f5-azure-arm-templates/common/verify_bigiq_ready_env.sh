#  expectValue = "license valid"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 60

case <LICENSE TYPE> in
bigiq)
    LICENSE_HOST=`az deployment group show -g <RESOURCE GROUP> -n <RESOURCE GROUP>-env | jq '.properties.outputs["bigiqIp"].value' --raw-output | cut -d' ' -f1`

    sshpass -p 'B!giq2017' ssh -o StrictHostKeyChecking=no admin@${LICENSE_HOST} 'bash set-basic-auth on'

    ACTIVATED=$(curl -skvvu admin:'B!giq2017' https://${LICENSE_HOST}/mgmt/cm/device/licensing/pool/utility/licenses | jq .items[0].status)

    if [[ $ACTIVATED == \"READY\" ]]; then
        echo "license valid"
    else
        echo "sleep 2 minutes before retry"
        sleep 120
    fi
    ;;
*)
    echo "license valid" ;;
esac
