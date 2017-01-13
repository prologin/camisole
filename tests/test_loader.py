import pytest

from camisole import loader
from camisole.languages import all, by_name


def custom_lang(name):
    return f'''
from camisole.models import Lang
class {name}(Lang):
    pass
'''


def test_loader_empty():
    before = set(all().values())
    assert loader.load_modules([], '') == set()
    assert set(all().values()) == before


def test_loader_error():
    with pytest.raises(ModuleNotFoundError):
        loader.load_modules(['foo'], '')


def test_loader_root_module(tmpdir):
    with pytest.raises(KeyError):
        by_name('mylang')

    # create foo.py
    file = tmpdir.ensure('foo.py')
    file.write(custom_lang('MyLang'))

    # wrong import path
    with pytest.raises(ModuleNotFoundError):
        loader.load_modules(['foo'], '')

    # good import path
    found_langs = loader.load_modules(['foo'], str(tmpdir))
    lang = by_name('mylang')
    assert found_langs == {lang}
    assert lang.__name__ == 'MyLang'


def test_loader_sub_module(tmpdir):
    with pytest.raises(KeyError):
        by_name('otherlang')

    # create tux/bar/baz.py
    file = tmpdir.mkdir('tux').mkdir('bar').ensure('baz.py')
    file.write(custom_lang('OtherLang'))

    # wrong import path
    with pytest.raises(ModuleNotFoundError):
        loader.load_modules(['tux.bar.baz'], '')

    # good import path
    found_langs = loader.load_modules(['tux.bar.baz'], str(tmpdir))
    lang = by_name('otherlang')
    assert found_langs == {lang}
    assert lang.__name__ == 'OtherLang'


def test_loader_multiple_modules(tmpdir):
    with pytest.raises(KeyError):
        assert by_name('lang1')
    with pytest.raises(KeyError):
        assert by_name('lang2')

    # create lang1 and lang2
    tmpdir.ensure('lang1.py').write(custom_lang('Lang1'))
    tmpdir.ensure('lang2.py').write(custom_lang('Lang2'))

    found_langs = loader.load_modules(['lang1', 'lang2'], str(tmpdir))
    assert found_langs == {by_name('lang1'), by_name('lang2')}
