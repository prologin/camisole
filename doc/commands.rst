Commands
========

.. highlight:: console

|project| exposes a few commands for inspection and self-testing, in addition
to the main ``serve`` command.

.. _commands-languages:

``camisole languages``
----------------------

List supported languages::

    $ camisole languages
    Name         | Display name  | Module                          | Class name
    ada          | Ada           | camisole.languages.ada          | Ada
    brainfuck    | Brainfuck     | camisole.languages.brainfuck    | Brainfuck
    c            | C             | camisole.languages.c            | C


You can remove the header by piping the result into ``tail``::

    $ camisole language | tail -n+2
    ada          | Ada           | camisole.languages.ada          | Ada

.. _commands-test:

``camisole test``
-----------------

List supported languages and check if they are working::

    $ camisole test
    ada ......... FAIL
    brainfuck ... OK
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
                          'exitsig': None,
                          'killed': 0,
                          'max-rss': 0,
                          'message': 'execve("/usr/bin/gnatmake"): No such file or '
                                     'directory',
                          'status': 'INTERNAL_ERROR',
                          'time': 0.0,
                          'time-wall': 0.0},
                 'stderr': '',
                 'stdout': ''}}

.. _commands-serve:

``camisole serve``
------------------

Run the |project| HTTP server::

    $ camisole serve

Host and port are customizable::

    $ camisole serve -h 0.0.0.0 -p 9000
