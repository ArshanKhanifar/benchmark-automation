import time
import packet

manager = packet.Manager(auth_token="PDDno4gUFgZqMpE97nTKdvc1asVjqUyS")
project = manager.list_projects()[0]

def get_device_ip(device):
    while (len(device.ip_addresses) == 0):
        print('ip address not ready, trying again...')
        time.sleep(5) 
        device = manager.get_device(device.id)
    return device.ip_addresses[0]["address"]

# creates a packet device and returns its ip
def create_device(args):
    print("Creating new device:")
    device = manager.create_device(project_id=project.id,
                 hostname=args.hostname,
                 plan=args.p, facility=args.facility,
                 operating_system=args.os,
                 spot_instance=args.s,
                 spot_price_max=args.spot_price_max)
    return get_device_ip(device)

