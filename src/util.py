import time
import packet

manager = packet.Manager(auth_token="PDDno4gUFgZqMpE97nTKdvc1asVjqUyS")
project = manager.list_projects()[0]

def reboot_device(device):
    print('rebooting the device')
    device.reboot()
    # sleep for 1 seconds so wait_till_active doesn't falsely get device as active
    time.sleep(1.0)

def get_device_ip(device):
    return device.ip_addresses[0]["address"]

def get_device_status(device_id):
    device = manager.get_device(device_id)
    return device.state

# wait until the device is active
def wait_till_active(device):
    while(get_device_status(device.id) != 'active'):
        print('device is not active, waiting...')
        time.sleep(1.0)
    print('device is active!')
    return

# either create the device or get device using id
def get_testing_device(args):
    device = None
    if args.create_device:
        device = manager.create_device(project_id=project.id,
                     hostname=args.hostname,
                     plan=args.p, facility=args.facility,
                     operating_system=args.os,
                     spot_instance=args.s,
                     spot_price_max=args.spot_price_max)
    else:
        device = manager.get_device(args.device_id)
    return device

def execute_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    print('#: ' + command)
    print(''.join(stdout.readlines()))
    print(''.join(stderr.readlines()))

