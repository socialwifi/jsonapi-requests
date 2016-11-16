from urllib import parse

import requests

from jsonapi_requests import configuration


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


class JsonApiObject(Record):
    schema = {
        'type': Scalar,
        'id': Scalar,
        'attributes': Dictionary,
        'relationships': Dictionary,
        'links': Dictionary,
    }

    # noinspection PyMissingConstructor
    def __init__(self, *, type=None, id=None, attributes=None, relationships=None, links=None):
        self.type = type
        self.id = id
        self.attributes = attributes
        self.relationships = relationships
        self.links = links


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


class ApiRequestFactory:
    def __init__(self, config: configuration.Configuration):
        self.config = config

    def get(self, api_path, **kwargs):
        return self.request(api_path, 'GET', **kwargs)

    def post(self, api_path, **kwargs):
        return self.request(api_path, 'POST', **kwargs)

    def delete(self, api_path, **kwargs):
        return self.request(api_path, 'DELETE', **kwargs)

    def put(self, api_path, **kwargs):
        return self.request(api_path, 'PUT', **kwargs)

    def patch(self, api_path, **kwargs):
        return self.request(api_path, 'PATCH', **kwargs)

    def request(self, api_path, method, *, object=None, **kwargs):
        url = self._build_absolute_url(api_path)
        if object is not None:
            assert 'json' not in kwargs
            kwargs['json'] = {'data': object.as_data()}
        try:
            response = self._request(url, method, **kwargs)
        except (requests.ConnectionError, requests.Timeout):
            raise ApiConnectionError
        else:
            return self._parse_response(response)

    def _build_absolute_url(self, api_path):
        url = parse.urljoin(self.config.API_ROOT, api_path)
        if self.config.APPEND_SLASH and not url.endswith('/'):
            url += '/'
        return url

    def _request(self, absolute_url, method, **kwargs):
        options = self.default_options
        options.update(self.configured_options)
        options.update(kwargs)
        return requests.request(method, absolute_url, **options)

    @property
    def default_options(self):
        return {
            'headers': {
                'Content-Type': 'application/vnd.api+json',
                'Accept': 'application/vnd.api+json',
            }
        }

    @property
    def configured_options(self):
        options = {'verify': self.config.VALIDATE_SSL}
        if self.config.AUTH:
            options['auth'] = self.config.AUTH
        if self.config.TIMEOUT:
            options['timeout'] = self.config.TIMEOUT
        return options

    def _parse_response(self, response):
        if response.status_code >= 500:
            raise ApiInternalServerError(response.status_code, response.content)
        elif 400 <= response.status_code < 500:
            raise ApiClientError(response.status_code, response.content)
        try:
            payload = response.json()
        except ValueError:
            raise ApiInvalidResponseError(response.status_code, response.content)
        else:
            return ApiResponse(response.status_code, payload)


class ApiResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    @property
    def data(self):
        data = self.content.data
        if data is None:
            return {}
        else:
            return data

    @property
    def content(self):
        return JsonApiResponse.from_data(self.payload)

    def __repr__(self):
        return '<ApiResponse({})>'.format(self.payload)


class ApiRequestError(Exception):
    pass


class ApiResponseError(ApiRequestError):
    pass


class ApiInvalidResponseError(ApiRequestError):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content


class ApiInternalServerError(ApiInvalidResponseError):
    pass


class ApiClientError(ApiInvalidResponseError):
    pass


class ApiConnectionError(ApiRequestError):
    pass
