from jsonapi_requests import base
from jsonapi_requests.orm import registry


class OrmApi:
    def __init__(self, api):
        self.type_registry = registry.TypeRegistry()
        self.api = api

    @classmethod
    def config(cls, *args, **kwargs):
        return cls(base.Api.config(*args, **kwargs))

    def endpoint(self, path):
        return self.api.endpoint(path)
