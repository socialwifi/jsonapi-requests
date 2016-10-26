class Configuration:
    def __init__(self, config_dict):
        self._config_dict = config_dict

    @property
    def API_ROOT(self):
        return self._config_dict['API_ROOT']

    @property
    def AUTH(self):
        return self._config_dict.get('AUTH', None)

    @property
    def VALIDATE_SSL(self):
        return self._config_dict.get('VALIDATE_SSL', True)

    @property
    def TIMEOUT(self):
        return self._config_dict.get('TIMEOUT', 1)
