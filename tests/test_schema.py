import pytest

import camisole.schema


def validate_schema(obj, schema):
    try:
        camisole.schema.validate_schema(obj, schema)
        return True
    except camisole.schema.ValidationError as e:
        print(e)
        return False


def test_schema_empty():
    assert validate_schema({}, {})


def test_schema_simple():
    s = {'a': int}
    assert validate_schema({'a': 1}, s)
    assert not validate_schema({}, s)
    assert not validate_schema({'a': 1.2}, s)
    assert not validate_schema({'a': 'b'}, s)


def test_schema_optional():
    from camisole.schema import O
    s = {'a': O(int)}
    assert validate_schema({}, s)
    assert validate_schema({'a': 1}, s)
    assert validate_schema({'a': None}, s)


def test_schema_union():
    from camisole.schema import Union
    s = {'a': Union(int, str)}
    assert validate_schema({'a': 1}, s)
    assert validate_schema({'a': 'b'}, s)
    assert not validate_schema({}, s)
    assert not validate_schema({'a': 1.1}, s)


def test_schema_list():
    s = {'a': [int]}
    assert validate_schema({'a': []}, s)
    assert validate_schema({'a': [1]}, s)
    assert validate_schema({'a': [1, 2, 3]}, s)
    assert not validate_schema({'a': [1, 2, 'b']}, s)


def test_schema_nested():
    s = {'a': {'b': [{'c': int}]}}
    assert validate_schema({'a': {'b': []}}, s)
    assert validate_schema({'a': {'b': [{'c': 1}, {'c': 2}]}}, s)
    assert not validate_schema({'a': {'b': [{'c': 1}, {'c': None}]}}, s)


def test_correct_simple():
    json = {
        'lang': 'python',
        'source': 'print(42)',
        'tests': [{}],
    }
    camisole.schema.validate_run(json)


def test_correct_complex():
    json = {
        'lang': 'c',
        'source': '''
#include <stdio.h>
int main(void) {
    printf("42\n");
    return 0;
}''',
        'execute': {
            'fsize': 19,
            'time': 78,
            'wall-time': 404,
            'quota': '1,8',
            'mem': 1337,
            'processes': 42,
        },
        'compile': {
            'quota': '1,8',
            'processes': 27,
            'fsize': 19,
            'mem': 44444444,
            'time': 546546,
            'wall-time': 200,
        },
        'tests': [
            {
                'name': 'test01',
                'stdin': '4224242422',
                'mem': 44444444,
            },
            {
                'quota': '1,8',
                'processes': 27,
                'fsize': 19,
                'mem': 44444444,
                'time': 546546,
                'wall-time': 200,
            },
            {},
        ],
    }
    camisole.schema.validate_run(json)


def test_bad_type():
    json = {
        'lang': 'python',
        'source': 42,
    }
    with pytest.raises(camisole.schema.ValidationError) as e:
        camisole.schema.validate_run(json)
    assert "expected a string or binary data, got an integer" in str(e)


def test_missing_field():
    json = {
        'source': 'print(42)',
    }
    with pytest.raises(camisole.schema.ValidationError) as e:
        camisole.schema.validate_run(json)
    assert "expected a string, got nothing" in str(e)
