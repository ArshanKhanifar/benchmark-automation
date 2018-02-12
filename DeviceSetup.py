import src.util as util
import sys

# used for initial package installation and updating the kernel
class DeviceSetup(object):
    def __init__(self, device):
        self.device = device
        self.device_ip = util.get_device_ip(device)

    def setup(self):
        commands_setup = [
            "sed -i .bak 's/quarterly/latest/' /etc/pkg/FreeBSD.conf",
            "sed -i .bak -e '/^#.*ASSUME_ALWAYS_YES /s/^#//' -e '/ASSUME_ALWAYS_YES /s/false/true/' /usr/local/etc/pkg.conf",
            "sed -i '.bak' -e 's/^mlxen/mlx4en/' /boot/loader.conf",
            "pkg install tmux vim-console git fzf zsh x86info yasm",
            "git clone https://github.com/freebsd/freebsd.git /usr/tmp.src",
            "cp -r /usr/tmp.src/. /usr/src",
            "chsh -s /bin/sh",
        ]
        client = util.create_client(self.device_ip)
        util.execute_commands(client, commands_setup)
        client.close()
    
    def update(self):
        commands_update = [
            ["make -C /usr/src KERNCONF=GENERIC-NODEBUG -j$(sysctl -n hw.ncpu) buildkernel buildworld", True],
            ["make -C /usr/src KERNCONF=GENERIC-NODEBUG installkernel installworld", True],
        ]
        client = util.create_client(self.device_ip)
        util.execute_commands(client, commands_update)
        client.close()
        util.reboot_device(self.device)

