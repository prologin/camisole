import camisole.languages


async def test(lang_name):
    expected = '42\n'
    lang_cls = camisole.languages.by_name(lang_name)
    lang = lang_cls({'source': lang_cls.reference_source, 'tests': [{}]})
    raw_result = await lang.run()
    try:
        stdout = raw_result['tests'][0]['stdout']
        if stdout == expected:
            return True, raw_result
        return False, raw_result
    except (KeyError, IndexError, ValueError):
        return False, raw_result
