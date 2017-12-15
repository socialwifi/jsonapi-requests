import abc


class BaseFieldConverter(abc.ABC):
    @abc.abstractmethod
    def decode(self, json_value):
        return json_value

    @abc.abstractmethod
    def encode(self, value):
        return value


class EnumConverter(BaseFieldConverter):
    def __init__(self, enum_cls, encode_as_name=False):
        self.enum_cls = enum_cls
        self.encode_as_name = encode_as_name

    def decode(self, json_value):
        if self.encode_as_name:
            return self.enum_cls[json_value]

        return self.enum_cls(json_value)

    def encode(self, value):
        if self.encode_as_name:
            return value.name

        return value.value
