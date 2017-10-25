import pytest

from camisole.languages.java import Java


async def run_java(source):
    return await Java({'source': source, 'tests': [{}]}).run()


@pytest.mark.asyncio
async def test_default_single():
    result = await run_java('''
class Noël {
    static class Læticia { }
    public static void main(String[] args) {
        System.out.println("défaut");
    }
}''')
    assert result['tests'][0]['stdout'] == 'défaut\n'.encode()


@pytest.mark.asyncio
async def test_default_single_nested():
    result = await run_java('''
class Foo {
    static class SubFoo {
        static class SubSubFoo {
            public static void main(String[] args) {
                System.out.println("inner");
            }
        }
    }
}''')
    assert result['tests'][0]['stdout'] == b'inner\n'


@pytest.mark.asyncio
async def test_default_multiple():
    result = await run_java('''
class Foo { }
class Bar {
    public static void main(String[] args) { System.out.println("bar"); }
}
class Baz { }
''')
    assert result['tests'][0]['stdout'] == b'bar\n'


@pytest.mark.asyncio
async def test_public_access():
    result = await run_java('''
class Private {
    public static void main(String[] args) {
        System.out.println("private");
    }
}
public class Foo {
    static class NestedYetIgnoredBecauseNotPublic {
        public static void main(String[] args) {
            System.out.println("nested");
        }
    }

    public static void main(String[] args) {
        System.out.println("public");
    }
}
class OtherPrivate {
    public static void main(String[] args) {
        System.out.println("otherprivate");
    }
}''')
    assert result['tests'][0]['stdout'] == b'public\n'


@pytest.mark.asyncio
async def test_heap_size_too_small():
    result = await Java({'source': Java.reference_source,
                         'execute': {'mem': 42},
                         'tests': [{}]}).run()
    assert result['tests'][0]['meta']['status'] == 'RUNTIME_ERROR'
    assert b'Too small initial heap' in result['tests'][0]['stdout']


@pytest.mark.asyncio
async def test_heap_size_big_enough():
    result = await Java({'source': Java.reference_source,
                         'execute': {'mem': 4200},
                         'tests': [{}]}).run()
    assert result['tests'][0]['meta']['status'] == 'OK'
    assert result['tests'][0]['stdout'] == b'42\n'
