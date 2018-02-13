import util
import os
from datetime import datetime
import sys
import ntpath

# name: name of the benchmark
# setup: commands to run prior to benchmarking
# setup_method: callback prior to benchmarking
# paths: absolute path of the files to grab after benchmarking is complete
# commands: commands to run when benchmarking

class Benchmark(object):
    def __init__(self, 
            name, 
            paths, 
            commands, 
            setup_method=None, 
            setup=[],
            needs_reboot=False):
        self.name = name
        self.setup = setup # all the setup commands go here
        self.commands = commands # main commands
        self.setup_method = setup_method # gets called before run
        self.paths = paths
        self.needs_reboot=needs_reboot

    def run(self, client, device):
        device_id = device.id # saving in case of reboot
        if self.setup_method is not None:
            self.setup_method()
        util.execute_commands(client, self.setup)
        if self.needs_reboot:
            util.reboot_device(device)
        client = util.create_client(util.get_device_ip(device))
        util.execute_commands(client, self.commands)

class BenchmarkRunner(object):
    def __init__(self, client, device):
        self.client = client
        self.device = device
        self.benchmarks = {} 
        self.device_id = device.id
    
    def add_benchmark(self, benchmark):
        self.benchmarks[benchmark.name] = benchmark
    
    def run_benchmarks(self, names=[], run_all=False):
        foldername = 'report_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') 
        os.mkdir(foldername)
        for name in names:
            self.run_benchmark(self.benchmarks[name], foldername)

        #TODO: implement run_all
    
    def run_benchmark(self, benchmark, foldername):
        try:
            benchmark.run(self.client, self.device)
        except Exception as e:
            print(e)
            print("Running benchmark %s failed!" %benchmark.name)
            sys.exit()
        if benchmark.needs_reboot:
            self.client = util.create_client(util.get_device_ip(self.device))

        sftp_client = self.client.open_sftp()
        output_path = foldername + '/' + benchmark.name
        os.mkdir(output_path)
        for path in benchmark.paths:
            try:
                sftp_client.get(path, output_path + '/' + ntpath.basename(path))
            except Exception as e:
                print(e)
                print('copying %s failed'%s)

