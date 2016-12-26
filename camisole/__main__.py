#!/usr/bin/python3

if __name__ == '__main__':
    import argparse
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
    args = parser.parse_args()

    logging.basicConfig(level=args.logging.upper())
    camisole.http.run(host=args.host, port=args.port)
