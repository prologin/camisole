#!/usr/bin/python3

import argparse
import logging
import logging.config
import sys
import yaml

from camisole.conf import conf
from camisole.languages import load_builtins, load_from_environ
from camisole.progs import languages, test, serve


def main():
    parser = argparse.ArgumentParser(
        description="asyncio-based source compiler and test runner")
    parser.add_argument(
        '-c',
        '--conf',
        type=argparse.FileType('r'),
        help="custom yaml configuration file to use")
    parser.add_argument(
        '-l',
        '--logging',
        choices=[l.lower() for l in logging._nameToLevel],
        help="logging level (overrides root logger level from file conf)")

    cmd = parser.add_subparsers(dest='command')
    commands = dict(getattr(module, 'build')(cmd)
                    for module in (languages, test, serve))
    args = parser.parse_args()

    if args.conf:
        # merge user defined conf
        conf.merge(yaml.load(args.conf))

    # default logging config from conf
    logging.config.dictConfig(conf['logging'])

    if args.logging:
        # override root logger level
        logging.root.setLevel(args.logging.upper())

    # import built-in languages
    load_builtins()
    # import user languages from environ
    load_from_environ()

    try:
        func = commands[args.command]
    except KeyError:
        parser.error("missing command")
    else:
        sys.exit(func(args))


if __name__ == '__main__':
    main()
