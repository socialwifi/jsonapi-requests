
class OrmException(Exception):
    pass


class TypeRegistry:
    def __init__(self):
        self.registry = {}

    def register(self, model):
        type = model._options.type
        if type in self.registry:
            raise OrmException('Api already has model of this type')
        self.registry[type] = model

    def get_orm_object(self, raw_object):
        model = self.get_model(raw_object.type)
        return model(raw_object)

    def get_model(self, type):
        return self.registry[type]
