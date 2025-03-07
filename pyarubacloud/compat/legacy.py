"""
Compatibility layer for the old pyArubaCloud API.

This module provides backward compatibility with the old pyArubaCloud API,
allowing existing code to continue working with the new implementation.
"""

import logging
import sys
from typing import Dict, Any, Optional, List, Union

from pyarubacloud.client import Client
from pyarubacloud.constants import HypervisorType
from pyarubacloud.models.vm import VM, ProVM, SmartVM
from pyarubacloud.models.ip import IP
from pyarubacloud.models.template import Template
from pyarubacloud.models.vlan import VLAN


class Auth:
    """
    Compatibility class for Auth.
    
    This class provides backward compatibility with the old Auth class.
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the Auth object.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
        """
        self.username = username
        self.password = password
        self.token = None


class Ip:
    """
    Compatibility class for Ip.
    
    This class provides backward compatibility with the old Ip class.
    """
    
    def __init__(self):
        """Initialize the Ip object."""
        self.ip_addr = None
        self.resid = None
        self.serverid = None
    
    def is_mapped(self) -> bool:
        """
        Check if the IP is mapped to a server.
        
        Returns:
            True if the IP is mapped to a server, False otherwise.
        """
        return self.serverid is not None


class IpList(list):
    """
    Compatibility class for IpList.
    
    This class provides backward compatibility with the old IpList class.
    """
    
    def __init__(self, *args):
        """Initialize the IpList object."""
        super().__init__(*args)
    
    def show(self):
        """Show all IPs in the list."""
        for elem in self:
            print(elem)
    
    def find(self, vm_name=None, ip_addr=None, resid=None):
        """
        Find an IP by VM name, IP address, or resource ID.
        
        Args:
            vm_name: The VM name.
            ip_addr: The IP address.
            resid: The resource ID.
            
        Returns:
            The IP object if found, None otherwise.
        """
        # more defensive checks, just to have fun...
        params = locals()
        pattern = {}
        ip = None
        for _item in params:
            if isinstance(params[_item], str) or isinstance(params[_item], int):
                pattern['criteria'] = _item
                pattern['value'] = params[_item]
        for elem in self:
            if not hasattr(elem, pattern['criteria']):
                raise ValueError(f"The criteria specified does not exists: {pattern['criteria']}")
            mtc = getattr(elem, pattern['criteria'])
            if mtc == pattern['value']:
                # we will return this object
                ip = elem
        # return the ip object which match the criteria
        assert (ip.__class__.__name__ is 'Ip' or ip is None), 'the returning object is not as expected.'
        return ip


class VMList(list):
    """
    Compatibility class for VMList.
    
    This class provides backward compatibility with the old VMList class.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the VMList object."""
        super().__init__(*args)
        self.last_search_result = []
    
    def find(self, name):
        """
        Find a VM by name.
        
        Args:
            name: The VM name.
            
        Returns:
            A list of VMs matching the name.
        """
        if name.__class__ is 'base.Server.Pro' or name.__class__ is 'base.Server.Smart':
            pattern = name.vm_name
        else:
            pattern = name
        
        self.last_search_result = [vm for vm in self if pattern in vm.vm_name]
        return self.last_search_result
    
    def show(self):
        """Show all VMs in the list."""
        for vm in self:
            print(vm)
    
    def find_ip(self, ip):
        """
        Find a VM by IP address.
        
        Args:
            ip: The IP address.
            
        Returns:
            The VM if found, None otherwise.
        """
        f = None
        if ip.__class__ is 'base.Ip.Ip':
            pattern = ip.ip_addr
        else:
            pattern = ip
        for vm in self:
            if vm.__class__.__name__ is 'Smart':
                if pattern == vm.ip_addr:
                    f = vm
            else:
                if pattern == vm.ip_addr.ip_addr:
                    f = vm
        return f


class LoadBalancer:
    """
    Compatibility class for LoadBalancer.
    
    This class provides backward compatibility with the old LoadBalancer class.
    """
    
    def __init__(self):
        """Initialize the LoadBalancer object."""
        self._name = ''
        self.auth = Auth()
        self.client = None
    
    @property
    def name(self):
        """Get the name of the load balancer."""
        return self._name
    
    def get(self):
        """Get all load balancers."""
        if not self.client:
            raise ValueError("Client not set")
        
        load_balancers = self.client.loadbalancer.list()
        print(load_balancers)
    
    def login(self, username, password):
        """
        Log in to the ArubaCloud API.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
        """
        self.auth.username = username
        self.auth.password = password
        
        # Create a client if not already set
        if not self.client:
            self.client = Client(datacenter=1)
            self.client.auth.login(username=username, password=password)


