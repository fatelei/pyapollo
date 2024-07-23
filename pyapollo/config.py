import json
import os

from .client import ApolloClient
from .exception import InvalidFormatException


class ConfigManager(object):
    
    def __init__(self, apollo_host: str, app_id: str, namespace, cluster: str = 'default',
                 secret: str = '', file_cache_dir='/tmp', data_format='properties'):
        self.cluster_name = cluster
        self.app_id = app_id
        self.file_cache_dir = file_cache_dir
        self.namespace = namespace
        self.config = {}
        self.is_hot_reload = False
        self.data_format = data_format
        self.client = ApolloClient(apollo_host=apollo_host,
                                   app_id=app_id,
                                   namespace=namespace,
                                   cluster=cluster,
                                   secret=secret,
                                   callback=self.receive_notification,
                                   data_format=data_format)
    
    def restore_from_file(self):
        path = f'{self.file_cache_dir}/{self.app_id}-{self.namespace}.json'
        if os.path.exists(path):
            with open(path) as f:
                self.config = json.loads(f.read())
    
    def sync_to_file(self):
        path = f'{self.file_cache_dir}/{self.app_id}-{self.namespace}.json'
        with open(path, 'w') as f:
            f.write(json.dumps(self.config))
    
    def receive_notification(self, data):
        self.config = data
        self.sync_to_file()
    
    def enable_hot_reload(self):
        if not self.is_hot_reload:
            self.client.start_long_polling()
            self.is_hot_reload = True
    
    def get_from_json(self, key, default=None):
        if self.data_format in ('properties', 'json'):
            if not self.config:
                self.restore_from_file()
                if not self.config:
                    self.config = self.client.get_config()
                    self.sync_to_file()
            return self.config.get(key, default)
        else:
            raise InvalidFormatException("only support properties / json")
    
    def get_from_yaml(self, key):
        raise NotImplementedError
    
    def get_from_xml(self, key):
        raise NotImplementedError
