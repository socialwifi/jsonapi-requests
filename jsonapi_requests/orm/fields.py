from jsonapi_requests.orm import registry


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
            if self.is_in_cache(instance):
                return self.get_cached(instance)
            else:
                related = self.get_new_related_object(instance)
                self.set_cache(instance, related)
                return related

    def __set__(self, instance, value):
        instance.relationships[self.source] = value.as_relationship()
        self.set_cache(instance, value)

    def get_new_related_object(self, instance):
        try:
            relationship = instance.relationships[self.source]
        except KeyError:
            return None
        else:
            data = relationship.data
            model = instance._options.api.type_registry.get_model(data.type)
            return model.from_id(data.id)

    def set_related(self, instance, object_map):
        try:
            relationship = instance.relationships[self.source]
        except KeyError:
            pass
        else:
            key = registry.ObjectKey(type=relationship.data.type, id=relationship.data.id)
            if key in object_map:
                self.set_cache(instance, object_map[key])

    def is_in_cache(self, instance):
        return self.source in instance.relationship_cache

    def set_cache(self, instance, related):
        instance.relationship_cache[self.source] = related

    def get_cached(self, instance):
        return instance.relationship_cache[self.source]
