import importlib
import logging
import sys
from itertools import chain
from pathlib import Path
from typing import Iterable

from camisole.languages import all
from camisole.utils import uniquify

logger = logging.getLogger(__name__)

DEFAULT_SEARCH_PATH = [
    Path('~/.local/share/camisole/lang').expanduser(),
    Path('/usr/share/camisole/lang'),
]


def parse_search_paths(paths: str) -> Iterable[Path]:
    paths = (Path(part).resolve() for part in paths.split(':')
             if part)
    return uniquify(chain(paths, DEFAULT_SEARCH_PATH))


def load_modules(modules: Iterable[str], extra_paths: str = ''):
    extra_paths = parse_search_paths(extra_paths)
    if extra_paths:
        sys.path[0:0] = map(str, extra_paths)

    found = set()
    for name in uniquify(modules):
        langs_before = set(all().values())
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                f"Could not find module '{name}' in path") from None
        diff = set(all().values()) - langs_before
        found |= diff
        if diff:
            logger.debug("Module '%s' provides %s", module.__name__,
                         ", ".join(map(repr, diff)))
    return found
