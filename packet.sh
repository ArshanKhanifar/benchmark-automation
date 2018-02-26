#!/usr/local/bin/zsh
source ./benchmark-automation/bin/activate

python ./main.py --passphrase 'Physics92' $@
