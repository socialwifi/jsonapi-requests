from jsonapi_requests.orm import registry


class ObjectKeyError(Exception):
    pass


class BaseField:
    pass


class AttributeField(BaseField):
    def __init__(self, source):
        self.source = source

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        else:
            return instance.attributes[self.source]

    def __set__(self, instance, value):
        instance.attributes[self.source] = value


class RelationField(BaseField):
    def __init__(self, source):
        self.source = source

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        else:
            return InstanceRelation(instance, self.source).get()

    def __set__(self, instance, value):
        InstanceRelation(instance, self.source).set(value)

    def set_related(self, instance, object_map):
        InstanceRelation(instance, self.source).set_related(object_map)


class InstanceRelation:
    def __init__(self, instance, source):
        self.instance = instance
        self.source = source

    def get(self):
        if self.is_in_cache():
            return self.get_cached()
        else:
            related = self.get_new_related_object()
            self.set_cache(related)
            return related

    def set(self, value):
        self.instance.relationships[self.source] = value.as_relationship()
        self.set_cache(value)

    def get_new_related_object(self):
        try:
            key = self.get_object_key()
        except ObjectKeyError:
            return None
        else:
            model = self.instance._options.api.type_registry.get_model(key.type)
            return model.from_id(key.id)

    def set_related(self, object_map):
        try:
            key = self.get_object_key()
        except ObjectKeyError:
            pass
        else:
            if key in object_map:
                self.set_cache(object_map[key])

    def get_object_key(self):
        try:
            relationship = self.instance.relationships[self.source]
        except KeyError:
            raise ObjectKeyError
        else:
            data = relationship.data
            if data.type is None or data.id is None:
                raise ObjectKeyError
            else:
                return registry.ObjectKey(type=data.type, id=data.id)

    def is_in_cache(self):
        return self.source in self.instance.relationship_cache

    def set_cache(self, related):
        self.instance.relationship_cache[self.source] = related

    def get_cached(self):
        return self.instance.relationship_cache[self.source]
