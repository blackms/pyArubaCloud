"""
SharedStorage service for ArubaCloud API.

This module provides a service for interacting with ArubaCloud shared storage resources.
"""

from typing import Dict, Any, Optional, List, Union

from pyarubacloud.api.base import BaseService, BaseRepository
from pyarubacloud.constants import (
    SharedStorageProtocolType,
    SharedStorageStatus
)
from pyarubacloud.exceptions import ResourceNotFoundError, ValidationError
from pyarubacloud.models.base import BaseModel


class SharedStorage(BaseModel):
    """
    Model for a shared storage.
    
    Attributes:
        id (str): The shared storage ID.
        name (str): The name of the shared storage.
        status (int): The status of the shared storage.
        protocol_type (int): The protocol type.
        size (int): The size in GB.
        created_at (datetime): The creation timestamp.
        updated_at (datetime): The last update timestamp.
    """
    
    _required_fields = {'name'}
    _optional_fields = {'id', 'status', 'protocol_type', 'size', 'created_at', 'updated_at'}
    _field_types = {
        'id': str,
        'name': str,
        'status': int,
        'protocol_type': int,
        'size': int
    }
    _field_mappings = {
        'id': 'SharedStorageID',
        'name': 'Name',
        'status': 'Status',
        'protocol_type': 'ProtocolType',
        'size': 'Size',
        'created_at': 'CreationDate',
        'updated_at': 'UpdatedDate'
    }
    
    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        status: Optional[int] = None,
        protocol_type: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize the shared storage.
        
        Args:
            name: The name of the shared storage.
            id: The shared storage ID.
            status: The status of the shared storage.
            protocol_type: The protocol type.
            size: The size in GB.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.name = name
        self.id = id
        self.status = status
        self.protocol_type = protocol_type
        self.size = size
        
        # Client reference for operations
        self.client = None
    
    def delete(self) -> bool:
        """
        Delete the shared storage.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.sharedstorage.delete(self.id)
    
    def is_running(self) -> bool:
        """
        Check if the shared storage is running.
        
        Returns:
            True if the shared storage is running, False otherwise.
        """
        return self.status == SharedStorageStatus.RUNNING
    
    def is_stopped(self) -> bool:
        """
        Check if the shared storage is stopped.
        
        Returns:
            True if the shared storage is stopped, False otherwise.
        """
        return self.status == SharedStorageStatus.STOPPED
    
    def is_pending(self) -> bool:
        """
        Check if the shared storage is in a pending state.
        
        Returns:
            True if the shared storage is in a pending state, False otherwise.
        """
        return self.status == SharedStorageStatus.PENDING


class SharedStorageIQN(BaseModel):
    """
    Model for a shared storage IQN.
    
    Attributes:
        id (str): The IQN ID.
        iqn (str): The IQN.
        shared_storage_id (str): The shared storage ID.
    """
    
    _required_fields = {'iqn', 'shared_storage_id'}
    _optional_fields = {'id'}
    _field_types = {
        'id': str,
        'iqn': str,
        'shared_storage_id': str
    }
    _field_mappings = {
        'id': 'IQNID',
        'iqn': 'IQN',
        'shared_storage_id': 'SharedStorageID'
    }
    
    def __init__(
        self,
        iqn: str,
        shared_storage_id: str,
        id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the shared storage IQN.
        
        Args:
            iqn: The IQN.
            shared_storage_id: The shared storage ID.
            id: The IQN ID.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.iqn = iqn
        self.shared_storage_id = shared_storage_id
        self.id = id
        
        # Client reference for operations
        self.client = None
    
    def delete(self) -> bool:
        """
        Delete the shared storage IQN.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.sharedstorage.delete_iqn(self.id)


