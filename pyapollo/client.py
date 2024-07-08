import asyncio
import base64
import hashlib
import hmac
import json
import socket
import time
import threading

from collections import defaultdict

import httpx
from httpx import ReadTimeout

from .exception import ConfigException


class ApolloClient(object):
    
    def __init__(self, apollo_host: str, app_id: str, namespace, cluster: str = 'default',
                 secret: str = '', callback=None):
        self.apollo_host = apollo_host
        self.app_id = app_id
        self.cluster = cluster
        self.secret = secret
        self.namespace = namespace
        self.notification_map = defaultdict(int)
        self._ip = None
        self.thread = threading.Thread(
            target=self.do_long_polling_refresh, name='refresh_config',
            args=(app_id, cluster, namespace, callback))
        self.exit_thread = False
    
    @property
    def ip(self):
        if self._ip is None:
            try:
                self._ip = socket.gethostbyname(socket.gethostname())
            except socket.gaierror:
                pass
        return self._ip
    
    def get_config(self, release_key: str = None):
        if not release_key:
            path = f'/configs/{self.app_id}/{self.cluster}/{self.namespace}?ip={self.ip}'
        else:
            path = f'/configs/{self.app_id}/{self.cluster}/{self.namespace}?ip={self.ip}&releaseKey={release_key}'
        url = f'{self.apollo_host}{path}'
        headers = self.get_headers(path)
        
        resp = httpx.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()['configurations']
        else:
            raise ConfigException(resp.text)
    
    def start_long_polling(self):
        self.thread.start()
    
    async def __long_polling(self, app_id, cluster_name, namespace, callback=None):
        while True:
            if self.exit_thread:
                return
            if namespace not in self.notification_map:
                self.notification_map[namespace] = 1
            notification_id = self.notification_map[namespace]
            params = {
                "appId": app_id,
                "cluster": cluster_name,
                "notifications": json.dumps([{
                    "namespaceName": namespace,
                    "notificationId": notification_id
                }])
            }
            url = f'{self.apollo_host}/notifications/v2'
            async with httpx.AsyncClient() as client:
                try:
                    r = await client.get(url, params=params, timeout=61)
                    print(r.text)
                    if r.status_code == 200:
                        notification_data = r.json()
                        self.notification_map[namespace] = notification_data[0]['notificationId']
                        try:
                            data = self.get_config()
                            if callback:
                                callback(data)
                        except (ConfigException, ReadTimeout):
                            pass
                except ReadTimeout:
                    pass
            await asyncio.sleep(5)
    
    def do_long_polling_refresh(self, app_id, cluster_name, namespace, callback):
        asyncio.run(self.__long_polling(app_id, cluster_name, namespace, callback=callback))
    
    @staticmethod
    def signature(timestamp, uri, secret):
        string_to_sign = '' + timestamp + '\n' + uri
        hmac_code = hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha1).digest()
        return base64.b64encode(hmac_code).decode()
    
    def get_headers(self, path):
        headers = {}
        if not self.secret:
            return headers
        time_unix_now = str(int(round(time.time() * 1000)))
        headers['Authorization'] = 'Apollo ' + self.app_id + ':' + self.signature(time_unix_now, path, self.secret)
        headers['Timestamp'] = time_unix_now
        return headers
