"""
Template model for ArubaCloud resources.

This module provides a model class for ArubaCloud template resources.
"""

from typing import Optional, Dict, Any, ClassVar, Set, Type

from pyarubacloud.models.base import BaseModel


class ResourceBounds(BaseModel):
    """
    Model for template resource bounds.
    
    Attributes:
        max_cpu (Optional[int]): The maximum number of CPUs.
        max_memory (Optional[int]): The maximum amount of RAM in GB.
        hdd0 (Optional[int]): The maximum size of the first disk in GB.
        hdd1 (Optional[int]): The maximum size of the second disk in GB.
        hdd2 (Optional[int]): The maximum size of the third disk in GB.
        hdd3 (Optional[int]): The maximum size of the fourth disk in GB.
    """
    
    _required_fields: ClassVar[Set[str]] = set()
    _optional_fields: ClassVar[Set[str]] = {'max_cpu', 'max_memory', 'hdd0', 'hdd1', 'hdd2', 'hdd3'}
    _field_types: ClassVar[Dict[str, Type]] = {
        'max_cpu': int,
        'max_memory': int,
        'hdd0': int,
        'hdd1': int,
        'hdd2': int,
        'hdd3': int
    }
    _field_mappings: ClassVar[Dict[str, str]] = {
        'max_cpu': 'MaxCPU',
        'max_memory': 'MaxMemory',
        'hdd0': 'HDD0',
        'hdd1': 'HDD1',
        'hdd2': 'HDD2',
        'hdd3': 'HDD3'
    }
    
    def __init__(
        self,
        max_cpu: Optional[int] = None,
        max_memory: Optional[int] = None,
        hdd0: Optional[int] = None,
        hdd1: Optional[int] = None,
        hdd2: Optional[int] = None,
        hdd3: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize the resource bounds.
        
        Args:
            max_cpu: The maximum number of CPUs.
            max_memory: The maximum amount of RAM in GB.
            hdd0: The maximum size of the first disk in GB.
            hdd1: The maximum size of the second disk in GB.
            hdd2: The maximum size of the third disk in GB.
            hdd3: The maximum size of the fourth disk in GB.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.max_cpu = max_cpu
        self.max_memory = max_memory
        self.hdd0 = hdd0
        self.hdd1 = hdd1
        self.hdd2 = hdd2
        self.hdd3 = hdd3


class Template(BaseModel):
    """
    Model for a template.
    
    Attributes:
        template_id (str): The template ID.
        name (str): The name of the template.
        description (str): The description of the template.
        hypervisor (str): The hypervisor type.
        id_code (Optional[str]): The identification code.
        enabled (bool): Whether the template is enabled.
        resource_bounds (ResourceBounds): The resource bounds.
    """
    
    _required_fields: ClassVar[Set[str]] = {'template_id', 'name', 'description', 'hypervisor'}
    _optional_fields: ClassVar[Set[str]] = {'id_code', 'enabled', 'resource_bounds'}
    _field_types: ClassVar[Dict[str, Type]] = {
        'template_id': str,
        'name': str,
        'description': str,
        'hypervisor': str,
        'id_code': str,
        'enabled': bool
    }
    _field_mappings: ClassVar[Dict[str, str]] = {
        'template_id': 'Id',
        'name': 'Name',
        'description': 'Description',
        'hypervisor': 'HypervisorType',
        'id_code': 'IdentificationCode',
        'enabled': 'Enabled'
    }
    
    def __init__(
        self,
        template_id: str,
        name: str,
        description: str,
        hypervisor: str,
        id_code: Optional[str] = None,
        enabled: bool = True,
        resource_bounds: Optional[ResourceBounds] = None,
        **kwargs
    ):
        """
        Initialize the template.
        
        Args:
            template_id: The template ID.
            name: The name of the template.
            description: The description of the template.
            hypervisor: The hypervisor type.
            id_code: The identification code.
            enabled: Whether the template is enabled.
            resource_bounds: The resource bounds.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.template_id = template_id
        self.name = name
        self.description = description
        self.hypervisor = hypervisor
        self.id_code = id_code
        self.enabled = enabled
        self.resource_bounds = resource_bounds or ResourceBounds()
        
        # Client reference for operations
        self.client = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """
        Create a template instance from a dictionary.
        
        Args:
            data: A dictionary of template attributes.
            
        Returns:
            A new template instance.
        """
        # Create a dictionary of model attributes
        kwargs = {}
        for field in cls._get_all_fields():
            api_field = cls._field_mappings.get(field, field)
            if api_field in data:
                kwargs[field] = data[api_field]
        
        # Handle resource bounds
        if 'ResourceBounds' in data and data['ResourceBounds']:
            resource_bounds = ResourceBounds()
            for rb in data['ResourceBounds']:
                resource_type = rb.get('ResourceType')
                max_value = rb.get('Max')
                
                if resource_type == 1:
                    resource_bounds.max_cpu = max_value
                elif resource_type == 2:
                    resource_bounds.max_memory = max_value
                elif resource_type == 3:
                    resource_bounds.hdd0 = max_value
                elif resource_type == 7:
                    resource_bounds.hdd1 = max_value
                elif resource_type == 8:
                    resource_bounds.hdd2 = max_value
                elif resource_type == 9:
                    resource_bounds.hdd3 = max_value
            
            kwargs['resource_bounds'] = resource_bounds
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the template to a dictionary.
        
        Returns:
            A dictionary representation of the template.
        """
        result = super().to_dict()
        
        # Handle resource bounds
        if self.resource_bounds:
            resource_bounds = []
            
            if self.resource_bounds.max_cpu is not None:
                resource_bounds.append({
                    'ResourceType': 1,
                    'Max': self.resource_bounds.max_cpu
                })
            
            if self.resource_bounds.max_memory is not None:
                resource_bounds.append({
                    'ResourceType': 2,
                    'Max': self.resource_bounds.max_memory
                })
            
            if self.resource_bounds.hdd0 is not None:
                resource_bounds.append({
                    'ResourceType': 3,
                    'Max': self.resource_bounds.hdd0
                })
            
            if self.resource_bounds.hdd1 is not None:
                resource_bounds.append({
                    'ResourceType': 7,
                    'Max': self.resource_bounds.hdd1
                })
            
            if self.resource_bounds.hdd2 is not None:
                resource_bounds.append({
                    'ResourceType': 8,
                    'Max': self.resource_bounds.hdd2
                })
            
            if self.resource_bounds.hdd3 is not None:
                resource_bounds.append({
                    'ResourceType': 9,
                    'Max': self.resource_bounds.hdd3
                })
            
            if resource_bounds:
                result['ResourceBounds'] = resource_bounds
        
        return result
    
    def is_enabled(self) -> bool:
        """
        Check if the template is enabled.
        
        Returns:
            True if the template is enabled, False otherwise.
        """
        return self.enabled
    
    def is_pro(self) -> bool:
        """
        Check if the template is for a Pro VM.
        
        Returns:
            True if the template is for a Pro VM, False otherwise.
        """
        return self.hypervisor != 'SMART'
    
    def is_smart(self) -> bool:
        """
        Check if the template is for a Smart VM.
        
        Returns:
            True if the template is for a Smart VM, False otherwise.
        """
        return self.hypervisor == 'SMART'