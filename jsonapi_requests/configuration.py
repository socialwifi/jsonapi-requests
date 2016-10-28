from collections import namedtuple


Configuration = namedtuple(
    'Configuration',
    ['API_ROOT', 'AUTH', 'VALIDATE_SSL', 'TIMEOUT', 'APPEND_SLASH']
)


class Factory:
    def __init__(self, config_dict):
        self._config_dict = config_dict

    def create(self) -> Configuration:
        return Configuration(
            API_ROOT=self.API_ROOT,
            AUTH=self.AUTH,
            VALIDATE_SSL=self.VALIDATE_SSL,
            TIMEOUT=self.TIMEOUT,
            APPEND_SLASH=self.APPEND_SLASH,
        )

    @property
    def API_ROOT(self):
        url = self._config_dict['API_ROOT']
        if not url.endswith('/'):
            url += '/'
        return url

    @property
    def AUTH(self):
        return self._config_dict.get('AUTH', None)

    @property
    def VALIDATE_SSL(self):
        return self._config_dict.get('VALIDATE_SSL', True)

    @property
    def TIMEOUT(self):
        return self._config_dict.get('TIMEOUT', 1)

    @property
    def APPEND_SLASH(self):
        return self._config_dict.get('APPEND_SLASH', True)
