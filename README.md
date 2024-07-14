# pyapollo
another apollo python client

## Usage

```python
from pyapollo.config import ConfigManager
apollo_host = 'http://localhost:8080'
app_id = 'SampleApp'
namespace = 'application'
config = ConfigManager(apollo_host=apollo_host, app_id=app_id, namespace=namespace)
bar = config['foo']
# if you want enable hot reload config
config.enable_hot_reload()
```

pyapollo has a file cache, you can specific `file_cache_dir` to `ConfigManager`.
