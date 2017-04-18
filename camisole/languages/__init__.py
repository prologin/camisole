import importlib
from typing import Mapping, Type

from camisole.models import Lang


def all() -> Mapping[str, Type[Lang]]:
    return Lang._registry


def by_name(name: str) -> Type[Lang]:
    return all()[name.lower()]


def _import_builtins():
    for name in __all__:
        importlib.import_module(f'{__name__}.{name}')


__all__ = [
    'ada',
    'brainfuck',
    'c',
    'csharp',
    'cxx',
    'fsharp',
    'haskell',
    'java',
    'javascript',
    'lua',
    'ocaml',
    'pascal',
    'perl',
    'php',
    'python',
    'ruby',
    'rust',
    'scheme',
    'visualbasic',
]
