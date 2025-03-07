"""
Caching utilities for the pyArubaCloud library.

This module provides caching functionality for the ArubaCloud API client,
including in-memory caching with time-to-live (TTL) support.
"""

import time
import threading
from typing import Dict, Any, Optional, Callable, TypeVar, cast

T = TypeVar('T')


class Cache:
    """
    Simple in-memory cache with TTL support.
    
    This class provides a thread-safe in-memory cache with support for
    time-to-live (TTL) expiration of cached items.
    
    Attributes:
        ttl (int): The default time-to-live in seconds.
        max_size (int): The maximum number of items to store in the cache.
    """
    
    def __init__(self, ttl: int = 300, max_size: int = 1000):
        """
        Initialize the cache.
        
        Args:
            ttl: The default time-to-live in seconds.
            max_size: The maximum number of items to store in the cache.
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value, or None if the key is not found or has expired.
        """
        with self._lock:
            if key in self._cache:
                if time.time() - self._timestamps[key] < self.ttl:
                    return self._cache[key]
                else:
                    # Remove expired item
                    del self._cache[key]
                    del self._timestamps[key]
            
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
            ttl: An optional custom time-to-live in seconds.
        """
        with self._lock:
            # If the cache is full, remove the oldest item
            if len(self._cache) >= self.max_size and key not in self._cache:
                oldest_key = min(self._timestamps.items(), key=lambda x: x[1])[0]
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            True if the key was found and deleted, False otherwise.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._timestamps[key]
                return True
            
            return False
    
    def clear(self) -> None:
        """Clear the entire cache."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def get_or_set(self, key: str, value_func: Callable[[], T], ttl: Optional[int] = None) -> T:
        """
        Get a value from the cache, or set it if not found.
        
        Args:
            key: The cache key.
            value_func: A function that returns the value to cache if not found.
            ttl: An optional custom time-to-live in seconds.
            
        Returns:
            The cached value, or the result of value_func if not found.
        """
        with self._lock:
            value = self.get(key)
            if value is None:
                value = value_func()
                self.set(key, value, ttl)
            
            return cast(T, value)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: A string pattern to match against keys.
            
        Returns:
            The number of keys invalidated.
        """
        count = 0
        with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
                del self._timestamps[key]
                count += 1
            
            return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            A dictionary of cache statistics.
        """
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'ttl': self.ttl,
                'oldest_item_age': time.time() - min(self._timestamps.values()) if self._timestamps else 0,
                'newest_item_age': time.time() - max(self._timestamps.values()) if self._timestamps else 0
            }


def cache_decorator(ttl: int = 300, key_prefix: str = ''):
    """
    Decorator for caching function results.
    
    Args:
        ttl: The time-to-live in seconds.
        key_prefix: A prefix for the cache key.
        
    Returns:
        A decorator function.
    """
    cache_instance = Cache(ttl=ttl)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create a cache key from the function name and arguments
            key = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check if the result is in the cache
            cached_result = cache_instance.get(key)
            if cached_result is not None:
                return cast(T, cached_result)
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache_instance.set(key, result)
            
            return result
        
        return wrapper
    
    return decorator