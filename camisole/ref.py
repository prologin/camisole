from pathlib import Path

import camisole.languages

REF_PATH = Path(__file__).parent.resolve() / 'ref-sources'


async def test(lang_name):
    lang_cls = camisole.languages.by_name(lang_name)
    with (REF_PATH / ('ref' + lang_cls.source_ext)).open() as source_file:
        source = source_file.read()

    l = lang_cls({'source': source, 'tests': [{}]})
    result = await l.run()
    try:
        if result['tests'][0]['stdout'].strip() != '42':
            raise ValueError
        return True, result
    except (KeyError, IndexError, ValueError):
        return False, result
