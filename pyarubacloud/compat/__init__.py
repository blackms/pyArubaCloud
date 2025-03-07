"""
Compatibility layer for the pyArubaCloud library.

This package provides backward compatibility with the old pyArubaCloud API,
allowing existing code to continue working with the new implementation.
"""

from pyarubacloud.compat.legacy import CloudInterface, LoadBalancer, Auth

__all__ = [
    'CloudInterface',
    'LoadBalancer',
    'Auth'
]