import util
import os
from datetime import datetime
import sys

class Benchmark(object):
    def __init__(self, name, paths, commands, setup_method=None, setup=[]):
        self.name = name
        self.setup = setup # all the setup commands go here
        self.commands = commands # main commands
        self.setup_method = setup_method # gets called before run
        self.paths = paths

    def run(self, client):
        if self.setup_method is not None:
            self.setup_method()
        util.execute_commands(client, self.setup)
        util.execute_commands(client, self.commands)

class BenchmarkRunner(object):
    def __init__(self, client):
        self.client = client
        self.benchmarks = {} 
    
    def add_benchmark(self, benchmark):
        self.benchmarks[benchmark.name] = benchmark
    
    def run_benchmarks(self, names=[], run_all=False):
        foldername = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '-report'
        os.mkdir(foldername)
        for name in names:
            self.run_benchmark(self.benchmarks[name], foldername)

        #TODO: implement run_all
    
    def run_benchmark(self, benchmark, foldername):
        try:
            benchmark.run(self.client)
        except Exception as e:
            print(e)
            print("Running benchmark %s failed!" %benchmark.name)
            sys.exit()

        sftp_client = self.client.open_sftp()
        for path in benchmark.paths:
            try:
                sftp_client.get(path, foldername + path)
            except Exception as e:
                print(e)
                print('copying %s failed'%s)


