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

    def from_response_content(self, jsonapi_response, to):
        object_map = self._get_object_map_from_response(jsonapi_response, )
        self._populate_related(object_map)
        if hasattr(jsonapi_response.data, 'items'):
            return
        else:
            result = []
            for object in jsonapi_response.data:
                new = self(raw_object=o)
            return new

    def _get_object_map_from_response(self, response):
        if hasattr(response.data, 'items'):
            data = [response.data]
        else:
            data = response.data or []
        included = response.included or []
        object_map = self.type_registry.get_mapped_orm_objects(data + included)
        return object_map

    @staticmethod
    def _populate_related(object_map):
        for object in object_map.values():
            object.set_related_fields(object_map)