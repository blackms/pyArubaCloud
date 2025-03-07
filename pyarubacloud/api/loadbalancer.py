"""
LoadBalancer service for ArubaCloud API.

This module provides a service for interacting with ArubaCloud load balancer resources.
"""

from typing import Dict, Any, Optional, List, Union

from pyarubacloud.api.base import BaseService, BaseRepository
from pyarubacloud.constants import (
    LoadBalancerAlgorithmType,
    LoadBalancerProtocol,
    LoadBalancerStatus,
    NotificationType
)
from pyarubacloud.exceptions import ResourceNotFoundError, ValidationError
from pyarubacloud.models.base import BaseModel


class LoadBalancer(BaseModel):
    """
    Model for a load balancer.
    
    Attributes:
        id (str): The load balancer ID.
        name (str): The name of the load balancer.
        status (int): The status of the load balancer.
        algorithm_type (int): The algorithm type.
        ip_address (str): The IP address.
        created_at (datetime): The creation timestamp.
        updated_at (datetime): The last update timestamp.
    """
    
    _required_fields = {'name'}
    _optional_fields = {'id', 'status', 'algorithm_type', 'ip_address', 'created_at', 'updated_at'}
    _field_types = {
        'id': str,
        'name': str,
        'status': int,
        'algorithm_type': int,
        'ip_address': str
    }
    _field_mappings = {
        'id': 'LoadBalancerID',
        'name': 'Name',
        'status': 'Status',
        'algorithm_type': 'AlgorithmType',
        'ip_address': 'IPAddress',
        'created_at': 'CreationDate',
        'updated_at': 'UpdatedDate'
    }
    
    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        status: Optional[int] = None,
        algorithm_type: Optional[int] = None,
        ip_address: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the load balancer.
        
        Args:
            name: The name of the load balancer.
            id: The load balancer ID.
            status: The status of the load balancer.
            algorithm_type: The algorithm type.
            ip_address: The IP address.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.name = name
        self.id = id
        self.status = status
        self.algorithm_type = algorithm_type
        self.ip_address = ip_address
        
        # Client reference for operations
        self.client = None
    
    def power_on(self) -> bool:
        """
        Power on the load balancer.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.loadbalancer.power_on(self.id)
    
    def power_off(self) -> bool:
        """
        Power off the load balancer.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.loadbalancer.power_off(self.id)
    
    def delete(self) -> bool:
        """
        Delete the load balancer.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.loadbalancer.delete(self.id)
    
    def is_running(self) -> bool:
        """
        Check if the load balancer is running.
        
        Returns:
            True if the load balancer is running, False otherwise.
        """
        return self.status == LoadBalancerStatus.RUNNING
    
    def is_stopped(self) -> bool:
        """
        Check if the load balancer is stopped.
        
        Returns:
            True if the load balancer is stopped, False otherwise.
        """
        return self.status == LoadBalancerStatus.STOPPED
    
    def is_pending(self) -> bool:
        """
        Check if the load balancer is in a pending state.
        
        Returns:
            True if the load balancer is in a pending state, False otherwise.
        """
        return self.status == LoadBalancerStatus.PENDING


class Rule(BaseModel):
    """
    Model for a load balancer rule.
    
    Attributes:
        id (str): The rule ID.
        name (str): The name of the rule.
        protocol (int): The protocol.
        port (int): The port.
        balancer_port (int): The balancer port.
        balancer_protocol (int): The balancer protocol.
        instance_port (int): The instance port.
        instance_protocol (int): The instance protocol.
        load_balancer_id (str): The load balancer ID.
    """
    
    _required_fields = {'name', 'protocol', 'port', 'balancer_port', 'balancer_protocol', 'instance_port', 'instance_protocol'}
    _optional_fields = {'id', 'load_balancer_id'}
    _field_types = {
        'id': str,
        'name': str,
        'protocol': int,
        'port': int,
        'balancer_port': int,
        'balancer_protocol': int,
        'instance_port': int,
        'instance_protocol': int,
        'load_balancer_id': str
    }
    _field_mappings = {
        'id': 'RuleID',
        'name': 'Name',
        'protocol': 'Protocol',
        'port': 'Port',
        'balancer_port': 'BalancerPort',
        'balancer_protocol': 'BalancerProtocol',
        'instance_port': 'InstancePort',
        'instance_protocol': 'InstanceProtocol',
        'load_balancer_id': 'LoadBalancerID'
    }
    
    def __init__(
        self,
        name: str,
        protocol: int,
        port: int,
        balancer_port: int,
        balancer_protocol: int,
        instance_port: int,
        instance_protocol: int,
        id: Optional[str] = None,
        load_balancer_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the rule.
        
        Args:
            name: The name of the rule.
            protocol: The protocol.
            port: The port.
            balancer_port: The balancer port.
            balancer_protocol: The balancer protocol.
            instance_port: The instance port.
            instance_protocol: The instance protocol.
            id: The rule ID.
            load_balancer_id: The load balancer ID.
            **kwargs: Additional attributes.
        """
        super().__init__(**kwargs)
        self.name = name
        self.protocol = protocol
        self.port = port
        self.balancer_port = balancer_port
        self.balancer_protocol = balancer_protocol
        self.instance_port = instance_port
        self.instance_protocol = instance_protocol
        self.id = id
        self.load_balancer_id = load_balancer_id
        
        # Client reference for operations
        self.client = None
    
    def delete(self) -> bool:
        """
        Delete the rule.
        
        Returns:
            True if successful, False otherwise.
            
        Raises:
            ValueError: If the client is not set.
        """
        if not self.client:
            raise ValueError("Client not set")
        
        return self.client.loadbalancer.delete_rule(self.id)


