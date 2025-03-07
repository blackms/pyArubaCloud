"""
Python Interface for ArubaCloud IaaS Service.

This library provides a Python interface to interact with the ArubaCloud IaaS API.
It allows you to manage virtual machines, IP addresses, load balancers, and other
cloud resources through a clean and consistent API.
"""

__version__ = '1.0.0'

from pyarubacloud.client import Client
from pyarubacloud.exceptions import (
    ArubaCloudException,
    AuthenticationError,
    APIError,
    ResourceNotFoundError,
    ValidationError,
    OperationNotPermittedError
)

__all__ = [
    'Client',
    'ArubaCloudException',
    'AuthenticationError',
    'APIError',
    'ResourceNotFoundError',
    'ValidationError',
    'OperationNotPermittedError'
]