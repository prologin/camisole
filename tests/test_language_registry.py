import pytest

from camisole.languages import by_name
from camisole.models import Lang


def test_default_name():
    class MyFoo(Lang):
        pass

    assert by_name('myfoo') is MyFoo


def test_user_name():
    class MyFoo(Lang, name='chiche'):
        pass

    assert by_name('chiche') is MyFoo


def test_overwrite_warning():
    class FooLang(Lang):
        pass

    assert by_name('foolang') is FooLang

    with pytest.warns(UserWarning) as record:
        class BarLang(Lang, name='foolang'):
            pass
        assert len(record) == 1
        message = str(record[0].message)
        assert repr(FooLang) in message
        assert "overwrites" in message
        assert repr(BarLang) in message

    assert by_name('foolang') is BarLang
