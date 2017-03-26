import jsonschema


ISOLATE_OPTS_PROPERTIES = {
    'fsize': {'type': 'number'},
    'mem': {'type': 'number'},
    'processes': {'type': 'number'},
    'quota': {'type': 'string'},
    'time': {'type': 'number'},
    'wall-time': {'type': 'number'},
}

SCHEMA = {
    'type': 'object',
    'properties': {
        'lang': {'type': 'string'},
        'source': {'type': 'string'},
        'compile': {
            'type': 'object',
            'properties': ISOLATE_OPTS_PROPERTIES,
        },
        'execute': {
            'type': 'object',
            'properties': {
                'stdin': {'type': 'string'},
                **ISOLATE_OPTS_PROPERTIES,
            }
        },
        'tests': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'stdin': {'type': 'string'},
                    **ISOLATE_OPTS_PROPERTIES,
                },
            },
        },
    },
    'required': ['lang', 'source'],
}


def validate(json):
    return jsonschema.validate(json, SCHEMA)
