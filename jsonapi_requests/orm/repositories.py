import collections

import itertools

ObjectKey = collections.namedtuple('ObjectKey', ['type', 'id'])


class Repository:
    def __init__(self, type_registry):
        self.type_registry = type_registry
        self.object_map = {}

    def add(self, orm_object):
        self.object_map[ObjectKey(orm_object.type, orm_object.id)] = orm_object

    def __getitem__(self, object_key):
        return self.object_map[object_key]

    def __contains__(self, object_key):
        return object_key in self.object_map

    def update_from_api_response(self, response):
        if hasattr(response.data, 'items'):
            data = [response.data]
        else:
            data = response.data or []
        included = response.included or []
        for raw_object in itertools.chain(data, included):
            self.update_or_create_form_raw_object(raw_object)
        self.pouplate_related()

    def update_or_create_form_raw_object(self, raw_object):
        key = ObjectKey(raw_object.type, raw_object.id)
        if key not in self.object_map:
            object = self.type_registry.get_orm_object(raw_object)
            self.object_map[key] = object
        else:
            self.object_map[key].raw_object = raw_object

    def pouplate_related(self):
        for object in self.object_map.values():
            object.set_related_fields(self)
