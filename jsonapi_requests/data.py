def make_collection(collection_type, element_type):
    class DynamicCollection(collection_type):
        type = element_type

    return DynamicCollection


def as_data(value):
    if hasattr(value, 'as_data'):
        return value.as_data()
    else:
        if isinstance(value, list):
            return List(value).as_data()
        elif isinstance(value, dict):
            return Dictionary(value).as_data()
        else:
            return Scalar(value).as_data()


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


class Scalar(AbstractValue):
    def __init__(self, data):
        self.data = data

    @classmethod
    def from_data(cls, data):
        return data

    def as_data(self):
        return self.data


class List(AbstractValue, list):
    type = Scalar

    @classmethod
    def from_data(cls, data):
        if not hasattr(data, '__iter__'):
            raise CantLoadData
        return cls([cls.type.from_data(element) for element in data])

    def as_data(self):
        return [as_data(element) for element in self]


class Dictionary(AbstractValue, dict):
    type = Scalar

    @classmethod
    def from_data(cls, data):
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
        if not hasattr(data, 'get'):
            raise CantLoadData
        fields = {}
        for field, field_class in cls.get_schema().items():
            field_data = data.get(field)
            if field_data is not None:
                fields[field] = field_class.from_data(field_data)

        return cls(**fields)

    def as_data(self):
        data = {}
        for field in self.get_schema():
            value = getattr(self, field)
            if value is not None:
                data[field] = as_data(value)
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
        exception = None
        for type in self.types:
            try:
                return type.from_data(data)
            except CantLoadData as e:
                exception = e
        if exception:
            raise exception


class Relationship(Record):
    schema = {
        'data': SchemaAlternativeWrapper(make_collection(List, ResourceIdentifier), ResourceIdentifier),
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
        'data': SchemaAlternativeWrapper(make_collection(List, JsonApiObject), JsonApiObject),
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
