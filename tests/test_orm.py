from unittest import mock

from jsonapi_requests import orm


class TestApiModel:
    def test_empty_declaration(self):
        class Test(orm.ApiModel):
            pass

    def test_refresh(self):
        mock_api = mock.Mock()
        mock_api.endpoint.return_value.get.return_value.data = mock.Mock(attributes={'name': 'alice'})

        class Test(orm.ApiModel):
            class Meta:
                api = mock_api
                type = 'test'

        test = Test.from_id('123')
        test.refresh()
        mock_api.endpoint.assert_called_with('test/123/')
        assert test.attributes['name'] == 'alice'

