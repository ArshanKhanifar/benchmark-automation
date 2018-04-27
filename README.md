### Automation Scripts

This repository is a set of python scripts facilitating automation of benchmarks on a remote machine. I used this to test/benchmark the performance of `PTI` patches on various versions of FreeBSD.

## Installation

## Usage

To see a list available options, use `--help`: 
```
$ python main.py --help
usage: main.py [-h] [--password PASSWORD] [--passphrase PASSPHRASE]
               [--load-keys] [--setup] [--update] [-s spotmarket]
               [--custom-update CUSTOM_UPDATE] [--device-ip DEVICE_IP]
               [--benchmarks-file BENCHMARKS_FILE] [--create-new]
               [-f facility] [-os OS] [-sp SPOT_PRICE_MAX]
               [-hostname HOSTNAME] [-p P]

Benchmark for pti, and ibrs:

optional arguments:
  -h, --help            show this help message and exit
  --password PASSWORD   Password for ssh authentication
  --passphrase PASSPHRASE
                        Passphrase for decrypting private keys
  --load-keys           Load system host keys, use when using private keys to
                        authenticate
  --setup               Does initial setup, refer to source to see what
                        commands are used
  --update              Updates the OS to HEAD, to update to a specific
                        revision, use --custom-update
  -s spotmarket, -spotmarket spotmarket
                        Use spotmarket pricing, defaults to true
  --custom-update CUSTOM_UPDATE
                        Used for updating the kernel to a specific revision,
                        and applying custom patches. Takes in the path to a
                        custom update json file.
  --device-ip DEVICE_IP
                        When not creating a new device, use the device id to
                        run the tests on an existing device
  --benchmarks-file BENCHMARKS_FILE
                        Relative address to the json file containing benchmark
                        commands
  --create-new          when set, creates a new device
  -f facility, --facility facility
                        facility to use
  -os OS                operating system to use
  -sp SPOT_PRICE_MAX, --spot-price-max SPOT_PRICE_MAX
                        operating system to use
  -hostname HOSTNAME    hostname of the machine
  -p P, -plan P         type of plan

```
