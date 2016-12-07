from jsonapi_requests import base, data


class JsonApiObjectStub:
    is_stub = True

    def __init__(self, id):
        self.id = id


class ApiModelMetaclass(type):
    def __new__(mcs, name, args, kwargs):
        klass = super().__new__(mcs, name, args, kwargs)
        if 'Meta' in kwargs:
            klass._options = Options(kwargs['Meta'])
        return klass


class Options:
    def __init__(self, meta):
        self.meta = meta

    @property
    def type(self):
        return getattr(self.meta, 'type', None)

    @property
    def api(self):
        return getattr(self.meta, 'api', None)


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

    _options = Options(None)
