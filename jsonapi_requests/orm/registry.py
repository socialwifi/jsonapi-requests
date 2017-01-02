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
