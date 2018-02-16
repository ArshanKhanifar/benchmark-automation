import argparse

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

mainParser = argparse.ArgumentParser(description='Benchmark for pti, and ibrs:')

mainParser.add_argument('--skip-setup',
                    action='store_true',
                    help='skips the machine setup')

mainParser.add_argument('--skip-update',
                    action='store_true',
                    help='skips the kernel update')

mainParser.add_argument('--skip-benchmark',
                    action='store_true',
                    help='does not perform benchmarking, used for setting up a server for other purposes')

mainParser.add_argument('--use-last',
                    action='store_true',
                    help='uses the last device id used, (stored in cache/deviceid)')

mainParser.add_argument('-s', '-spotmarket',
                    action='store',
                    default=True,
                    metavar='spotmarket',
                    type=str2bool,
                    help='use spotmarket pricing, defaults to true')

mainParser.add_argument('--custom-setup',
                    action='store',
                    help='used for updating the kernel to a specific revision, and applying custom patches. Takes in the path to a custom setup json file.') 

mainParser.add_argument('--device-id',
                    action='store',
                    help='when not creating a new device, use the device id to run the tests on an existing device') 

mainParser.add_argument('--benchmarks-file',
                    action='store',
                    default='benchmarks.json',
                    help='relative address to the json file containing benchmark commands') 

mainParser.add_argument('--create-new',
                    action='store_true',
                    help='when set, creates a new device')

mainParser.add_argument('-f', '--facility',
                    metavar='facility',
                    action='store',
                    default='ewr1',
                    help='facility to use')

mainParser.add_argument('-os',
                    action='store',
                    default='freebsd_11_0',
                    help='operating system to use')

mainParser.add_argument('-sp', '--spot-price-max',
                    action='store',
                    type=float,
                    default=0.40,
                    help='operating system to use')

mainParser.add_argument('-hostname',
                    action='store',
                    default='test',
                    help='hostname of the machine')

mainParser.add_argument('-p', '-plan',
                    action='store',
                    default='baremetal_2',
                    help='type of plan')

