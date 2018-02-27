from paramiko.client import SSHClient,AutoAddPolicy
import time, sys, select

class Device(object):
    def __init__(self,
            device_ip,
            inputdir='input',
            outputdir='output',
            load_keys=False,
            password='',
            passphrase=''):
        self.device_ip = device_ip
        self.inputdir = inputdir
        self.outputdir = outputdir
        self.password = password
        self.passphrase = passphrase
        self.load_keys = load_keys

    def clear_in_out_dir(self):
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

    def execute_command(self, command, timeout=0):
        ignore = False
        exit_not_success = False
        if isinstance(command, list):
            ignore = command[1]
            if len(command) > 2:
                exit_not_success = command[2]
            command = command[0]

        client = self.__get_client()

        # a chunk-based solution to read from stdout/stderr from here:
        #https://stackoverflow.com/questions/23504126/do-you-have-to-check-exit-status-ready-if-you-are-going-to-check-recv-ready/32758464#32758464

        # one channel per command
        print '~ %s'%command
        stdin, stdout, stderr = client.exec_command(command) 
        # get the shared channel for stdout/stderr/stdin
        channel = stdout.channel
        
        # we do not need stdin.
        stdin.close()                 
        # indicate that we're not going to write to that channel anymore
        channel.shutdown_write()      

        # read stdout/stderr in order to prevent read block hangs
        stdout_chunks = []
        stdout_chunks.append(stdout.channel.recv(len(stdout.channel.in_buffer)))

        stderr_chunks = []

        # chunked read to prevent stalls
        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready(): 
            # stop if channel was closed prematurely, and there is no data in the buffers.
            got_chunk = False
            readq, _, _ = select.select([stdout.channel], [], [], timeout)
            for c in readq:
                if c.recv_ready(): 
                    stdout_chunks.append(stdout.channel.recv(len(c.in_buffer)))
                    got_chunk = True
                if c.recv_stderr_ready(): 
                    # make sure to read stderr to prevent stall    
                    stderr_chunks.append(stderr.channel.recv_stderr(len(c.in_stderr_buffer)))
                    got_chunk = True  
            '''
            1) make sure that there are at least 2 cycles with no data in the input buffers in order to not exit too early (i.e. cat on a >200k file).
            2) if no data arrived in the last loop, check if we already received the exit code
            3) check if input buffers are empty
            4) exit the loop
            '''
            if not got_chunk \
                and stdout.channel.exit_status_ready() \
                and not stderr.channel.recv_stderr_ready() \
                and not stdout.channel.recv_ready(): 
                # indicate that we're not going to read from this channel anymore
                stdout.channel.shutdown_read()  
                # close the channel
                stdout.channel.close()
                break    # exit as remote side is finished and our bufferes are empty

        # close all the pseudofiles
        stdout.close()
        stderr.close()
        
        dataout = ''.join(stdout_chunks).strip()
        if not ignore and dataout:
            print dataout

        # exit code is always ready at this point
        if exit_not_success and stdout.channel.recv_exit_status() != 0:
            print ''.join(stderr_chunks)
            sys.exit()

        client.close()

    def isReady(self):
        client = self.__get_client()
        client.close()

    def __get_client(self):
        client = None
        while True:
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
                break
            except Exception as e:
                print e
                print("ssh couldn't connect, trying again...")

        return client

