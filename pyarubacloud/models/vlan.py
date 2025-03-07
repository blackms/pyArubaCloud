"""
VLAN model for ArubaCloud resources.

This module provides a model class for ArubaCloud VLAN resources.
"""

from typing import Optional, Dict, Any, ClassVar, Set, Type, List

from pyarubacloud.models.base import BaseModel


class VLAN(BaseModel):
    """
    Model for a VLAN.
    
    Attributes:
        name (str): The name of the VLAN.
        resource_id (str): The resource ID.
        vlan_code (Optional[str]): The VLAN code.
        servers (List[str]): The server IDs associated with the VLAN.
    """
    
    _required_fields: ClassVar[Set[str]] = {'name', 'resource_id'}
    _optional_fields: ClassVar[Set[str]] = {'vlan_code', 'servers'}
    _field_types: ClassVar[Dict[str, Type]] = {
        'name': str,
        'resource_id': str,
        'vlan_code': str
    }
    _field_mappings: ClassVar[Dict[str, str]] = {
        'name': 'Name',
        'resource_id': 'ResourceId',
        'vlan_code': 'VlanCode'
    }
    
    def __init__(
        self,
        name: str,
        resource_id: str,
        vlan_code: Optional[str] = None,
        servers: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize the VLAN.
        
        Args:
            name: The name of the VLAN.
            resource_id: The resource ID.
            vlan_code: The VLAN code.
            servers: The server IDs associated with the VLAN.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.name = name
        self.resource_id = resource_id
        self.vlan_code = vlan_code
        self.servers = servers or []
        
        # Client reference for operations
        self.client = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VLAN':
        """
        Create a VLAN instance from a dictionary.
        
        Args:
            data: A dictionary of VLAN attributes.
            
        Returns:
            A new VLAN instance.
        """
        # Create a dictionary of model attributes
        kwargs = {}
        for field in cls._get_all_fields():
            api_field = cls._field_mappings.get(field, field)
            if api_field in data:
                kwargs[field] = data[api_field]
        
        # Handle servers
        if 'Servers' in data and data['Servers']:
            kwargs['servers'] = [server.get('ServerId') for server in data['Servers']]
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the VLAN to a dictionary.
        
        Returns:
            A dictionary representation of the VLAN.
        """
        result = super().to_dict()
        
        # Handle servers
        if self.servers:
            result['Servers'] = [{'ServerId': server_id} for server_id in self.servers]
        
        return result
    
    def delete(self) -> bool:
        """
        Delete the VLAN.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vlan.delete(self.resource_id)
    
    def attach(self, server_id: str, network_adapter_id: int, ip: Optional[str] = None, subnet_mask: Optional[str] = None, gateway: Optional[str] = None) -> bool:
        """
        Attach the VLAN to a server.
        
        Args:
            server_id: The server ID.
            network_adapter_id: The network adapter ID.
            ip: The IP address.
            subnet_mask: The subnet mask.
            gateway: The gateway.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vlan.attach(
            self.resource_id,
            server_id,
            network_adapter_id,
            ip,
            subnet_mask,
            gateway
        )
    
    def detach(self, server_id: str, network_adapter_id: int) -> bool:
        """
        Detach the VLAN from a server.
        
        Args:
            server_id: The server ID.
            network_adapter_id: The network adapter ID.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.compute.vlan.detach(
            self.resource_id,
            server_id,
            network_adapter_id
        )