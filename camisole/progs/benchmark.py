import asyncio
import statistics

from camisole import ref


def format_bar(mi, ma, a, b, v,
               width=80, mark='\N{FULL BLOCK}', opaque='\N{MEDIUM SHADE}',
               empty='\N{LIGHT SHADE}'):
    f = (ma - mi) // width
    half_opaque = ((b - a) // 2 // f)
    return (empty * ((a - mi) // f)
            + opaque * half_opaque
            + mark
            + opaque * half_opaque
            + empty * ((ma - b) // f))


def format_stats(series, d, f=0):
    mean = statistics.mean(series)
    med = statistics.median(series)
    std = statistics.stdev(series)
    return f"x {mean:{d}.{f}f}  μ {med:{d}.{f}f}  σ² {std:{d}.{f}f}"


async def benchmark(lang_name, verbose):
    min = a = 4_000  # 4 MB
    max = b = 800_000  # 800 MB

    metas = []

    while b - a > 1_000:
        memory = (a + b) // 2
        limits = {'mem': memory, 'cg-mem': memory,
                  'wall-time': 2, 'time': 1, 'extra-time': .2}
        ok, result = await ref.test(lang_name, execute=limits)
        meta = result['tests'][0]['meta']
        if verbose:
            bar = format_bar(min, max, a, b, memory)
            print(f" {lang_name:>10s} {memory:>7d} {bar}", end="\r")
        if ok:
            metas.append(meta)
            b = memory
        else:
            a = memory

    if not metas:
        return ("n/a", "", "", "")

    return (str(memory),
            format_stats([m['max-rss'] for m in metas], 5),
            format_stats([m['time'] for m in metas], 1, 3),
            format_stats([m['time-wall'] for m in metas], 1, 3))


def handle(args):
    from camisole.languages import all
    from camisole.utils import tabulate

    async def execute():
        return [(lang,) + await benchmark(lang, args.verbose)
                for lang in sorted(all())]

    rows = asyncio.get_event_loop().run_until_complete(execute())
    headers = ("Language",
               "Memory (kB)",
               "Max RSS (kB)",
               "Time (s)",
               "Wall time (s)")
    print("\n".join(tabulate(rows, headers=headers, align='<><<<')))
    return 0


def build(parser):
    p = parser.add_parser('benchmark')
    p.add_argument('-v',
                   '--verbose',
                   action='store_true',
                   help="show progress")
    return 'benchmark', handle
