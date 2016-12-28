import collections


class OrmException(Exception):
    pass


ObjectKey = collections.namedtuple('ObjectKey', ['type', 'id'])


class TypeRegistry:
    def __init__(self):
        self.registry = {}

    def register(self, model):
        type = model._options.type
        if type in self.registry:
            raise OrmException('Api already has model of this type')
        self.registry[type] = model

    def get_mapped_orm_objects(self, raw_objects):
        mapping = {}
        for raw_object in raw_objects:
            object = self.get_orm_object(raw_object)
            mapping[ObjectKey(object.type, object.id)] = object
        return mapping

    def get_orm_object(self, raw_object):
        model = self.get_model(raw_object.type)
        return model(raw_object)

    def get_model(self, type):
        return self.registry[type]
