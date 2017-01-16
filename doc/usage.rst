Usage
=====

.. highlight:: console

TODO

.. _usage-languages:

``camisole languages``
----------------------

List supported languages and check if they are working::

    $ camisole languages
    ada ......... FAIL
    brainfuck ... OK
    c ........... OK

You can show slightly more verbose failures::

    $ camisole languages -v
    ada ......... FAIL
        execve("/usr/bin/gnatmake"): No such file or directory

Or much more verbose failures::

    $ camisole languages -vv
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


``camisole serve``
------------------

Run the |project| HTTP server::

    $ camisole serve

Host and port are customizable::

    $ camisole serve -h 0.0.0.0 -p 9000

Sending jobs
------------

TODO::

    $ curl

.. highlight:: python

TODO::

    import requests
    requests.get()

Request grammar
***************

Response grammar
****************
