from . import AioTestCase

import camisole.languages


class WalltimeTest(AioTestCase):
    wall_time = 1.2

    def python_sleep(self, duration):
        return camisole.languages.Python({
            'execute': {'wall-time': self.wall_time},
            'tests': [{}],
            'source': 'import time; time.sleep({:f})'.format(duration),
        })

    async def test_ok(self):
        duration = 1.0
        r = await self.python_sleep(duration).run()
        test = r['tests'][0]['meta']
        self.assertEqual(test['status'], 'OK')
        self.assertAlmostEqual(test['time-wall'], duration, delta=.2)

    async def test_exceed(self):
        r = await self.python_sleep(2.0).run()
        test = r['tests'][0]['meta']
        self.assertEqual(test['status'], 'TIMED_OUT')
        self.assertAlmostEqual(test['time-wall'], self.wall_time, delta=.2)
        self.assertIn("time limit exceeded", test['message'].lower())
