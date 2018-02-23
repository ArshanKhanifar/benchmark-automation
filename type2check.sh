curl -H 'X-Auth-Token: PDDno4gUFgZqMpE97nTKdvc1asVjqUyS' https://api.packet.net/market/spot/prices | jq '.| .[] | to_entries | .[] | {type:.key, price:.value.baremetal_2.price}'
