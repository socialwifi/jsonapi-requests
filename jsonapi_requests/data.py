def make_collection(collection_type, element_type, allow_empty_data=False):
    class DynamicCollection(collection_type):
        type = element_type
        allow_empty = allow_empty_data

    return DynamicCollection


def as_data(value):
    if hasattr(value, 'as_data'):
        return value.as_data()
    else:
        return value


class AbstractValue:
    @classmethod
    def from_data(cls, data):
        raise NotImplementedError

    def as_data(self):
        raise NotImplementedError

    def __eq__(self, other):
        try:
            return self.as_data() == other.as_data()
        except AttributeError:
            return False

    @classmethod
    def allow_as_data(cls, data):
        return bool(data)


class Scalar(AbstractValue):
    def __init__(self, data):
        self.data = data

    @classmethod
    def from_data(cls, data):
        return data

    def as_data(self):
        return self.data


class AbstractCollectionValue(AbstractValue):
    type = Scalar
    allow_empty = False

    @classmethod
    def allow_as_data(cls, value):
        return bool(value) or cls.allow_empty


class List(AbstractCollectionValue, list):
    @classmethod
    def from_data(cls, data):
        if data is None:
            return cls()
        if not hasattr(data, '__iter__'):
            raise CantLoadData
        return cls([cls.type.from_data(element) for element in data])

    def as_data(self):
        return [as_data(element) for element in self]


class Dictionary(AbstractCollectionValue, dict):
    @classmethod
    def from_data(cls, data):
        if data is None:
            return cls()
        if not hasattr(data, 'items'):
            raise CantLoadData
        return cls({key: cls.type.from_data(element) for key, element in data.items()})

    def as_data(self):
        return {key: as_data(element) for key, element in self.items()}


class Record(AbstractValue):
    schema = {}

    def __init__(self, **kwargs):
        for field in self.get_schema():
            setattr(self, field, kwargs.get(field))

    @classmethod
    def get_schema(cls):
        return cls.schema

    @classmethod
    def from_data(cls, data):
        if data is None:
            data = {}
        if not hasattr(data, 'get'):
            raise CantLoadData
        fields = {}
        for field, field_class in cls.get_schema().items():
            field_data = data.get(field)
            fields[field] = field_class.from_data(field_data)
        return cls(**fields)

    def as_data(self):
        data = {}
        for field, type in self.get_schema().items():
            value = as_data(getattr(self, field))
            if type.allow_as_data(value):
                data[field] = value
        return data


class ResourceIdentifier(Record):
    schema = {
        'type': Scalar,
        'id': Scalar,
    }

    # noinspection PyMissingConstructor
    def __init__(self, *, type=None, id=None):
        self.type = type
        self.id = id


class SchemaAlternativeWrapper:
    def __init__(self, *types):
        self.types = types

    def from_data(self, data):
        return self.get_type(data).from_data(data)

    def allow_as_data(self, data):
        return self.get_type(data).allow_as_data(data)

    def get_type(self, data):
        exception = None
        for type in self.types:
            try:
                type.from_data(data)
            except CantLoadData as e:
                exception = e
            else:
                return type
        if exception:
            raise exception


class Relationship(Record):
    schema = {
        'data': SchemaAlternativeWrapper(
            ResourceIdentifier, make_collection(List, ResourceIdentifier, allow_empty_data=True)),
        'links': Dictionary,
    }

    # noinspection PyMissingConstructor
    def __init__(self, *, data=None, links=None):
        self.data = data
        self.links = links


class JsonApiObject(Record):
    schema = {
        'type': Scalar,
        'id': Scalar,
        'attributes': Dictionary,
        'relationships': make_collection(Dictionary, Relationship),
        'links': Dictionary,
    }

    # noinspection PyMissingConstructor
    def __init__(self, *, type=None, id=None, attributes=None, relationships=None, links=None):
        self.type = type
        self.id = id
        self.attributes = attributes
        self.relationships = relationships
        self.links = links


class JsonApiResponse(Record):
    schema = {
        'data': SchemaAlternativeWrapper(JsonApiObject, make_collection(List, JsonApiObject, allow_empty_data=True)),
        'errors': List,
        'meta': Scalar,
        'jsonapi': Scalar,
        'links': Dictionary,
        'included': make_collection(List, JsonApiObject),
    }

    # noinspection PyMissingConstructor
    def __init__(self, *, data=None, errors=None, meta=None, jsonapi=None, links=None, included=None):
        self.data = data
        self.errors = errors
        self.meta = meta
        self.jsonapi = jsonapi
        self.links = links
        self.included = included


class CantLoadData(Exception):
    pass
