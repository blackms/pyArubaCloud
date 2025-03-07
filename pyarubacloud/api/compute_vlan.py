"""
VLAN repository implementation for ArubaCloud API.

This module provides the VLAN repository implementation for the ArubaCloud API,
including methods for creating, listing, and managing VLANs.
"""

from typing import Dict, Any, Optional, List, Union

from pyarubacloud.api.base import BaseRepository, BaseService
from pyarubacloud.exceptions import ResourceNotFoundError, ValidationError
from pyarubacloud.models.vlan import VLAN


class VLANRepository(BaseRepository[VLAN]):
    """
    Repository for VLAN resources.
    
    This class provides methods for interacting with VLAN resources,
    including listing, creating, and deleting VLANs.
    """
    
    def __init__(self, service: BaseService):
        """
        Initialize the VLAN repository.
        
        Args:
            service: The parent service.
        """
        super().__init__(
            service=service,
            model_class=VLAN,
            resource_name='VLan',
            list_method='GetPurchasedVLans'
        )
    
    def list(self, **kwargs) -> List[VLAN]:
        """
        List all purchased VLANs.
        
        Args:
            **kwargs: Additional parameters for the API call.
            
        Returns:
            A list of VLAN objects.
        """
        response = self.service._call_api(
            method='GetPurchasedVLans',
            data=kwargs,
            cache_key='vlan_list'
        )
        
        vlans = []
        for item in response.get('Value', []):
            vlan = VLAN(
                name=item.get('Name'),
                resource_id=item.get('ResourceId'),
                vlan_code=item.get('VlanCode')
            )
            
            # Set the client reference
            vlan.client = self.client
            
            vlans.append(vlan)
        
        return vlans
    
    def get(self, vlan_id: Union[str, int]) -> VLAN:
        """
        Get a VLAN by ID.
        
        Args:
            vlan_id: The VLAN ID.
            
        Returns:
            The VLAN object.
            
        Raises:
            ResourceNotFoundError: If the VLAN is not found.
        """
        # List all VLANs and find the one with the matching ID
        vlans = self.list()
        for vlan in vlans:
            if vlan.resource_id == str(vlan_id):
                return vlan
        
        raise ResourceNotFoundError(f"VLAN with ID {vlan_id} not found")
    
    def get_by_name(self, name: str) -> VLAN:
        """
        Get a VLAN by name.
        
        Args:
            name: The VLAN name.
            
        Returns:
            The VLAN object.
            
        Raises:
            ResourceNotFoundError: If the VLAN is not found.
        """
        # List all VLANs and find the one with the matching name
        vlans = self.list()
        for vlan in vlans:
            if vlan.name == name:
                return vlan
        
        raise ResourceNotFoundError(f"VLAN with name {name} not found")
    
    def create(self, name: str) -> VLAN:
        """
        Create a new VLAN.
        
        Args:
            name: The VLAN name.
            
        Returns:
            The created VLAN object.
        """
        # Validate input
        if not name:
            raise ValidationError("Name is required")
        
        response = self.service._call_api(
            method='SetPurchaseVLan',
            data={'VLanName': name}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('vlan_list')
        
        if not response.get('Success', False) or 'Value' not in response:
            raise Exception("Failed to create VLAN")
        
        vlan = VLAN(
            name=response['Value'].get('Name'),
            resource_id=response['Value'].get('ResourceId'),
            vlan_code=response['Value'].get('VlanCode')
        )
        
        # Set the client reference
        vlan.client = self.client
        
        return vlan
    
    def delete(self, vlan_id: Union[str, int]) -> bool:
        """
        Delete a VLAN.
        
        Args:
            vlan_id: The VLAN ID.
            
        Returns:
            True if successful, False otherwise.
        """
        response = self.service._call_api(
            method='SetRemoveVLan',
            data={'VLanResourceId': vlan_id}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('vlan_list')
        
        return response.get('Success', False)
    
    def attach(
        self,
        vlan_id: Union[str, int],
        server_id: Union[str, int],
        network_adapter_id: int,
        ip: Optional[str] = None,
        subnet_mask: Optional[str] = None,
        gateway: Optional[str] = None
    ) -> bool:
        """
        Attach a VLAN to a server.
        
        Args:
            vlan_id: The VLAN ID.
            server_id: The server ID.
            network_adapter_id: The network adapter ID.
            ip: The IP address.
            subnet_mask: The subnet mask.
            gateway: The gateway.
            
        Returns:
            True if successful, False otherwise.
        """
        # Prepare the request data
        if gateway is not None:
            vlan_request = {
                "VLanRequest": {
                    "NetworkAdapterId": network_adapter_id,
                    "SetOnVirtualMachine": "true",
                    "VLanResourceId": vlan_id,
                    "PrivateIps": [{
                        "GateWay": gateway,
                        "IP": ip,
                        "SubNetMask": subnet_mask
                    }]
                }
            }
        else:
            vlan_request = {
                "VLanRequest": {
                    "NetworkAdapterId": network_adapter_id,
                    "SetOnVirtualMachine": "false",
                    "VLanResourceId": vlan_id,
                    "PrivateIps": [{
                        "GateWay": None,
                        "IP": None,
                        "SubNetMask": None
                    }]
                }
            }
        
        response = self.service._call_api(
            method='SetEnqueueAssociateVLan',
            data=vlan_request
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{server_id}')
        
        return response.get('Success', False)
    
    def detach(
        self,
        vlan_id: Union[str, int],
        server_id: Union[str, int],
        network_adapter_id: int
    ) -> bool:
        """
        Detach a VLAN from a server.
        
        Args:
            vlan_id: The VLAN ID.
            server_id: The server ID.
            network_adapter_id: The network adapter ID.
            
        Returns:
            True if successful, False otherwise.
        """
        vlan_request = {
            "VLanRequest": {
                "NetworkAdapterId": network_adapter_id,
                "SetOnVirtualMachine": "false",
                "VLanResourceId": vlan_id
            }
        }
        
        response = self.service._call_api(
            method='SetEnqueueDeassociateVLan',
            data=vlan_request
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{server_id}')
        
        return response.get('Success', False)