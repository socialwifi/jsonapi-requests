Changelog for jsonapi-requests
=================

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
