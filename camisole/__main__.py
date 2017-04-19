#!/usr/bin/python3

import asyncio

from camisole.utils import indent, tabulate


async def print_working_languages(languages, verbosity):
    from camisole.ref import test
    from pprint import pformat
    import sys

    def extract_fail_message(result):
        relevant = (result['compile'] if 'compile' in result
                    else result['tests'][0])
        messages = [relevant['meta']['message'], relevant['stderr']]
        return '\n'.join(msg for msg in messages if msg)

    use_color = sys.stdout.isatty()
    max_length = max(map(len, languages)) + 2

    res = [asyncio.Task(test(lang_name)) for lang_name in languages]
    await asyncio.wait(res)

    for i, lang_name in enumerate(languages):
        success, raw = res[i].result()
        status, color = ('OK', 32) if success else ('FAIL', 31)
        ok_msg = (f'\x1B[{color}m{status}\033[0m' if use_color else status)
        print(f'{lang_name + " ":.<{max_length}} {ok_msg}', flush=True)

        if not success and verbosity > 0:
            if verbosity == 1:
                print(indent(extract_fail_message(raw).strip()))
            else:
                print(indent(pformat(raw)))


def main():
    import argparse
    import asyncio
    import camisole.loader
    import camisole.http
    import logging
    import os

    parser = argparse.ArgumentParser(
        description="asyncio-based source compiler and test runner")
    parser.add_argument(
        '-l',
        '--logging',
        default='error',
        choices=[l.lower() for l in logging._nameToLevel],
        help="logging level")
    parser.add_argument(
        '-m',
        '--module',
        dest='modules',
        action='append',
        help="extra modules to load (customize search path with CAMISOLEPATH)")

    cmd = parser.add_subparsers(dest='command')

    parse_serve = cmd.add_parser('serve', add_help=False)
    parse_serve.add_argument('-h', '--host', default='0.0.0.0')
    parse_serve.add_argument('-p', '--port', type=int, default=8080)
    parse_serve.add_argument('--help', action='help')

    parse_languages = cmd.add_parser('languages')

    parse_test = cmd.add_parser('test')
    parse_test.add_argument(
        '-v',
        dest='verbose',
        action='append_const',
        const=1,
        help="increase verbosity (up to two)")
    parse_test.add_argument(
        'languages',
        nargs=argparse.REMAINDER,
        help="languages to test")
    args = parser.parse_args()

    logging.basicConfig(level=args.logging.upper())

    # import built-in languages
    camisole.languages._import_builtins()

    # import extra languages
    if args.modules:
        path = os.environ.get('CAMISOLEPATH', '')
        camisole.loader.load_modules(args.modules, path)

    loop = asyncio.get_event_loop()

    if args.command == 'languages':
        from camisole.languages import all
        rows = [(lang, cls.name, cls.__module__, cls.__name__)
                for lang, cls in sorted(all().items())]
        print("\n".join(tabulate(rows,
            headers=("Name", "Display name", "Module", "Class name"))))

    elif args.command == 'test':
        from camisole.languages import all
        languages = args.languages or all().keys()
        verbosity = sum(args.verbose or [])
        loop.run_until_complete(print_working_languages(languages, verbosity))

    elif args.command == 'serve':
        from camisole.languages import all
        logging.info("Registry has %d languages:\n%s", len(all()),
                     '\n'.join(f'    {l!r}' for l in all().values()))
        camisole.http.run(host=args.host, port=args.port)

    else:
        parser.exit(message=parser.format_usage())


if __name__ == '__main__':
    main()
