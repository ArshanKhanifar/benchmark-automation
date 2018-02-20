import packet
import subprocess
from src.arguments import mainParser
import src.util as util
import json
import time
import sys
import copy
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
    print("Skipping setup.")
else:
    if args.custom_setup is not None:
        config = json.load(open(args.custom_setup))
        device_setup.setup(**config)
    else:
        device_setup.setup()

# update: builds and updates the kernel 
if args.skip_update:
    print("Skipping update.")
else:
    device_setup.update()

if args.skip_benchmark:
    print("Skipping benchmark.")
    sys.exit()

configDict = json.load(open(args.benchmarks_file))
client = util.create_client(ip_address)
benchmarkRunnerDict = copy.deepcopy(configDict)
benchmarkRunnerDict.pop('benchmarks')
benchmark_runner = BenchmarkRunner(
                        client, 
                        device,
                        **benchmarkRunnerDict)

bNames= []

for benchmark in configDict['benchmarks']:
    bDict = Benchmark(**benchmark)
    benchmark_runner.add_benchmark(bDict)
    bNames = bNames + [benchmark['name']]

benchmark_runner.run_benchmarks(names=bNames)
client.close()

print("BUENO")

sys.exit()

