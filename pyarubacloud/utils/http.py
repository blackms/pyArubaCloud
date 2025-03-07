"""
HTTP client for the pyArubaCloud library.

This module provides HTTP client functionality for making requests to the ArubaCloud API,
including connection pooling, request strategies, and error handling.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pyarubacloud.exceptions import (
    HTTPError,
    ParseError,
    APIError,
    TimeoutError,
    RateLimitError
)


class RequestStrategy(ABC):
    """
    Abstract base class for request strategies.
    
    This class defines the interface for request strategies, which are responsible
    for executing HTTP requests and handling responses.
    """
    
    @abstractmethod
    def execute(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Execute an HTTP request.
        
        Args:
            url: The URL to request.
            data: The data to send.
            headers: Optional headers.
            
        Returns:
            The parsed response.
            
        Raises:
            HTTPError: If the HTTP request fails.
            ParseError: If the response cannot be parsed.
            APIError: If the API returns an error.
        """
        pass


class JSONRequestStrategy(RequestStrategy):
    """
    JSON request strategy.
    
    This strategy sends JSON requests and parses JSON responses.
    """
    
    def __init__(self, session: Optional[requests.Session] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the JSON request strategy.
        
        Args:
            session: An optional requests session to use.
            logger: An optional logger to use.
        """
        self.session = session or requests.Session()
        self.logger = logger
    
    def execute(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Execute a JSON HTTP request.
        
        Args:
            url: The URL to request.
            data: The data to send as JSON.
            headers: Optional headers.
            
        Returns:
            The parsed JSON response.
            
        Raises:
            HTTPError: If the HTTP request fails.
            ParseError: If the response cannot be parsed as JSON.
            APIError: If the API returns an error.
        """
        if headers is None:
            headers = {}
        
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        
        json_data = json.dumps(data)
        headers["Content-Length"] = str(len(json_data))
        
        if self.logger:
            self.logger.debug(f"Request URL: {url}")
            self.logger.debug(f"Request headers: {headers}")
            self.logger.debug(f"Request data: {json_data}")
        
        try:
            response = self.session.post(url, data=json_data, headers=headers)
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {url} timed out")
        except requests.exceptions.RequestException as e:
            raise HTTPError(f"HTTP error: {str(e)}")
        
        if self.logger:
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Response content: {response.text}")
        
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise RateLimitError("Rate limit exceeded", retry_after=retry_after_int)
        
        if response.status_code != 200:
            raise HTTPError(f"HTTP error {response.status_code}: {response.text}", status_code=response.status_code)
        
        try:
            parsed_response = response.json()
        except ValueError:
            raise ParseError(f"Failed to parse response as JSON: {response.text}")
        
        if not parsed_response.get("Success", False):
            raise APIError(
                message=parsed_response.get("ResultMessage", "Unknown API error"),
                status_code=response.status_code,
                response=parsed_response
            )
        
        return parsed_response


class MockRequestStrategy(RequestStrategy):
    """
    Mock request strategy for testing.
    
    This strategy returns predefined responses for testing purposes.
    """
    
    def __init__(self, responses: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize the mock request strategy.
        
        Args:
            responses: A dictionary mapping request keys to mock responses.
        """
        self.responses = responses or {}
    
    def add_response(self, url: str, data: Dict[str, Any], response: Dict[str, Any]) -> None:
        """
        Add a mock response for a specific request.
        
        Args:
            url: The URL to match.
            data: The request data to match.
            response: The response to return.
        """
        key = self._get_key(url, data)
        self.responses[key] = response
    
    def execute(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Execute a mock HTTP request.
        
        Args:
            url: The URL to request.
            data: The data to send.
            headers: Optional headers.
            
        Returns:
            The mock response.
            
        Raises:
            ValueError: If no mock response is found for the request.
        """
        key = self._get_key(url, data)
        
        if key not in self.responses:
            raise ValueError(f"No mock response found for request: {url}, {data}")
        
        return self.responses[key]
    
    def _get_key(self, url: str, data: Dict[str, Any]) -> str:
        """
        Get a unique key for a request.
        
        Args:
            url: The URL.
            data: The request data.
            
        Returns:
            A unique key.
        """
        return f"{url}:{json.dumps(data, sort_keys=True)}"


class HttpClient:
    """
    HTTP client for making requests to the ArubaCloud API.
    
    This class provides a high-level interface for making HTTP requests to the ArubaCloud API,
    with support for connection pooling, retries, and different request strategies.
    """
    
    def __init__(
        self,
        base_url: str,
        strategy: Optional[RequestStrategy] = None,
        timeout: int = 60,
        max_retries: int = 3,
        pool_connections: int = 10,
        pool_maxsize: int = 100,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the HTTP client.
        
        Args:
            base_url: The base URL for API requests.
            strategy: The request strategy to use.
            timeout: The request timeout in seconds.
            max_retries: The maximum number of retry attempts.
            pool_connections: The number of connection pools to cache.
            pool_maxsize: The maximum number of connections to save in the pool.
            logger: An optional logger to use.
        """
        self.base_url = base_url
        self.timeout = timeout
        self.logger = logger
        
        # Create a session with connection pooling and retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Set the request strategy
        self.strategy = strategy or JSONRequestStrategy(session=self.session, logger=self.logger)
    
    def post(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            endpoint: The API endpoint.
            data: The data to send.
            headers: Optional headers.
            
        Returns:
            The parsed response.
            
        Raises:
            HTTPError: If the HTTP request fails.
            ParseError: If the response cannot be parsed.
            APIError: If the API returns an error.
        """
        url = f"{self.base_url}/{endpoint}"
        return self.strategy.execute(url, data, headers)
    
    def set_strategy(self, strategy: RequestStrategy) -> None:
        """
        Set the request strategy.
        
        Args:
            strategy: The strategy to use.
        """
        self.strategy = strategy