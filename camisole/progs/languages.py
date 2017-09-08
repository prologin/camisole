import asyncio
import pprint
import sys


async def print_working_languages(languages, verbosity):
    from camisole.ref import test
    from camisole.utils import indent

    def extract_fail_message(result):
        relevant = (result['compile'] if 'compile' in result
                    else result['tests'][0])
        messages = [relevant['meta']['message'], relevant['stderr']]
        return '\n'.join(msg for msg in messages if msg)

    error_count = 0
    use_color = sys.stdout.isatty()
    max_length = max(map(len, languages)) + 2

    res = [asyncio.Task(test(lang_name)) for lang_name in languages]
    await asyncio.wait(res)

    for i, lang_name in enumerate(languages):
        success, raw = res[i].result()
        status, color = ('OK', 32) if success else ('FAIL', 31)
        ok_msg = (f'\x1B[{color}m{status}\033[0m' if use_color else status)
        print(f'{lang_name + " ":.<{max_length}} {ok_msg}', flush=True)

        if not success:
            error_count += 1
        if not success and verbosity > 0:
            if verbosity == 1:
                print(indent(extract_fail_message(raw).strip()))
            else:
                print(indent(pprint.pformat(raw)))

    return min(error_count, 0xff)


def handle(args):
    from camisole.languages import all
    from camisole.utils import tabulate
    headers = ("Name", "Display name", "Module", "Class name")
    rows = [(lang, cls.name, cls.__module__, cls.__name__)
            for lang, cls in sorted(all().items())]
    print("\n".join(tabulate(rows, headers=headers)))
    return 0


def build(parser):
    parser.add_parser('languages')
    return 'languages', handle
