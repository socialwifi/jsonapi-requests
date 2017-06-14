from jsonapi_requests import data
from jsonapi_requests.orm import fields as orm_fields
from jsonapi_requests.orm import repositories


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
            if 'list_endpoint' not in kwargs:
                cls.list_endpoint = cls._options.api.endpoint('{}/'.format(cls._options.type))


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
    def __init__(self, raw_object=None):
        self.raw_object = raw_object or data.JsonApiObject(type=self._options.type)
        self.relationship_cache = {}

    @classmethod
    def from_id(cls, id):
        return cls(raw_object=JsonApiObjectStub(id))


    @classmethod
    def get_list(cls):
        response = cls.list_endpoint.get()
        return cls.from_response_content(response.content)

    @classmethod
    def from_response_content(cls, jsonapi_response):
        repository = repositories.Repository(cls._options.api.type_registry)
        if hasattr(jsonapi_response.data, 'items'):
            assert jsonapi_response.data.type == cls._options.type
            result = cls(raw_object=jsonapi_response.data)
            repository.add(result)
        else:
            result = []
            for object in jsonapi_response.data:
                assert object.type == cls._options.type
                new = cls(raw_object=object)
                result.append(new)
                repository.add(new)
        repository.update_from_api_response(jsonapi_response)
        return result


    @property
    def type(self):
        if not self.is_stub:
            return self.raw_object.type
        else:
            return self._options.type

    @property
    def is_stub(self):
        return getattr(self.raw_object, 'is_stub', False)

    @property
    def id(self):
        return self.raw_object.id

    @id.setter
    def id(self, new_id):
        self.raw_object.id = new_id

    def __getattr__(self, item):
        try:
            return getattr(self.raw_object, item)
        except AttributeError:
            if self.is_stub:
                self.refresh()
                return getattr(self.raw_object, item)
            else:
                raise

    def as_identifier(self):
        return data.ResourceIdentifier(type=self.type, id=self.id)

    def refresh(self):
        api_response = self.endpoint.get()
        jsonapi_response = api_response.content
        assert jsonapi_response.data.type == self.type
        assert jsonapi_response.data.id == self.id
        repository = repositories.Repository(self._options.api.type_registry)
        repository.add(self)
        repository.update_from_api_response(jsonapi_response)

    def save(self):
        if not self.id:
            self.create()
        else:
            self.update()

    def create(self):
        api_response = self.list_endpoint.post(object=self.raw_object)
        if api_response.status_code == 201:
            self.raw_object = api_response.content.data

    def update(self):
        api_response = self.endpoint.patch(object=self.raw_object)
        if api_response.status_code == 200 and api_response.content.data:
            self.raw_object = api_response.content.data

    def set_related_fields(self, repository):
        for field in self._options.fields.values():
            if hasattr(field, 'set_related'):
                field.set_related(self, repository)

    @property
    def endpoint(self):
        return self._options.api.endpoint('{}/{}/'.format(self._options.type, self.id))

    _options = Options(None, None, {})
