camisole
========

.. image:: https://travis-ci.org/prologin/camisole.svg?branch=master
   :target: https://travis-ci.org/prologin/camisole

.. image:: https://coveralls.io/repos/github/prologin/camisole/badge.svg?branch=master
   :target: https://coveralls.io/github/prologin/camisole?branch=master

*camisole* is a **secure online judge** for code compilation and execution. You
give some untrusted source code and a test suite, and *camisole* compiles the
code and runs it against the test suite.

It uses isolate_ as a backend to safely compile and execute source codes using
Linux kernel features such as namespaces, cgroups, chroot and resources limits.

Documentation
-------------

The **full documentation** of Camisole, including installation instructions and
usage examples, is available at https://camisole.prologin.org

Features
--------

- Built-in support for a wide variety of languages, including Ada, C, C#, C++,
  Haskell, Java, JavaScript, Lua, OCaml, Pascal, Perl, PHP, Python, Ruby,
  Scheme…
- Isolation: *camisole* runs both the compilation and execution stages in a
  **sandboxed** environment provided by isolate_
- Limitation of resources (time, wall-time, memory…)
- Simple HTTP + JSON or MessagePack interface

Demo
----

.. highlight:: console

*camisole* is used through a simple HTTP/JSON interface. Sending a program
is as simple as that::

    $ curl -s localhost:8080/run -d '{"lang": "python", "source": "print(42)"}' | python -m json.tool
    {
        "tests": [
            {
                "stdout": "42\n",
                "stderr": "",
                "meta": {
                    "status": "OK",
                    "exitcode": 0,
                    "wall-time": 0.067,
                    "cg-mem": 2528,
                    "killed": 0,
                    "exitsig": 0,
                    "exitsig-message": null,
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

License
-------

GPLv2+, see the ``LICENSE`` file.

.. _isolate: https://github.com/ioi/isolate
