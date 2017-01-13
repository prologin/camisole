import enum

import camisole.languages


class Result(enum.Enum):
    exact = ('OK', 32)
    whitespace = ('WHITESPACE', 33)
    different = ('WRONG OUTPUT', 31)
    error = ('ERROR', 31)


async def test(lang_name):
    expected = '42\n'
    lang_cls = camisole.languages.by_name(lang_name)
    lang = lang_cls({'source': lang_cls.reference_source, 'tests': [{}]})
    raw_result = await lang.run()
    try:
        stdout = raw_result['tests'][0]['stdout']
        if stdout == expected:
            return Result.exact, raw_result
        elif stdout.strip() == expected.strip():
            return Result.whitespace, raw_result
        return Result.different, raw_result
    except (KeyError, IndexError, ValueError):
        return Result.error, raw_result
