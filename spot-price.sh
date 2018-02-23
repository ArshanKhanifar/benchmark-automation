#!/bin/sh
if [ -z $1 ]; then echo 'usage: ./spot-price.sh type'; fi;
#curl -H 'X-Auth-Token: PDDno4gUFgZqMpE97nTKdvc1asVjqUyS' https://api.packet.net/market/spot/prices | jq ".| .[] | to_entries | .[] | {location:.key, price:.value.$1.price}"
