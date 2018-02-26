#!/usr/local/bin/zsh
source ./benchmark-automation/bin/activate

python ./main.py --device-ip '220.128.104.120' --password 'freebsd18' $@