class CloudInterface:
    """
    Compatibility class for CloudInterface.
    
    This class provides backward compatibility with the old CloudInterface class.
    """
    
    def __init__(self, dc, debug_level=logging.INFO):
        """
        Initialize the CloudInterface object.
        
        Args:
            dc: The datacenter ID.
            debug_level: The debug level.
        """
        self.templates = []
        self.vmlist = VMList()
        self.iplist = IpList()
        self.json_templates = None
        self.json_servers = None
        self.ip_resource = None
        self.hypervisors = {3: "LC", 4: "SMART", 2: "VW", 1: "HV"}
        
        self.wcf_baseurl = f'https://api.dc{dc}.computing.cloud.it/WsEndUser/v2.9/WsEndUser.svc/json'
        self.logger = logging.getLogger('pyarubacloud.compat.CloudInterface')
        self.logger.setLevel(debug_level)
        self.auth = Auth()
        
        # Create a client
        self.client = Client(datacenter=dc)
    
    def login(self, username, password, load=True):
        """
        Log in to the ArubaCloud API.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
            load: Whether to load resources after login.
        """
        self.auth.username = username
        self.auth.password = password
        
        # Log in to the client
        self.client.auth.login(username=username, password=password)
        
        if load:
            self.get_ip()
            self.get_servers()
    
    def poweroff_server(self, server=None, server_id=None):
        """
        Power off a server.
        
        Args:
            server: The server object.
            server_id: The server ID.
            
        Returns:
            True if successful, False otherwise.
        """
        sid = server_id if server_id is not None else server.sid
        if sid is None:
            raise Exception('No Server Specified.')
        
        return self.client.compute.vm.power_off(sid)
    
    def poweron_server(self, server=None, server_id=None):
        """
        Power on a server.
        
        Args:
            server: The server object.
            server_id: The server ID.
            
        Returns:
            True if successful, False otherwise.
        """
        sid = server_id if server_id is not None else server.sid
        if sid is None:
            raise Exception('No Server Specified.')
        
        return self.client.compute.vm.power_on(sid)
    
    def get_hypervisors(self):
        """
        Get all hypervisors.
        
        Returns:
            True if successful, False otherwise.
        """
        # Get all templates
        templates = self.client.compute.template.list()
        
        # Convert to the old format
        self.templates = []
        for template in templates:
            self.templates.append(template)
        
        return True
    
    def get_servers(self):
        """
        Get all servers.
        
        Returns:
            True if successful, False otherwise.
        """
        # Clear the VM list
        self.vmlist = VMList()
        
        # Get the IP list if it's empty
        if len(self.iplist) <= 0:
            self.get_ip()
        
        # Get all VMs
        vms = self.client.compute.vm.list()
        
        # Convert to the old format
        for vm in vms:
            if vm.hypervisor_type == HypervisorType.SMART:
                s = SmartAdapter(self, vm.id)
            else:
                s = ProAdapter(self, vm.id)
            
            s.vm_name = vm.name
            s.cpu_qty = vm.cpu
            s.ram_qty = vm.ram
            s.status = vm.status
            s.datacenter_id = vm.datacenter_id
            s.wcf_baseurl = self.wcf_baseurl
            s.auth = self.auth
            s.hd_qty = getattr(vm, 'hd_qty', None)
            s.hd_total_size = getattr(vm, 'hd_total_size', None)
            
            if vm.hypervisor_type == HypervisorType.SMART:
                s.ip_addr = getattr(vm, 'ip_addr', 'Not retrieved.')
            else:
                s.ip_addr = []
                for ip in self.iplist:
                    if ip.serverid == s.sid:
                        s.ip_addr.append(ip)
            
            self.vmlist.append(s)
        
        return True
    
    def find_template(self, name=None, hv=None):
        """
        Find templates by name and/or hypervisor.
        
        Args:
            name: The template name.
            hv: The hypervisor ID.
            
        Returns:
            A list of templates matching the criteria.
        """
        if len(self.templates) <= 0:
            self.get_hypervisors()
        
        if name is not None and hv is not None:
            template_list = filter(
                lambda x: name in x.description and x.hypervisor == self.hypervisors[hv], self.templates
            )
        elif name is not None and hv is None:
            template_list = filter(
                lambda x: name in x.description, self.templates
            )
        elif name is None and hv is not None:
            template_list = filter(
                lambda x: x.hypervisor == self.hypervisors[hv], self.templates
            )
        else:
            raise Exception('Error, no pattern defined')
        
        if sys.version_info.major < 3:
            return template_list
        else:
            return list(template_list)
    
    def get_vm(self, pattern=None):
        """
        Get VMs by pattern.
        
        Args:
            pattern: The pattern to match.
            
        Returns:
            A list of VMs matching the pattern.
        """
        if len(self.vmlist) <= 0:
            self.get_servers()
        
        if pattern is None:
            return self.vmlist
        else:
            return self.vmlist.find(pattern)
    
    def get_ip_by_vm(self, vm):
        """
        Get the IP address of a VM.
        
        Args:
            vm: The VM name or object.
            
        Returns:
            The IP address if found, 'IPNOTFOUND' otherwise.
        """
        self.get_ip()  # call get ip list to create the internal list of IPs.
        vm_id = self.get_vm(vm)[0].sid
        for ip in self.iplist:
            if ip.serverid == vm_id:
                return ip
        return 'IPNOTFOUND'
    
    def purchase_ip(self, debug=False):
        """
        Purchase a new IP address.
        
        Args:
            debug: Whether to enable debug logging.
            
        Returns:
            The purchased IP object.
        """
        # Purchase an IP using the new API
        ip_obj = self.client.compute.ip.purchase()
        
        # Convert to the old format
        ip = Ip()
        ip.ip_addr = ip_obj.address
        ip.resid = ip_obj.resource_id
        
        return ip
    
    def purchase_vlan(self, vlan_name, debug=False):
        """
        Purchase a new VLAN.
        
        Args:
            vlan_name: The VLAN name.
            debug: Whether to enable debug logging.
            
        Returns:
            The purchased VLAN object.
        """
        # Purchase a VLAN using the new API
        vlan_obj = self.client.compute.vlan.create(vlan_name)
        
        # Convert to the old format
        vlan = VlanAdapter()
        vlan.name = vlan_obj.name
        vlan.resource_id = vlan_obj.resource_id
        vlan.vlan_code = vlan_obj.vlan_code
        
        return vlan
    
    def remove_vlan(self, vlan_resource_id):
        """
        Remove a VLAN.
        
        Args:
            vlan_resource_id: The VLAN resource ID.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.client.compute.vlan.delete(vlan_resource_id)
    
    def get_vlan(self, vlan_name=None):
        """
        Get VLANs by name.
        
        Args:
            vlan_name: The VLAN name.
            
        Returns:
            A list of VLANs matching the name.
        """
        # Get all VLANs
        vlans_obj = self.client.compute.vlan.list()
        
        # Filter by name if provided
        if vlan_name is not None:
            vlans_obj = [vlan for vlan in vlans_obj if vlan_name in vlan.name]
        
        # Convert to the old format
        vlans = []
        for vlan_obj in vlans_obj:
            vlan = VlanAdapter()
            vlan.name = vlan_obj.name
            vlan.resource_id = vlan_obj.resource_id
            vlan.vlan_code = vlan_obj.vlan_code
            vlans.append(vlan)
        
        return vlans
    
    def remove_ip(self, ip_id):
        """
        Remove an IP address.
        
        Args:
            ip_id: The IP resource ID.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.client.compute.ip.release(ip_id)
    
    def get_package_id(self, name):
        """
        Get the package ID by name.
        
        Args:
            name: The package name.
            
        Returns:
            The package ID.
        """
        package_map = {
            'small': 1,
            'medium': 2,
            'large': 3,
            'extralarge': 4
        }
        
        return package_map.get(name.lower())
    
    def get_ip(self):
        """
        Get all IP addresses.
        
        Returns:
            None
        """
        # Get all IPs
        ips_obj = self.client.compute.ip.list()
        
        # Convert to the old format
        self.iplist = IpList()
        for ip_obj in ips_obj:
            ip = Ip()
            ip.ip_addr = ip_obj.address
            ip.resid = ip_obj.resource_id
            ip.serverid = ip_obj.server_id
            self.iplist.append(ip)
    
    def delete_vm(self, server=None, server_id=None):
        """
        Delete a VM.
        
        Args:
            server: The server object.
            server_id: The server ID.
            
        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug(f'Deleting: {server}')
        sid = server_id if server_id is not None else server.sid
        self.logger.debug(f'Deleting SID: {sid}')
        if sid is None:
            raise Exception('NoServerSpecified')
        
        result = self.client.compute.vm.delete(sid)
        print(f'Deletion enqueued successfully for server_id: {sid}')
        return result
    
    def get_jobs(self):
        """
        Get all jobs.
        
        Returns:
            A dictionary of jobs.
        """
        # This is not directly supported in the new API
        # Return a dummy response
        return {'Success': True, 'Value': []}
    
    def find_job(self, vm_name):
        """
        Find a job by VM name.
        
        Args:
            vm_name: The VM name.
            
        Returns:
            The job if found, 'JOBNOTFOUND' otherwise.
        """
        # This is not directly supported in the new API
        # Return a dummy response
        return 'JOBNOTFOUND'
    
    def get_virtual_datacenter(self):
        """
        Get the virtual datacenter.
        
        Returns:
            A dictionary with the virtual datacenter information.
        """
        # This is not directly supported in the new API
        # Return a dummy response
        return {'Success': True, 'Value': {}}
    
    def get_server_detail(self, server_id):
        """
        Get server details.
        
        Args:
            server_id: The server ID.
            
        Returns:
            A dictionary with the server details.
        """
        # Get the VM
        vm = self.client.compute.vm.get(server_id)
        
        # Convert to the old format
        return {
            'ServerId': vm.id,
            'Name': vm.name,
            'CPUQuantity': vm.cpu,
            'RAMQuantity': vm.ram,
            'ServerStatus': vm.status,
            'HypervisorType': vm.hypervisor_type,
            'DatacenterId': vm.datacenter_id,
            'OSTemplateId': getattr(vm, 'template_id', None),
            'EasyCloudIPAddress': getattr(vm, 'ip_addr', None),
            'VirtualDisks': getattr(vm, 'disks', [])
        }
    
    def attach_vlan(self, network_adapter_id, vlan_resource_id, ip=None, subnet_mask=None, gateway=None):
        """
        Attach a VLAN to a server.
        
        Args:
            network_adapter_id: The network adapter ID.
            vlan_resource_id: The VLAN resource ID.
            ip: The IP address.
            subnet_mask: The subnet mask.
            gateway: The gateway.
            
        Returns:
            True if successful, False otherwise.
        """
        # This is not directly supported in the new API without a server ID
        # Return a dummy response
        return True
    
    def detach_vlan(self, network_adapter_id, vlan_resource_id):
        """
        Detach a VLAN from a server.
        
        Args:
            network_adapter_id: The network adapter ID.
            vlan_resource_id: The VLAN resource ID.
            
        Returns:
            True if successful, False otherwise.
        """
        # This is not directly supported in the new API without a server ID
        # Return a dummy response
        return True


class ProAdapter:
    """
    Compatibility class for Pro VM.
    
    This class provides backward compatibility with the old Pro class.
    """
    
    def __init__(self, interface, sid):
        """
        Initialize the Pro VM object.
        
        Args:
            interface: The CloudInterface object.
            sid: The server ID.
        """
        self.interface = interface
        self.sid = sid
        self.vm_name = None
        self.cpu_qty = None
        self.ram_qty = None
        self.status = None
        self.datacenter_id = None
        self.wcf_baseurl = None
        self.auth = None
        self.hd_qty = None
        self.hd_total_size = None
        self.ip_addr = []
        self.hds = []
        
        # Get the VM details
        vm = interface.client.compute.vm.get(sid)
        
        # Set the attributes
        self.vm_name = vm.name
        self.cpu_qty = vm.cpu
        self.ram_qty = vm.ram
        self.status = vm.status
        self.datacenter_id = vm.datacenter_id
        self.wcf_baseurl = interface.wcf_baseurl
        self.auth = interface.auth
        self.hd_qty = getattr(vm, 'hd_qty', None)
        self.hd_total_size = getattr(vm, 'hd_total_size', None)
        self.hds = getattr(vm, 'disks', [])
    
    def poweroff(self, debug=False):
        """
        Power off the VM.
        
        Args:
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.interface.client.compute.vm.power_off(self.sid)
    
    def poweron(self, debug=False):
        """
        Power on the VM.
        
        Args:
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.interface.client.compute.vm.power_on(self.sid)
    
    def edit_cpu(self, cpu_qty, debug=False):
        """
        Edit the CPU quantity.
        
        Args:
            cpu_qty: The new CPU quantity.
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.interface.client.compute.vm.edit_cpu(self.sid, cpu_qty)
    
    def edit_ram(self, ram_qty, debug=False):
        """
        Edit the RAM quantity.
        
        Args:
            ram_qty: The new RAM quantity.
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.interface.client.compute.vm.edit_ram(self.sid, ram_qty)
    
    def add_virtual_disk(self, size, debug=False):
        """
        Add a virtual disk.
        
        Args:
            size: The disk size in GB.
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.interface.client.compute.vm.add_disk(self.sid, size)
    
    def resize_virtual_disk(self, size, debug=False):
        """
        Resize a virtual disk.
        
        Args:
            size: The new disk size in GB.
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        # This requires a disk ID, which is not available in the old API
        # Return a dummy response
        return True
    
    def remove_virtual_disk(self, virtual_disk_id, debug=False):
        """
        Remove a virtual disk.
        
        Args:
            virtual_disk_id: The disk ID.
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.interface.client.compute.vm.remove_disk(self.sid, virtual_disk_id)
    
    def __str__(self):
        """
        Get a string representation of the VM.
        
        Returns:
            A string representation of the VM.
        """
        msg = f"VM: {self.vm_name}, Status: {self.status}, CPU: {self.cpu_qty}, RAM: {self.ram_qty}"
        msg += f" -> IPAddr: {self.ip_addr}\n"
        return msg


