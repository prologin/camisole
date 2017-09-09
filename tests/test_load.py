from camisole.languages import load_from_environ, by_name
from pathlib import Path
import contextlib
import logging
import os
import pytest
import sys


@contextlib.contextmanager
def environ_langs(*modules):
    os.environ['CAMISOLE_LANGS'] = ':'.join(modules)
    yield
    os.environ.pop('CAMISOLE_LANGS')


@contextlib.contextmanager
def path(*paths):
    paths = [str(p) for p in paths]
    sys.path[0:0] = paths
    yield
    del sys.path[:len(paths)]


def test_load_by_environ_empty():
    with environ_langs('', '', ''):
        load_from_environ()


def test_load_by_environ_bad_path(caplog):
    module = 'langs'
    with caplog.at_level(logging.ERROR):
        with environ_langs(module):
            load_from_environ()

        log = ''.join(
            r.msg + getattr(r, 'exc_text', '') for r in caplog.records)
        assert "could not load" in log
        assert f"No module named '{module}'" in log


def test_load_by_environ_runtime_error(caplog):
    with caplog.at_level(logging.ERROR):
        with path(Path(__file__).parent / 'dummy'):
            with environ_langs('error'):
                load_from_environ()

        log = ''.join(
            r.msg + getattr(r, 'exc_text', '') for r in caplog.records)
        assert 'could not load' in log
        assert 'ZeroDivisionError' in log

    with pytest.raises(KeyError):
        by_name('compiledlang')


def test_load_by_environ():
    with path(Path(__file__).parent / 'dummy'):
        with environ_langs('langs'):
            # before load, does not work
            with pytest.raises(KeyError):
                by_name('compiledlang')

            # after load, does work
            load_from_environ()
            assert by_name('compiledlang').compiler.cmd.endswith('/echo')
            assert by_name('interpretedlang').interpreter.cmd.endswith('/echo')
