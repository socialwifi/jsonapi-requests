from unittest import mock

from jsonapi_requests import data
from jsonapi_requests import orm


class TestApiModel:
    def test_empty_declaration(self):
        class Test(orm.ApiModel):
            pass

    def test_refresh(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.get.return_value.content.data = data.JsonApiObject(
            type='test', id='123', attributes={'name': 'alice'})
        orm_api = orm.OrmApi(mock_api)

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            name = orm.AttributeField(source='name')

        test = Test.from_id('123')
        test.refresh()
        mock_api.endpoint.assert_called_with('test/123')
        assert test.name == 'alice'

    def test_refresh_with_relationships(self):
        mock_api = mock.Mock()
        mock_api.endpoint.return_value.get.return_value.content = data.JsonApiResponse(
            data=data.JsonApiObject(
                type='test', id='123', relationships={
                    'other': data.Relationship(data=data.ResourceIdentifier(id='1', type='test'))
                }
            ),
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
        response_content = data.JsonApiResponse(
            data=data.JsonApiObject(type='test', relationships={
                'other': data.Relationship(data=data.ResourceIdentifier(id='1', type='test'))
            }),
            included=[mock.MagicMock(id='1', type='test', attributes={'name': 'alice'})]
        )
        orm_api = orm.OrmApi(mock.MagicMock())

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            other = orm.RelationField(source='other')
            name = orm.AttributeField(source='name')

        test = Test.from_response_content(response_content)
        assert test.other.name == 'alice'

    def test_from_response_with_relationship_with_none_type(self):
        response_content = data.JsonApiResponse(
            data=data.JsonApiObject(id='1', type='test', relationships={
                'other': data.Relationship(data=data.ResourceIdentifier(id=None, type=None))
            })
        )
        orm_api = orm.OrmApi(mock.MagicMock())

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            other = orm.RelationField(source='other')
            name = orm.AttributeField(source='name')

        test = Test.from_response_content(response_content)
        assert test.other is None

    def test_issue_19_attributes_are_readable_with_multiple_relations(self):
        response_content = data.JsonApiResponse(
            data=data.JsonApiObject(
                type='designs',
                relationships={'sub_designs': data.Relationship(data=[data.ResourceIdentifier(id=3, type='designs')])},
                attributes={'name': 'doctor_x'}
            ),
        )
        orm_api = orm.OrmApi(mock.MagicMock())

        class Design(orm.ApiModel):
            class Meta:
                type = 'designs'
                api = orm_api

            name = orm.AttributeField('name')
            sub_designs = orm.RelationField('sub_designs')

        design = Design.from_response_content(response_content)
        assert design.name == 'doctor_x'

    def test_saving_new(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.post.return_value.status_code = 201
        mock_api.endpoint.return_value.post.return_value.content.data = data.JsonApiObject(
            attributes={'name': 'doctor_x'},
            id='1',
            type='test'
        )
        orm_api = orm.OrmApi(mock_api)

        class Design(orm.ApiModel):
            class Meta:
                type = 'designs'
                api = orm_api

            name = orm.AttributeField('name')

        design = Design()
        design.name = 'doctor_x'
        assert design.id is None
        design.save()
        assert design.id == '1'
        mock_api.endpoint.return_value.post.assert_called_with(
            object=data.JsonApiObject.from_data({'type': 'designs', 'attributes': {'name': 'doctor_x'}})
        )

    def test_creating_with_id(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.post.return_value.status_code = 204
        orm_api = orm.OrmApi(mock_api)

        class Design(orm.ApiModel):
            class Meta:
                type = 'designs'
                api = orm_api

            name = orm.AttributeField('name')

        design = Design()
        design.id = '1'
        design.name = 'doctor_x'
        design.create()
        assert design.raw_object.id == '1'
        mock_api.endpoint.return_value.post.assert_called_with(
            object=data.JsonApiObject.from_data({'id': '1', 'type': 'designs', 'attributes': {'name': 'doctor_x'}})
        )

    def test_saving_updated(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.patch.return_value.status_code = 204
        orm_api = orm.OrmApi(mock_api)

        class Design(orm.ApiModel):
            class Meta:
                type = 'designs'
                api = orm_api

            name = orm.AttributeField('name')

        design = Design()
        design.name = 'doctor_x'
        design.id = '1'
        design.save()
        mock_api.endpoint.return_value.patch.assert_called_with(
            object=data.JsonApiObject.from_data({'id': '1', 'type': 'designs', 'attributes': {'name': 'doctor_x'}})
        )

    def test_saving_updated_with_some_server_side_changes(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.patch.return_value.status_code = 200
        mock_api.endpoint.return_value.patch.return_value.content = mock.MagicMock(
            data=mock.Mock(
                type='designs',
                attributes={'name': 'doctor_x', 'status': 'complete'}
            ),
        )
        orm_api = orm.OrmApi(mock_api)

        class Design(orm.ApiModel):
            class Meta:
                type = 'designs'
                api = orm_api

            name = orm.AttributeField('name')
            status = orm.AttributeField('status')

        design = Design()
        design.name = 'doctor_x'
        design.id = '1'
        design.save()
        mock_api.endpoint.return_value.patch.assert_called_with(
            object=data.JsonApiObject.from_data({'id': '1', 'type': 'designs', 'attributes': {'name': 'doctor_x'}})
        )
        assert design.status == 'complete'

    def test_saving_updated_with_metadata(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.patch.return_value.status_code = 200
        mock_api.endpoint.return_value.patch.return_value.content = data.JsonApiResponse.from_data({
            'meta': {'success-level': 'great'}
        })
        orm_api = orm.OrmApi(mock_api)

        class Design(orm.ApiModel):
            class Meta:
                type = 'designs'
                api = orm_api

            name = orm.AttributeField('name')
        
        design = Design()
        design.name = 'doctor_x'
        design.id = '1'
        design.save()
        mock_api.endpoint.return_value.patch.assert_called_with(
            object=data.JsonApiObject.from_data({'id': '1', 'type': 'designs', 'attributes': {'name': 'doctor_x'}})
        )
        assert design.name == 'doctor_x'

    def test_relation_to_main_object(self):
        response_content = mock.MagicMock(
            data=mock.Mock(
                id=2,
                type='designs',
                relationships={'sub_designs': mock.Mock(data=mock.Mock(id=3, type='designs'))},
                attributes={'name': 'doctor_x'}
            ),
            included=[
                mock.Mock(
                    id=3,
                    type='designs',
                    relationships={'sub_designs': mock.Mock(data=mock.Mock(id=2, type='designs'))},
                    attributes={'name': 'doctor_y'}
                ),
            ],
        )
        orm_api = orm.OrmApi(mock.MagicMock())

        class Design(orm.ApiModel):
            class Meta:
                type = 'designs'
                api = orm_api

            name = orm.AttributeField('name')
            sub_designs = orm.RelationField('sub_designs')

        design = Design.from_response_content(response_content)
        assert design.sub_designs.sub_designs.name == 'doctor_x'

    def test_saving_relation_to_many(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.patch.return_value.status_code = 200
        orm_api = orm.OrmApi(mock_api)

        class Design(orm.ApiModel):
            class Meta:
                type = 'designs'
                api = orm_api

            others = orm.RelationField('others')

        design = Design()
        design.id = '1'
        design.others = [design]
        design.save()
        mock_api.endpoint.return_value.patch.assert_called_with(
            object=data.JsonApiObject.from_data({
                'id': '1',
                'type': 'designs',
                'relationships': {'others': {'data': [{'type': 'designs', 'id': '1'}]}}
            })
        )

    def test_getting_list(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.get.return_value.content.data = [mock.Mock(
            type='test', id='123', attributes={'name': 'alice'})]
        orm_api = orm.OrmApi(mock_api)

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            name = orm.AttributeField(source='name')

        result = Test.get_list()
        mock_api.endpoint.assert_called_with('test')
        assert result[0].name == 'alice'

    def test_getting_list_with_relationships(self):
        mock_api = mock.Mock()
        mock_api.endpoint.return_value.get.return_value.content = mock.MagicMock(
            data=[mock.Mock(
                type='test', id='123', attributes={'name': 'bob'},
                relationships={'other': mock.Mock(data=mock.Mock(id='1', type='test'))}
            ), mock.MagicMock(
                type='test', id='1', attributes={'name': 'alice'}
            )],
            included=[]
        )
        orm_api = orm.OrmApi(mock_api)

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            other = orm.RelationField(source='other')
            name = orm.AttributeField(source='name')

        result = Test.get_list()
        mock_api.endpoint.assert_called_with('test')
        assert result[0].name == 'bob'
        assert result[1].name == 'alice'
        assert result[0].other.name == 'alice'


    def test_delete(self):
        mock_api = mock.MagicMock()
        mock_api.endpoint.return_value.get.return_value.content.data = data.JsonApiObject(
            type='test', id='123', attributes={'name': 'alice'})
        mock_api.endpoint.return_value.delete.return_value.status_code = 204
        orm_api = orm.OrmApi(mock_api)

        class Test(orm.ApiModel):
            class Meta:
                api = orm_api
                type = 'test'
            name = orm.AttributeField(source='name')

        test = Test.from_id('123')
        test.delete()
        mock_api.endpoint.assert_called_with('test/123')
        mock_api.endpoint.return_value.delete.assert_called()

