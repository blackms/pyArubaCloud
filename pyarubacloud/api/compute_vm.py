"""
VM repository implementation for ArubaCloud API.

This module provides the VM repository implementation for the ArubaCloud API,
including methods for creating and managing VMs.
"""

from typing import Dict, Any, Optional, List, Union

from pyarubacloud.api.base import BaseRepository, BaseService
from pyarubacloud.constants import (
    ServerStatus,
    HypervisorType,
    SmartVMPackage,
    VirtualDiskOperation
)
from pyarubacloud.exceptions import (
    ResourceNotFoundError,
    OperationNotPermittedError,
    ValidationError
)
from pyarubacloud.models.vm import VM, ProVM, SmartVM


class VMRepositoryExtensions:
    """
    Extensions for the VM repository.
    
    This class provides additional methods for the VM repository.
    """
    
    def create_pro(
        self,
        name: str,
        template_id: Union[str, int],
        admin_password: str,
        cpu: int,
        ram: int,
        disks: Optional[List[int]] = None,
        public_ip: bool = False,
        ssh_key_path: Optional[str] = None,
        note: Optional[str] = None
    ) -> ProVM:
        """
        Create a Pro VM.
        
        Args:
            name: The name of the VM.
            template_id: The template ID.
            admin_password: The administrator password.
            cpu: The number of CPUs.
            ram: The amount of RAM in GB.
            disks: A list of disk sizes in GB.
            public_ip: Whether to add a public IP.
            ssh_key_path: The path to the SSH key file.
            note: A note for the VM.
            
        Returns:
            The created VM.
            
        Raises:
            ValidationError: If the input is invalid.
        """
        # Validate input
        if not name:
            raise ValidationError("Name is required")
        
        if not template_id:
            raise ValidationError("Template ID is required")
        
        if not admin_password:
            raise ValidationError("Administrator password is required")
        
        if cpu <= 0:
            raise ValidationError("CPU quantity must be positive")
        
        if ram <= 0:
            raise ValidationError("RAM quantity must be positive")
        
        # Prepare the VM configuration
        vm_config = {
            'AdministratorPassword': admin_password,
            'CPUQuantity': cpu,
            'Name': name,
            'NetworkAdaptersConfiguration': [],
            'Note': note or 'Created by pyArubaCloud',
            'OSTemplateId': template_id,
            'RAMQuantity': ram,
            'VirtualDisks': []
        }
        
        # Add disks
        if disks:
            for i, size in enumerate(disks):
                vm_config['VirtualDisks'].append({
                    'Size': size,
                    'VirtualDiskType': i
                })
        
        # Add SSH key if provided
        if ssh_key_path:
            with open(ssh_key_path, 'r') as f:
                ssh_key = f.read()
            vm_config['SshKey'] = ssh_key
            vm_config['SshPasswordAuthAllowed'] = True
        
        # Add public IP if requested
        if public_ip:
            # Purchase a new IP
            ip = self.client.compute.ip.purchase()
            
            vm_config['NetworkAdaptersConfiguration'].append({
                'NetworkAdapterType': 0,
                'PublicIpAddresses': [{
                    'PrimaryIPAddress': 'true',
                    'PublicIpAddressResourceId': ip.resource_id
                }]
            })
        
        # Create the VM
        response = self.service._call_api(
            method='SetEnqueueServerCreation',
            data={'Server': vm_config}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('vm_list')
        
        # Get the created VM
        if response.get('Success', False) and 'Value' in response:
            vm_id = response['Value'].get('ServerId')
            if vm_id:
                return self.get(vm_id)
        
        # If we can't get the created VM, create a new one with the provided data
        vm = ProVM(
            name=name,
            template_id=template_id,
            admin_password=admin_password,
            cpu=cpu,
            ram=ram,
            status=ServerStatus.PENDING,
            hypervisor_type=HypervisorType.VMWARE,
            note=note
        )
        
        # Set the client reference
        vm.client = self.client
        
        return vm
    
    def create_smart(
        self,
        name: str,
        template_id: Union[str, int],
        admin_password: str,
        package: Union[str, int],
        ssh_key_path: Optional[str] = None,
        note: Optional[str] = None
    ) -> SmartVM:
        """
        Create a Smart VM.
        
        Args:
            name: The name of the VM.
            template_id: The template ID.
            admin_password: The administrator password.
            package: The package name or ID.
            ssh_key_path: The path to the SSH key file.
            note: A note for the VM.
            
        Returns:
            The created VM.
            
        Raises:
            ValidationError: If the input is invalid.
        """
        # Validate input
        if not name:
            raise ValidationError("Name is required")
        
        if not template_id:
            raise ValidationError("Template ID is required")
        
        if not admin_password:
            raise ValidationError("Administrator password is required")
        
        if not package:
            raise ValidationError("Package is required")
        
        # Convert package name to ID if needed
        if isinstance(package, str):
            package_map = {
                'small': SmartVMPackage.SMALL,
                'medium': SmartVMPackage.MEDIUM,
                'large': SmartVMPackage.LARGE,
                'extralarge': SmartVMPackage.EXTRA_LARGE
            }
            
            if package.lower() not in package_map:
                raise ValidationError(f"Invalid package: {package}. Must be one of: small, medium, large, extralarge")
            
            package_id = package_map[package.lower()]
        else:
            package_id = package
        
        # Prepare the VM configuration
        vm_config = {
            'AdministratorPassword': admin_password,
            'Name': name,
            'SmartVMWarePackageID': package_id,
            'Note': note or 'Created by pyArubaCloud',
            'OSTemplateId': template_id
        }
        
        # Add SSH key if provided
        if ssh_key_path:
            with open(ssh_key_path, 'r') as f:
                ssh_key = f.read()
            vm_config['SshKey'] = ssh_key
            vm_config['SshPasswordAuthAllowed'] = True
        
        # Create the VM
        response = self.service._call_api(
            method='SetEnqueueServerCreation',
            data={'Server': vm_config}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('vm_list')
        
        # Get the created VM
        if response.get('Success', False) and 'Value' in response:
            vm_id = response['Value'].get('ServerId')
            if vm_id:
                return self.get(vm_id)
        
        # If we can't get the created VM, create a new one with the provided data
        vm = SmartVM(
            name=name,
            template_id=template_id,
            admin_password=admin_password,
            package_id=package_id,
            status=ServerStatus.PENDING,
            hypervisor_type=HypervisorType.SMART,
            note=note
        )
        
        # Set the client reference
        vm.client = self.client
        
        return vm
    
    def add_disk(self, vm_id: Union[str, int], size: int) -> bool:
        """
        Add a disk to a VM.
        
        Args:
            vm_id: The VM ID.
            size: The size of the disk in GB.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValidationError: If the input is invalid.
            OperationNotPermittedError: If the operation is not permitted.
        """
        # Validate input
        if size <= 0:
            raise ValidationError("Disk size must be positive")
        
        # Get the VM to check its status and disk count
        vm = self.get(vm_id)
        
        # Check if the VM is stopped
        if vm.status != ServerStatus.STOPPED:
            raise OperationNotPermittedError("VM must be stopped to add a disk")
        
        # Check if the VM is a Pro VM
        if not isinstance(vm, ProVM):
            raise OperationNotPermittedError("Only Pro VMs can have disks added")
        
        # Check if the VM already has the maximum number of disks
        if len(vm.disks) >= 4:
            raise ValidationError("VM already has the maximum number of disks (4)")
        
        # Add the disk
        response = self.service._call_api(
            method='SetEnqueueVirtualDiskManage',
            data={
                'ServerId': vm_id,
                'Disk': {
                    'CustomVirtualDiskPath': None,
                    'Size': size,
                    'VirtualDiskType': len(vm.disks),
                    'VirtualDiskUpdateType': VirtualDiskOperation.CREATE
                }
            }
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{vm_id}')
        
        return response.get('Success', False)
    
    def resize_disk(self, vm_id: Union[str, int], disk_id: int, size: int) -> bool:
        """
        Resize a disk.
        
        Args:
            vm_id: The VM ID.
            disk_id: The disk ID.
            size: The new size of the disk in GB.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValidationError: If the input is invalid.
            OperationNotPermittedError: If the operation is not permitted.
        """
        # Validate input
        if size <= 0:
            raise ValidationError("Disk size must be positive")
        
        # Get the VM to check its status
        vm = self.get(vm_id)
        
        # Check if the VM is stopped
        if vm.status != ServerStatus.STOPPED:
            raise OperationNotPermittedError("VM must be stopped to resize a disk")
        
        # Check if the VM is a Pro VM
        if not isinstance(vm, ProVM):
            raise OperationNotPermittedError("Only Pro VMs can have disks resized")
        
        # Check if the disk exists
        if disk_id >= len(vm.disks):
            raise ValidationError(f"Disk with ID {disk_id} not found")
        
        # Check if the new size is larger than the current size
        if size <= vm.disks[disk_id].size:
            raise ValidationError("New size must be larger than the current size")
        
        # Resize the disk
        response = self.service._call_api(
            method='SetEnqueueVirtualDiskManage',
            data={
                'ServerId': vm_id,
                'Disk': {
                    'CustomVirtualDiskPath': None,
                    'Size': size,
                    'VirtualDiskType': disk_id,
                    'VirtualDiskUpdateType': VirtualDiskOperation.RESIZE
                }
            }
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{vm_id}')
        
        return response.get('Success', False)
    
    def remove_disk(self, vm_id: Union[str, int], disk_id: int) -> bool:
        """
        Remove a disk.
        
        Args:
            vm_id: The VM ID.
            disk_id: The disk ID.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValidationError: If the input is invalid.
            OperationNotPermittedError: If the operation is not permitted.
        """
        # Get the VM to check its status
        vm = self.get(vm_id)
        
        # Check if the VM is stopped
        if vm.status != ServerStatus.STOPPED:
            raise OperationNotPermittedError("VM must be stopped to remove a disk")
        
        # Check if the VM is a Pro VM
        if not isinstance(vm, ProVM):
            raise OperationNotPermittedError("Only Pro VMs can have disks removed")
        
        # Check if the disk exists
        if disk_id >= len(vm.disks):
            raise ValidationError(f"Disk with ID {disk_id} not found")
        
        # Remove the disk
        response = self.service._call_api(
            method='SetEnqueueVirtualDiskManage',
            data={
                'ServerId': vm_id,
                'Disk': {
                    'CustomVirtualDiskPath': None,
                    'Size': 0,
                    'VirtualDiskType': disk_id,
                    'VirtualDiskUpdateType': VirtualDiskOperation.DELETE
                }
            }
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{vm_id}')
        
        return response.get('Success', False)
    
    def edit_cpu(self, vm_id: Union[str, int], cpu: int) -> bool:
        """
        Edit the number of CPUs.
        
        Args:
            vm_id: The VM ID.
            cpu: The new number of CPUs.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValidationError: If the input is invalid.
            OperationNotPermittedError: If the operation is not permitted.
        """
        # Validate input
        if cpu <= 0:
            raise ValidationError("CPU quantity must be positive")
        
        # Get the VM to check its status
        vm = self.get(vm_id)
        
        # Check if the VM is stopped
        if vm.status != ServerStatus.STOPPED:
            raise OperationNotPermittedError("VM must be stopped to edit CPU")
        
        # Check if the VM is a Pro VM
        if not isinstance(vm, ProVM):
            raise OperationNotPermittedError("Only Pro VMs can have CPU edited")
        
        # Edit the CPU
        response = self.service._call_api(
            method='SetEnqueueHardwareUpdate',
            data={
                'ServerId': vm_id,
                'CpuQuantity': cpu,
                'RamQuantity': vm.ram,
                'RestartAfterExecuted': 'true'
            }
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{vm_id}')
        
        return response.get('Success', False)
    
    def edit_ram(self, vm_id: Union[str, int], ram: int) -> bool:
        """
        Edit the amount of RAM.
        
        Args:
            vm_id: The VM ID.
            ram: The new amount of RAM in GB.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValidationError: If the input is invalid.
            OperationNotPermittedError: If the operation is not permitted.
        """
        # Validate input
        if ram <= 0:
            raise ValidationError("RAM quantity must be positive")
        
        # Get the VM to check its status
        vm = self.get(vm_id)
        
        # Check if the VM is stopped
        if vm.status != ServerStatus.STOPPED:
            raise OperationNotPermittedError("VM must be stopped to edit RAM")
        
        # Check if the VM is a Pro VM
        if not isinstance(vm, ProVM):
            raise OperationNotPermittedError("Only Pro VMs can have RAM edited")
        
        # Edit the RAM
        response = self.service._call_api(
            method='SetEnqueueHardwareUpdate',
            data={
                'ServerId': vm_id,
                'CpuQuantity': vm.cpu,
                'RamQuantity': ram,
                'RestartAfterExecuted': 'true'
            }
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{vm_id}')
        
        return response.get('Success', False)
    
    def upgrade(self, vm_id: Union[str, int], package: Union[str, int]) -> bool:
        """
        Upgrade a Smart VM.
        
        Args:
            vm_id: The VM ID.
            package: The package name or ID.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValidationError: If the input is invalid.
            OperationNotPermittedError: If the operation is not permitted.
        """
        # Validate input
        if not package:
            raise ValidationError("Package is required")
        
        # Convert package name to ID if needed
        if isinstance(package, str):
            package_map = {
                'small': SmartVMPackage.SMALL,
                'medium': SmartVMPackage.MEDIUM,
                'large': SmartVMPackage.LARGE,
                'extralarge': SmartVMPackage.EXTRA_LARGE
            }
            
            if package.lower() not in package_map:
                raise ValidationError(f"Invalid package: {package}. Must be one of: small, medium, large, extralarge")
            
            package_id = package_map[package.lower()]
        else:
            package_id = package
        
        # Get the VM to check its status
        vm = self.get(vm_id)
        
        # Check if the VM is stopped
        if vm.status != ServerStatus.STOPPED:
            raise OperationNotPermittedError("VM must be stopped to upgrade")
        
        # Check if the VM is a Smart VM
        if not isinstance(vm, SmartVM):
            raise OperationNotPermittedError("Only Smart VMs can be upgraded")
        
        # Upgrade the VM
        response = self.service._call_api(
            method='SetEnqueueServerUpdate',
            data={
                'Server': {
                    'ServerId': vm_id,
                    'SmartVMWarePackageID': package_id
                }
            }
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{vm_id}')
        
        return response.get('Success', False)
    
    def reinitialize(self, vm_id: Union[str, int], admin_password: str, template_id: Optional[Union[str, int]] = None) -> bool:
        """
        Reinitialize a Smart VM.
        
        Args:
            vm_id: The VM ID.
            admin_password: The administrator password.
            template_id: The template ID.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValidationError: If the input is invalid.
            OperationNotPermittedError: If the operation is not permitted.
        """
        # Validate input
        if not admin_password:
            raise ValidationError("Administrator password is required")
        
        # Get the VM to check its type
        vm = self.get(vm_id)
        
        # Check if the VM is a Smart VM
        if not isinstance(vm, SmartVM):
            raise OperationNotPermittedError("Only Smart VMs can be reinitialized")
        
        # Prepare the request data
        data = {
            'AdministratorPassword': admin_password,
            'ServerId': vm_id,
            'ConfigureIPv6': False
        }
        
        if template_id:
            data['OSTemplateID'] = template_id
        
        # Reinitialize the VM
        response = self.service._call_api(
            method='SetEnqueueReinitializeServer',
            data=data
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{vm_id}')
        
        return response.get('Success', False)