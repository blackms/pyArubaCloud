"""
VM models for ArubaCloud resources.

This module provides model classes for ArubaCloud VM resources,
including Pro and Smart VMs.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, ClassVar, Set, Type, Union

from pyarubacloud.constants import ServerStatus, HypervisorType
from pyarubacloud.models.base import BaseModel


class Disk(BaseModel):
    """
    Model for a virtual disk.
    
    Attributes:
        size (int): The size of the disk in GB.
        disk_type (int): The type of the disk.
    """
    
    _required_fields: ClassVar[Set[str]] = {'size', 'disk_type'}
    _optional_fields: ClassVar[Set[str]] = set()
    _field_types: ClassVar[Dict[str, Type]] = {
        'size': int,
        'disk_type': int
    }
    _field_mappings: ClassVar[Dict[str, str]] = {
        'size': 'Size',
        'disk_type': 'VirtualDiskType'
    }
    
    def __init__(self, size: int, disk_type: int, **kwargs):
        """
        Initialize the disk.
        
        Args:
            size: The size of the disk in GB.
            disk_type: The type of the disk.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.size = size
        self.disk_type = disk_type


class NetworkAdapter(BaseModel):
    """
    Model for a network adapter.
    
    Attributes:
        adapter_type (int): The type of the adapter.
        public_ip (Optional[str]): The public IP address.
        private_ip (Optional[str]): The private IP address.
        subnet_mask (Optional[str]): The subnet mask.
        gateway (Optional[str]): The gateway.
        vlan_id (Optional[str]): The VLAN ID.
    """
    
    _required_fields: ClassVar[Set[str]] = {'adapter_type'}
    _optional_fields: ClassVar[Set[str]] = {'public_ip', 'private_ip', 'subnet_mask', 'gateway', 'vlan_id'}
    _field_types: ClassVar[Dict[str, Type]] = {
        'adapter_type': int,
        'public_ip': str,
        'private_ip': str,
        'subnet_mask': str,
        'gateway': str,
        'vlan_id': str
    }
    _field_mappings: ClassVar[Dict[str, str]] = {
        'adapter_type': 'NetworkAdapterType',
        'public_ip': 'PublicIpAddress',
        'private_ip': 'IPAddress',
        'subnet_mask': 'SubNetMask',
        'gateway': 'Gateway',
        'vlan_id': 'VLanResourceId'
    }
    
    def __init__(
        self,
        adapter_type: int,
        public_ip: Optional[str] = None,
        private_ip: Optional[str] = None,
        subnet_mask: Optional[str] = None,
        gateway: Optional[str] = None,
        vlan_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the network adapter.
        
        Args:
            adapter_type: The type of the adapter.
            public_ip: The public IP address.
            private_ip: The private IP address.
            subnet_mask: The subnet mask.
            gateway: The gateway.
            vlan_id: The VLAN ID.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.adapter_type = adapter_type
        self.public_ip = public_ip
        self.private_ip = private_ip
        self.subnet_mask = subnet_mask
        self.gateway = gateway
        self.vlan_id = vlan_id


class VM(BaseModel):
    """
    Base model for a virtual machine.
    
    Attributes:
        name (str): The name of the VM.
        status (int): The status of the VM.
        cpu (int): The number of CPUs.
        ram (int): The amount of RAM in GB.
        disks (List[Disk]): The virtual disks.
        network_adapters (List[NetworkAdapter]): The network adapters.
        hypervisor_type (int): The hypervisor type.
        datacenter_id (int): The datacenter ID.
        note (Optional[str]): A note for the VM.
        template_id (Optional[str]): The template ID.
        admin_password (Optional[str]): The administrator password.
    """
    
    _required_fields: ClassVar[Set[str]] = {'name'}
    _optional_fields: ClassVar[Set[str]] = {
        'id', 'status', 'cpu', 'ram', 'disks', 'network_adapters',
        'hypervisor_type', 'datacenter_id', 'note', 'template_id',
        'admin_password', 'created_at', 'updated_at'
    }
    _field_types: ClassVar[Dict[str, Type]] = {
        'id': str,
        'name': str,
        'status': int,
        'cpu': int,
        'ram': int,
        'hypervisor_type': int,
        'datacenter_id': int,
        'note': str,
        'template_id': str,
        'admin_password': str,
        'created_at': datetime,
        'updated_at': datetime
    }
    _field_mappings: ClassVar[Dict[str, str]] = {
        'id': 'ServerId',
        'name': 'Name',
        'status': 'ServerStatus',
        'cpu': 'CPUQuantity',
        'ram': 'RAMQuantity',
        'hypervisor_type': 'HypervisorType',
        'datacenter_id': 'DatacenterId',
        'note': 'Note',
        'template_id': 'OSTemplateId',
        'admin_password': 'AdministratorPassword',
        'created_at': 'CreationDate',
        'updated_at': 'UpdatedDate'
    }
    
    def __init__(
        self,
        name: str,
        status: Optional[int] = None,
        cpu: Optional[int] = None,
        ram: Optional[int] = None,
        disks: Optional[List[Disk]] = None,
        network_adapters: Optional[List[NetworkAdapter]] = None,
        hypervisor_type: Optional[int] = None,
        datacenter_id: Optional[int] = None,
        note: Optional[str] = None,
        template_id: Optional[str] = None,
        admin_password: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the VM.
        
        Args:
            name: The name of the VM.
            status: The status of the VM.
            cpu: The number of CPUs.
            ram: The amount of RAM in GB.
            disks: The virtual disks.
            network_adapters: The network adapters.
            hypervisor_type: The hypervisor type.
            datacenter_id: The datacenter ID.
            note: A note for the VM.
            template_id: The template ID.
            admin_password: The administrator password.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.name = name
        self.status = status
        self.cpu = cpu
        self.ram = ram
        self.disks = disks or []
        self.network_adapters = network_adapters or []
        self.hypervisor_type = hypervisor_type
        self.datacenter_id = datacenter_id
        self.note = note
        self.template_id = template_id
        self.admin_password = admin_password
        
        # Client reference for operations
        self.client = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VM':
        """
        Create a VM instance from a dictionary.
        
        Args:
            data: A dictionary of VM attributes.
            
        Returns:
            A new VM instance.
        """
        # Create a dictionary of model attributes
        kwargs = {}
        for field in cls._get_all_fields():
            api_field = cls._field_mappings.get(field, field)
            if api_field in data:
                kwargs[field] = data[api_field]
        
        # Handle disks
        if 'VirtualDisks' in data and data['VirtualDisks']:
            kwargs['disks'] = [Disk.from_dict(disk) for disk in data['VirtualDisks']]
        
        # Handle network adapters
        if 'NetworkAdapters' in data and data['NetworkAdapters']:
            kwargs['network_adapters'] = [NetworkAdapter.from_dict(adapter) for adapter in data['NetworkAdapters']]
        
        # Create the appropriate VM type
        if 'HypervisorType' in data:
            hypervisor_type = data['HypervisorType']
            if hypervisor_type == HypervisorType.SMART:
                return SmartVM(**kwargs)
            else:
                return ProVM(**kwargs)
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the VM to a dictionary.
        
        Returns:
            A dictionary representation of the VM.
        """
        result = super().to_dict()
        
        # Handle disks
        if self.disks:
            result['VirtualDisks'] = [disk.to_dict() for disk in self.disks]
        
        # Handle network adapters
        if self.network_adapters:
            result['NetworkAdapters'] = [adapter.to_dict() for adapter in self.network_adapters]
        
        return result
    
    def power_on(self) -> bool:
        """
        Power on the VM.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.power_on(self.id)
    
    def power_off(self) -> bool:
        """
        Power off the VM.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.power_off(self.id)
    
    def delete(self) -> bool:
        """
        Delete the VM.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.delete(self.id)
    
    def is_running(self) -> bool:
        """
        Check if the VM is running.
        
        Returns:
            True if the VM is running, False otherwise.
        """
        return self.status == ServerStatus.RUNNING
    
    def is_stopped(self) -> bool:
        """
        Check if the VM is stopped.
        
        Returns:
            True if the VM is stopped, False otherwise.
        """
        return self.status == ServerStatus.STOPPED
    
    def is_pending(self) -> bool:
        """
        Check if the VM is in a pending state.
        
        Returns:
            True if the VM is in a pending state, False otherwise.
        """
        return self.status == ServerStatus.PENDING


class ProVM(VM):
    """
    Model for a Pro VM.
    
    Attributes:
        hd_total_size (Optional[int]): The total size of all disks in GB.
        hd_qty (Optional[int]): The number of disks.
    """
    
    _optional_fields = VM._optional_fields.union({'hd_total_size', 'hd_qty'})
    _field_types.update({
        'hd_total_size': int,
        'hd_qty': int
    })
    _field_mappings.update({
        'hd_total_size': 'HDTotalSize',
        'hd_qty': 'HDQuantity'
    })
    
    def __init__(
        self,
        name: str,
        hd_total_size: Optional[int] = None,
        hd_qty: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize the Pro VM.
        
        Args:
            name: The name of the VM.
            hd_total_size: The total size of all disks in GB.
            hd_qty: The number of disks.
            **kwargs: Additional attributes.
        """
        super().__init__(name, **kwargs)
        self.hd_total_size = hd_total_size
        self.hd_qty = hd_qty
    
    def add_disk(self, size: int) -> bool:
        """
        Add a disk to the VM.
        
        Args:
            size: The size of the disk in GB.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.add_disk(self.id, size)
    
    def resize_disk(self, disk_id: int, size: int) -> bool:
        """
        Resize a disk.
        
        Args:
            disk_id: The ID of the disk.
            size: The new size of the disk in GB.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.resize_disk(self.id, disk_id, size)
    
    def remove_disk(self, disk_id: int) -> bool:
        """
        Remove a disk.
        
        Args:
            disk_id: The ID of the disk.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.remove_disk(self.id, disk_id)
    
    def edit_cpu(self, cpu: int) -> bool:
        """
        Edit the number of CPUs.
        
        Args:
            cpu: The new number of CPUs.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.edit_cpu(self.id, cpu)
    
    def edit_ram(self, ram: int) -> bool:
        """
        Edit the amount of RAM.
        
        Args:
            ram: The new amount of RAM in GB.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.edit_ram(self.id, ram)


class SmartVM(VM):
    """
    Model for a Smart VM.
    
    Attributes:
        package_id (Optional[int]): The package ID.
        ip_addr (Optional[str]): The IP address.
    """
    
    _optional_fields = VM._optional_fields.union({'package_id', 'ip_addr'})
    _field_types.update({
        'package_id': int,
        'ip_addr': str
    })
    _field_mappings.update({
        'package_id': 'SmartVMWarePackageID',
        'ip_addr': 'EasyCloudIPAddress'
    })
    
    def __init__(
        self,
        name: str,
        package_id: Optional[int] = None,
        ip_addr: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Smart VM.
        
        Args:
            name: The name of the VM.
            package_id: The package ID.
            ip_addr: The IP address.
            **kwargs: Additional attributes.
        """
        super().__init__(name, **kwargs)
        self.package_id = package_id
        self.ip_addr = ip_addr
    
    def upgrade(self, package_id: int) -> bool:
        """
        Upgrade the VM.
        
        Args:
            package_id: The new package ID.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.upgrade(self.id, package_id)
    
    def reinitialize(self, admin_password: str, template_id: Optional[str] = None) -> bool:
        """
        Reinitialize the VM.
        
        Args:
            admin_password: The administrator password.
            template_id: The template ID.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vm.reinitialize(self.id, admin_password, template_id)