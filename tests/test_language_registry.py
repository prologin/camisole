import pytest

from camisole.languages import by_name
from camisole.models import Lang


def test_default_name():
    class MyFoo(Lang):
        pass

    assert by_name('myfoo') is MyFoo
    assert by_name('myfoo').name == MyFoo.__name__


def test_user_name():
    class MyFoo(Lang, name='Chiche'):
        pass

    assert by_name('chiche') is MyFoo
    assert by_name('chiche').name == 'Chiche'


def test_overwrite_warning():
    class FooLang(Lang):
        pass

    assert by_name('foolang') is FooLang
    assert by_name('foolang').name == 'FooLang'

    with pytest.warns(UserWarning) as record:
        class BarLang(Lang, name='Foolang'):
            pass
        assert len(record) == 1
        message = str(record[0].message)
        assert "foolang" in message
        assert FooLang.__name__ in message
        assert "overwrites" in message
        assert BarLang.__name__ in message

    assert by_name('foolang') is BarLang
    assert by_name('foolang').name == 'Foolang'
