import textwrap

import math


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


def tabulate(rows, headers=None, fmt="", margin=1):
    ncols = len(rows[0])
    lengths = [-math.inf] * ncols
    # don't side-effect modify rows
    rows = ([headers] or []) + rows
    for row in rows:
        lengths = [max(l, len(col)) for l, col in zip(lengths, row)]
    lengths = [l + margin for l in lengths]
    if not fmt:
        fmt = "".join("{:<{s%d}}%s" % (i, " | " if i < ncols  - 1 else "")
                      for i in range(ncols))
    for row in rows:
        yield fmt.format(*row, **{f's{i}': l for i, l in enumerate(lengths)})
