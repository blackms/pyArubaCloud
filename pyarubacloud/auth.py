"""
Authentication module for the pyArubaCloud library.

This module provides authentication functionality for the ArubaCloud API,
including username/password authentication and token management.
"""

from typing import Optional
from datetime import datetime, timedelta

from pyarubacloud.exceptions import AuthenticationError


class Auth:
    """
    Authentication handler for ArubaCloud API.
    
    This class manages authentication credentials and tokens for
    accessing the ArubaCloud API.
    
    Attributes:
        username (str): The username for authentication.
        password (str): The password for authentication.
        token (Optional[str]): The authentication token, if available.
        token_expiry (Optional[datetime]): The expiry time of the token.
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize the Auth object.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
            token: An optional authentication token.
        """
        self.username = username
        self.password = password
        self.token = token
        self.token_expiry: Optional[datetime] = None
    
    def login(self, username: str, password: str) -> None:
        """
        Set the authentication credentials.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
        """
        self.username = username
        self.password = password
        self.token = None
        self.token_expiry = None
    
    def set_token(self, token: str, expiry_seconds: int = 3600) -> None:
        """
        Set the authentication token.
        
        Args:
            token: The authentication token.
            expiry_seconds: The number of seconds until the token expires.
        """
        self.token = token
        self.token_expiry = datetime.now() + timedelta(seconds=expiry_seconds)
    
    def clear_token(self) -> None:
        """Clear the authentication token."""
        self.token = None
        self.token_expiry = None
    
    def is_token_valid(self) -> bool:
        """
        Check if the token is valid.
        
        Returns:
            True if the token is valid, False otherwise.
        """
        if not self.token or not self.token_expiry:
            return False
        
        return datetime.now() < self.token_expiry
    
    def get_auth_headers(self) -> dict:
        """
        Get the authentication headers.
        
        Returns:
            A dictionary of authentication headers.
            
        Raises:
            AuthenticationError: If no authentication credentials are available.
        """
        if self.is_token_valid():
            return {"Authorization": f"Bearer {self.token}"}
        
        if not self.username or not self.password:
            raise AuthenticationError("No authentication credentials available")
        
        return {}
    
    def to_dict(self) -> dict:
        """
        Convert the authentication credentials to a dictionary.
        
        Returns:
            A dictionary containing the authentication credentials.
        """
        return {
            "Username": self.username,
            "Password": self.password
        }