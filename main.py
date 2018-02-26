from src.arguments import args
from src.Benchmark import Benchmark, BenchmarkRunner
from src.Device import Device
from src.DeviceSetup import DeviceSetup
import src.PacketUtil as PacketUtil

import json
import sys
import copy

device_ip = args.device_ip 

if args.create_new:
    device_ip = PacketUtil.create_device(args)

device = Device(device_ip,
            password=args.password,
            passphrase=args.passphrase,
            load_keys=args.load_keys)
device_setup = DeviceSetup(device)

# setup: installs packages, sets environment configs
if args.setup:
    device_setup.setup()

# update: builds and updates the kernel 
if args.update:
    if args.custom_update is not None:
        config = json.load(open(args.custom_update))
        device_setup.update(**config)
    else:
        device_setup.update()

if args.benchmarks_file is None:
    print("No benchmarks file provided.")
    sys.exit()

configDict = json.load(open(args.benchmarks_file))
benchmarkRunnerDict = copy.deepcopy(configDict)
benchmarkRunnerDict.pop('benchmarks')
benchmark_runner = BenchmarkRunner(
                        device,
                        **benchmarkRunnerDict)

bNames= []

for benchmark in configDict['benchmarks']:
    bDict = Benchmark(**benchmark)
    benchmark_runner.add_benchmark(bDict)
    bNames = bNames + [benchmark['name']]

benchmark_runner.run_benchmarks(names=bNames)

print("BUENO")

sys.exit()

