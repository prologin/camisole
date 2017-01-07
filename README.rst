camisole
========

*camisole* is an asyncio_-based source compiler and test runner. The main
purpose of this tool is to build programs from user-provided source and then
execute them against a user-provided test suite.

It uses isolate_ as a backend to safely compile and execute source codes using
linux kernel features such as namespaces, cgroups, chroot and resources limits.
You can learn more about isolate in this paper[#isolatepaper]_ .

*camisole* requires Python 3.6 or newer.

Features
--------

- Built-in support for a wide variety of languages, including:
  Ada,
  Brainfuck,
  C,
  C#,
  C++,
  F#,
  Haskell,
  Java,
  JavaScript,
  Lua,
  OCaml,
  Pascal,
  Perl,
  PHP,
  Python,
  Scheme,
  Visual Basic.
- Wall-time limitation (timeout)
- Memory limitation
- Isolation: *camisole* runs both the compilation and execution stages in a
  sandboxed environment provided by isolate_
- Simple HTTP/JSON interface

Usage
-----

*camisole* is meant to be used through a HTTP/JSON interface. To launch the web
server with default configuration::

    $ pip install -r requirements.txt
    $ python -m camisole

Then run a program::

    $ curl -s localhost:8080/run -d '{"lang": "python", "source": "print(42)", "tests": [{}]}' | python -m json.tool
    {
        "tests": [
            {
                "stdout": "42\n",
                "stderr": "",
                "meta": {
                    "status": "OK",
                    "exitcode": 0,
                    "time-wall": 0.067,
                    "cg-mem": 2528,
                    "killed": 0,
                    "exitsig": null,
                    "time": 0.019,
                    "max-rss": 6264,
                    "csw-forced": 12,
                    "csw-voluntary": 4,
                    "message": null
                },
                "name": "test000",
                "exitcode": 0
            }
        ],
        "success": true
    }

You can customize the web app by calling the ``run()`` endpoint manually::

    $ python -c 'import camisole.http; camisole.http.run(port=9999)'

Tests
-----

Run tests (and coverage) with::

    $ pip install -r requirements-dev.txt
    $ pytest --cov=camisole

You can then generate an HTML report (browse to http://localhost:8000/)::

    $ coverage html
    $ ( cd htmlcov && python -m http.server )

Frequently Asked Question
-------------------------

Can I run this in Docker/LXC/… or even directly on my server?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, but we don't think it's a good idea for production environments. By using
a VM, you considerably reduce the attack surface and you won't risk getting
your host taken over if an exploit is found in the kernel that could allow an
attacker to exit the chroot or the namespaces in which they are sandboxed and
thus gain privilege escalation. `This has happened before`_.

Can I use this to run multiple source files?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We're not planning on adding this feature. Camisole is designed for "quick and
dirty" source code evaluation. If you're planning to do anything more complex
than "take this source file, compile it and evaluate it", you'd be better off
using isolate_ directly and make it suit your needs better.

Why is it called *camisole*?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It means *straitjacket*, because we restrain what the programs can do. In
french, « Ça m'isole » means "It isolates me", it's a fun nod to our isolation
backend, isolate_.

License
-------

GPLv2+, see the ``LICENSE`` file.

.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _isolate: https://github.com/ioi/isolate
.. _This has happened before: https://lwn.net/Articles/543273/

.. [#isolatepaper] `MAREŠ, Martin et BLACKHAM, Bernard. A new contest sandbox. Olympiads in Informatics, 2012, vol. 6, p.  100 <http://mj.ucw.cz/papers/isolate.pdf>`_.
