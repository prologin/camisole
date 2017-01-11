#!/usr/bin/python3

async def print_working_languages():
    from camisole.languages import all
    from camisole.ref import test
    import sys

    use_color = sys.stdout.isatty()
    status = {True: 'OK', False: 'FAIL'}
    colors = {True: 32, False: 31}  # green, red

    max_length = max(map(len, all())) + 2
    for lang_name in sorted(all()):
        ok, result = await test(lang_name)
        ok = (f'\x1B[{colors[ok]}m{status[ok]}\033[0m' if use_color
              else status[ok])
        print(f'{lang_name + " ":.<{max_length}} {ok}', flush=True)


if __name__ == '__main__':
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
    parser.add_argument(
        'command',
        nargs='?',
        default='serve',
        choices=['serve', 'languages'])
    parser.add_argument('--help', action='help')
    args = parser.parse_args()

    logging.basicConfig(level=args.logging.upper())
    loop = asyncio.get_event_loop()

    if args.command == 'languages':
        loop.run_until_complete(print_working_languages())
    elif args.command == 'serve':
        camisole.http.run(host=args.host, port=args.port)
