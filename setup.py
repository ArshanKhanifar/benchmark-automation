import src.util as util
import sys

def setup_device(ip_address):
    commands_setup = [
        "sed -i .bak 's/quarterly/latest/' /etc/pkg/FreeBSD.conf",
        "sed -i .bak -e '/^#.*ASSUME_ALWAYS_YES /s/^#//' -e '/ASSUME_ALWAYS_YES /s/false/true/' /usr/local/etc/pkg.conf",
        "pkg install tmux vim-console git fzf zsh x86info yasm",
        "git clone https://github.com/freebsd/freebsd.git /usr/tmp.src",
        "cp -r /usr/tmp.src/. /usr/src",
        "chsh -s /bin/sh",
    ]
    client = util.create_client(ip_address)
    util.execute_commands(client, commands_setup)
    client.close()

def update_device(ip_address):
    commands_update = [
        "make -C /usr/src KERNCONF=GENERIC-NODEBUG -j$(sysctl -n hw.ncpu) buildkernel buildworld",
        "make -C /usr/src KERNCONF=GENERIC-NODEBUG installkernel installworld"
    ]
    client = util.create_client(ip_address)
    util.execute_commands(client, commands_update)
    client.close()
    util.reboot_device(device)
    util.wait_till_active(device)
