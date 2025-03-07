"""
Template repository implementation for ArubaCloud API.

This module provides the Template repository implementation for the ArubaCloud API,
including methods for listing and finding templates.
"""

from typing import Dict, Any, Optional, List, Union

from pyarubacloud.api.base import BaseRepository, BaseService
from pyarubacloud.constants import HypervisorType
from pyarubacloud.exceptions import ResourceNotFoundError
from pyarubacloud.models.template import Template, ResourceBounds


class TemplateRepository(BaseRepository[Template]):
    """
    Repository for template resources.
    
    This class provides methods for interacting with template resources,
    including listing and finding templates.
    """
    
    def __init__(self, service: BaseService):
        """
        Initialize the template repository.
        
        Args:
            service: The parent service.
        """
        super().__init__(
            service=service,
            model_class=Template,
            resource_name='Template',
            list_method='GetHypervisors'
        )
    
    def list(self, hypervisor_type: Optional[int] = None, **kwargs) -> List[Template]:
        """
        List all templates.
        
        Args:
            hypervisor_type: The hypervisor type.
            **kwargs: Additional parameters for the API call.
            
        Returns:
            A list of template objects.
        """
        response = self.service._call_api(
            method='GetHypervisors',
            data=kwargs,
            cache_key='template_list'
        )
        
        templates = []
        for hypervisor in response.get('Value', []):
            # Skip if hypervisor_type is specified and doesn't match
            if hypervisor_type is not None and hypervisor.get('HypervisorType') != hypervisor_type:
                continue
            
            # Map hypervisor type to string
            hypervisor_map = {
                HypervisorType.HYPER_V: 'HV',
                HypervisorType.VMWARE: 'VW',
                HypervisorType.HYPER_V_LOW_COST: 'LC',
                HypervisorType.SMART: 'SMART'
            }
            
            hypervisor_str = hypervisor_map.get(hypervisor.get('HypervisorType'), 'UNKNOWN')
            
            for template_data in hypervisor.get('Templates', []):
                # Create resource bounds
                resource_bounds = ResourceBounds()
                
                for rb in template_data.get('ResourceBounds', []):
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
                
                # Create template
                template = Template(
                    template_id=template_data.get('Id'),
                    name=template_data.get('Name'),
                    description=template_data.get('Description'),
                    hypervisor=hypervisor_str,
                    id_code=template_data.get('IdentificationCode'),
                    enabled=template_data.get('Enabled'),
                    resource_bounds=resource_bounds
                )
                
                # Set the client reference
                template.client = self.client
                
                templates.append(template)
        
        return templates
    
    def get(self, template_id: Union[str, int]) -> Template:
        """
        Get a template by ID.
        
        Args:
            template_id: The template ID.
            
        Returns:
            The template object.
            
        Raises:
            ResourceNotFoundError: If the template is not found.
        """
        # List all templates and find the one with the matching ID
        templates = self.list()
        for template in templates:
            if template.template_id == str(template_id):
                return template
        
        raise ResourceNotFoundError(f"Template with ID {template_id} not found")
    
    def find_by_name(self, name: str, hypervisor_type: Optional[int] = None) -> List[Template]:
        """
        Find templates by name.
        
        Args:
            name: The template name.
            hypervisor_type: The hypervisor type.
            
        Returns:
            A list of template objects.
        """
        # List all templates and filter by name
        templates = self.list(hypervisor_type=hypervisor_type)
        return [template for template in templates if name.lower() in template.name.lower() or name.lower() in template.description.lower()]
    
    def find_by_hypervisor(self, hypervisor_type: int) -> List[Template]:
        """
        Find templates by hypervisor type.
        
        Args:
            hypervisor_type: The hypervisor type.
            
        Returns:
            A list of template objects.
        """
        return self.list(hypervisor_type=hypervisor_type)
    
    def find_enabled(self, hypervisor_type: Optional[int] = None) -> List[Template]:
        """
        Find enabled templates.
        
        Args:
            hypervisor_type: The hypervisor type.
            
        Returns:
            A list of template objects.
        """
        # List all templates and filter by enabled
        templates = self.list(hypervisor_type=hypervisor_type)
        return [template for template in templates if template.enabled]