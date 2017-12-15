import enum

from unittest import mock

from jsonapi_requests import data
from jsonapi_requests import orm
from jsonapi_requests.orm import converters


class TestFieldConverters:
    def test_enum_converter_value(self):
        class Test(enum.Enum):
            valueA = 0
            valueB = 1
            valueC = 2

        converter = converters.EnumConverter(Test)
        assert converter.encode(Test.valueA) == 0
        assert converter.decode(2) is Test.valueC

    def test_enum_converter_name(self):
        class Test(enum.Enum):
            valueA = 0
            valueB = 1
            valueC = 2

        converter = converters.EnumConverter(Test, encode_as_name=True)
        assert converter.encode(Test.valueA) == 'valueA'
        assert converter.decode('valueC') is Test.valueC

    def test_custom_field_converter(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.post.return_value.status_code = 201
        mock_api.endpoint.return_value.post.return_value.content.data = data.JsonApiObject(
            type='test',
            id='123',
            attributes={'name': 'alice', 'extra': '0x1000'}
        )
        orm_api = orm.OrmApi(mock_api)

        class HexConverter(converters.BaseFieldConverter):
            def decode(self, json_value):
                return int(json_value, 16)

            def encode(self, value):
                return hex(value)

        converter = HexConverter()
        # NOTE: assert_has_calls([]) used in place of assert_not_called() for py3.4 compatibility in this test
        decode_spy = mock.patch.object(converter, 'decode', wraps=converter.decode).start()
        encode_spy = mock.patch.object(converter, 'encode', wraps=converter.encode).start()

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            name = orm.AttributeField(source='name')
            extra = orm.AttributeField(source='extra', converter=converter)

        test = Test()
        test.name = 'alice'
        test.extra = 1024
        assert test.extra == 1024

        # verify that we can successfully change the value and re-read it
        test.extra = 2048
        assert test.extra == 2048

        # nothing should have been decoded at this point -- the reads (for assert) should have been cached
        decode_spy.assert_has_calls([])
        # should have done an encode for each set
        encode_spy.assert_has_calls([mock.call(1024), mock.call(2048)], any_order=False)
        encode_spy.reset_mock()

        test.save()

        mock_api.endpoint.return_value.post.assert_called_with(
            object=data.JsonApiObject.from_data(
                {
                    'type': 'test',
                    'attributes': {'name': 'alice', 'extra': '0x800'}
                }
            )
        )

        # no further encoding/decoding should have happened
        decode_spy.assert_has_calls([])
        decode_spy.assert_has_calls([])

        # verify that the new value that the API returned was set and decoded properly
        assert test.extra == 4096
        decode_spy.assert_called_once_with('0x1000')
        decode_spy.reset_mock()

        # read the property again but check that we didn't re-decode it
        assert test.extra == 4096
        decode_spy.assert_has_calls([])
