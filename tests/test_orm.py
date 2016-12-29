from unittest import mock

from jsonapi_requests import orm


class TestApiModel:
    def test_empty_declaration(self):
        class Test(orm.ApiModel):
            pass

    def test_refresh(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.get.return_value.content.data = mock.Mock(attributes={'name': 'alice'})
        orm_api = orm.OrmApi(mock_api)

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            name = orm.AttributeField(source='name')

        test = Test.from_id('123')
        test.refresh()
        mock_api.endpoint.assert_called_with('test/123/')
        assert test.name == 'alice'

    def test_refresh_with_relationships(self):
        mock_api = mock.Mock()
        mock_api.endpoint.return_value.get.return_value.content = mock.MagicMock(
            data=mock.Mock(relationships={'other': mock.Mock(data=mock.Mock(id='1', type='test'))}),
            included=[mock.MagicMock(id='1', type='test', attributes={'name': 'alice'})]
        )
        orm_api = orm.OrmApi(mock_api)

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            other = orm.RelationField(source='other')
            name = orm.AttributeField(source='name')

        test = Test.from_id('123')
        test.refresh()

        assert test.other.name == 'alice'

    def test_from_response_with_relationships(self):
        response_content = mock.MagicMock(
            data=mock.Mock(relationships={'other': mock.Mock(data=mock.Mock(id='1', type='test'))}),
            included=[mock.MagicMock(id='1', type='test', attributes={'name': 'alice'})]
        )
        orm_api = orm.OrmApi(None)

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            other = orm.RelationField(source='other')
            name = orm.AttributeField(source='name')

        test = Test.from_response_content(response_content)
        assert test.other.name == 'alice'
