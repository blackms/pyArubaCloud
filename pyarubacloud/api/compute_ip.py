"""
IP repository implementation for ArubaCloud API.

This module provides the IP repository implementation for the ArubaCloud API,
including methods for purchasing, releasing, and managing IP addresses.
"""

from typing import Dict, Any, Optional, List, Union

from pyarubacloud.api.base import BaseRepository, BaseService
from pyarubacloud.exceptions import ResourceNotFoundError, ValidationError
from pyarubacloud.models.ip import IP


class IPRepository(BaseRepository[IP]):
    """
    Repository for IP resources.
    
    This class provides methods for interacting with IP resources,
    including listing, purchasing, and releasing IPs.
    """
    
    def __init__(self, service: BaseService):
        """
        Initialize the IP repository.
        
        Args:
            service: The parent service.
        """
        super().__init__(
            service=service,
            model_class=IP,
            resource_name='IpAddress',
            list_method='GetPurchasedIpAddresses'
        )
    
    def list(self, **kwargs) -> List[IP]:
        """
        List all purchased IP addresses.
        
        Args:
            **kwargs: Additional parameters for the API call.
            
        Returns:
            A list of IP objects.
        """
        response = self.service._call_api(
            method='GetPurchasedIpAddresses',
            data=kwargs,
            cache_key='ip_list'
        )
        
        ips = []
        for item in response.get('Value', []):
            ip = IP(
                address=item.get('Value'),
                resource_id=item.get('ResourceId'),
                server_id=item.get('ServerId') if item.get('ServerId') != 'None' else None
            )
            
            # Set the client reference
            ip.client = self.client
            
            ips.append(ip)
        
        return ips
    
    def get(self, ip_id: Union[str, int]) -> IP:
        """
        Get an IP by ID.
        
        Args:
            ip_id: The IP ID.
            
        Returns:
            The IP object.
            
        Raises:
            ResourceNotFoundError: If the IP is not found.
        """
        # List all IPs and find the one with the matching ID
        ips = self.list()
        for ip in ips:
            if ip.resource_id == str(ip_id):
                return ip
        
        raise ResourceNotFoundError(f"IP with ID {ip_id} not found")
    
    def get_by_address(self, address: str) -> IP:
        """
        Get an IP by address.
        
        Args:
            address: The IP address.
            
        Returns:
            The IP object.
            
        Raises:
            ResourceNotFoundError: If the IP is not found.
        """
        # List all IPs and find the one with the matching address
        ips = self.list()
        for ip in ips:
            if ip.address == address:
                return ip
        
        raise ResourceNotFoundError(f"IP with address {address} not found")
    
    def purchase(self) -> IP:
        """
        Purchase a new IP address.
        
        Returns:
            The purchased IP object.
        """
        response = self.service._call_api(
            method='SetPurchaseIpAddress',
            data={}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('ip_list')
        
        if not response.get('Success', False) or 'Value' not in response:
            raise Exception("Failed to purchase IP address")
        
        ip = IP(
            address=response['Value'].get('Value'),
            resource_id=response['Value'].get('ResourceId')
        )
        
        # Set the client reference
        ip.client = self.client
        
        return ip
    
    def release(self, ip_id: Union[str, int]) -> bool:
        """
        Release an IP address.
        
        Args:
            ip_id: The IP ID.
            
        Returns:
            True if successful, False otherwise.
        """
        response = self.service._call_api(
            method='SetRemoveIpAddress',
            data={'IpAddressResourceId': ip_id}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('ip_list')
        
        return response.get('Success', False)
    
    def assign(self, ip_id: Union[str, int], server_id: Union[str, int]) -> bool:
        """
        Assign an IP address to a server.
        
        Args:
            ip_id: The IP ID.
            server_id: The server ID.
            
        Returns:
            True if successful, False otherwise.
        """
        # Get the VM to check its network adapters
        vm = self.client.compute.vm.get(server_id)
        
        # Find the first available network adapter
        adapter_id = len(vm.network_adapters)
        if adapter_id >= 3:
            raise ValidationError("VM already has the maximum number of network adapters (3)")
        
        # Assign the IP
        response = self.service._call_api(
            method='SetEnqueueAssociateIpAddress',
            data={
                'IpAddressResourceId': ip_id,
                'ServerId': server_id
            }
        )
        
        # Invalidate the cache
        self.cache.delete(f'vm_{server_id}')
        self.cache.invalidate_pattern('ip_list')
        
        return response.get('Success', False)
    
    def unassign(self, ip_id: Union[str, int]) -> bool:
        """
        Unassign an IP address from a server.
        
        Args:
            ip_id: The IP ID.
            
        Returns:
            True if successful, False otherwise.
        """
        # Get the IP to check if it's assigned
        ip = self.get(ip_id)
        
        if not ip.server_id:
            raise ValidationError("IP is not assigned to a server")
        
        # Unassign the IP
        response = self.service._call_api(
            method='SetEnqueueDeassociateIpAddress',
            data={'IpAddressResourceId': ip_id}
        )
        
        # Invalidate the cache
        if ip.server_id:
            self.cache.delete(f'vm_{ip.server_id}')
        self.cache.invalidate_pattern('ip_list')
        
        return response.get('Success', False)