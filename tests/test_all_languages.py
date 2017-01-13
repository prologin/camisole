import pytest

import camisole.languages
camisole.languages._import_builtins()


@pytest.mark.asyncio
@pytest.mark.parametrize("language", map(pytest.mark.xfail, camisole.languages.all()))
async def test(language):
    lang_cls = camisole.languages.by_name(language)
    l = lang_cls({'source': lang_cls.reference_source, 'tests': [{}]})
    r = await l.run()
    assert r['tests'][0]['exitcode'] == 0
