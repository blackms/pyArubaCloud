"""
Exceptions for the pyArubaCloud library.

This module defines the exception hierarchy used throughout the library,
providing consistent error handling and reporting.
"""

from typing import Dict, Optional, Any


class ArubaCloudException(Exception):
    """Base exception for all ArubaCloud errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class AuthenticationError(ArubaCloudException):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class APIError(ArubaCloudException):
    """Exception raised when the API returns an error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class ResourceNotFoundError(ArubaCloudException):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class ValidationError(ArubaCloudException):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


class OperationNotPermittedError(ArubaCloudException):
    """Exception raised when an operation is not permitted."""
    
    def __init__(self, message: str = "Operation not permitted"):
        super().__init__(message)


class HTTPError(ArubaCloudException):
    """Exception raised when an HTTP request fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class ParseError(ArubaCloudException):
    """Exception raised when parsing a response fails."""
    
    def __init__(self, message: str = "Failed to parse response"):
        super().__init__(message)


class RateLimitError(ArubaCloudException):
    """Exception raised when rate limiting is encountered."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(message)


class TimeoutError(ArubaCloudException):
    """Exception raised when a request times out."""
    
    def __init__(self, message: str = "Request timed out"):
        super().__init__(message)