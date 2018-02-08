#!/bin/sh

curl -s -H 'X-Auth-Token: PDDno4gUFgZqMpE97nTKdvc1asVjqUyS' https://api.packet.net/market/spot/prices |\
        jq -c --stream . |\
        sed -e 's/.$//' |\
        awk -F, 'NF >4 { print $2","$3","$5 }' 
