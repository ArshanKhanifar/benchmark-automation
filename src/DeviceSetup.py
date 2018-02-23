import sys

# used for initial package installation and updating the kernel
class DeviceSetup(object):
    def __init__(self, device):
        self.device = device

    def setup(self):
        commands_setup = [
            #"sed -i .bak 's/quarterly/latest/' /etc/pkg/FreeBSD.conf",
            #"sed -i .bak -e '/^#.*ASSUME_ALWAYS_YES /s/^#//' -e '/ASSUME_ALWAYS_YES /s/false/true/' /usr/local/etc/pkg.conf",
            #"sed -i '.bak' -e 's/^mlxen/mlx4en/' /boot/loader.conf",
            #"pkg install tmux vim-console git fzf zsh x86info yasm bash",
            #"chsh -s /usr/local/bin/zsh",
            "sh -c \"$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)\""
        ]
        self.device.execute_commands(commands_setup)

    def update(self, revision='HEAD', patches=[]):
        self.__source_tree_setup(revision)
        self.__apply_patches(patches)

        commands_update = [
            ["make -C /usr/src KERNCONF=GENERIC-NODEBUG -j$(sysctl -n hw.ncpu) buildkernel buildworld", True],
            ["make -C /usr/src KERNCONF=GENERIC-NODEBUG installkernel installworld", True],
        ]
        self.device.execute_commands(commands_update)
        self.device.reboot()

    def __source_tree_setup(self, rev):
        commands_source_setup = [
            "git clone https://github.com/freebsd/freebsd.git /usr/tmp.src",
            "cp -r /usr/tmp.src/. /usr/src",
            "cd /usr/src && git checkout %s"%rev
        ]
        self.device.execute_commands(commands_source_setup)

    def __apply_patches(self, patches):
        # patch is either a link to a diff file or a relative path to a diff file
        for patch in patches:
            if patch.startswith('http'):
                self.device.execute_commands([
                        'cd /usr/src',
                        'curl -k %s | git apply -p0'%patch
                    ])
            else:
                self.send_file(patch)
                patchname = patch.split('/')[-1]
                self.device.execute_commands([
                        'cd /usr/src',
                        'git apply -p0 < /root/%s/%s'%(self.device.inputdir, patchname)
                    ])

