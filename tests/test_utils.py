import pytest

from camisole.utils import (
    uniquify, indent, parse_size, parse_float, tabulate, which, AcceptHeader)


def test_uniquify():
    assert list(uniquify([])) == []
    assert list(uniquify([1])) == [1]
    assert list(uniquify([1, 1])) == [1]
    assert list(uniquify([1, 2, 1, 1])) == [1, 2]


def test_indent():
    assert indent('foo') == '    foo'
    assert indent('foo', n=2) == '  foo'
    assert indent('foo\nbar', n=2) == '  foo\n  bar'


def test_parse_size():
    assert parse_size('1') == 1
    assert parse_size('1024') == 1024
    assert parse_size('1k') == 1024
    assert parse_size('2k') == 1024 * 2
    assert parse_size('1m') == 1024 * 1024
    assert parse_size('1g') == 1024 * 1024 * 1024
    assert parse_size('1kb') == 1024
    assert parse_size('1kB') == 1024
    assert parse_size('1 kB') == 1024


def test_parse_float():
    assert parse_float('0.1') == 0.1
    assert parse_float(None) is None


def test_tabulate():
    rows = [['foo', 'a'], ['barbar', 'baz'], ]
    assert '\n'.join(tabulate(rows, margin=0)) == (
        'foo    | a  \n'
        'barbar | baz'
    )

    assert '\n'.join(tabulate(rows, margin=0, align='>>')) == (
        '   foo |   a\n'
        'barbar | baz'
    )

    assert '\n'.join(tabulate(rows, margin=1)) == (
        'foo     | a   \n'
        'barbar  | baz '
    )

    assert '\n'.join(tabulate(rows, headers=['FOO', 'BARBAZZZ'], margin=0)) == (
        'FOO    | BARBAZZZ\n'
        'foo    | a       \n'
        'barbar | baz     '
    )


def test_which():
    assert which('echo') in ('/usr/bin/echo', '/bin/echo')
    assert which('/bin/echo') in ('/usr/bin/echo', '/bin/echo')
    assert which('/a/b/c/idonteven') == '/a/b/c/idonteven'


def test_accept_header():
    h = 'text/html,*/*;q=0.8,application/xhtml+xml,application/xml;q=0.9,'
    a = AcceptHeader.parse_header(h)
    assert len(a) == 4
    assert a[0].mime_type == 'text/html'
    pytest.approx(a[0].weight, 1)
    assert a[1].mime_type == 'application/xhtml+xml'
    pytest.approx(a[1].weight, 1)
    assert a[2].mime_type == 'application/xml'
    pytest.approx(a[2].weight, .9)
    assert a[3].mime_type == '*/*'
    pytest.approx(a[3].weight, .8)
