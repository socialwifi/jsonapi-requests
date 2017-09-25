from unittest import mock

import pytest

from flask import Flask

from jsonapi_requests import configuration
from jsonapi_requests import auth
from jsonapi_requests import request_factory


@pytest.fixture
def api_configuration():
    return configuration.Factory({'API_ROOT': 'http://testing', 'AUTH': auth.FlaskForwardAuth()}).create()


@pytest.fixture
def flask_app():
    app = Flask(__name__)
    yield app


@pytest.fixture
def valid_response():
    response = mock.Mock(status_code=200)
    response.json.return_value = {}
    return response


@pytest.fixture
def request_send_mock():
    with mock.patch('requests.sessions.Session.send') as mocked:
        mocked.return_value = valid_response()
        yield mocked


def test_flask_auth_forward(api_configuration, request_send_mock, flask_app):
    with flask_app.test_request_context(headers={'Authorization': 'Bearer 11111111-1111-1111-1111-111111111111'}):
        request_factory.ApiRequestFactory(api_configuration).get('endpoint')
    args, kwargs = request_send_mock.call_args
    headers = args[0].headers
    assert 'Bearer 11111111-1111-1111-1111-111111111111' in headers['Authorization']
