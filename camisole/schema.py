import jsonschema

# Monkey-patch Draft4Validator to define 'bytes' type
# FIXME: find a clean way to implement this hack
validator = jsonschema.Draft4Validator
validator.DEFAULT_TYPES['bytes'] = bytes
validator.META_SCHEMA['definitions']['simpleTypes']['enum'].append('bytes')

ISOLATE_OPTS_PROPERTIES = {
    'fsize': {'type': 'number'},
    'mem': {'type': 'number'},
    'processes': {'type': 'number'},
    'quota': {'type': 'string'},
    'stack': {'type': 'number'},
    'time': {'type': 'number'},
    'wall-time': {'type': 'number'},
}

EXECUTE_PROPERTIES = {
    'stdin': {'type': ['string', 'bytes']},
    **ISOLATE_OPTS_PROPERTIES,
}

SCHEMA = {
    'type': 'object',
    'properties': {
        'lang': {'type': 'string'},
        'source': {'type': ['string', 'bytes']},
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
