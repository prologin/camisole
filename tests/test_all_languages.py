from pathlib import Path
import pytest

import camisole.languages


@pytest.mark.asyncio
@pytest.mark.parametrize("language", map(pytest.mark.xfail,
                                         camisole.languages.all()))
async def test(language):
    lang_cls = camisole.languages.by_name(language)
    dirpath = Path(__file__).parent.resolve() / '42'
    with (dirpath / ('ref' + lang_cls.source_ext)).open() as sourcefile:
        source = sourcefile.read()
    l = lang_cls({'source': source, 'tests': [{}]})
    r = await l.run()
    assert r['tests'][0]['exitcode'] == 0
