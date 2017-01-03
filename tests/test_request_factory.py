import pytest
import requests
from unittest import mock

from jsonapi_requests import request_factory
from jsonapi_requests import data
from jsonapi_requests import configuration


@pytest.fixture
def api_configuration():
    return configuration.Factory({'API_ROOT': 'testing', 'RETRIES': 2}).create()


@pytest.fixture
def request_mock():
    with mock.patch('requests.request') as mocked:
        yield mocked


@pytest.fixture
def valid_response():
    response = mock.Mock(status_code=200)
    response.json.return_value = {}
    return response


def test_get(api_configuration, request_mock, valid_response):
    request_mock.return_value = valid_response
    response = request_factory.ApiRequestFactory(api_configuration).get('endpoint')
    assert response.content == data.JsonApiResponse.from_data({})


def test_retrying(api_configuration, request_mock, valid_response):
    request_mock.side_effect = [requests.Timeout, valid_response]
    response = request_factory.ApiRequestFactory(api_configuration).get('endpoint')
    assert response.content == data.JsonApiResponse.from_data({})


def test_reraises(api_configuration, request_mock, valid_response):
    request_mock.side_effect = [requests.Timeout, requests.Timeout, valid_response]
    with pytest.raises(request_factory.ApiConnectionError):
        request_factory.ApiRequestFactory(api_configuration).get('endpoint')
