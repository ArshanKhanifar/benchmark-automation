import src.util as util
import json
import sys

# used for initial package installation and updating the kernel
class DeviceSetup(object):
    def __init__(self, device):
        self.device = device
        self.device_ip = util.get_device_ip(device)

    def setup(self, revision='HEAD', patches=[]):
        self.__env_setup()
        self.__source_tree_setup(revision)
        self.__apply_patches(patches)
  
    def __env_setup(self):
        commands_setup = [
            "sed -i .bak 's/quarterly/latest/' /etc/pkg/FreeBSD.conf",
            "sed -i .bak -e '/^#.*ASSUME_ALWAYS_YES /s/^#//' -e '/ASSUME_ALWAYS_YES /s/false/true/' /usr/local/etc/pkg.conf",
            "sed -i '.bak' -e 's/^mlxen/mlx4en/' /boot/loader.conf",
            "pkg install tmux vim-console git fzf zsh x86info yasm",
            "chsh -s /usr/local/bin/zsh"
        ]
        client = util.create_client(self.device_ip)
        util.execute_commands(client, commands_setup)
        client.close()

    def __source_tree_setup(self, rev):
        commands_source_setup = [
            "git clone https://github.com/freebsd/freebsd.git /usr/tmp.src",
            "cp -r /usr/tmp.src/. /usr/src",
            "cd /usr/src && git checkout %s"%rev
        ]

        client = util.create_client(self.device_ip)
        util.execute_commands(client, commands_source_setup)
        client.close()

    def __apply_patches(self, patches):
        client = util.create_client(self.device_ip)
        sftp_client = client.open_sftp()
        patchdir = 'patches'
        # all the patches will be at remote /root/patches directory
        if util.dir_exists(sftp_client, patchdir):
            util.rm_dir_recursive(client, patchdir)
        sftp_client.mkdir(patchdir)
        # patch is either a link to a diff file or a relative path to a diff file
        for patch in patches:
            if patch.startswith('http'):
                util.execute_command(client, 'curl -k %s | git --git-dir=/usr/src/.git apply -p0'%patch)
            else:
                sftp_client.put(patch, '/root/%s/%s'%(patchdir, patch))
                util.execute_commands(client, [
                        'cd /usr/src',
                        'git apply -p0 < /root/%s/%s'%(patchdir, patch)
                    ])

    def update(self):
        commands_update = [
            ["make -C /usr/src KERNCONF=GENERIC-NODEBUG -j$(sysctl -n hw.ncpu) buildkernel buildworld", True],
            ["make -C /usr/src KERNCONF=GENERIC-NODEBUG installkernel installworld", True],
        ]
        client = util.create_client(self.device_ip)
        util.execute_commands(client, commands_update)
        client.close()
        util.reboot_device(self.device)

