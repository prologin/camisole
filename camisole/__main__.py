#!/usr/bin/python3

async def print_working_languages(verbosity):
    from camisole.languages import all
    from camisole.ref import test
    from pprint import pformat
    import sys

    def extract_fail_message(result):
        relevant = (result['compile'] if 'compile' in result
                    else result['tests'][0])
        return '\n'.join((relevant['meta']['message'], relevant['stderr']))

    use_color = sys.stdout.isatty()
    status = {True: 'OK', False: 'FAIL'}
    colors = {True: 32, False: 31}  # green, red

    max_length = max(map(len, all())) + 2
    for lang_name in sorted(all()):
        ok, result = await test(lang_name)
        ok_msg = (f'\x1B[{colors[ok]}m{status[ok]}\033[0m' if use_color
                  else status[ok])
        print(f'{lang_name + " ":.<{max_length}} {ok_msg}', flush=True)

        if not ok and verbosity > 0:
            if verbosity == 1:
                message = extract_fail_message(result).strip()
            else:
                message = pformat(result)
            print('\n'.join(f'    {line}' for line in message.splitlines()))


def main():
    import argparse
    import asyncio
    import camisole.http
    import logging

    parser = argparse.ArgumentParser(
        description="asyncio-based source compiler and test runner",
        add_help=False)
    parser.add_argument('-h', '--host', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int, default=8080)
    parser.add_argument(
        '-l',
        '--logging',
        default='error',
        choices=[l.lower() for l in logging._nameToLevel],
        help="logging level")
    parser.add_argument('--help', action='help')

    sub = parser.add_subparsers(dest='command')
    sub.add_parser('serve')
    parse_languages = sub.add_parser('languages')
    parse_languages.add_argument(
        '-v',
        dest='verbose',
        action='append_const',
        const=1,
        help="repeat to increase verbosity")

    args = parser.parse_args()

    logging.basicConfig(level=args.logging.upper())
    loop = asyncio.get_event_loop()

    if args.command == 'languages':
        verbosity = sum(args.verbose or [])
        loop.run_until_complete(print_working_languages(verbosity))
    else:  # default is serve
        camisole.http.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
