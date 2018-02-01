Commands
========

.. highlight:: console

In addition to the main ``serve`` command, |project| exposes multiple tools
for inspection and self-testing.

.. _commands-serve:

``camisole serve``
------------------

Run the |project| HTTP server::

    $ camisole serve

Host and port are customizable::

    $ camisole serve -h 0.0.0.0 -p 9000

.. _commands-languages:

``camisole languages``
----------------------

List supported languages::

    $ camisole languages
    Name         | Display name  | Module                          | Class name
    ada          | Ada           | camisole.languages.ada          | Ada
    c            | C             | camisole.languages.c            | C

.. _commands-test:

``camisole test``
-----------------

List supported languages and check if they are working::

    $ camisole test
    ada ......... FAIL
    c ........... OK

You can show slightly more verbose failures::

    $ camisole test -v
    ada ......... FAIL
        execve("/usr/bin/gnatmake"): No such file or directory

Or much more verbose failures::

    $ camisole test -vv
    ada ......... FAIL
    {'compile': {'exitcode': 2,
                 'meta': {'cg-mem': 0,
                          'csw-forced': 0,
                          'csw-voluntary': 0,
                          'exitcode': 0,
                          'exitsig': 0,
                          'exitsig-message': null,
                          'killed': 0,
                          'max-rss': 0,
                          'message': 'execve("/usr/bin/gnatmake"): No such file or '
                                     'directory',
                          'status': 'INTERNAL_ERROR',
                          'time': 0.0,
                          'wall-time': 0.0},
                 'stderr': '',
                 'stdout': ''}}

.. _commands-benchmark:

``camisole benchmark``
----------------------

Give statistics on available langages when run on their reference source code
(a program that shall print ``42\n``), namely the minimum memory quota required
to run the test, the max resident set side (RSS) observed, the duration and
wall-clock duration::

    $ camisole benchmark -v
    Language    |  Memory (kB) | Max RSS (kB)                | Time (s)                    | Wall time (s)
    c           |         7886 | x  1579  μ  1588  σ²    42  | x 0.001  μ 0.001  σ² 0.001  | x 0.047  μ 0.047  σ² 0.005
    java        |        12549 | x 29276  μ 29320  σ²   977  | x 0.109  μ 0.104  σ² 0.013  | x 0.132  μ 0.127  σ² 0.018
    lua         |        12549 | x  2072  μ  2060  σ²    38  | x 0.001  μ 0.001  σ² 0.001  | x 0.050  μ 0.049  σ² 0.017
    …

``x``: average, ``µ``: mean, ``σ²``: standard deviation.

.. note::

   The benchmark results will be highly dependent of the host system running
   this test, especially its CPU, I/O capabilities and the system load while the
   benchmark is run.
