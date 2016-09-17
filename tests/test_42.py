from . import AioTestCase
from pathlib import Path

import camisole.languages


class Test42(AioTestCase):
    async def test(self):
        dirpath = Path(__file__).parent.resolve() / '42'
        for lang in camisole.languages.languages.values():
            try:
                with (dirpath / ('ref' + lang.source_ext)).open() as sourcefile:
                    source = sourcefile.read()
            except FileNotFoundError:
                continue
            l = lang({'source': source, 'tests': [{}]})
            r = await l.run()
            self.assertEqual(r['tests'][0]['exitcode'], 0)
