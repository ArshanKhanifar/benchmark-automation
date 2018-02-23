from paramiko.client import SSHClient,AutoAddPolicy
import time, sys

class Device(object):
    def __init__(self, device_ip, inputdir='input', outputdir='output'):
        self.device_ip = device_ip
        self.inputdir = inputdir
        self.outputdir = outputdir
        self.execute_commands([
                'rm -rf %s; mkdir %s'%(self.inputdir, self.inputdir),
                'rm -rf %s; mkdir %s'%(self.outputdir, self.outputdir)
            ])
    
    def execute_commands(self, commands):
        client = self.__get_client()
        for command in commands:
            self.execute_command(command, client)
        client.close()
    
    def send_files(self, paths):
        for path in paths:
            self.send_file(path)

    def get_file(self, remotepath, localpath):
        client = self.__get_client()
        sftp_client = client.open_sftp()
        sftp_client.get(remotepath, localpath)
        sftp_client.close()
        client.close()

    def send_file(self, path):
        client = self.__get_client()
        sftp_client = client.open_sftp()
        filename = path.split('/')[-1]
        sftp_client.put(path, '/root/%s/%s'%(self.inputdir, filename))
        sftp_client.close()
        client.close()
    
    def reboot(self):
        self.execute_command('reboot')
        # call to __get_client() to wait until the device is up again
        client = self.__get_client()
        client.close()

    def execute_command(self, command, client=None):
        needs_close = False 
        if client is None:
            client = self.__get_client()
            needs_close = True
        ignore = False
        if isinstance(command, list):
            ignore = command[1]
            command = command[0]
        channel = client.get_transport().open_session()
        print('#: ' + command)
        channel.exec_command(command)
        while not channel.exit_status_ready():
            pass
        if channel.recv_exit_status() == 0:
            if not ignore:
                data = ''
                d = 'a' # some nonempty value to enter the loop
                while d:
                    d = channel.recv(1024)
                    data = data + d
                print data,
        else:
            print("Error: exiting...")
            err = ''
            e = 'a'
            while e:
                e = channel.recv_stderr(1024)
                err = err + e
            print err,
            sys.exit()
        if needs_close:
            client.close()

    def isReady(self):
        client = self.__get_client()
        client.close()

    def __get_client(self):
        client = None
        try:
            client = SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(self.device_ip, 
                           username='root',
                           passphrase='Physics92',
                           timeout=1)
        except:
            print("ssh couldn't connect, trying again...")
            return self.__get_client()
        return client

