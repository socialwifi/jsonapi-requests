from urllib import parse

import requests

from jsonapi_requests import configuration


class JsonApiObject:
    meta_fields = ['type', 'id', 'attributes', 'relations', 'links']

    def __init__(self, *, type=None, id=None, attributes=None, relations=None, links=None):
        self.type = type
        self.id = id
        self.attributes = attributes
        self.relations = relations
        self.links = links

    @classmethod
    def from_data(cls, data):
        filtered = {}
        for field in cls.meta_fields:
            filtered[field] = data.get(field)
        return cls(**filtered)

    def as_data(self):
        data = {}
        for field in self.meta_fields:
            value = getattr(self, field)
            if value is not None:
                data[field] = value
        return data


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
        absolute_url = parse.urljoin(self.config.API_ROOT, api_path)
        if object is not None:
            assert 'json' not in kwargs
            kwargs['json'] = {'data': object.as_data()}
        try:
            response = self._request(absolute_url, method, **kwargs)
        except (requests.ConnectionError, requests.Timeout):
            raise ApiConnectionError
        else:
            return self._parse_response(response)

    def _request(self, absolute_url, method, **kwargs):
        options = self.configured_options
        options.update(kwargs)
        return requests.request(method, absolute_url, **options)

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
        if isinstance(self.raw_data, list):
            return [
                JsonApiObject.from_data(instance) for instance in self.raw_data
            ]
        else:
            return JsonApiObject.from_data(self.raw_data)

    @property
    def raw_data(self):
        if 'data' in self.payload:
            return self.payload['data']
        else:
            return {}

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
