import util
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

    def run(self, client, device):
        device_id = device.id # saving in case of reboot
        if self.setup_method is not None:
            self.setup_method()
        util.execute_commands(client, self.setup)
        if self.needs_reboot:
            util.reboot_device(device)
        client = util.create_client(util.get_device_ip(device))
        util.execute_commands(client, self.commands)

# client: SSH client to run the commands on 
# device: device object return from packet's api
# command_once: only runs once prior to all the benchmarks
# common_setup: runs this before setup of each benchmark
# common_commands: runs these commands before the commands of each benchmark
# sendfiles: local paths to the files to be sent to the server
class BenchmarkRunner(object):
    def __init__(self,
            client,
            device,
            command_once = [],
            common_setup = [],
            common_commands = [],
            sendfiles=[]
           ):
        self.client = client
        self.device = device
        self.benchmarks = {} 
        self.device_id = device.id
        self.command_once = command_once
        self.common_setup = common_setup
        self.common_commands = common_commands

        sftp_client = self.client.open_sftp()
        # creating input and output directories, deletes them if they exist
        if util.dir_exists(sftp_client, 'output'):
            util.rm_dir_recursive(client, 'output')
        sftp_client.mkdir('output')
        if util.dir_exists(sftp_client, 'input'):
            util.rm_dir_recursive(client, 'input')
        sftp_client.mkdir('input')

        # sending input files
        for filename in sendfiles:
            sftp_client.put(filename, '/root/input/' + filename)
        # executing the commands that are meant to be run only once
        util.execute_commands(client, self.command_once)

    def add_benchmark(self, benchmark):
        self.benchmarks[benchmark.name] = benchmark
    
    def run_benchmarks(self, names=[], run_all=False):
        foldername = 'report_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') 
        os.mkdir(foldername)
        for name in names:
            self.run_benchmark(self.benchmarks[name], foldername)

        #TODO: implement run_all
    
    def run_benchmark(self, benchmark, foldername):
        # adding the common setup and commands 
        benchmark.setup = self.common_setup + benchmark.setup
        benchmark.commands = self.common_commands + benchmark.commands
        try:
            # running the specific commands to each benchmark
            benchmark.run(self.client, self.device)
        except Exception as e:
            print(e)
            print("Running benchmark %s failed!" %benchmark.name)
            sys.exit()
        if benchmark.needs_reboot:
            self.client = util.create_client(util.get_device_ip(self.device))
        
        sftp_client = self.client.open_sftp()
        # where to store the report
        output_path = foldername + '/' + benchmark.name 
        output_file = output_path + '/output.tar' 
        os.mkdir(output_path)

        # compressing output files
        util.execute_commands(self.client, [
                ["tar -cf output.tar output", True]
            ])

        try: 
            sftp_client.get('output.tar', output_file)
        except Exception as e:
            print(e)
            print('couldn\'t get output.tar')
        call(['tar', '-xf', output_file, '-C', output_path])

