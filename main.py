import packet
import subprocess
from src.arguments import mainParser
import src.util as util
import json
import time
import sys
from src.Benchmark import Benchmark, BenchmarkRunner
from DeviceSetup import DeviceSetup

args = mainParser.parse_args()

manager = packet.Manager(auth_token="PDDno4gUFgZqMpE97nTKdvc1asVjqUyS")

# get the device
device = util.get_testing_device(args)
# wait until device is active
util.wait_till_active(device)
ip_address = util.get_device_ip(device)

device_setup = DeviceSetup(device)

# setup: installs packages, sets environment configs
if args.skip_setup:
    print("skipping setup.")
else:
    device_setup.setup()

# update: builds and updates the kernel 
if args.skip_update:
    print("skipping update.")
else:
    device_setup.update()

if args.skip_benchmark:
    print("skipping benchmark.")
    sys.exit()

benchmarks = json.load(open(args.benchmarks_file))
client = util.create_client(ip_address)
benchmark_runner = BenchmarkRunner(client, device)
bNames= []
for benchmark in benchmarks:
    bObj = Benchmark(name=benchmark['name'],
            setup=benchmark['setup'],
            paths=benchmark['paths'],
            needs_reboot=benchmark['needs_reboot'],
            commands=benchmark['commands'])
    benchmark_runner.add_benchmark(bObj)
    bNames = bNames + [benchmark['name']]

benchmark_runner.run_benchmarks(names=bNames)
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
