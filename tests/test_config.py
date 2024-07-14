import unittest

from unittest import mock

from pyapollo.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    
    @mock.patch("pyapollo.config.ApolloClient")
    def test_get_config(self, mock_apollo_client):
        instance = mock_apollo_client.return_value
        instance.get_config.return_value = {'foo': 'bar'}
        
        config = ConfigManager(apollo_host='http://localhost:8080',
                               app_id='foo',
                               namespace='bar')
        self.assertEqual('bar', config['foo'])
