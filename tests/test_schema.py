import jsonschema
import pytest

import camisole.schema


def test_correct_simple():
    json = {
        'lang': 'python',
        'source': 'print(42)',
        'tests': [{}],
    }
    camisole.schema.validate(json)


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
    camisole.schema.validate(json)


def test_bad_type():
    json = {
        'lang': 'python',
        'source': 42,
    }
    with pytest.raises(jsonschema.exceptions.ValidationError) as e:
        camisole.schema.validate(json)
    assert "42 is not of type 'string'" in str(e.value)


def test_missing_field():
    json = {
        'source': 'print(42)',
    }
    with pytest.raises(jsonschema.exceptions.ValidationError) as e:
        camisole.schema.validate(json)
    assert "'lang' is a required property" in str(e.value)
