import time
import packet
import sys
import os
from paramiko.client import SSHClient,AutoAddPolicy

manager = packet.Manager(auth_token="PDDno4gUFgZqMpE97nTKdvc1asVjqUyS")
project = manager.list_projects()[0]

def dir_exists(sftp_client, directory):
    return directory in sftp_client.listdir()

def rm_dir_recursive(client, directory):
    execute_command(client, ["rm -rf %s"%directory, True])

def reboot_device(device):
    print('Rebooting the device.')
    print('ERROR! SHOULDNT HIT HERE!')
    sys.exit()
    device.reboot()
    # sleep for 1 seconds so wait_till_active doesn't falsely get device as active
    time.sleep(1.0)
    wait_till_active(device)

#cache the currently used device
def write_last(device_id):
    if not os.path.isdir('cache'):
        os.mkdir('cache')
    fh = open('cache/deviceid', 'w')
    fh.write(device_id)
    fh.close()

# get cached device
def read_last():
    if not os.path.isfile('cache/deviceid'):
        return None
    fh = open('cache/deviceid', 'r')
    return fh.readline()

def get_device_ip(device):
    while (len(device.ip_addresses) == 0):
        print('ip address not ready, trying again...')
        time.sleep(5) 
        device = manager.get_device(device.id)
    return device.ip_addresses[0]["address"]

def get_device_status(device_id):
    device = manager.get_device(device_id)
    return device.state

# wait until the device is active
def wait_till_active(device):
    while(get_device_status(device.id) != 'active'):
        print('device is not active, waiting...')
        time.sleep(10.0)
    print('device is active!')
    return
 
# either create the device or get device using id
def get_testing_device(args):
    if args.use_last:
        device_id = read_last()
        if device_id is None:
            print('No cached device id\'s found')
            sys.exit()
        else:
            return manager.get_device(device_id)

    if (args.device_id is None) and not args.create_new:
        print("Please specify either a device id or create new.")
        sys.exit()
    device = None
    if args.device_id is None:
        print("Creating new device:")
        device = manager.create_device(project_id=project.id,
                     hostname=args.hostname,
                     plan=args.p, facility=args.facility,
                     operating_system=args.os,
                     spot_instance=args.s,
                     spot_price_max=args.spot_price_max)

    else:
        device = manager.get_device(args.device_id)
    write_last(device.id)
    return device

# executes command in the client environment
# if command is a string, then executes it
# if command is specified as an array: ['command':string , 'surpress': boolean]
# then it will surpress the output of the command if boolean is set to true

def execute_command(client, command):
    ignore = False
    if isinstance(command, list):
        ignore = command[1]
        command = command[0]
    print('#: ' + command)
    stdin, stdout, stderr = client.exec_command(command)
    # read the stdin in chunks (used for tasks with big outputs)
    # such as buildkernel and buildworld
    while True:
        line = stdout.readline()
        if line != '':
            if not ignore:
                print line,
        else:
            break
    errstuff = stderr.readlines()
    if len(errstuff):
        print(''.join(errstuff))

def execute_commands(client, commands):
    for command in commands:
        execute_command(client, command)

def create_client(ip_address):
    client = None
    try:
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(ip_address, 
                       username='root',
                       passphrase='Physics92',
                       timeout=5)
    except:
        print("ssh couldn't connect, trying again...")
        time.sleep(1)
        return create_client(ip_address)
    return client

