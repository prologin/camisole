import pytest

from camisole.languages.java import Java


async def run_java(source):
    return await Java({'source': source, 'tests': [{}]}).run()


@pytest.mark.asyncio
async def test_default_single():
    result = await run_java('''
class Foo {
    static class SubFoo { }
    public static void main(String[] args) {
        System.out.println("default");
    }
}''')
    assert result['tests'][0]['stdout'] == 'default\n'


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
