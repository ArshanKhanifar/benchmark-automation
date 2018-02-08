import packet
import subprocess
from src.arguments import mainParser
import src.util as util
import json
from paramiko.client import SSHClient,AutoAddPolicy
import time

args = mainParser.parse_args()

manager = packet.Manager(auth_token="PDDno4gUFgZqMpE97nTKdvc1asVjqUyS")

# get the device
device = util.get_testing_device(args)
# wait until device is active
util.wait_till_active(device)

ip_address = util.get_device_ip(device)

print(ip_address)

def create_client():
    client = None
    try:
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(ip_address, 
                       username='root',
                       passphrase='Physics92',
                       timeout=5)
    except:
        print("ssh couldn't connect, trying again...")
        time.sleep(1)
        return create_client()
    return client

commands = [
#    "sed -i .bak 's/quarterly/latest/' /etc/pkg/FreeBSD.conf",
#    "sed -i .bak -e '/^#.*ASSUME_ALWAYS_YES /s/^#//' -e '/ASSUME_ALWAYS_YES /s/false/true/' /usr/local/etc/pkg.conf",
#    "pkg install tmux vim-console git fzf zsh x86info yasm",
#    "git clone https://github.com/freebsd/freebsd.git /usr/tmp.src",
#    "cp -r /usr/tmp.src/. /usr/src",
    "make -C /usr/src KERNCONF=GENERIC-NODEBUG -j$(sysctl hw.ncpu|awk 'NF>1{print $NF}) buildkernel buildworld",
    "make -C /usr/src KERNCONF=GENERIC-NODEBUG installkernel installworld"
]
client = create_client()
for command in commands: 
    util.execute_command(client, command)

client.close()
util.reboot_device(device)
util.wait_till_active(device)

post_reboot_commands = [
    "uname -a"
]

client = create_client()
for command in post_reboot_commands:
    util.execute_command(client, command)

client.close()
