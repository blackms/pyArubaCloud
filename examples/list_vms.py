"""
Example script to list all VMs in an ArubaCloud account.

This script demonstrates how to use the pyarubacloud library to list all VMs
in an ArubaCloud account.
"""

import argparse
import logging
from pprint import pprint

from pyarubacloud import Client


def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='List all VMs in an ArubaCloud account.')
    parser.add_argument('-d', '--datacenter', help='Specify datacenter to login.', type=int, default=1)
    parser.add_argument('-u', '--username', help='Specify username.', required=True)
    parser.add_argument('-p', '--password', help='Specify password.', required=True)
    parser.add_argument('--debug', help='Enable debug logging.', action='store_true')
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Initialize the client
    client = Client(datacenter=args.datacenter)
    client.auth.login(username=args.username, password=args.password)

    # List all VMs
    vms = client.compute.vm.list()
    
    # Print the results
    print(f"Found {len(vms)} VMs:")
    for vm in vms:
        print(f"VM: {vm.name}")
        print(f"  ID: {vm.id}")
        print(f"  Status: {vm.status}")
        print(f"  CPU: {vm.cpu}")
        print(f"  RAM: {vm.ram} GB")
        print(f"  Hypervisor: {vm.hypervisor_type}")
        
        # Print IP addresses
        if hasattr(vm, 'ip_addr') and vm.ip_addr:
            if isinstance(vm.ip_addr, str):
                print(f"  IP: {vm.ip_addr}")
            else:
                for ip in vm.ip_addr:
                    print(f"  IP: {ip.ip_addr}")
        
        # Print disks
        if hasattr(vm, 'disks') and vm.disks:
            for i, disk in enumerate(vm.disks):
                print(f"  Disk {i}: {disk.size} GB")
        
        print()


if __name__ == '__main__':
    main()