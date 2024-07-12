import jsonapi_requests.data


class TestJsonApiResponse:
    def test_keeps_example(self):
        assert jsonapi_requests.data.JsonApiResponse.from_data(example_response).as_data() == example_response

    def test_links_always_present_in_parsed_response(self):
        parsed = jsonapi_requests.data.JsonApiResponse.from_data({})
        parsed.links['xxx'] = 'fake'
        assert parsed.as_data() == {'links': {'xxx': 'fake'}}

    def test_add_object_to_parsed_response(self):
        parsed = jsonapi_requests.data.JsonApiResponse.from_data({'data': []})
        parsed.data.append({'id': '1', 'type': 'x'})
        assert parsed.as_data() == {'data': [{'id': '1', 'type': 'x'}]}

    def test_remove_object_from_parsed_response(self):
        parsed = jsonapi_requests.data.JsonApiResponse.from_data({'data': [{'id': '1', 'type': 'x'}]})
        del parsed.data[0]
        assert parsed.as_data() == {'data': []}

    def test_add_included_object_to_parsed_response(self):
        parsed = jsonapi_requests.data.JsonApiResponse.from_data({'included': [{'id': '1', 'type': 'x'}]})
        del parsed.included[0]
        assert parsed.as_data() == {}

    def test_remove_included_object_from_parsed_response(self):
        parsed = jsonapi_requests.data.JsonApiResponse.from_data({})
        parsed.included.append({'id': '1', 'type': 'x'})
        assert parsed.as_data() == {'included': [{'id': '1', 'type': 'x'}]}

    def test_add_relationship_to_parsed_response(self):
        parsed = jsonapi_requests.data.JsonApiResponse.from_data({})
        parsed.data.relationships['chicken'] = {'data': {'type': 'chicken', 'id': '2'}}
        assert parsed.as_data() == {'data': {'relationships': {'chicken': {'data': {'type': 'chicken', 'id': '2'}}}}}

    def test_remove_relationship_from_parsed_response(self):
        parsed = jsonapi_requests.data.JsonApiResponse.from_data(
          {'data': {'relationships': {'chicken': {'data': {'type': 'chicken', 'id': '2'}}}}},
        )
        del parsed.data.relationships['chicken']
        assert parsed.as_data() == {}


example_response = {
  "links": {
    "self": "http://example.com/articles",
    "next": "http://example.com/articles?page[offset]=2",
    "last": "http://example.com/articles?page[offset]=10",
  },
  "data": [{
    "type": "articles",
    "id": "1",
    "attributes": {
      "title": "JSON API paints my bikeshed!",
    },
    "relationships": {
      "author": {
        "links": {
          "self": "http://example.com/articles/1/relationships/author",
          "related": "http://example.com/articles/1/author",
        },
        "data": {"type": "people", "id": "9"},
      },
      "comments": {
        "links": {
          "self": "http://example.com/articles/1/relationships/comments",
          "related": "http://example.com/articles/1/comments",
        },
        "data": [
          {"type": "comments", "id": "5"},
          {"type": "comments", "id": "12"},
        ],
      },
    },
    "links": {
      "self": "http://example.com/articles/1",
    },
  }],
  "included": [{
    "type": "people",
    "id": "9",
    "attributes": {
      "first-name": "Dan",
      "last-name": "Gebhardt",
      "twitter": "dgeb",
    },
    "links": {
      "self": "http://example.com/people/9",
    },
  }, {
    "type": "comments",
    "id": "5",
    "attributes": {
      "body": "First!",
    },
    "relationships": {
      "author": {
        "data": {"type": "people", "id": "2"},
      },
    },
    "links": {
      "self": "http://example.com/comments/5",
    },
  }, {
    "type": "comments",
    "id": "12",
    "attributes": {
      "body": "I like XML better",
    },
    "relationships": {
      "author": {
        "data": {"type": "people", "id": "9"},
      },
    },
    "links": {
      "self": "http://example.com/comments/12",
    },
  }],
}
