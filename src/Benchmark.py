import os
from datetime import datetime
import sys
import ntpath
from subprocess import call

# name: name of the benchmark
# setup: commands to run prior to benchmarking
# setup_method: callback prior to benchmarking
# paths: absolute path of the files to grab after benchmarking is complete
# commands: commands to run when benchmarking
# reboots the device between setup time and benchmark time
class Benchmark(object):
    def __init__(self, 
            name, 
            commands=[], 
            setup_method=None, 
            setup=[],
            needs_reboot=False):
        self.name = name
        self.setup = setup # all the setup commands go here
        self.commands = commands # main commands
        self.setup_method = setup_method # gets called before run
        self.needs_reboot=needs_reboot

    def run(self, device):
        if self.setup_method is not None:
            self.setup_method()
        device.execute_commands(self.setup)
        if self.needs_reboot:
            device.reboot()
        device.execute_commands(self.commands)

# device: device object returned from src/Device
# command_once: only runs once prior to all the benchmarks
# common_setup: runs this before setup of each benchmark
# common_commands: runs these commands before the commands of each benchmark
# sendfiles: local paths to the files to be sent to the server
class BenchmarkRunner(object):
    def __init__(self,
            device,
            command_once = [],
            common_setup = [],
            common_commands = [],
            sendfiles=[]
           ):
        self.device = device
        self.benchmarks = {} 
        self.command_once = command_once
        self.common_setup = common_setup
        self.common_commands = common_commands
        
        # making input and output directories, sending input files
        self.device.clear_in_out_dir()
        self.device.send_files(sendfiles)

        # executing the commands that are meant to be run only once
        self.device.execute_commands(self.command_once)

    def add_benchmark(self, benchmark):
        self.benchmarks[benchmark.name] = benchmark
    
    def run_benchmarks(self, names=[], run_all=False):
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        foldername = 'report_' + time
        os.mkdir(foldername)
        deviceinfo = open('%s/deviceinfo.log' %foldername, 'w')
        deviceinfo.writelines([
                'device ip: %s\n' %self.device.device_ip,
                'time: %s\n'%time
            ])
        deviceinfo.close()
        for name in names:
            self.run_benchmark(self.benchmarks[name], foldername)

        #TODO: implement run_all
    
    def run_benchmark(self, benchmark, foldername):
        # adding the common setup and commands 
        benchmark.setup = self.common_setup + benchmark.setup
        benchmark.commands = self.common_commands + benchmark.commands
        try:
            # running the specific commands to each benchmark
            benchmark.run(self.device)
        except Exception as e:
            print(e)
            print("Running benchmark %s failed!" %benchmark.name)
            sys.exit()
        
        # where to store the report
        output_path = foldername + '/' + benchmark.name 
        output_file = output_path + '/%s.tar'%self.device.outputdir
        os.mkdir(output_path)

        # compressing output files
        self.device.execute_commands([
                ["tar -cf %s.tar %s"%(self.device.outputdir, self.device.outputdir), True]
            ])

        try:
            self.device.get_file('%s.tar'%self.device.outputdir, output_file)
        except Exception as e:
            print(e)
            print('couldn\'t get output.tar')
        call(['tar', '-xf', output_file, '-C', output_path])