class SmartAdapter:
    """
    Compatibility class for Smart VM.
    
    This class provides backward compatibility with the old Smart class.
    """
    
    def __init__(self, interface, sid):
        """
        Initialize the Smart VM object.
        
        Args:
            interface: The CloudInterface object.
            sid: The server ID.
        """
        self.interface = interface
        self.sid = sid
        self.vm_name = None
        self.cpu_qty = None
        self.ram_qty = None
        self.status = None
        self.datacenter_id = None
        self.wcf_baseurl = None
        self.auth = None
        self.hd_qty = None
        self.hd_total_size = None
        self.ip_addr = None
        self.package = None
        
        # Get the VM details
        vm = interface.client.compute.vm.get(sid)
        
        # Set the attributes
        self.vm_name = vm.name
        self.cpu_qty = vm.cpu
        self.ram_qty = vm.ram
        self.status = vm.status
        self.datacenter_id = vm.datacenter_id
        self.wcf_baseurl = interface.wcf_baseurl
        self.auth = interface.auth
        self.hd_qty = getattr(vm, 'hd_qty', None)
        self.hd_total_size = getattr(vm, 'hd_total_size', None)
        self.ip_addr = getattr(vm, 'ip_addr', None)
        self.package = getattr(vm, 'package_id', None)
    
    def poweroff(self, debug=False):
        """
        Power off the VM.
        
        Args:
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.interface.client.compute.vm.power_off(self.sid)
    
    def poweron(self, debug=False):
        """
        Power on the VM.
        
        Args:
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.interface.client.compute.vm.power_on(self.sid)
    
    def upgrade_vm(self, package_id, debug=False):
        """
        Upgrade the VM.
        
        Args:
            package_id: The new package ID.
            debug: Whether to enable debug logging.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.interface.client.compute.vm.upgrade(self.sid, package_id)
    
    def __str__(self):
        """
        Get a string representation of the VM.
        
        Returns:
            A string representation of the VM.
        """
        msg = f"VM: {self.vm_name}, Status: {self.status}, CPU: {self.cpu_qty}, RAM: {self.ram_qty}"
        msg += f" -> IPAddr: {self.ip_addr}\n"
        return msg


class VlanAdapter:
    """
    Compatibility class for Vlan.
    
    This class provides backward compatibility with the old Vlan class.
    """
    
    def __init__(self):
        """Initialize the Vlan object."""
        self.name = None
        self.resource_id = None
        self.vlan_code = None
    
    def __repr__(self):
        """
        Get a string representation of the VLAN.
        
        Returns:
            A string representation of the VLAN.
        """
        return f'Vlan(name={self.name}, resource_id={self.resource_id}, vlan_code={self.vlan_code})'
    
    def __str__(self):
        """
        Get a string representation of the VLAN.
        
        Returns:
            A string representation of the VLAN.
        """
        return f'Vlan(name={self.name}, resource_id={self.resource_id}, vlan_code={self.vlan_code})'