from unittest import mock

from jsonapi_requests import data
from jsonapi_requests import orm


class TestField:
    def test_field_equivalence(self):
        import uuid

        class UuidField(orm.AttributeField):
            def deserialize(self, json_value):
                return uuid.UUID(json_value)

            def serialize(self, value):
                return str(value)

        class Test(orm.ApiModel):
            class Meta:
                type = 'test'
            value = UuidField(source='value')

        test = Test()
        val = uuid.uuid4()
        test.value = val
        assert test.value is val

    def test_custom_field_serialization(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.post.return_value.status_code = 201
        mock_api.endpoint.return_value.post.return_value.content.data = data.JsonApiObject(
            type='test',
            id='123',
            attributes={'name': 'alice', 'extra': '0x1000'}
        )
        orm_api = orm.OrmApi(mock_api)

        class HexField(orm.AttributeField):
            def deserialize(self, json_value):
                return int(json_value, 16)

            def serialize(self, value):
                return hex(value)

        hex_field = HexField(source='extra')

        # NOTE: assert_not_called() isn't used for py3.4 compatibility in this test
        decode_spy = mock.patch.object(HexField, 'deserialize', wraps=hex_field.deserialize).start()
        encode_spy = mock.patch.object(HexField, 'serialize', wraps=hex_field.serialize).start()

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            name = orm.AttributeField(source='name')
            extra = hex_field

        test = Test()
        test.name = 'alice'
        test.extra = 1024
        assert test.extra == 1024

        # verify that we can successfully change the value and re-read it
        test.extra = 2048
        assert test.extra == 2048

        # nothing should have been decoded at this point -- the reads (for assert) should have been cached
        assert not decode_spy.called
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
        assert not decode_spy.called
