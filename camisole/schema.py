import jsonschema


ISOLATE_OPTS_PROPERTIES = {
    'fsize': {'type': 'number'},
    'mem': {'type': 'number'},
    'processes': {'type': 'number'},
    'quota': {'type': 'string'},
    'stack': {'type': 'string'},
    'time': {'type': 'number'},
    'wall-time': {'type': 'number'},
}

EXECUTE_PROPERTIES = {
    'stdin': {'type': 'string'},
    **ISOLATE_OPTS_PROPERTIES,
}

SCHEMA = {
    'type': 'object',
    'properties': {
        'lang': {'type': 'string'},
        'source': {'type': 'string'},
        'all_fatal': {'type': 'boolean'},
        'compile': {
            'type': 'object',
            'properties': ISOLATE_OPTS_PROPERTIES,
        },
        'execute': {
            'type': 'object',
            'properties': EXECUTE_PROPERTIES,
        },
        'tests': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'fatal': {'type': 'boolean'},
                    **EXECUTE_PROPERTIES,
                },
            },
        },
    },
    'required': ['lang', 'source'],
}


def validate(json):
    return jsonschema.validate(json, SCHEMA)
