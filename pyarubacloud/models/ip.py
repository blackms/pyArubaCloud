"""
IP model for ArubaCloud resources.

This module provides a model class for ArubaCloud IP resources.
"""

from typing import Optional, Dict, Any, ClassVar, Set, Type

from pyarubacloud.models.base import BaseModel


class IP(BaseModel):
    """
    Model for an IP address.
    
    Attributes:
        address (str): The IP address.
        resource_id (str): The resource ID.
        server_id (Optional[str]): The server ID.
        gateway (Optional[str]): The gateway.
        subnet_mask (Optional[str]): The subnet mask.
        is_public (bool): Whether the IP is public.
    """
    
    _required_fields: ClassVar[Set[str]] = {'address', 'resource_id'}
    _optional_fields: ClassVar[Set[str]] = {'server_id', 'gateway', 'subnet_mask', 'is_public'}
    _field_types: ClassVar[Dict[str, Type]] = {
        'address': str,
        'resource_id': str,
        'server_id': str,
        'gateway': str,
        'subnet_mask': str,
        'is_public': bool
    }
    _field_mappings: ClassVar[Dict[str, str]] = {
        'address': 'Value',
        'resource_id': 'ResourceId',
        'server_id': 'ServerId',
        'gateway': 'Gateway',
        'subnet_mask': 'SubNetMask',
        'is_public': 'IsPublic'
    }
    
    def __init__(
        self,
        address: str,
        resource_id: str,
        server_id: Optional[str] = None,
        gateway: Optional[str] = None,
        subnet_mask: Optional[str] = None,
        is_public: bool = True,
        **kwargs
    ):
        """
        Initialize the IP.
        
        Args:
            address: The IP address.
            resource_id: The resource ID.
            server_id: The server ID.
            gateway: The gateway.
            subnet_mask: The subnet mask.
            is_public: Whether the IP is public.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.address = address
        self.resource_id = resource_id
        self.server_id = server_id
        self.gateway = gateway
        self.subnet_mask = subnet_mask
        self.is_public = is_public
        
        # Client reference for operations
        self.client = None
    
    def is_mapped(self) -> bool:
        """
        Check if the IP is mapped to a server.
        
        Returns:
            True if the IP is mapped to a server, False otherwise.
        """
        return self.server_id is not None
    
    def release(self) -> bool:
        """
        Release the IP.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.ip.release(self.resource_id)
    
    def assign(self, server_id: str) -> bool:
        """
        Assign the IP to a server.
        
        Args:
            server_id: The server ID.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.ip.assign(self.resource_id, server_id)
    
    def unassign(self) -> bool:
        """
        Unassign the IP from a server.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set or the IP is not mapped.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        if not self.is_mapped():
            raise ValueError("IP is not mapped to a server")
        
        return self.client.compute.ip.unassign(self.resource_id)