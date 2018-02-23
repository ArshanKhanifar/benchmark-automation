import argparse

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

mainParser = argparse.ArgumentParser(description='Benchmark for pti, and ibrs:')

mainParser.add_argument('--setup',
                    action='store_true',
                    help='Does initial setup, refer to source to see what commands are used')

mainParser.add_argument('--update',
                    action='store_true',
                    help='Updates the OS to HEAD, to update to a specific revision, use --custom-update')

mainParser.add_argument('-s', '-spotmarket',
                    action='store',
                    default=True,
                    metavar='spotmarket',
                    type=str2bool,
                    help='Use spotmarket pricing, defaults to true')

mainParser.add_argument('--custom-update',
                    action='store',
                    help='Used for updating the kernel to a specific revision, and applying custom patches. Takes in the path to a custom update json file.') 

mainParser.add_argument('--device-ip',
                    action='store',
                    help='When not creating a new device, use the device id to run the tests on an existing device') 

mainParser.add_argument('--benchmarks-file',
                    action='store',
                    help='Relative address to the json file containing benchmark commands') 

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

