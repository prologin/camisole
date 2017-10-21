import math
import os
import re
import textwrap
from decimal import Decimal


def force_bytes(s):
    if isinstance(s, bytes):
        return s
    return s.encode()


def uniquify(seq):
    seen = set()
    return (x for x in seq if not (x in seen or seen.add(x)))


def indent(text, n=4):
    return textwrap.indent(text, ' ' * n)


def parse_size(str_size):
    """
    Transforms "1K", "1k" or "1 kB"-like strings to actual integers.
    Returns None if input is None.
    """
    if str_size is None:
        return None
    str_size = str_size.lower().strip().rstrip('b')
    for l, m in (('k', 1 << 10), ('m', 1 << 20), ('g', 1 << 30)):
        if str_size.endswith(l):
            return int(str_size.rstrip(l)) * m
    return int(str_size)


def parse_float(str_float):
    if str_float is None:
        return None
    return float(str_float)


def tabulate(rows, headers=None, margin=1, align=None):
    ncols = len(rows[0])
    lengths = [-math.inf] * ncols
    if headers:
        # don't side-effect modify rows
        rows = [headers] + rows
    for row in rows:
        lengths = [max(l, len(col)) for l, col in zip(lengths, row)]
    lengths = [l + margin for l in lengths]
    if align is None:
        align = ['<'] * ncols
    fmt = "".join("{:%s{s%d}}%s" % (a, i, " | " if i < ncols - 1 else "")
                  for i, a in enumerate(align))
    for row in rows:
        yield fmt.format(*row, **{f's{i}': l for i, l in enumerate(lengths)})


def which(binary):
    search_prefixes = ['/usr', '/lib', '/bin']
    path = [*os.environ.get('PATH').split(os.pathsep),
            '/usr/bin',
            '/usr/local/bin'
            '/bin']
    if os.path.dirname(binary) and os.access(binary, os.X_OK):
        return binary
    for part in path:
        # Ignore matches that are not inside standard directories
        if not any(part.startswith(prefix) for prefix in search_prefixes):
            continue
        p = os.path.join(part, binary)
        if os.access(p, os.X_OK):
            return p
    return binary


class cached_classmethod:
    """
    Memoize a class method result.

    class Foo:
        @cached_classmethod
        def heavy_stuff(cls):
            return 42
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, cls=None):
        if cls is None:
            return self
        res = self.func(cls)
        setattr(cls, self.name, res)
        return res


class AcceptHeader:
    class AcceptableType:
        RE_MIME_TYPE = re.compile(
            r'^(\*|[a-zA-Z0-9._-]+)(/(\*|[a-zA-Z0-9._-]+))?$')
        RE_Q = re.compile(r'(?:^|;)\s*q=([0-9.-]+)(?:$|;)')

        def __init__(self, raw_mime_type):
            bits = raw_mime_type.split(';', 1)
            mime_type = bits[0]
            if not self.RE_MIME_TYPE.match(mime_type):
                raise ValueError('"%s" is not a valid mime type' % mime_type)
            tail = ''
            if len(bits) > 1:
                tail = bits[1]
            self.mime_type = mime_type
            self.weight = self.get_weight(tail)
            self.pattern = self.get_pattern(mime_type)

        @classmethod
        def get_weight(cls, tail):
            match = cls.RE_Q.search(tail)
            try:
                return Decimal(match.group(1))
            except (AttributeError, ValueError):
                return Decimal(1)

        @staticmethod
        def get_pattern(mime_type):
            pat = mime_type.replace('*', '[a-zA-Z0-9_.$#!%^*-]+')
            return re.compile(f'^{pat}$')

        def matches(self, mime_type):
            return self.pattern.match(mime_type)

    @classmethod
    def parse_header(cls, header):
        mime_types = []
        for raw_mime_type in header.split(','):
            try:
                mime_types.append(cls.AcceptableType(raw_mime_type.strip()))
            except ValueError:
                pass
        return sorted(mime_types, key=lambda x: x.weight, reverse=True)

    @classmethod
    def get_best_accepted_types(cls, header, available):
        available = list(available)
        for acceptable_type in cls.parse_header(header):
            for available_type in available[:]:
                if acceptable_type.matches(available_type):
                    yield available_type
                    available.remove(available_type)
                    if not available:
                        return
