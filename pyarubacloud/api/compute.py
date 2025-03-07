"""
Compute service for ArubaCloud API.

This module provides a service for interacting with ArubaCloud compute resources,
including virtual machines, IP addresses, templates, and VLANs.
"""

from typing import Dict, Any, Optional, List, Union, Type

from pyarubacloud.api.base import BaseService
from pyarubacloud.api.compute_vm import VMRepositoryExtensions
from pyarubacloud.api.compute_ip import IPRepository
from pyarubacloud.api.compute_template import TemplateRepository
from pyarubacloud.api.compute_vlan import VLANRepository
from pyarubacloud.models.vm import VM


class VMRepository(VMRepositoryExtensions):
    """
    Repository for VM resources.
    
    This class provides methods for interacting with VM resources,
    including listing, getting, creating, and deleting VMs.
    """
    
    def __init__(self, service: BaseService):
        """
        Initialize the VM repository.
        
        Args:
            service: The parent service.
        """
        super().__init__(
            service=service,
            model_class=VM,
            resource_name='Server',
            list_method='GetServers',
            get_method='GetServerDetails',
            delete_method='SetEnqueueServerDeletion'
        )


class ComputeService(BaseService):
    """
    Service for interacting with ArubaCloud compute resources.
    
    This class provides access to repositories for VMs, IPs, templates, and VLANs.
    
    Attributes:
        vm (VMRepository): The VM repository.
        ip (IPRepository): The IP repository.
        template (TemplateRepository): The template repository.
        vlan (VLANRepository): The VLAN repository.
    """
    
    def __init__(self, client):
        """
        Initialize the compute service.
        
        Args:
            client: The ArubaCloud client.
        """
        super().__init__(client)
        self.vm = VMRepository(self)
        self.ip = IPRepository(self)
        self.template = TemplateRepository(self)
        self.vlan = VLANRepository(self)
