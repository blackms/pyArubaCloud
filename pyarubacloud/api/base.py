"""
Base service for ArubaCloud API services.

This module provides a base service class for ArubaCloud API services,
with common functionality for making API requests and handling responses.
"""

import logging
from typing import Dict, Any, Optional, TypeVar, Generic, Type, List, Union

from pyarubacloud.exceptions import ResourceNotFoundError
from pyarubacloud.models.base import BaseModel
from pyarubacloud.utils.http import HttpClient
from pyarubacloud.utils.cache import Cache

T = TypeVar('T', bound=BaseModel)


class BaseService:
    """
    Base service for ArubaCloud API services.
    
    This class provides common functionality for all ArubaCloud API services,
    including making API requests and handling responses.
    
    Attributes:
        client: The ArubaCloud client.
        http_client: The HTTP client.
        logger: The logger instance.
        cache: The cache instance.
    """
    
    def __init__(self, client):
        """
        Initialize the service.
        
        Args:
            client: The ArubaCloud client.
        """
        self.client = client
        self.http_client = client.http_client
        self.logger = client.logger.get_child(self.__class__.__name__)
        self.cache = client.cache
    
    def _call_api(
        self,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Call the API.
        
        Args:
            method: The API method to call.
            data: The data to send.
            headers: Optional headers.
            cache_key: An optional cache key.
            cache_ttl: An optional cache TTL.
            
        Returns:
            The API response.
        """
        # Check cache if a cache key is provided
        if cache_key:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                self.logger.debug(f"Cache hit for {cache_key}")
                return cached_result
        
        # Prepare request data
        request_data = {
            "ApplicationId": method,
            "RequestId": method,
            "SessionId": method,
            "Password": self.client.auth.password,
            "Username": self.client.auth.username
        }
        
        # Add additional data if provided
        if data:
            request_data.update(data)
        
        # Make the API call
        self.logger.debug(f"Calling API method: {method}")
        response = self.http_client.post(method, request_data, headers)
        
        # Cache the result if a cache key is provided
        if cache_key:
            self.cache.set(cache_key, response, cache_ttl)
        
        return response


class BaseRepository(Generic[T]):
    """
    Base repository for ArubaCloud resources.
    
    This class provides common CRUD operations for ArubaCloud resources,
    with support for caching and validation.
    
    Attributes:
        service: The parent service.
        model_class: The model class for the resource.
        resource_name: The name of the resource.
        list_method: The API method for listing resources.
        get_method: The API method for getting a resource.
        create_method: The API method for creating a resource.
        update_method: The API method for updating a resource.
        delete_method: The API method for deleting a resource.
    """
    
    def __init__(
        self,
        service: BaseService,
        model_class: Type[T],
        resource_name: str,
        list_method: Optional[str] = None,
        get_method: Optional[str] = None,
        create_method: Optional[str] = None,
        update_method: Optional[str] = None,
        delete_method: Optional[str] = None
    ):
        """
        Initialize the repository.
        
        Args:
            service: The parent service.
            model_class: The model class for the resource.
            resource_name: The name of the resource.
            list_method: The API method for listing resources.
            get_method: The API method for getting a resource.
            create_method: The API method for creating a resource.
            update_method: The API method for updating a resource.
            delete_method: The API method for deleting a resource.
        """
        self.service = service
        self.client = service.client
        self.http_client = service.http_client
        self.logger = service.logger.get_child(self.__class__.__name__)
        self.cache = service.cache
        
        self.model_class = model_class
        self.resource_name = resource_name
        
        self.list_method = list_method
        self.get_method = get_method
        self.create_method = create_method
        self.update_method = update_method
        self.delete_method = delete_method
    
    def list(self, **kwargs) -> List[T]:
        """
        List resources.
        
        Args:
            **kwargs: Additional parameters for the API call.
            
        Returns:
            A list of resource models.
            
        Raises:
            NotImplementedError: If the list method is not defined.
        """
        if not self.list_method:
            raise NotImplementedError(f"List method not defined for {self.resource_name}")
        
        # Generate a cache key
        cache_key = f"{self.resource_name}_list"
        if kwargs:
            cache_key += f"_{hash(frozenset(kwargs.items()))}"
        
        # Call the API
        response = self.service._call_api(
            method=self.list_method,
            data=kwargs,
            cache_key=cache_key
        )
        
        # Parse the response
        items = response.get("Value", [])
        return [self.model_class.from_dict(item) for item in items]
    
    def get(self, resource_id: Union[str, int]) -> T:
        """
        Get a resource by ID.
        
        Args:
            resource_id: The resource ID.
            
        Returns:
            The resource model.
            
        Raises:
            NotImplementedError: If the get method is not defined.
            ResourceNotFoundError: If the resource is not found.
        """
        if not self.get_method:
            raise NotImplementedError(f"Get method not defined for {self.resource_name}")
        
        # Generate a cache key
        cache_key = f"{self.resource_name}_{resource_id}"
        
        # Call the API
        response = self.service._call_api(
            method=self.get_method,
            data={f"{self.resource_name}Id": resource_id},
            cache_key=cache_key
        )
        
        # Parse the response
        if not response.get("Success", False) or "Value" not in response:
            raise ResourceNotFoundError(f"{self.resource_name} with ID {resource_id} not found")
        
        return self.model_class.from_dict(response["Value"])
    
    def get_by_name(self, name: str) -> T:
        """
        Get a resource by name.
        
        Args:
            name: The resource name.
            
        Returns:
            The resource model.
            
        Raises:
            ResourceNotFoundError: If the resource is not found.
        """
        # List all resources and filter by name
        resources = self.list()
        for resource in resources:
            if getattr(resource, "name", None) == name:
                return resource
        
        raise ResourceNotFoundError(f"{self.resource_name} with name {name} not found")
    
    def create(self, model: T, **kwargs) -> T:
        """
        Create a resource.
        
        Args:
            model: The resource model.
            **kwargs: Additional parameters for the API call.
            
        Returns:
            The created resource model.
            
        Raises:
            NotImplementedError: If the create method is not defined.
            ValueError: If the model is invalid.
        """
        if not self.create_method:
            raise NotImplementedError(f"Create method not defined for {self.resource_name}")
        
        # Validate the model
        errors = model.validate()
        if errors:
            raise ValueError(f"Invalid {self.resource_name} model: {', '.join(errors)}")
        
        # Prepare the request data
        data = {self.resource_name: model.to_dict()}
        data.update(kwargs)
        
        # Call the API
        response = self.service._call_api(
            method=self.create_method,
            data=data
        )
        
        # Invalidate the list cache
        self.cache.invalidate_pattern(f"{self.resource_name}_list")
        
        # Parse the response
        if "Value" in response and isinstance(response["Value"], dict):
            return self.model_class.from_dict(response["Value"])
        
        # If the response doesn't contain the created resource, try to get it by ID
        if "ResourceId" in response.get("Value", {}):
            resource_id = response["Value"]["ResourceId"]
            return self.get(resource_id)
        
        # If we can't get the created resource, return the original model
        return model
    
    def update(self, resource_id: Union[str, int], model: T, **kwargs) -> T:
        """
        Update a resource.
        
        Args:
            resource_id: The resource ID.
            model: The resource model.
            **kwargs: Additional parameters for the API call.
            
        Returns:
            The updated resource model.
            
        Raises:
            NotImplementedError: If the update method is not defined.
            ValueError: If the model is invalid.
        """
        if not self.update_method:
            raise NotImplementedError(f"Update method not defined for {self.resource_name}")
        
        # Validate the model
        errors = model.validate()
        if errors:
            raise ValueError(f"Invalid {self.resource_name} model: {', '.join(errors)}")
        
        # Prepare the request data
        data = {
            f"{self.resource_name}Id": resource_id,
            self.resource_name: model.to_dict()
        }
        data.update(kwargs)
        
        # Call the API
        response = self.service._call_api(
            method=self.update_method,
            data=data
        )
        
        # Invalidate the cache
        self.cache.delete(f"{self.resource_name}_{resource_id}")
        self.cache.invalidate_pattern(f"{self.resource_name}_list")
        
        # Parse the response
        if "Value" in response and isinstance(response["Value"], dict):
            return self.model_class.from_dict(response["Value"])
        
        # If the response doesn't contain the updated resource, try to get it by ID
        return self.get(resource_id)
    
    def delete(self, resource_id: Union[str, int], **kwargs) -> bool:
        """
        Delete a resource.
        
        Args:
            resource_id: The resource ID.
            **kwargs: Additional parameters for the API call.
            
        Returns:
            True if the resource was deleted, False otherwise.
            
        Raises:
            NotImplementedError: If the delete method is not defined.
        """
        if not self.delete_method:
            raise NotImplementedError(f"Delete method not defined for {self.resource_name}")
        
        # Prepare the request data
        data = {f"{self.resource_name}Id": resource_id}
        data.update(kwargs)
        
        # Call the API
        response = self.service._call_api(
            method=self.delete_method,
            data=data
        )
        
        # Invalidate the cache
        self.cache.delete(f"{self.resource_name}_{resource_id}")
        self.cache.invalidate_pattern(f"{self.resource_name}_list")
        
        return response.get("Success", False)