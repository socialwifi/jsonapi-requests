Changelog for jsonapi-requests
=================

0.6.2 (unreleased)
------------------

- Nothing changed yet.


0.6.1 (2020-01-15)
------------------

- Added Python 3.7 and Python 3.8 support. ([#47](https://github.com/socialwifi/jsonapi-requests/pull/47))
- Dropped Python 3.4 support. ([#47](https://github.com/socialwifi/jsonapi-requests/pull/47))
- Fixed `id` type in documentation. 
([#47](https://github.com/socialwifi/jsonapi-requests/pull/47))
([#46](https://github.com/socialwifi/jsonapi-requests/issues/46))
- Added long description to package (for pypi description page). ([#48](https://github.com/socialwifi/jsonapi-requests/pull/48))


0.6.0 (2018-01-06)
------------------

- Added ability to delete a resource. ([#33](https://github.com/socialwifi/jsonapi-requests/pull/33))
- Allow passing arguments through to get_list. ([#34](https://github.com/socialwifi/jsonapi-requests/pull/34))
- Added exists method to ApiModel. ([#36](https://github.com/socialwifi/jsonapi-requests/pull/36))


0.5.0 (2017-12-13)
------------------

- Custom endpoint path support. ([#32](https://github.com/socialwifi/jsonapi-requests/pull/32))


0.4.1 (2017-11-15)
------------------

- Fixed saving "to many" relation.


0.4.0 (2017-09-25)
------------------

- Added `jsonapi_requests.auth.FlaskForwardAuth()` as `AUTH` configuration option.
- Added Flask as optional dependency.


0.3.2 (2017-07-28)
------------------

- Fixed `orm.ApiModel` not respecting `APPEND_SLASH` configuration. ([#27](https://github.com/socialwifi/jsonapi-requests/issues/27))


0.3.1 (2017-07-03)
------------------

- Fixed single object orm response.


0.3.0 (2017-06-20)
------------------

- Added save method in orm.
- Added get_list method in orm.
- Basic support for to many relationship in orm.
- Include orm in jsonapi-requests import.


0.2.1 (2017-02-03)
------------------

- Added RETRIES configuration (default 3)
- Added retrying requests when there is network or server side problem.
- Added Python 3.6 to supported versions.
- Fixed handling relations with none value.


0.2.0 (2017-01-02)
------------------

- Added basic orm. ([#11](https://github.com/socialwifi/jsonapi-requests/pull/11))
- Added more parsers and serializers.
- Added pytest tests.
- Fix handling response 204 "No content" ([#10](https://github.com/socialwifi/jsonapi-requests/pull/10))


0.1 (2016-11-04)
----------------

- Append slash to API root if needed. ([#2](https://github.com/socialwifi/jsonapi-requests/pull/2))
- Allow to automatically append slash. ([#4](https://github.com/socialwifi/jsonapi-requests/pull/4))
- Set headers according to JSON:API specification. ([#3](https://github.com/socialwifi/jsonapi-requests/pull/3))


0.0 (2016-10-27)
----------------

- Initial lowlevel api.
