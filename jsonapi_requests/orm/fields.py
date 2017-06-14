from jsonapi_requests import data
from jsonapi_requests.orm import registry
from jsonapi_requests.orm import repositories


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
            return self.get_instance_relation(instance).get()

    def __set__(self, instance, value):
        if hasattr(value, 'id'):
            instance_relation = self.get_instance_to_one_relation(instance)
        else:
            instance_relation = self.get_instance_to_many_relation(instance)
        instance_relation.set(value)

    def set_related(self, instance, repository):
        self.get_instance_relation(instance).set_related(repository)

    def get_instance_relation(self, instance):
        if self.is_to_many(instance):
            return self.get_instance_to_many_relation(instance)
        else:
            return self.get_instance_to_one_relation(instance)

    def get_instance_to_one_relation(self, instance):
        return InstanceToOneRelation(instance, self.source)

    def get_instance_to_many_relation(self, instance):
        return InstanceToManyRelation(instance, self.source)

    def is_to_many(self, instance):
        try:
            return not hasattr(self.get_data(instance), 'id')
        except ObjectKeyError:
            return False

    def get_data(self, instance):
        try:
            relationship = instance.relationships[self.source]
        except KeyError:
            raise ObjectKeyError
        else:
            return relationship.data


class BaseInstanceRelation:
    def __init__(self, instance, source):
        self.instance = instance
        self.source = source
        self.cache = InstanceCache(instance, source)

    def get(self):
        raise NotImplementedError

    def set(self, value):
        raise NotImplementedError

    def set_related(self, object_map):
        raise NotImplementedError


class InstanceToOneRelation(BaseInstanceRelation):
    def get(self):
        if self.cache.is_in_cache():
            return self.cache.get_cached()
        else:
            related = self.get_new_related_object()
            self.cache.set_cache(related)
            return related

    def set(self, value):
        self.instance.relationships[self.source] = data.Relationship(data=value.as_identifier())
        self.cache.set_cache(value)

    def get_new_related_object(self):
        try:
            key = self.get_object_key()
        except ObjectKeyError:
            return None
        else:
            model = self.instance._options.api.type_registry.get_model(key.type)
            return model.from_id(key.id)

    def set_related(self, repository):
        try:
            key = self.get_object_key()
        except ObjectKeyError:
            pass
        else:
            if key in repository:
                self.cache.set_cache(repository[key])

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
                return repositories.ObjectKey(type=data.type, id=data.id)


class InstanceToManyRelation(BaseInstanceRelation):
    def get(self):
        if self.cache.is_in_cache():
            return self.cache.get_cached()
        else:
            related = self.get_new_related_objects()
            self.cache.set_cache(related)
            return related

    def set(self, values):
        self.instance.relationships[self.source] = data.Relationship(data=[value.as_identifier() for value in values])
        self.cache.set_cache(values)

    def get_new_related_objects(self):
        try:
            keys = list(self.get_object_keys())
        except ObjectKeyError:
            return []
        else:
            return [self.get_new_related_object(key) for key in keys]

    def set_related(self, object_map):
        keys = list(self.get_object_keys())
        result = []
        for key in keys:
            if key in object_map:
                result.append(object_map[key])
            else:
                result.append(self.get_new_related_object(key))
        self.cache.set_cache(result)

    def get_new_related_object(self, key):
        model = self.instance._options.api.type_registry.get_model(key.type)
        return model.from_id(key.id)

    def get_object_keys(self):
        relationship = self.instance.relationships[self.source]
        for relation in relationship.data:
            if relation.type is not None and relation.id is not None:
                yield repositories.ObjectKey(type=relation.type, id=relation.id)


class InstanceCache:
    def __init__(self, instance, source):
        self.instance = instance
        self.source = source

    def is_in_cache(self):
        return self.source in self.instance.relationship_cache

    def set_cache(self, related):
        self.instance.relationship_cache[self.source] = related

    def get_cached(self):
        return self.instance.relationship_cache[self.source]
