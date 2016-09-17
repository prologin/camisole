import asyncio
import unittest
from pathlib import Path

import camisole.languages


class Test42(unittest.TestCase):
    async def async_test_42(self):
        dirpath = Path(__file__).parent.resolve() / '42'
        for lang in camisole.languages.languages.values():
            with (dirpath / ('ref' + lang.source_ext)).open() as sourcefile:
                source = sourcefile.read()
            l = lang({'source': source, 'tests': [{}]})
            r = await l.run()
            self.assertEqual(r['tests'][0]['exitcode'], 0)

    def test_42(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_test_42())
        loop.close()


if __name__ == '__main__':
    unittest.main()
