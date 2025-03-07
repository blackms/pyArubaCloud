"""
Test the client module.

This module contains tests for the client module.
"""

import unittest
from unittest.mock import MagicMock, patch

from pyarubacloud.client import Client
from pyarubacloud.constants import DatacenterLocation
from pyarubacloud.exceptions import AuthenticationError


class TestClient(unittest.TestCase):
    """Test the Client class."""

    def setUp(self):
        """Set up the test."""
        self.client = Client(datacenter=DatacenterLocation.ITALY_1)

    def test_init(self):
        """Test the __init__ method."""
        self.assertEqual(self.client.base_url, 'https://api.dc1.computing.cloud.it/WsEndUser/v2.9/WsEndUser.svc/json')
        self.assertIsNotNone(self.client.auth)
        self.assertIsNotNone(self.client.config)
        self.assertIsNotNone(self.client.logger)
        self.assertIsNotNone(self.client.cache)
        self.assertIsNotNone(self.client.http_client)
        self.assertIsNotNone(self.client.compute)
        self.assertIsNotNone(self.client.loadbalancer)
        self.assertIsNotNone(self.client.reversedns)
        self.assertIsNotNone(self.client.sharedstorage)

    def test_login(self):
        """Test the login method."""
        # Mock the auth.login method
        self.client.auth.login = MagicMock()

        # Call the login method
        self.client.login('username', 'password')

        # Check that the auth.login method was called with the correct arguments
        self.client.auth.login.assert_called_once_with(username='username', password='password')

    def test_set_datacenter(self):
        """Test the set_datacenter method."""
        # Mock the http_client
        self.client.http_client = MagicMock()

        # Call the set_datacenter method
        self.client.set_datacenter(DatacenterLocation.ITALY_2)

        # Check that the base_url was updated
        self.assertEqual(self.client.base_url, 'https://api.dc2.computing.cloud.it/WsEndUser/v2.9/WsEndUser.svc/json')

    def test_clear_cache(self):
        """Test the clear_cache method."""
        # Mock the cache.clear method
        self.client.cache.clear = MagicMock()

        # Call the clear_cache method
        self.client.clear_cache()

        # Check that the cache.clear method was called
        self.client.cache.clear.assert_called_once()


if __name__ == '__main__':
    unittest.main()