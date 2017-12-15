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
       ...:     'API_ROOT': 'https://localhost/api/2.0',
       ...:     'AUTH': ('basic_auth_login', 'basic_auth_password'),
       ...:     'VALIDATE_SSL': False,
       ...:     'TIMEOUT': 1,
       ...: })

    In [3]: class Person(jsonapi_requests.orm.ApiModel):
       ...:     class Meta:
       ...:         type = 'person'
       ...:         api = api
       ...:
       ...:     name = jsonapi_requests.orm.AttributeField('name')
       ...:     married_to = jsonapi_requests.orm.RelationField('married-to')

    In [4]: class Car(jsonapi_requests.orm.ApiModel):
       ...:     class Meta:
       ...:         type = 'car'
       ...:         api = api
       ...:
       ...:     color = jsonapi_requests.orm.AttributeField('color')
       ...:     driver = jsonapi_requests.orm.RelationField('driver')

    In [5]: car  = Car.from_id(2)

    In [6]: car.color # request happens here
    Out[6]: 'red'

    In [7]: car.driver.name
    Out[7]: 'Kowalski'

    In [8]: car.driver.married_to.name
    Out[8]: 'Kowalska'

    In [9]: car.driver.married_to.married_to.name
    Out[9]: 'Kowalski'

### Custom Field Types

It's possible to use custom types for an `AttributeField` by subclassing `jsonapi_requests.orm.converters.BaseConverter`.
Example:

    from enum import Enum
    from uuid import UUID

    from jsonapi_requets import orm
    from jsonapi_requests.orm.converters import BaseConverter, EnumConverter
    
    class Color(Enum):
        RED = 'red'
        BLUE = 'blue'
       
    class UuidConverter(BaseConverter):
        def encode(self, value):
            # take a UUID object and make it JSON serializable
            return str(value)
        
        def decode(self, raw_value):
            # take the JSON value (a string in this case) and turn it into a UUID
            return UUID(raw_value)
    
    class Car(jsonapi_requests.orm.ApiModel):
        class Meta:
            type = 'car'
           
        color = jsonapi_requests.orm.AttributeField('color', converter=EnumConverter(Color)
        guid = jsonapi_requests.orm.AttributeField('guid', converter=UuidConverter())
    
    car = Car()
    car.color = Color.RED
    car.guid = UUID('4cbecc77-fc43-4d29-8915-222d87029ec3')
    car.save()


## Authorization HTTP header forwarding in Flask application

When using jsonapi\_requests with Flask, we can set `jsonapi_requests.auth.FlaskForwardAuth()` as `AUTH` configuration option to copy authorization header from current request context.
It can be useful when fetching resources from different microservices.

Installation with flask support:

    pip install jsonapi-requests[flask]

Example usage:

    import jsonapi_requests

    api = jsonapi_requests.Api.config({
        'API_ROOT': 'https://localhost/api/2.0',
        'AUTH': jsonapi_requests.auth.FlaskForwardAuth(),
    })

## Documentation
For more documentation check our [wiki](https://github.com/socialwifi/jsonapi-requests/wiki).
