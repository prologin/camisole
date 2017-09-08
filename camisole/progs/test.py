import argparse
import asyncio

from camisole.languages import all
from camisole.progs.languages import print_working_languages


def handle(args):
    languages = args.languages or all().keys()
    verbosity = sum(args.verbose or [])
    check = print_working_languages(languages, verbosity)
    return asyncio.get_event_loop().run_until_complete(check)


def build(parser):
    p = parser.add_parser('test')
    p.add_argument(
        '-v',
        dest='verbose',
        action='append_const',
        const=1,
        help="increase verbosity (up to two)")
    p.add_argument(
        'languages',
        nargs=argparse.REMAINDER,
        help="languages to test")
    return 'test', handle
