"""
Data models for ArubaCloud resources.

This package contains model classes that represent ArubaCloud resources
such as virtual machines, IP addresses, templates, and VLANs.
"""

from pyarubacloud.models.base import BaseModel
from pyarubacloud.models.vm import VM, ProVM, SmartVM
from pyarubacloud.models.ip import IP
from pyarubacloud.models.template import Template
from pyarubacloud.models.vlan import VLAN

__all__ = [
    'BaseModel',
    'VM',
    'ProVM',
    'SmartVM',
    'IP',
    'Template',
    'VLAN'
]