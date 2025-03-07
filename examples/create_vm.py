"""
Example script to create a VM in an ArubaCloud account.

This script demonstrates how to use the pyarubacloud library to create a VM
in an ArubaCloud account.
"""

import argparse
import logging
import time

from pyarubacloud import Client
from pyarubacloud.constants import ServerStatus


def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create a VM in an ArubaCloud account.')
    parser.add_argument('-d', '--datacenter', help='Specify datacenter to login.', type=int, default=1)
    parser.add_argument('-u', '--username', help='Specify username.', required=True)
    parser.add_argument('-p', '--password', help='Specify password.', required=True)
    parser.add_argument('-n', '--name', help='Specify VM name.', required=True)
    parser.add_argument('-t', '--template', help='Specify template ID.', required=True)
    parser.add_argument('--admin-password', help='Specify VM admin password.', required=True)
    parser.add_argument('--type', help='Specify VM type (pro or smart).', choices=['pro', 'smart'], default='pro')
    parser.add_argument('--cpu', help='Specify CPU quantity (Pro only).', type=int, default=2)
    parser.add_argument('--ram', help='Specify RAM quantity in GB (Pro only).', type=int, default=4)
    parser.add_argument('--disk', help='Specify disk size in GB (Pro only, can be used multiple times).', type=int, action='append')
    parser.add_argument('--package', help='Specify package (Smart only, small/medium/large/extralarge).', default='small')
    parser.add_argument('--public-ip', help='Add a public IP.', action='store_true')
    parser.add_argument('--ssh-key', help='Specify SSH key path.')
    parser.add_argument('--wait', help='Wait for VM to be ready.', action='store_true')
    parser.add_argument('--debug', help='Enable debug logging.', action='store_true')
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Initialize the client
    client = Client(datacenter=args.datacenter)
    client.auth.login(username=args.username, password=args.password)

    # Create the VM
    if args.type == 'pro':
        logger.info(f"Creating Pro VM '{args.name}'...")
        vm = client.compute.vm.create_pro(
            name=args.name,
            template_id=args.template,
            admin_password=args.admin_password,
            cpu=args.cpu,
            ram=args.ram,
            disks=args.disk,
            public_ip=args.public_ip,
            ssh_key_path=args.ssh_key
        )
    else:
        logger.info(f"Creating Smart VM '{args.name}'...")
        vm = client.compute.vm.create_smart(
            name=args.name,
            template_id=args.template,
            admin_password=args.admin_password,
            package=args.package,
            ssh_key_path=args.ssh_key
        )

    logger.info(f"VM '{args.name}' created with ID: {vm.id}")

    # Wait for the VM to be ready if requested
    if args.wait:
        logger.info("Waiting for VM to be ready...")
        while True:
            # Get the latest VM status
            vm = client.compute.vm.get(vm.id)
            
            if vm.status == ServerStatus.RUNNING:
                logger.info("VM is now running.")
                break
            elif vm.status == ServerStatus.STOPPED:
                logger.info("VM is stopped. Powering on...")
                client.compute.vm.power_on(vm.id)
            elif vm.status == ServerStatus.PENDING:
                logger.info("VM is still being created. Waiting...")
                time.sleep(10)
            else:
                logger.info(f"VM is in status: {vm.status}. Waiting...")
                time.sleep(10)

    # Print VM details
    logger.info("VM Details:")
    logger.info(f"  Name: {vm.name}")
    logger.info(f"  ID: {vm.id}")
    logger.info(f"  Status: {vm.status}")
    
    if hasattr(vm, 'cpu') and vm.cpu:
        logger.info(f"  CPU: {vm.cpu}")
    
    if hasattr(vm, 'ram') and vm.ram:
        logger.info(f"  RAM: {vm.ram} GB")
    
    # Print IP addresses
    if hasattr(vm, 'ip_addr') and vm.ip_addr:
        if isinstance(vm.ip_addr, str):
            logger.info(f"  IP: {vm.ip_addr}")
        else:
            for ip in vm.ip_addr:
                logger.info(f"  IP: {ip.ip_addr}")
    
    # Print disks
    if hasattr(vm, 'disks') and vm.disks:
        for i, disk in enumerate(vm.disks):
            logger.info(f"  Disk {i}: {disk.size} GB")


if __name__ == '__main__':
    main()