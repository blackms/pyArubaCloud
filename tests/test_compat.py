"""
Test the compatibility layer.

This module contains tests for the compatibility layer.
"""

import unittest
from unittest.mock import MagicMock, patch

from pyarubacloud.compat.legacy import CloudInterface, Auth, Ip, IpList, VMList, LoadBalancer


class TestCompat(unittest.TestCase):
    """Test the compatibility layer."""

    def setUp(self):
        """Set up the test."""
        # Mock the Client class
        self.client_patcher = patch('pyarubacloud.compat.legacy.Client')
        self.mock_client = self.client_patcher.start()
        
        # Create a CloudInterface instance
        self.cloud_interface = CloudInterface(dc=1)
        
        # Mock the client instance
        self.mock_client_instance = self.mock_client.return_value
        self.cloud_interface.client = self.mock_client_instance
    
    def tearDown(self):
        """Tear down the test."""
        self.client_patcher.stop()
    
    def test_init(self):
        """Test the __init__ method."""
        self.assertEqual(self.cloud_interface.wcf_baseurl, 'https://api.dc1.computing.cloud.it/WsEndUser/v2.9/WsEndUser.svc/json')
        self.assertIsNotNone(self.cloud_interface.auth)
        self.assertIsInstance(self.cloud_interface.vmlist, VMList)
        self.assertIsInstance(self.cloud_interface.iplist, IpList)
        self.assertEqual(self.cloud_interface.hypervisors, {3: "LC", 4: "SMART", 2: "VW", 1: "HV"})
    
    def test_login(self):
        """Test the login method."""
        # Mock the client.auth.login method
        self.mock_client_instance.auth.login = MagicMock()
        
        # Call the login method
        self.cloud_interface.login('username', 'password')
        
        # Check that the auth attributes were set
        self.assertEqual(self.cloud_interface.auth.username, 'username')
        self.assertEqual(self.cloud_interface.auth.password, 'password')
        
        # Check that the client.auth.login method was called with the correct arguments
        self.mock_client_instance.auth.login.assert_called_once_with(username='username', password='password')
    
    def test_poweroff_server(self):
        """Test the poweroff_server method."""
        # Mock the client.compute.vm.power_off method
        self.mock_client_instance.compute.vm.power_off = MagicMock(return_value=True)
        
        # Call the poweroff_server method
        result = self.cloud_interface.poweroff_server(server_id=123)
        
        # Check that the client.compute.vm.power_off method was called with the correct arguments
        self.mock_client_instance.compute.vm.power_off.assert_called_once_with(123)
        
        # Check that the result is correct
        self.assertTrue(result)
    
    def test_poweron_server(self):
        """Test the poweron_server method."""
        # Mock the client.compute.vm.power_on method
        self.mock_client_instance.compute.vm.power_on = MagicMock(return_value=True)
        
        # Call the poweron_server method
        result = self.cloud_interface.poweron_server(server_id=123)
        
        # Check that the client.compute.vm.power_on method was called with the correct arguments
        self.mock_client_instance.compute.vm.power_on.assert_called_once_with(123)
        
        # Check that the result is correct
        self.assertTrue(result)
    
    def test_purchase_ip(self):
        """Test the purchase_ip method."""
        # Create a mock IP object
        mock_ip = MagicMock()
        mock_ip.address = '1.2.3.4'
        mock_ip.resource_id = '123'
        
        # Mock the client.compute.ip.purchase method
        self.mock_client_instance.compute.ip.purchase = MagicMock(return_value=mock_ip)
        
        # Call the purchase_ip method
        result = self.cloud_interface.purchase_ip()
        
        # Check that the client.compute.ip.purchase method was called
        self.mock_client_instance.compute.ip.purchase.assert_called_once()
        
        # Check that the result is correct
        self.assertIsInstance(result, Ip)
        self.assertEqual(result.ip_addr, '1.2.3.4')
        self.assertEqual(result.resid, '123')
    
    def test_delete_vm(self):
        """Test the delete_vm method."""
        # Mock the client.compute.vm.delete method
        self.mock_client_instance.compute.vm.delete = MagicMock(return_value=True)
        
        # Call the delete_vm method
        result = self.cloud_interface.delete_vm(server_id=123)
        
        # Check that the client.compute.vm.delete method was called with the correct arguments
        self.mock_client_instance.compute.vm.delete.assert_called_once_with(123)
        
        # Check that the result is correct
        self.assertTrue(result)


class TestLoadBalancer(unittest.TestCase):
    """Test the LoadBalancer class."""
    
    def setUp(self):
        """Set up the test."""
        # Mock the Client class
        self.client_patcher = patch('pyarubacloud.compat.legacy.Client')
        self.mock_client = self.client_patcher.start()
        
        # Create a LoadBalancer instance
        self.load_balancer = LoadBalancer()
        
        # Mock the client instance
        self.mock_client_instance = self.mock_client.return_value
        self.load_balancer.client = self.mock_client_instance
    
    def tearDown(self):
        """Tear down the test."""
        self.client_patcher.stop()
    
    def test_init(self):
        """Test the __init__ method."""
        self.assertEqual(self.load_balancer._name, '')
        self.assertIsNotNone(self.load_balancer.auth)
    
    def test_login(self):
        """Test the login method."""
        # Call the login method
        self.load_balancer.login('username', 'password')
        
        # Check that the auth attributes were set
        self.assertEqual(self.load_balancer.auth.username, 'username')
        self.assertEqual(self.load_balancer.auth.password, 'password')


if __name__ == '__main__':
    unittest.main()