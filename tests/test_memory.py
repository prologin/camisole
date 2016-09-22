from . import AioTestCase

import camisole.languages


class MemoryTest(AioTestCase):
    def python_list(self, n):
        return camisole.languages.Python({
            'execute': {'mem': 50000},
            'tests': [{}],
            'source': 'print(list(range({}))[-1])'.format(n)
        })

    async def test_ok(self):
        n = int(1e5)
        r = await self.python_list(n).run()
        self.assertEqual(r['tests'][0]['meta']['status'], 'OK')
        self.assertEqual(r['tests'][0]['stdout'].strip(), str(n - 1))

    async def test_exceed(self):
        n = int(1e6)
        r = await self.python_list(n).run()
        self.assertEqual(r['tests'][0]['meta']['status'], 'RUNTIME_ERROR')
        self.assertIn('MemoryError', r['tests'][0]['stderr'])
        self.assertEqual(r['tests'][0]['stdout'].strip(), '')