class LoadBalancerRepository(BaseRepository[LoadBalancer]):
    """
    Repository for load balancer resources.
    
    This class provides methods for interacting with load balancer resources,
    including listing, getting, creating, and deleting load balancers.
    """
    
    def __init__(self, service: BaseService):
        """
        Initialize the load balancer repository.
        
        Args:
            service: The parent service.
        """
        super().__init__(
            service=service,
            model_class=LoadBalancer,
            resource_name='LoadBalancer',
            list_method='GetLoadBalancers',
            delete_method='SetEnqueueLoadBalancerDeletion'
        )
    
    def list(self, **kwargs) -> List[LoadBalancer]:
        """
        List all load balancers.
        
        Args:
            **kwargs: Additional parameters for the API call.
            
        Returns:
            A list of load balancer objects.
        """
        response = self.service._call_api(
            method='GetLoadBalancers',
            data=kwargs,
            cache_key='loadbalancer_list'
        )
        
        load_balancers = []
        for item in response.get('Value', []):
            load_balancer = LoadBalancer(
                id=item.get('LoadBalancerID'),
                name=item.get('Name'),
                status=item.get('Status'),
                algorithm_type=item.get('AlgorithmType'),
                ip_address=item.get('IPAddress')
            )
            
            # Set the client reference
            load_balancer.client = self.client
            
            load_balancers.append(load_balancer)
        
        return load_balancers
    
    def get(self, load_balancer_id: Union[str, int]) -> LoadBalancer:
        """
        Get a load balancer by ID.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            The load balancer object.
            
        Raises:
            ResourceNotFoundError: If the load balancer is not found.
        """
        # List all load balancers and find the one with the matching ID
        load_balancers = self.list()
        for load_balancer in load_balancers:
            if load_balancer.id == str(load_balancer_id):
                return load_balancer
        
        raise ResourceNotFoundError(f"Load balancer with ID {load_balancer_id} not found")
    
    def get_by_name(self, name: str) -> LoadBalancer:
        """
        Get a load balancer by name.
        
        Args:
            name: The load balancer name.
            
        Returns:
            The load balancer object.
            
        Raises:
            ResourceNotFoundError: If the load balancer is not found.
        """
        # List all load balancers and find the one with the matching name
        load_balancers = self.list()
        for load_balancer in load_balancers:
            if load_balancer.name == name:
                return load_balancer
        
        raise ResourceNotFoundError(f"Load balancer with name {name} not found")
    
    def create(
        self,
        name: str,
        algorithm_type: Union[int, LoadBalancerAlgorithmType] = LoadBalancerAlgorithmType.ROUND_ROBIN
    ) -> LoadBalancer:
        """
        Create a new load balancer.
        
        Args:
            name: The load balancer name.
            algorithm_type: The algorithm type.
            
        Returns:
            The created load balancer object.
        """
        # Validate input
        if not name:
            raise ValidationError("Name is required")
        
        response = self.service._call_api(
            method='SetEnqueueLoadBalancerCreation',
            data={
                'LoadBalancerCreation': {
                    'Name': name,
                    'AlgorithmType': algorithm_type
                }
            }
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('loadbalancer_list')
        
        if not response.get('Success', False) or 'Value' not in response:
            raise Exception("Failed to create load balancer")
        
        load_balancer = LoadBalancer(
            id=response['Value'].get('LoadBalancerID'),
            name=name,
            status=LoadBalancerStatus.PENDING,
            algorithm_type=algorithm_type
        )
        
        # Set the client reference
        load_balancer.client = self.client
        
        return load_balancer
    
    def delete(self, load_balancer_id: Union[str, int]) -> bool:
        """
        Delete a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            True if successful, False otherwise.
        """
        response = self.service._call_api(
            method='SetEnqueueLoadBalancerDeletion',
            data={'LoadBalancerID': load_balancer_id}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('loadbalancer_list')
        
        return response.get('Success', False)
    
    def power_on(self, load_balancer_id: Union[str, int]) -> bool:
        """
        Power on a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            True if successful, False otherwise.
        """
        response = self.service._call_api(
            method='SetEnqueueLoadBalancerStart',
            data={'LoadBalancerID': load_balancer_id}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('loadbalancer_list')
        
        return response.get('Success', False)
    
    def power_off(self, load_balancer_id: Union[str, int]) -> bool:
        """
        Power off a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            True if successful, False otherwise.
        """
        response = self.service._call_api(
            method='SetEnqueueLoadBalancerPowerOff',
            data={'LoadBalancerID': load_balancer_id}
        )
        
        # Invalidate the cache
        self.cache.invalidate_pattern('loadbalancer_list')
        
        return response.get('Success', False)
    
    def add_rule(
        self,
        load_balancer_id: Union[str, int],
        name: str,
        protocol: Union[int, LoadBalancerProtocol],
        port: int,
        balancer_port: int,
        balancer_protocol: Union[int, LoadBalancerProtocol],
        instance_port: int,
        instance_protocol: Union[int, LoadBalancerProtocol]
    ) -> Rule:
        """
        Add a rule to a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            name: The rule name.
            protocol: The protocol.
            port: The port.
            balancer_port: The balancer port.
            balancer_protocol: The balancer protocol.
            instance_port: The instance port.
            instance_protocol: The instance protocol.
            
        Returns:
            The created rule object.
        """
        # Validate input
        if not name:
            raise ValidationError("Name is required")
        
        if port <= 0 or port > 65535:
            raise ValidationError("Port must be between 1 and 65535")
        
        if balancer_port <= 0 or balancer_port > 65535:
            raise ValidationError("Balancer port must be between 1 and 65535")
        
        if instance_port <= 0 or instance_port > 65535:
            raise ValidationError("Instance port must be between 1 and 65535")
        
        response = self.service._call_api(
            method='SetAddLoadBalancerRule',
            data={
                'NewLoadBalancerRule': {
                    'LoadBalancerID': load_balancer_id,
                    'Name': name,
                    'Protocol': protocol,
                    'Port': port,
                    'BalancerPort': balancer_port,
                    'BalancerProtocol': balancer_protocol,
                    'InstancePort': instance_port,
                    'InstanceProtocol': instance_protocol
                }
            }
        )
        
        if not response.get('Success', False) or 'Value' not in response:
            raise Exception("Failed to add rule to load balancer")
        
        rule = Rule(
            id=response['Value'].get('RuleID'),
            name=name,
            protocol=protocol,
            port=port,
            balancer_port=balancer_port,
            balancer_protocol=balancer_protocol,
            instance_port=instance_port,
            instance_protocol=instance_protocol,
            load_balancer_id=load_balancer_id
        )
        
        # Set the client reference
        rule.client = self.client
        
        return rule
    
    def delete_rule(self, rule_id: Union[str, int]) -> bool:
        """
        Delete a rule.
        
        Args:
            rule_id: The rule ID.
            
        Returns:
            True if successful, False otherwise.
        """
        response = self.service._call_api(
            method='SetRemoveLoadBalancerRule',
            data={'RuleID': rule_id}
        )
        
        return response.get('Success', False)
    
    def get_rules(self, load_balancer_id: Union[str, int]) -> List[Rule]:
        """
        Get all rules for a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            A list of rule objects.
        """
        response = self.service._call_api(
            method='GetLoadBalancerRules',
            data={'LoadBalancerID': load_balancer_id},
            cache_key=f'loadbalancer_{load_balancer_id}_rules'
        )
        
        rules = []
        for item in response.get('Value', []):
            rule = Rule(
                id=item.get('RuleID'),
                name=item.get('Name'),
                protocol=item.get('Protocol'),
                port=item.get('Port'),
                balancer_port=item.get('BalancerPort'),
                balancer_protocol=item.get('BalancerProtocol'),
                instance_port=item.get('InstancePort'),
                instance_protocol=item.get('InstanceProtocol'),
                load_balancer_id=load_balancer_id
            )
            
            # Set the client reference
            rule.client = self.client
            
            rules.append(rule)
        
        return rules


class LoadBalancerService(BaseService):
    """
    Service for interacting with ArubaCloud load balancer resources.
    
    This class provides access to repositories for load balancers.
    
    Attributes:
        loadbalancer (LoadBalancerRepository): The load balancer repository.
    """
    
    def __init__(self, client):
        """
        Initialize the load balancer service.
        
        Args:
            client: The ArubaCloud client.
        """
        super().__init__(client)
        self.loadbalancer = LoadBalancerRepository(self)
    
    def list(self, **kwargs) -> List[LoadBalancer]:
        """
        List all load balancers.
        
        Args:
            **kwargs: Additional parameters for the API call.
            
        Returns:
            A list of load balancer objects.
        """
        return self.loadbalancer.list(**kwargs)
    
    def get(self, load_balancer_id: Union[str, int]) -> LoadBalancer:
        """
        Get a load balancer by ID.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            The load balancer object.
        """
        return self.loadbalancer.get(load_balancer_id)
    
    def create(
        self,
        name: str,
        algorithm_type: Union[int, LoadBalancerAlgorithmType] = LoadBalancerAlgorithmType.ROUND_ROBIN
    ) -> LoadBalancer:
        """
        Create a new load balancer.
        
        Args:
            name: The load balancer name.
            algorithm_type: The algorithm type.
            
        Returns:
            The created load balancer object.
        """
        return self.loadbalancer.create(name, algorithm_type)
    
    def delete(self, load_balancer_id: Union[str, int]) -> bool:
        """
        Delete a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.loadbalancer.delete(load_balancer_id)
    
    def power_on(self, load_balancer_id: Union[str, int]) -> bool:
        """
        Power on a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.loadbalancer.power_on(load_balancer_id)
    
    def power_off(self, load_balancer_id: Union[str, int]) -> bool:
        """
        Power off a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.loadbalancer.power_off(load_balancer_id)
    
    def add_rule(
        self,
        load_balancer_id: Union[str, int],
        name: str,
        protocol: Union[int, LoadBalancerProtocol],
        port: int,
        balancer_port: int,
        balancer_protocol: Union[int, LoadBalancerProtocol],
        instance_port: int,
        instance_protocol: Union[int, LoadBalancerProtocol]
    ) -> Rule:
        """
        Add a rule to a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            name: The rule name.
            protocol: The protocol.
            port: The port.
            balancer_port: The balancer port.
            balancer_protocol: The balancer protocol.
            instance_port: The instance port.
            instance_protocol: The instance protocol.
            
        Returns:
            The created rule object.
        """
        return self.loadbalancer.add_rule(
            load_balancer_id,
            name,
            protocol,
            port,
            balancer_port,
            balancer_protocol,
            instance_port,
            instance_protocol
        )
    
    def delete_rule(self, rule_id: Union[str, int]) -> bool:
        """
        Delete a rule.
        
        Args:
            rule_id: The rule ID.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.loadbalancer.delete_rule(rule_id)
    
    def get_rules(self, load_balancer_id: Union[str, int]) -> List[Rule]:
        """
        Get all rules for a load balancer.
        
        Args:
            load_balancer_id: The load balancer ID.
            
        Returns:
            A list of rule objects.
        """
        return self.loadbalancer.get_rules(load_balancer_id)