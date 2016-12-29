from jsonapi_requests import data
from jsonapi_requests.orm import fields as orm_fields
from jsonapi_requests.orm import registry


class JsonApiObjectStub:
    is_stub = True

    def __init__(self, id):
        self.id = id


class ApiModelMetaclass(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs, **kwargs)
        options = OptionsFactory(cls, attrs).get()
        cls._options = options
        if options.api and options.type:
            options.api.type_registry.register(cls)


class OptionsFactory:
    def __init__(self, klass, klass_attrs):
        self.klass = klass
        self.klass_attrs = klass_attrs

    def get(self):
        return Options(type=self.type, api=self.api, fields=self.fields)

    @property
    def type(self):
        return self.get_setting('type')

    @property
    def api(self):
        return self.get_setting('api')

    def get_setting(self, setting_name):
        return getattr(self.meta, setting_name, getattr(self.previous_options, setting_name, None))

    @property
    def meta(self):
        return self.klass_attrs.get('Meta')

    @property
    def fields(self):
        fields = getattr(self.previous_options, 'fields', {}).copy()
        for name, value in self.klass_attrs.items():
            if isinstance(value, orm_fields.BaseField):
                fields[name] = value
        return fields

    @property
    def previous_options(self):
        return getattr(self.klass, '_options', None)


class Options:
    def __init__(self, type, api, fields):
        self.type = type
        self.api = api
        self.fields = fields


class ApiModel(metaclass=ApiModelMetaclass):
    def __init__(self, raw_object):
        self.raw_object = raw_object
        self.relationship_cache = {}

    @classmethod
    def from_id(cls, id):
        return cls(raw_object=JsonApiObjectStub(id))

    @classmethod
    def from_response_content(cls, jsonapi_response):
        new = cls(raw_object=jsonapi_response.data)
        new._populate_related(jsonapi_response)
        return new

    @property
    def type(self):
        if not self.is_stub:
            return self.raw_object.type
        else:
            return self._options.type

    @property
    def is_stub(self):
        return getattr(self.raw_object, 'is_stub', False)

    def __getattr__(self, item):
        try:
            return getattr(self.raw_object, item)
        except AttributeError:
            if self.is_stub:
                self.refresh()
                return getattr(self.raw_object, item)
            else:
                raise

    def as_relationship(self):
        return data.Relationship(data=data.ResourceIdentifier(type=self.type, id=self.id))

    def refresh(self):
        api_response = self.endpoint.get()
        jsonapi_response = api_response.content
        self.raw_object = jsonapi_response.data
        self._populate_related(jsonapi_response)

    def _populate_related(self, response):
        object_map = self._get_included_object_map_from_response(response)
        object_map[registry.ObjectKey(type=self._options.type, id=self.id)] = self
        for object in object_map.values():
            object._set_related_fields(object_map)

    def _set_related_fields(self, object_map):
        for field in self._options.fields.values():
            if hasattr(field, 'set_related'):
                field.set_related(self, object_map)

    def _get_included_object_map_from_response(self, response):
        object_map = self._options.api.type_registry.get_mapped_orm_objects(response.included or [])
        return object_map

    @property
    def endpoint(self):
        return self._options.api.endpoint('{}/{}/'.format(self._options.type, self.id))

    _options = Options(None, None, {})
