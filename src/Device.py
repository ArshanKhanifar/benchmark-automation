from paramiko.client import SSHClient,AutoAddPolicy
from datetime import datetime
import time, sys

class Device(object):
    def __init__(self,
            device_ip,
            inputdir='input',
            outputdir='output',
            load_keys=False,
            password='',
            passphrase=''):
        self.device_ip = device_ip
        self.password = password
        self.inputdir = inputdir
        self.outputdir = outputdir
        self.passphrase = passphrase
        self.load_keys = load_keys
        self.execute_commands([
                'rm -rf %s; mkdir %s'%(self.inputdir, self.inputdir),
                'rm -rf %s; mkdir %s'%(self.outputdir, self.outputdir)
            ])
    
    def execute_commands(self, commands):
        for command in commands:
            self.execute_command(command)
    
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

    def execute_command(self, command):
        client = self.__get_client()
        ignore = False
        if isinstance(command, list):
            ignore = command[1]
            command = command[0]

        print "~ %s"%command
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.readlines()
        error = stderr.readlines()
        if not ignore:
            print '\n'.join(stdout)
        
        print 'ERROR:'
        print '\n'.join(error)
         
        client.close()

    def isReady(self):
        client = self.__get_client()
        client.close()

    def __get_client(self):
        client = None
        while client == None:
            try:
                client = SSHClient()
                if self.load_keys:
                    client.load_system_host_keys()
                client.set_missing_host_key_policy(AutoAddPolicy())
                connect_arguments = {
                        'username': 'root',
                        'timeout': 1
                }
                if self.password:
                    connect_arguments['password'] = self.password
                if self.passphrase:
                    connect_arguments['passphrase'] = self.passphrase
                client.connect(self.device_ip, **connect_arguments)
            except Exception as e:
                print e
                print("ssh couldn't connect, trying again...")
        return client

