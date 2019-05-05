from collections.abc import Mapping

import os
import yaml

DEFAULT_CONF_NAME = 'conf.default.yml'


class Conf(Mapping):
    _instance = None

    @classmethod
    def reset(cls):
        cls._instance = None

    def __init__(self):
        super().__init__()
        self._data = {}

    def _load(self):
        # lazy loading of default config
        if Conf._instance is not None:
            return
        Conf._instance = self

        import pkg_resources
        default_conf = pkg_resources.resource_stream(
            'camisole', DEFAULT_CONF_NAME)
        with default_conf:
            self.merge(yaml.safe_load(default_conf))

        conf_from_environ = os.environ.get('CAMISOLE_CONF')
        if conf_from_environ:  # noqa
            with open(conf_from_environ) as f:
                self.merge(yaml.safe_load(f))

    def merge(self, data):
        self._load()

        def merge(data, into):
            for k, v in data.items():
                if (k in into and
                        isinstance(v, dict) and
                        isinstance(into[k], dict)):
                    merge(v, into[k])
                else:
                    into[k] = v
        merge(data, self._data)

    def __getitem__(self, item):
        self._load()
        return self._data[item]

    def __contains__(self, item):
        self._load()
        return item in self._data

    def __iter__(self):
        self._load()
        return iter(self._data)

    def __len__(self):
        self._load()
        return len(self._data)


conf = Conf()
