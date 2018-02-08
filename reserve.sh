#!/usr/bin/env bash

# provisioning spot market
# usage:
#    packet-spot-market-provision packet/example-provisioning.json

source ~/.config/packet-api/api
PROJECT=465c261b-19bc-45b0-a1b5-55f9dd6f5f09
(($# > 0)) && cat <<EOF && exit 1
This script accepts no arguments, all configuration is via env vars.
The following env vars (and defaults) are used:
FACILITY: ewr1
NAME:  test
OS: ubuntu_16_04
TYPE: baremetal_1
EOF
FACILITY=ewr1
TYPE=baremetal_1
OS=freebsd_11_0
json=$(
       cat <<EOF
{
   "hostname": "${NAME:-test}",
   "plan": "${TYPE:-baremetal_1}",
   "operating_system": "${OS:-ubuntu_16_04}",
   "facility": "${FACILITY:-ewr1}",
   "billing_cycle": "hourly",
   "spot_instance": true,
   "spot_price_max":0.5,
   "termination_time": null,
   "project_ssh_keys":[],
   "user_ssh_keys":[]
}
EOF
)

echo "request:"
echo $json | jq -S .

echo "response:"
curl -fH "X-Auth-Token: $PACKET_API_AUTH_TOKEN_RW" \
       -H "Content-Type: application/json" \
       -X POST \
       -d "$json" \
       https://api.packet.net/projects/$PROJECT/devices | jq -S .
