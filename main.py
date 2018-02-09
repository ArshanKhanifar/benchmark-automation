import packet
import subprocess
from src.arguments import mainParser
import src.util as util
import json
import time
import sys
from src.Benchmark import Benchmark, BenchmarkRunner

def setup_device():
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

def update_device():
    commands_build = [
        ["make -C /usr/src KERNCONF=GENERIC-NODEBUG -j$(sysctl -n hw.ncpu) buildkernel buildworld", True],
        ["make -C /usr/src KERNCONF=GENERIC-NODEBUG installkernel installworld", True],
    ]
    client = util.create_client(ip_address)
    util.execute_commands(client, commands_build)
    client.close()
    util.reboot_device(device)
    util.wait_till_active(device)

args = mainParser.parse_args()

manager = packet.Manager(auth_token="PDDno4gUFgZqMpE97nTKdvc1asVjqUyS")

# get the device
device = util.get_testing_device(args)
# wait until device is active
util.wait_till_active(device)
ip_address = util.get_device_ip(device)

# setup: installs packages, sets environment configs
if args.skip_setup:
    print("skipping setup.")
else:
    setup_device()

# update: builds and updates the kernel 
if args.skip_update:
    print("skipping update.")
else:
    update_device()

test_setup = [
    "make -C /usr/src/tools/tools/syscall_timing",
]

test_commands = [
    "uname -a > uname.log",
    "x86info -a > x86info.log",
    "/usr/obj/usr/src/amd64.amd64/tools/tools/syscall_timing/syscall_timing getppid > getppid.log"
]

test_paths = [
    "/root/uname.log",
    "/root/x86info.log",
    "/root/getppid.log",
]

test_benchmark = Benchmark(name='test',
                           setup=test_setup,
                           paths=test_paths,
                           commands=test_commands)

client = util.create_client(ip_address)
benchmark_runner = BenchmarkRunner(client)
benchmark_runner.run_benchmarks(names=['test'])
client.close()
print("BUENO")

sys.exit()

client = util.create_client(ip_address)
sftp_client = client.open_sftp()
sftp_client.put('binaries.tar', '/root/binaries.tar')
util.execute_commands(client, [
        "kldload cpuctl",
        #"tar -xf binaries.tar",
        "for x in $("
                      "jot $("
                               "expr $(sysctl -n hw.ncpu) - 1"
                           ") 0"
                  ");"
                      "do cpucontrol -u -d ./binaries /dev/cpuctl$x;"
                      "done"
    ])
