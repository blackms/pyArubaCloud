# pyArubaCloud

[![PyPI version](https://badge.fury.io/py/pyarubacloud.svg)](https://badge.fury.io/py/pyarubacloud)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyarubacloud.svg)](https://pypi.org/project/pyarubacloud/)
[![License](https://img.shields.io/github/license/Arubacloud/pyArubaCloud.svg)](https://github.com/Arubacloud/pyArubaCloud/blob/master/LICENSE.txt)

Python Interface for ArubaCloud IaaS Service. This library provides a clean and modern interface to interact with the ArubaCloud API.

## Installation

### From PyPI

```bash
pip install pyarubacloud
```

### From Source

```bash
git clone https://github.com/Arubacloud/pyArubaCloud.git
cd pyArubaCloud
pip install -e .
```

## Quick Start

```python
from pyarubacloud import Client

# Initialize the client
client = Client(datacenter=1)  # DC1 = Italy 1
client.auth.login(username="YOUR_USERNAME", password="YOUR_PASSWORD")

# List all VMs
vms = client.compute.vm.list()
for vm in vms:
    print(f"VM: {vm.name}, Status: {vm.status}")

# Create a Pro VM
vm = client.compute.vm.create_pro(
    name="my-vm",
    template_id=1234,
    admin_password="password",
    cpu=2,
    ram=4,
    disks=[20, 40],
    public_ip=True
)

# Power on the VM
vm.power_on()

# Delete the VM
vm.delete()
```

## Datacenter Locations

When initializing the client, you need to specify the datacenter location:

- 1: DC1 - Italy 1
- 2: DC2 - Italy 2
- 3: DC3 - Czech Republic
- 4: DC4 - France
- 5: DC5 - Germany
- 6: DC6 - UK
- 7: DC7 - Italy 3
- 8: DC8 - Poland

```python
from pyarubacloud import Client
from pyarubacloud.constants import DatacenterLocation

# Using the enum
client = Client(datacenter=DatacenterLocation.ITALY_1)

# Or using the integer value
client = Client(datacenter=1)
```

## Features

### Virtual Machines

#### Pro VMs

```python
# Create a Pro VM
vm = client.compute.vm.create_pro(
    name="my-vm",
    template_id=1234,
    admin_password="password",
    cpu=2,
    ram=4,
    disks=[20, 40],
    public_ip=True,
    ssh_key_path="~/.ssh/id_rsa.pub"  # Optional
)

# Edit CPU
client.compute.vm.edit_cpu(vm.id, 4)

# Edit RAM
client.compute.vm.edit_ram(vm.id, 8)

# Add a disk
client.compute.vm.add_disk(vm.id, 100)

# Remove a disk
client.compute.vm.remove_disk(vm.id, 1)  # Disk ID
```

#### Smart VMs

```python
# Create a Smart VM
vm = client.compute.vm.create_smart(
    name="my-vm",
    template_id=1234,
    admin_password="password",
    package="small",  # small, medium, large, extralarge
    ssh_key_path="~/.ssh/id_rsa.pub"  # Optional
)

# Upgrade a Smart VM
client.compute.vm.upgrade(vm.id, "medium")

# Reinitialize a Smart VM
client.compute.vm.reinitialize(vm.id, "new_password", template_id=5678)
```

### IP Addresses

```python
# List all IPs
ips = client.compute.ip.list()

# Purchase a new IP
ip = client.compute.ip.purchase()

# Assign an IP to a VM
client.compute.ip.assign(ip.resource_id, vm.id)

# Unassign an IP
client.compute.ip.unassign(ip.resource_id)

# Release an IP
client.compute.ip.release(ip.resource_id)
```

### Templates

```python
# List all templates
templates = client.compute.template.list()

# Find templates by name
debian_templates = client.compute.template.find_by_name("Debian")

# Find templates by hypervisor
smart_templates = client.compute.template.find_by_hypervisor(4)  # 4 = Smart

# Find enabled templates
enabled_templates = client.compute.template.find_enabled()
```

### VLANs

```python
# List all VLANs
vlans = client.compute.vlan.list()

# Create a VLAN
vlan = client.compute.vlan.create("my-vlan")

# Attach a VLAN to a VM
client.compute.vlan.attach(
    vlan.resource_id,
    vm.id,
    network_adapter_id=1,
    ip="192.168.1.10",
    subnet_mask="255.255.255.0",
    gateway="192.168.1.1"
)

# Detach a VLAN from a VM
client.compute.vlan.detach(vlan.resource_id, vm.id, network_adapter_id=1)

# Delete a VLAN
client.compute.vlan.delete(vlan.resource_id)
```

### Load Balancers

```python
# List all load balancers
load_balancers = client.loadbalancer.list()

# Create a load balancer
lb = client.loadbalancer.create("my-lb")

# Add a rule
rule = client.loadbalancer.add_rule(
    lb.id,
    name="http",
    protocol=1,  # TCP
    port=80,
    balancer_port=80,
    balancer_protocol=1,  # TCP
    instance_port=80,
    instance_protocol=1  # TCP
)

# Power on a load balancer
client.loadbalancer.power_on(lb.id)

# Power off a load balancer
client.loadbalancer.power_off(lb.id)

# Delete a load balancer
client.loadbalancer.delete(lb.id)
```

### Reverse DNS

```python
# Get a reverse DNS entry
rdns = client.reversedns.get("1.2.3.4")

# Set a reverse DNS entry
client.reversedns.set("1.2.3.4", ["example.com"])

# Reset a reverse DNS entry
client.reversedns.reset("1.2.3.4")
```

### Shared Storage

```python
# List all shared storages
storages = client.sharedstorage.list()

# Create a shared storage
storage = client.sharedstorage.create(
    name="my-storage",
    size=100,
    protocol_type=1  # 1 = iSCSI, 2 = NFS
)

# Add an IQN
iqn = client.sharedstorage.add_iqn(
    storage.id,
    "iqn.2005-03.org.open-iscsi:01:11ecf02e86f7"
)

# Delete a shared storage
client.sharedstorage.delete(storage.id)
```

## Advanced Usage

### Caching

The client automatically caches API responses to improve performance. You can clear the cache at any time:

```python
# Clear the entire cache
client.clear_cache()
```

### Logging

You can enable debug logging to see detailed information about API requests and responses:

```python
import logging
from pyarubacloud import Client

# Enable debug logging
client = Client(datacenter=1, config={"debug": True})

# Or configure logging manually
logging.basicConfig(level=logging.DEBUG)
```

### Custom Configuration

You can customize the client configuration:

```python
from pyarubacloud import Client
from pyarubacloud.config import Config

config = Config(
    timeout=120,  # Request timeout in seconds
    cache_ttl=600,  # Cache time-to-live in seconds
    max_retries=5,  # Maximum number of retry attempts
    retry_delay=2.0,  # Initial delay between retries in seconds
    retry_backoff=2.0,  # Backoff multiplier for retries
    debug=True  # Enable debug logging
)

client = Client(datacenter=1, config=config)
```

## Migrating from v0.x

If you're migrating from v0.x of the library, please refer to the [Migration Guide](https://github.com/Arubacloud/pyArubaCloud/blob/master/migration_guide.md) for detailed instructions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.txt](https://github.com/Arubacloud/pyArubaCloud/blob/master/LICENSE.txt) file for details.
