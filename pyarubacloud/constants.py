"""
Constants and enumerations for the pyArubaCloud library.

This module defines constants and enumerations used throughout the library,
providing a centralized location for configuration values and magic numbers.
"""

from enum import Enum, IntEnum


class DatacenterLocation(IntEnum):
    """Enumeration of ArubaCloud datacenter locations."""
    
    ITALY_1 = 1
    ITALY_2 = 2
    CZECH_REPUBLIC = 3
    FRANCE = 4
    GERMANY = 5
    UK = 6
    ITALY_3 = 7
    POLAND = 8


class HypervisorType(IntEnum):
    """Enumeration of ArubaCloud hypervisor types."""
    
    HYPER_V = 1
    VMWARE = 2
    HYPER_V_LOW_COST = 3
    SMART = 4


class ServerStatus(IntEnum):
    """Enumeration of server status values."""
    
    STOPPED = 0
    RUNNING = 1
    PENDING = 2
    UNKNOWN = 3


class SmartVMPackage(IntEnum):
    """Enumeration of Smart VM package types."""
    
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    EXTRA_LARGE = 4


class VirtualDiskType(IntEnum):
    """Enumeration of virtual disk types."""
    
    PRIMARY = 0
    ADDITIONAL_1 = 1
    ADDITIONAL_2 = 2
    ADDITIONAL_3 = 3


class VirtualDiskOperation(IntEnum):
    """Enumeration of virtual disk operations."""
    
    RESIZE = 1
    CREATE = 2
    DELETE = 3


class LoadBalancerAlgorithmType(IntEnum):
    """Enumeration of load balancer algorithm types."""
    
    ROUND_ROBIN = 1
    WEIGHTED_ROUND_ROBIN = 2
    LEAST_CONNECTIONS = 3


class LoadBalancerProtocol(IntEnum):
    """Enumeration of load balancer protocols."""
    
    TCP = 1
    HTTP = 2
    HTTPS = 3


class LoadBalancerStatus(IntEnum):
    """Enumeration of load balancer status values."""
    
    STOPPED = 0
    RUNNING = 1
    PENDING = 2
    UNKNOWN = 3


class SharedStorageProtocolType(IntEnum):
    """Enumeration of shared storage protocol types."""
    
    ISCSI = 1
    NFS = 2


class SharedStorageStatus(IntEnum):
    """Enumeration of shared storage status values."""
    
    STOPPED = 0
    RUNNING = 1
    PENDING = 2
    UNKNOWN = 3


class NotificationType(IntEnum):
    """Enumeration of notification types."""
    
    EMAIL = 1
    SMS = 2


# API endpoints
API_BASE_URL_TEMPLATE = "https://api.dc{}.computing.cloud.it/WsEndUser/v2.9/WsEndUser.svc/json"

# Default values
DEFAULT_TIMEOUT = 60  # seconds
DEFAULT_CACHE_TTL = 300  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # seconds
DEFAULT_RETRY_BACKOFF = 2.0

# Resource limits
MAX_CPU_QUANTITY = 16
MAX_RAM_QUANTITY = 64  # GB
MAX_DISK_SIZE = 500  # GB
MAX_DISKS_PER_VM = 4
MAX_NETWORK_ADAPTERS_PER_VM = 3