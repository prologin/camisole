import logging


def handle(args):
    from camisole.httpserver import run
    from camisole.languages import all
    logging.info("Registry has %d languages:\n%s", len(all()),
                 '\n'.join(f'    {l!r}' for l in all().values()))
    run(host=args.host, port=args.port)
    return 0


def build(parser):
    p = parser.add_parser('serve', add_help=False)
    p.add_argument('-h', '--host', default='0.0.0.0')
    p.add_argument('-p', '--port', type=int, default=8080)
    p.add_argument('--help', action='help')
    return 'serve', handle
