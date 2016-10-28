from jsonapi_requests import configuration
from jsonapi_requests import request_factory


class Api:
    @classmethod
    def config(cls, dict_or_config=None, **kwargs):
        config_dict = {}
        if isinstance(dict_or_config, dict):
            config_dict.update(dict_or_config)
        else:
            for setting in dir(dict_or_config):
                if setting.isupper():
                    config_dict[setting] = getattr(dict_or_config, setting)
        config_dict.update(kwargs)
        return cls(configuration.Factory(config_dict).create())

    def __init__(self, config: configuration.Configuration):
        self.requests = request_factory.ApiRequestFactory(config)

    def endpoint(self, path):
        return Endpoint(path, self.requests)


class Endpoint:
    def __init__(self, path, requests):
        self.path = path
        self.requests = requests

    def get(self, **kwargs):
        return self.requests.get(self.path, **kwargs)

    def post(self, **kwargs):
        return self.requests.post(self.path, **kwargs)

    def delete(self, **kwargs):
        return self.requests.delete(self.path, **kwargs)

    def put(self, **kwargs):
        return self.requests.put(self.path, **kwargs)

    def patch(self, **kwargs):
        return self.requests.patch(self.path, **kwargs)
