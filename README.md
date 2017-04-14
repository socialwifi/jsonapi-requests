# jsonapi-requests

[![Build Status](https://travis-ci.org/socialwifi/jsonapi-requests.svg?branch=master)](https://travis-ci.org/socialwifi/jsonapi-requests)
[![Latest Version](https://img.shields.io/pypi/v/jsonapi-requests.svg)](https://github.com/socialwifi/jsonapi-requests/blob/master/CHANGELOG.md)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/jsonapi-requests.svg)](https://pypi.python.org/pypi/jsonapi-requests/)
[![Wheel Status](https://img.shields.io/pypi/wheel/jsonapi-requests.svg)](https://pypi.python.org/pypi/jsonapi-requests/)
[![License](https://img.shields.io/pypi/l/jsonapi-requests.svg)](https://github.com/socialwifi/jsonapi-requests/blob/master/LICENSE)

Python client implementation for json api. http://jsonapi.org/

----
## Usage example

    In [1]: import jsonapi_requests

    In [2]: api = jsonapi_requests.Api.config({
        ...:     'API_ROOT': 'https://localhost/api/2.0',
        ...:     'AUTH': ('basic_auth_login', 'basic_auth_password'),
        ...:     'VALIDATE_SSL': False,
        ...:     'TIMEOUT': 1,
        ...: })
        ...:

    In [3]: endpoint = api.endpoint('networks/cd9c124a-acc3-4e20-8c02-3a37d460df22/available-profiles')

    In [4]: response = endpoint.get()

    In [5]: for profile in  response.data:
        ...:     print(profile.attributes['name'])
        ...:
    162 Sushi
    In [6]: endpoint = api.endpoint('cookies')
    In [7]: endpoint.post(object=jsonapi_requests.JsonApiObject(
        attributes={'uuid': '09d3a4fff8d64335a1ee9f1d9d054161', 'domain': 'some.domain.pl'},
        type='cookies'))
    Out[7]: <ApiResponse({'data': {'id': '81', 'attributes': {'uuid': '09d3a4fff8d64335a1ee9f1d9d054161', 'domain': 'some.domain.pl'}, 'type': 'cookies'}})>

## Orm example

Lets say we have api endpoint: https://localhost/api/2.0/car/2
which returns

    {
        'data':{
            'id': 2,
            'type': 'car',
            'attributes': {'color': 'red'},
            'relationships': {'driver':{'data': {'id': 3, 'type': 'person'}}}
        },
        'included':[
            {
                'id': 3,
                'type': 'person',
                'attributes': {'name': 'Kowalski'},
                'relationships': {'married-to': {'data': {'id': 4, 'type': 'person'}}}
            },
            {
                'id': 4,
                'type': 'person',
                'attributes': {'name': 'Kowalska'},
                'relationships': {'married-to': {'data': {'id': 3, 'type': 'person'}}}
            },
        ]
    }

Then we can run:

    In [1]: import jsonapi_requests

    In [2]: api = jsonapi_requests.orm.OrmApi.config({
        ...:         ...:     'API_ROOT': 'https://localhost/api/2.0',
        ...:         ...:     'AUTH': ('basic_auth_login', 'basic_auth_password'),
        ...:         ...:     'VALIDATE_SSL': False,
        ...:         ...:     'TIMEOUT': 1,
        ...:         ...: })

    In [3]: class Person(jsonapi_requests.orm.ApiModel):
        ...:     class Meta:
        ...:         type = 'person'
        ...:         api = api
        ...:
        ...:     name = jsonapi_requests.orm.AttributeField('name')
        ...:     married_to = jsonapi_requests.orm.RelationField('married-to')
        ...:

    In [4]: class Car(jsonapi_requests.orm.ApiModel):
        ...:     class Meta:
        ...:         type = 'car'
        ...:         api = api
        ...:
        ...:     color = jsonapi_requests.orm.AttributeField('color')
        ...:     driver = jsonapi_requests.orm.RelationField('driver')
        ...:

    In [5]: car  = Car.from_id(2)

    In [6]: car.color # request happens here
    Out[6]: 'red'

    In [7]: car.driver.name
    Out[7]: 'Kowalski'

    In [8]: car.driver.married_to.name
    Out[8]: 'Kowalska'

    In [9]: car.driver.married_to.married_to.name
    Out[9]: 'Kowalski'

## Documentation
For more documentation check our [wiki](https://github.com/socialwifi/jsonapi-requests/wiki).
