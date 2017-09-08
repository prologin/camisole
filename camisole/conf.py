from collections.abc import Mapping
import logging
import yaml

logger = logging.getLogger(__name__)

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
        import pkg_resources
        default_conf = pkg_resources.resource_stream(
            'camisole', DEFAULT_CONF_NAME)
        if hasattr(default_conf, 'name'):
            logger.debug("loading default conf from file %s", default_conf.name)
        self.merge(yaml.load(default_conf))
        Conf._instance = self

    def merge(self, data):
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
