"""
Configuration module for the pyArubaCloud library.

This module provides configuration management for the ArubaCloud API client,
including default values and user-configurable settings.
"""

from typing import Optional, Dict, Any, Union
import os
import json

from pyarubacloud.constants import (
    DEFAULT_TIMEOUT,
    DEFAULT_CACHE_TTL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_RETRY_BACKOFF
)


class Config:
    """
    Configuration handler for ArubaCloud API client.
    
    This class manages configuration settings for the ArubaCloud API client,
    including timeouts, retry behavior, and caching.
    
    Attributes:
        timeout (int): The request timeout in seconds.
        cache_ttl (int): The cache time-to-live in seconds.
        max_retries (int): The maximum number of retry attempts.
        retry_delay (float): The initial delay between retries in seconds.
        retry_backoff (float): The backoff multiplier for retries.
        debug (bool): Whether to enable debug logging.
        user_agent (str): The user agent string to use for requests.
    """
    
    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        debug: bool = False,
        user_agent: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Config object.
        
        Args:
            timeout: The request timeout in seconds.
            cache_ttl: The cache time-to-live in seconds.
            max_retries: The maximum number of retry attempts.
            retry_delay: The initial delay between retries in seconds.
            retry_backoff: The backoff multiplier for retries.
            debug: Whether to enable debug logging.
            user_agent: The user agent string to use for requests.
            **kwargs: Additional configuration options.
        """
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.debug = debug
        self.user_agent = user_agent or f"pyArubaCloud/{self._get_version()}"
        self._extra_config = kwargs
    
    def _get_version(self) -> str:
        """
        Get the library version.
        
        Returns:
            The library version string.
        """
        try:
            from pyarubacloud import __version__
            return __version__
        except ImportError:
            return "unknown"
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key.
            default: The default value to return if the key is not found.
            
        Returns:
            The configuration value, or the default if not found.
        """
        if hasattr(self, key):
            return getattr(self, key)
        
        return self._extra_config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key.
            value: The configuration value.
        """
        if hasattr(self, key) and not key.startswith('_'):
            setattr(self, key, value)
        else:
            self._extra_config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.
        
        Args:
            config_dict: A dictionary of configuration values.
        """
        for key, value in config_dict.items():
            self.set(key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            A dictionary containing the configuration values.
        """
        result = {
            'timeout': self.timeout,
            'cache_ttl': self.cache_ttl,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'retry_backoff': self.retry_backoff,
            'debug': self.debug,
            'user_agent': self.user_agent
        }
        
        result.update(self._extra_config)
        return result
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """
        Create a Config object from a dictionary.
        
        Args:
            config_dict: A dictionary of configuration values.
            
        Returns:
            A new Config object.
        """
        return cls(**config_dict)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'Config':
        """
        Create a Config object from a JSON file.
        
        Args:
            file_path: The path to the JSON configuration file.
            
        Returns:
            A new Config object.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        
        return cls.from_dict(config_dict)
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save the configuration to a JSON file.
        
        Args:
            file_path: The path to the JSON configuration file.
            
        Raises:
            PermissionError: If the file cannot be written.
        """
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)