class SharedStorageRepository(BaseRepository[SharedStorage]):
    """
    Repository for shared storage resources.
    
    This class provides methods for interacting with shared storage resources,
    including listing, getting, creating, and deleting shared storages.
    """
    
    def __init__(self, service: BaseService):
        """
        Initialize the shared storage repository.
        
        Args:
            service: The parent service.
        """
        super().__init__(
            service=service,
            model_class=SharedStorage,
            resource_name='SharedStorage',
            list_method='GetSharedStorages',
            delete_method='SetEnqueueRemoveSharedStorage'
        )
    
    def list(self, **kwargs) -> List[SharedStorage]:
        """
        List all shared storages.
        
        Args:
            **kwargs: Additional parameters for the API call.
            
        Returns:
            A list of shared storage objects.
        """
        response = self.service._call_api(
            method='GetSharedStorages',
            data=kwargs,
            cache_key='sharedstorage_list'
        )
        
        shared_storages = []
        for item in response.get('Value', []):
            shared_storage = SharedStorage(
                id=item.get('SharedStorageID'),
                name=item.get('Name'),
                status=item.get('Status'),
                protocol_type=item.get('ProtocolType'),
                size=item.get('Size')
            )
            
            # Set the client reference
            shared_storage.client = self.client
            
            shared_storages.append(shared_storage)
        
        return shared_storages
    
    def get(self, shared_storage_id: Union[str, int]) -> SharedStorage:
        """
        Get a shared storage by ID.
        
        Args:
            shared_storage_id: The shared storage ID.
            
        Returns:
            The shared storage object.
            
        Raises:
            ResourceNotFoundError: If the shared storage is not found.
        """
        # List all shared storages and find the one with the matching ID
        shared_storages = self.list()
        for shared_storage in shared_storages:
            if shared_storage.id == str(shared_storage_id):
                return shared_storage
        
        raise ResourceNotFoundError(f"Shared storage with ID {shared_storage_id} not found")
    
    def get_by_name(self, name: str) -> SharedStorage:
        """
        Get a shared storage by name.
        
        Args:
            name: The shared storage name.
            
        Returns:
            The shared storage object.
            
        Raises:
            ResourceNotFoundError: If the shared storage is not found.
        """
        # List all shared storages and find the one with the matching name
        shared_storages = self.list()
        for shared_storage in shared_storages:
            if shared_storage.name == name:
                return shared_storage
        
        raise ResourceNotFoundError(f"Shared storage with name {name} not found")
    
    def create(
        self,
        name: str,
        size: int,
        protocol_type: Union[int, SharedStorageProtocolType] = SharedStorageProtocolType.ISCSI
    ) -> SharedStorage:
        """
        Create a new shared storage.
        
        Args:
            name: The shared storage name.
            size: The size in GB.
            protocol_type: The protocol type.
            
        Returns:
            The created shared storage object.
        """
        # Validate input
        if not name:
            raise ValidationError("Name is required")
        
        if size <= 0:
            raise ValidationError("Size must be positive")
        
        response = self.service._call_api(
            method='SetEnqueuePurchaseSharedStorage',
            data={
                'SharedStoragePurchase': {
                    'Name': name,
                    'Size': size,
                    'ProtocolType': protocol_type
                }
            }
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('sharedstorage_list')
        
        if not response.get('Success', False) or 'Value' not in response:
            raise Exception("Failed to create shared storage")
        
        shared_storage = SharedStorage(
            id=response['Value'].get('SharedStorageID'),
            name=name,
            status=SharedStorageStatus.PENDING,
            protocol_type=protocol_type,
            size=size
        )
        
        # Set the client reference
        shared_storage.client = self.client
        
        return shared_storage
    
    def delete(self, shared_storage_id: Union[str, int]) -> bool:
        """
        Delete a shared storage.
        
        Args:
            shared_storage_id: The shared storage ID.
            
        Returns:
            True if successful, False otherwise.
        """
        response = self.service._call_api(
            method='SetEnqueueRemoveSharedStorage',
            data={'SharedStorageID': shared_storage_id}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('sharedstorage_list')
        
        return response.get('Success', False)
    
    def add_iqn(self, shared_storage_id: Union[str, int], iqn: str) -> SharedStorageIQN:
        """
        Add an IQN to a shared storage.
        
        Args:
            shared_storage_id: The shared storage ID.
            iqn: The IQN.
            
        Returns:
            The created shared storage IQN object.
        """
        # Validate input
        if not iqn:
            raise ValidationError("IQN is required")
        
        response = self.service._call_api(
            method='SetEnqueueAddIQNSharedStorage',
            data={
                'SharedStorageIQN': {
                    'SharedStorageID': shared_storage_id,
                    'IQN': iqn
                }
            }
        )
        
        if not response.get('Success', False) or 'Value' not in response:
            raise Exception("Failed to add IQN to shared storage")
        
        shared_storage_iqn = SharedStorageIQN(
            id=response['Value'].get('IQNID'),
            iqn=iqn,
            shared_storage_id=str(shared_storage_id)
        )
        
        # Set the client reference
        shared_storage_iqn.client = self.client
        
        return shared_storage_iqn
    
    def delete_iqn(self, iqn_id: Union[str, int]) -> bool:
        """
        Delete an IQN.
        
        Args:
            iqn_id: The IQN ID.
            
        Returns:
            True if successful, False otherwise.
        """
        response = self.service._call_api(
            method='SetEnqueueRemoveIQNSharedStorage',
            data={'IQNID': iqn_id}
        )
        
        return response.get('Success', False)
    
    def get_iqns(self, shared_storage_id: Union[str, int]) -> List[SharedStorageIQN]:
        """
        Get all IQNs for a shared storage.
        
        Args:
            shared_storage_id: The shared storage ID.
            
        Returns:
            A list of shared storage IQN objects.
        """
        response = self.service._call_api(
            method='GetSharedStorageIQNs',
            data={'SharedStorageID': shared_storage_id},
            cache_key=f'sharedstorage_{shared_storage_id}_iqns'
        )
        
        iqns = []
        for item in response.get('Value', []):
            iqn = SharedStorageIQN(
                id=item.get('IQNID'),
                iqn=item.get('IQN'),
                shared_storage_id=str(shared_storage_id)
            )
            
            # Set the client reference
            iqn.client = self.client
            
            iqns.append(iqn)
        
        return iqns


class SharedStorageService(BaseService):
    """
    Service for interacting with ArubaCloud shared storage resources.
    
    This class provides access to repositories for shared storages.
    
    Attributes:
        sharedstorage (SharedStorageRepository): The shared storage repository.
    """
    
    def __init__(self, client):
        """
        Initialize the shared storage service.
        
        Args:
            client: The ArubaCloud client.
        """
        super().__init__(client)
        self.sharedstorage = SharedStorageRepository(self)
    
    def list(self, **kwargs) -> List[SharedStorage]:
        """
        List all shared storages.
        
        Args:
            **kwargs: Additional parameters for the API call.
            
        Returns:
            A list of shared storage objects.
        """
        return self.sharedstorage.list(**kwargs)
    
    def get(self, shared_storage_id: Union[str, int]) -> SharedStorage:
        """
        Get a shared storage by ID.
        
        Args:
            shared_storage_id: The shared storage ID.
            
        Returns:
            The shared storage object.
        """
        return self.sharedstorage.get(shared_storage_id)
    
    def create(
        self,
        name: str,
        size: int,
        protocol_type: Union[int, SharedStorageProtocolType] = SharedStorageProtocolType.ISCSI
    ) -> SharedStorage:
        """
        Create a new shared storage.
        
        Args:
            name: The shared storage name.
            size: The size in GB.
            protocol_type: The protocol type.
            
        Returns:
            The created shared storage object.
        """
        return self.sharedstorage.create(name, size, protocol_type)
    
    def delete(self, shared_storage_id: Union[str, int]) -> bool:
        """
        Delete a shared storage.
        
        Args:
            shared_storage_id: The shared storage ID.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.sharedstorage.delete(shared_storage_id)
    
    def add_iqn(self, shared_storage_id: Union[str, int], iqn: str) -> SharedStorageIQN:
        """
        Add an IQN to a shared storage.
        
        Args:
            shared_storage_id: The shared storage ID.
            iqn: The IQN.
            
        Returns:
            The created shared storage IQN object.
        """
        return self.sharedstorage.add_iqn(shared_storage_id, iqn)
    
    def delete_iqn(self, iqn_id: Union[str, int]) -> bool:
        """
        Delete an IQN.
        
        Args:
            iqn_id: The IQN ID.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.sharedstorage.delete_iqn(iqn_id)
    
    def get_iqns(self, shared_storage_id: Union[str, int]) -> List[SharedStorageIQN]:
        """
        Get all IQNs for a shared storage.
        
        Args:
            shared_storage_id: The shared storage ID.
            
        Returns:
            A list of shared storage IQN objects.
        """
        return self.sharedstorage.get_iqns(shared_storage_id)