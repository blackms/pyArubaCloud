"""
Main client interface for the pyArubaCloud library.

This module provides the main client interface for interacting with the ArubaCloud API,
including authentication, configuration, and access to API services.
"""

import logging
from typing import Optional, Dict, Any, Union

from pyarubacloud.auth import Auth
from pyarubacloud.config import Config
from pyarubacloud.constants import API_BASE_URL_TEMPLATE, DatacenterLocation
from pyarubacloud.utils.http import HttpClient
from pyarubacloud.utils.logging import ArubaLogger
from pyarubacloud.utils.cache import Cache
from pyarubacloud.api.compute import ComputeService
from pyarubacloud.api.loadbalancer import LoadBalancerService
from pyarubacloud.api.reversedns import ReverseDnsService
from pyarubacloud.api.sharedstorage import SharedStorageService


class Client:
    """
    Main client interface for the ArubaCloud API.
    
    This class provides the main entry point for interacting with the ArubaCloud API,
    including authentication, configuration, and access to API services.
    
    Attributes:
        auth (Auth): The authentication handler.
        config (Config): The configuration handler.
        logger (ArubaLogger): The logger instance.
        cache (Cache): The cache instance.
        http_client (HttpClient): The HTTP client.
        compute (ComputeService): The compute service.
        loadbalancer (LoadBalancerService): The load balancer service.
        reversedns (ReverseDnsService): The reverse DNS service.
        sharedstorage (SharedStorageService): The shared storage service.
    """
    
    def __init__(
        self,
        datacenter: Union[int, DatacenterLocation] = DatacenterLocation.ITALY_1,
        username: Optional[str] = None,
        password: Optional[str] = None,
        config: Optional[Config] = None,
        logger: Optional[logging.Logger] = None,
        cache: Optional[Cache] = None
    ):
        """
        Initialize the client.
        
        Args:
            datacenter: The datacenter location.
            username: The username for authentication.
            password: The password for authentication.
            config: An optional configuration object.
            logger: An optional logger instance.
            cache: An optional cache instance.
        """
        # Set up authentication
        self.auth = Auth(username, password)
        
        # Set up configuration
        self.config = config or Config()
        
        # Set up logging
        if logger:
            self.logger = ArubaLogger()
            self.logger.logger = logger
        else:
            self.logger = ArubaLogger(
                name="pyarubacloud",
                level=logging.DEBUG if self.config.debug else logging.INFO
            )
        
        # Set up cache
        self.cache = cache or Cache(ttl=self.config.cache_ttl)
        
        # Set up HTTP client
        self.base_url = API_BASE_URL_TEMPLATE.format(datacenter)
        self.http_client = HttpClient(
            base_url=self.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
            logger=self.logger.logger
        )
        
        # Set up API services
        self.compute = ComputeService(self)
        self.loadbalancer = LoadBalancerService(self)
        self.reversedns = ReverseDnsService(self)
        self.sharedstorage = SharedStorageService(self)
    
    def login(self, username: str, password: str) -> None:
        """
        Log in to the ArubaCloud API.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
        """
        self.auth.login(username, password)
        self.logger.info(f"Logged in as {username}")
    
    def set_datacenter(self, datacenter: Union[int, DatacenterLocation]) -> None:
        """
        Set the datacenter location.
        
        Args:
            datacenter: The datacenter location.
        """
        self.base_url = API_BASE_URL_TEMPLATE.format(datacenter)
        self.http_client = HttpClient(
            base_url=self.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
            logger=self.logger.logger
        )
        
        # Update API services with the new HTTP client
        self.compute.http_client = self.http_client
        self.loadbalancer.http_client = self.http_client
        self.reversedns.http_client = self.http_client
        self.sharedstorage.http_client = self.http_client
        
        self.logger.info(f"Set datacenter to {datacenter}")
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.logger.info("Cache cleared")