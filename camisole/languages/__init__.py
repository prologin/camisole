from pathlib import Path
from typing import Mapping, Type
import importlib
import logging
import os
import sys

logger = logging.getLogger(__name__)

from camisole.models import Lang
from camisole.conf import conf


def all() -> Mapping[str, Type[Lang]]:
    return Lang._registry


def by_name(name: str) -> Type[Lang]:
    return all()[name.lower()]


def load_builtins():
    sys.path.extend(
        str(Path(path).expanduser()) for path in conf.get('syspath', []))
    logger.debug("sys.path: %s", sys.path)
    for name in __all__:
        importlib.import_module(f'camisole.languages.{name}')


def load_from_environ():
    for module in os.environ.get('CAMISOLE_LANGS', '').split(':'):
        if not module:
            continue
        try:
            importlib.import_module(module)
        except Exception:
            logger.exception("could not load %s", module)

__all__ = [
    'ada',
    'c',
    'd',
    'csharp',
    'cxx',
    'go',
    'haskell',
    'java',
    'javascript',
    'lua',
    'ocaml',
    'pascal',
    'perl',
    'php',
    'prolog',
    'python',
    'ruby',
    'rust',
    'scheme',
    'scala'
]
