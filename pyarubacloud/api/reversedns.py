"""
ReverseDns service for ArubaCloud API.

This module provides a service for interacting with ArubaCloud reverse DNS resources.
"""

from typing import Dict, Any, Optional, List, Union

from pyarubacloud.api.base import BaseService, BaseRepository
from pyarubacloud.exceptions import ResourceNotFoundError, ValidationError
from pyarubacloud.models.base import BaseModel


class ReverseDns(BaseModel):
    """
    Model for a reverse DNS entry.
    
    Attributes:
        address (str): The IP address.
        hostname (List[str]): The hostnames.
    """
    
    _required_fields = {'address'}
    _optional_fields = {'hostname'}
    _field_types = {
        'address': str
    }
    _field_mappings = {
        'address': 'Address',
        'hostname': 'HostName'
    }
    
    def __init__(
        self,
        address: str,
        hostname: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize the reverse DNS entry.
        
        Args:
            address: The IP address.
            hostname: The hostnames.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.address = address
        self.hostname = hostname or []
        
        # Client reference for operations
        self.client = None
    
    def reset(self) -> bool:
        """
        Reset the reverse DNS entry.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.reversedns.reset(self.address)
    
    def set(self, hostname: List[str]) -> bool:
        """
        Set the reverse DNS entry.
        
        Args:
            hostname: The hostnames.
            
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.reversedns.set(self.address, hostname)


class ReverseDnsRepository(BaseRepository[ReverseDns]):
    """
    Repository for reverse DNS resources.
    
    This class provides methods for interacting with reverse DNS resources,
    including getting, setting, and resetting reverse DNS entries.
    """
    
    def __init__(self, service: BaseService):
        """
        Initialize the reverse DNS repository.
        
        Args:
            service: The parent service.
        """
        super().__init__(
            service=service,
            model_class=ReverseDns,
            resource_name='ReverseDns'
        )
    
    def get(self, address: str) -> ReverseDns:
        """
        Get a reverse DNS entry by IP address.
        
        Args:
            address: The IP address.
            
        Returns:
            The reverse DNS entry.
            
        Raises:
            ResourceNotFoundError: If the reverse DNS entry is not found.
        """
        response = self.service._call_api(
            method='GetReverseDns',
            data={'Addresses': [address]},
            cache_key=f'reversedns_{address}'
        )
        
        if not response.get('Success', False) or 'Value' not in response:
            raise ResourceNotFoundError(f"Reverse DNS entry for {address} not found")
        
        # Find the entry for the specified address
        for entry in response['Value']:
            if entry.get('Address') == address:
                reverse_dns = ReverseDns(
                    address=address,
                    hostname=entry.get('HostName', [])
                )
                
                # Set the client reference
                reverse_dns.client = self.client
                
                return reverse_dns
        
        raise ResourceNotFoundError(f"Reverse DNS entry for {address} not found")
    
    def set(self, address: str, hostname: List[str]) -> bool:
        """
        Set a reverse DNS entry.
        
        Args:
            address: The IP address.
            hostname: The hostnames.
            
        Returns:
            True if successful, False otherwise.
        """
        # Validate input
        if not address:
            raise ValidationError("Address is required")
        
        if not hostname:
            raise ValidationError("Hostname is required")
        
        response = self.service._call_api(
            method='SetEnqueueSetReverseDns',
            data={
                'Address': address,
                'HostName': hostname
            }
        )
        
        # Invalidate the cache
        self.cache.delete(f'reversedns_{address}')
        
        return response.get('Success', False)
    
    def reset(self, address: str) -> bool:
        """
        Reset a reverse DNS entry.
        
        Args:
            address: The IP address.
            
        Returns:
            True if successful, False otherwise.
        """
        # Validate input
        if not address:
            raise ValidationError("Address is required")
        
        response = self.service._call_api(
            method='SetEnqueueResetReverseDns',
            data={'Addresses': [address]}
        )
        
        # Invalidate the cache
        self.cache.delete(f'reversedns_{address}')
        
        return response.get('Success', False)
    
    def get_multiple(self, addresses: List[str]) -> List[ReverseDns]:
        """
        Get multiple reverse DNS entries.
        
        Args:
            addresses: The IP addresses.
            
        Returns:
            A list of reverse DNS entries.
        """
        # Validate input
        if not addresses:
            raise ValidationError("Addresses are required")
        
        response = self.service._call_api(
            method='GetReverseDns',
            data={'Addresses': addresses}
        )
        
        if not response.get('Success', False) or 'Value' not in response:
            return []
        
        reverse_dns_entries = []
        for entry in response['Value']:
            address = entry.get('Address')
            if address in addresses:
                reverse_dns = ReverseDns(
                    address=address,
                    hostname=entry.get('HostName', [])
                )
                
                # Set the client reference
                reverse_dns.client = self.client
                
                reverse_dns_entries.append(reverse_dns)
        
        return reverse_dns_entries
    
    def reset_multiple(self, addresses: List[str]) -> bool:
        """
        Reset multiple reverse DNS entries.
        
        Args:
            addresses: The IP addresses.
            
        Returns:
            True if successful, False otherwise.
        """
        # Validate input
        if not addresses:
            raise ValidationError("Addresses are required")
        
        response = self.service._call_api(
            method='SetEnqueueResetReverseDns',
            data={'Addresses': addresses}
        )
        
        # Invalidate the cache
        for address in addresses:
            self.cache.delete(f'reversedns_{address}')
        
        return response.get('Success', False)


class ReverseDnsService(BaseService):
    """
    Service for interacting with ArubaCloud reverse DNS resources.
    
    This class provides access to repositories for reverse DNS entries.
    
    Attributes:
        reversedns (ReverseDnsRepository): The reverse DNS repository.
    """
    
    def __init__(self, client):
        """
        Initialize the reverse DNS service.
        
        Args:
            client: The ArubaCloud client.
        """
        super().__init__(client)
        self.reversedns = ReverseDnsRepository(self)
    
    def get(self, address: str) -> ReverseDns:
        """
        Get a reverse DNS entry by IP address.
        
        Args:
            address: The IP address.
            
        Returns:
            The reverse DNS entry.
        """
        return self.reversedns.get(address)
    
    def set(self, address: str, hostname: List[str]) -> bool:
        """
        Set a reverse DNS entry.
        
        Args:
            address: The IP address.
            hostname: The hostnames.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.reversedns.set(address, hostname)
    
    def reset(self, address: str) -> bool:
        """
        Reset a reverse DNS entry.
        
        Args:
            address: The IP address.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.reversedns.reset(address)
    
    def get_multiple(self, addresses: List[str]) -> List[ReverseDns]:
        """
        Get multiple reverse DNS entries.
        
        Args:
            addresses: The IP addresses.
            
        Returns:
            A list of reverse DNS entries.
        """
        return self.reversedns.get_multiple(addresses)
    
    def reset_multiple(self, addresses: List[str]) -> bool:
        """
        Reset multiple reverse DNS entries.
        
        Args:
            addresses: The IP addresses.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.reversedns.reset_multiple(addresses)