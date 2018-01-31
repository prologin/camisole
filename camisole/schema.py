class ValidationError(ValueError):
    def __init__(self, path, msg):
        self.path = path
        self.msg = msg
        super().__init__(str(self))

    def __str__(self):
        return f"{self.path}: {self.msg}"


class O:
    """Optional."""

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __repr__(self):
        return f"O[{self.wrapped}]"


class Union:
    """Any of."""

    def __init__(self, *wrapped):
        self.wrapped = wrapped

    def __repr__(self):
        return f"Union[{self.wrapped}]"


def human_type_name(cls):
    return {
        bytes: "binary data",
        int: "an integer",
        str: "a string",
        type(None): "nothing",
    }.get(cls, f"a {cls.__name__}")


def validate_schema(obj, schema):
    htn = human_type_name

    def explore(obj, schema, path):
        if isinstance(schema, O):
            if obj is None:
                return
            explore(obj, schema.wrapped, path)

        elif isinstance(schema, Union):
            for subtype in schema.wrapped:
                try:
                    explore(obj, subtype, path)
                    # one of the types is OK, early stop
                    return
                except ValidationError:
                    pass
            expected = ' or '.join(htn(s) for s in schema.wrapped)
            raise ValidationError(
                path, f"expected {expected}, got {htn(obj.__class__)}")

        elif isinstance(schema, list):
            subtype, = schema
            try:
                for i, item in enumerate(obj):
                    explore(item, subtype, f'{path}[{i}]')
            except TypeError:
                raise ValidationError(
                    path, f"expected a list, got {htn(obj.__class__)}")

        elif isinstance(schema, dict):
            try:
                for key, subtype in schema.items():
                    explore(obj.get(key), subtype, f'{path}.{key}')
            except ValidationError:
                raise
            except Exception:
                raise ValidationError(
                    path, f"expected a mapping, got {htn(obj.__class__)}")

        elif not isinstance(obj, schema):
            raise ValidationError(
                path, f"expected {htn(schema)}, got {htn(obj.__class__)}")

    explore(obj, schema, '')


str_bytes = Union(str, bytes)
number = Union(float, int)

ISOLATE_OPTS_PROPERTIES = {
    'fsize': O(int),
    'mem': O(int),
    'processes': O(int),
    'quota': O(str),
    'stack': O(int),
    'time': O(number),
    'virt-mem': O(int),
    'wall-time': O(number),
}

EXECUTE_PROPERTIES = {
    'stdin': O(str_bytes),
    **ISOLATE_OPTS_PROPERTIES,
}

RUN_SCHEMA = {
    'lang': str,
    'source': str_bytes,
    'all_fatal': O(bool),
    'compile': O(ISOLATE_OPTS_PROPERTIES),
    'execute': O(EXECUTE_PROPERTIES),
    'tests': O([{
        'name': O(str),
        'fatal': O(bool),
        **EXECUTE_PROPERTIES,
    }]),
}


def validate_run(json):
    validate_schema(json, RUN_SCHEMA)
