import asyncio
import unittest


class AioTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        self._function_cache = {}
        super().__init__(methodName=methodName)

    def coroutine_function_decorator(self, func):
        def wrapper(*args, **kw):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(func(*args, **kw))
            finally:
                loop.close()
        return wrapper

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if asyncio.iscoroutinefunction(attr):
            if item not in self._function_cache:
                self._function_cache[item] = self.coroutine_function_decorator(attr)
            return self._function_cache[item]
        return attr
