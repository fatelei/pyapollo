import json
import os

from .client import ApolloClient


class ConfigManager(object):
    
    def __init__(self, apollo_host: str, app_id: str, namespace, cluster: str = 'default',
                 secret: str = '', file_cache_dir='/tmp'):
        self.cluster_name = cluster
        self.app_id = app_id
        self.file_cache_dir = file_cache_dir
        self.namespace = namespace
        self.config = {}
        self.is_hot_reload = False
        self.client = ApolloClient(apollo_host=apollo_host,
                                   app_id=app_id,
                                   namespace=namespace,
                                   cluster=cluster,
                                   secret=secret,
                                   callback=self.receive_notification)
    
    def restore_from_file(self):
        path = f'{self.file_cache_dir}/{self.app_id}.json'
        if os.path.exists(path):
            with open(path) as f:
                self.config = json.loads(f.read())
    
    def sync_to_file(self):
        path = f'{self.file_cache_dir}/{self.app_id}.json'
        with open(path, 'w') as f:
            f.write(json.dumps(self.config))
    
    def receive_notification(self, data):
        self.config = data
        self.sync_to_file()
    
    def enable_hot_reload(self):
        if not self.is_hot_reload:
            self.client.start_long_polling()
            self.is_hot_reload = True

    def __getitem__(self, item, default=None):
        if not self.config:
            self.restore_from_file()
            if not self.config:
                self.config = self.client.get_config()
                self.sync_to_file()
        return self.config.get(item)
