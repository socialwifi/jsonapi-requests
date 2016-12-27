from jsonapi_requests.orm import fields as orm_fields


class JsonApiObjectStub:
    is_stub = True

    def __init__(self, id):
        self.id = id


class ApiModelMetaclass(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs, **kwargs)
        cls._options = OptionsFactory(cls, attrs).get()
        return cls


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

    @classmethod
    def from_id(cls, id):
        return cls(raw_object=JsonApiObjectStub(id))

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

    def refresh(self):
        response = self.endpoint.get()
        self.raw_object = response.data

    @property
    def endpoint(self):
        return self._options.api.endpoint('{}/{}/'.format(self._options.type, self.id))

    _options = Options(None, None, {})
