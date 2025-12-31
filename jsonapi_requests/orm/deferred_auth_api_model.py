from typing import Callable

from jsonapi_requests.orm import ApiModel, OrmApi
from jsonapi_requests.orm.api_model import OptionsFactory, Options, ApiModelMetaclass


class JSONAPIClientNotFound(KeyError):
    pass


class DeferredAuthOptionsFactory(OptionsFactory):
    """API Options Factory connected to flask.g for jsonapi client fetch."""

    def __init__(self, klass, klass_attrs):
        super().__init__(klass, klass_attrs)
        self._api_builder = None

    def get(self):
        api = self.api_builder()
        return Options(type=self.type, api=api, fields=self.fields, path=self.path)

    @property
    def api_builder(self) -> Callable[..., OrmApi]:
        return self._api_builder

    @api_builder.setter
    def api_builder(self, api_builder: Callable[..., OrmApi]):
        self._api_builder = api_builder


class DeferredAuthOptionsFactoryMetaclass(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)


class DeferredAuthAPIModelMetaclass(ApiModelMetaclass, type):
    """A Metaclass enabling complex querying of JSONAPI resources, building API config options later than class def."""

    def __init__(metacls, cls, bases, classdict):
        """Defer options construction to a later stage than class definition.

        Args:
            metacls: this metaclass instance
            cls: the class name for the class to create
            bases: the base classes for the class to create
            classdict: all the attributes and methods to put inside the __dict__
        """
        super().__init__(cls, bases, classdict)
        metacls.classdict = classdict
        metacls._options = None

    def __call__(self, *args, **kwargs):
        """Defer API configuration at class instantiation time and not definition time.

        Args:
            args : tuple, Position only arguments of the new class
            kwargs : dict, Keyword only arguments of the new class

        """
        instance = DeferredAuthApiModel.__new__(self)
        DeferredAuthApiModel.__init__(instance, *args, **kwargs)
        if not hasattr(instance, "api"):
            raise NotImplementedError(
                f"Instance of class {instance.__class__.__name__} is derived from"
                f" metaclass {self.__class__.__name__}. "
                "Therefore it is required to implement interface classmethod"
                f" `{instance.__class__.__name__}.api`."
            )
        _options_factory = DeferredAuthOptionsFactory(self, self.classdict)
        _options_factory.api_builder = instance.api
        self._options = _options_factory.get()
        if self._options.api and self._options.type:
            self._options.api.type_registry.register(instance.__class__)
        return instance


class DeferredAuthApiModel(ApiModel, metaclass=DeferredAuthAPIModelMetaclass):
    """An ORM Model for PR-API resources objects, able to build complex JSONAPI queries."""

    @classmethod
    def api(cls) -> OrmApi:
        raise NotImplementedError(
            "Any class derived from metaclass DeferredAuthAPIModelMetaclass should implement api classmethod."
        )
