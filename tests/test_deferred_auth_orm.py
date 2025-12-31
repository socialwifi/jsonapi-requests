from typing import Optional
from unittest import mock

import pytest
from flask import Flask
from jsonapi_requests import data

from jsonapi_requests.orm import AttributeField, RelationField

from jsonapi_requests.orm.deferred_auth_api_model import DeferredAuthApiModel
from jsonapi_requests.orm.flask.api_model import FlaskAuthApiModel


@pytest.fixture
def flask_app():
    app = Flask(__name__)
    yield app


@pytest.fixture
def valid_response():
    response = mock.Mock(status_code=200)
    response.json.return_value = {
        "data": data.JsonApiObject(type="person", id="123", attributes={"first-name": "alice"}).as_data()
    }
    return response


@pytest.fixture
def request_send_mock(valid_response):
    with mock.patch("requests.sessions.Session.send") as mocked:
        mocked.return_value = valid_response
        yield mocked


class FlaskClientToRailsServer(FlaskAuthApiModel):
    @classmethod
    def timeout(cls) -> Optional[int]:
        return None

    @classmethod
    def validate_ssl(cls) -> bool:
        return False

    @classmethod
    def api_root(cls) -> str:
        return "http://some.rails/api/endpoint/"


class TestDeferredAuthApiModel:
    def test_class_definition_without_api_meta_attribute(self):
        class Person(DeferredAuthApiModel):
            class Meta:
                type = "person"
                path = "patients"

            first_name = AttributeField("first-name")

    def test_class_instantiation_without_api_defined_method_raises_not_implemented(self):
        class Person(DeferredAuthApiModel):
            class Meta:
                type = "person"
                path = "patients"

            first_name = AttributeField("first-name")

        with pytest.raises(NotImplementedError):
            Person("123")


class TestFlaskAuthApiModel:
    def test_class_definition_without_api_meta_attribute(self):
        class Person(FlaskAuthApiModel):
            class Meta:
                type = "person"
                path = "http://some/api/endpoint/patients"

            first_name = AttributeField("first-name")

    def test_get_request(self, flask_app, request_send_mock):
        class Person(FlaskClientToRailsServer):
            class Meta:
                type = "person"
                path = "persons"

            first_name = AttributeField("first-name")

        with flask_app.app_context():
            with flask_app.test_request_context(
                headers={"Authorization": "Bearer 11111111-1111-1111-1111-111111111111"}
            ):
                _ = Person.from_id("123").first_name
                args, kwargs = request_send_mock.call_args
                headers = args[0].headers
                assert "Bearer 11111111-1111-1111-1111-111111111111" in headers["Authorization"]
