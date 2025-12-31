from typing import Optional

from jsonapi_requests import Api
from jsonapi_requests.auth import FlaskForwardAuth
from jsonapi_requests.orm import OrmApi
from jsonapi_requests.orm.deferred_auth_api_model import DeferredAuthApiModel


class FlaskAuthApiModel(DeferredAuthApiModel):
    @classmethod
    def api(cls) -> OrmApi:
        return OrmApi(
            Api.config({
                "API_ROOT": cls.api_root(),
                "AUTH": cls.auth(),
                "VALIDATE_SSL": cls.validate_ssl(),
                "TIMEOUT": cls.timeout(),
            })
        )

    @classmethod
    def auth(cls):
        return FlaskForwardAuth()

    @classmethod
    def timeout(cls) -> Optional[int]:
        raise NotImplementedError()

    @classmethod
    def validate_ssl(cls) -> bool:
        raise NotImplementedError()

    @classmethod
    def api_root(cls) -> str:
        raise NotImplementedError()
