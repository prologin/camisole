from camisole.models import Program


def test_version():
    v = Program('cp').version()
    assert '.' in v


def test_long_version():
    v = Program('cp').long_version()
    assert v.startswith('cp')


def test_no_version():
    echo = Program('echo', version_opt=None)
    assert echo._version() is None
    assert echo.long_version() is None
    assert echo.long_version() is None
