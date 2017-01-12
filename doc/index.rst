camisole's documentation
========================

|project| is an asyncio_-based source compiler and test runner. The main
purpose of this tool is to build programs from user-provided source and then
execute them against a user-provided test suite.

It uses isolate_ as a backend to safely compile and execute source codes using
linux kernel features such as namespaces, cgroups, chroot and resources limits.
You can learn more about isolate in this paper [#isolatepaper]_.

Communication with the |project| engine relies on a simple HTTP/JSON API.

|project| requires Python 3.6 or newer.

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   configuration
   usage
   extending

Quick demo
----------

.. highlight:: shell

The |project| HTTP server is run by calling::

    $ python -m camisole serve
    ======== Running on http://0.0.0.0:8080 ========

Then, jobs are submitted with an HTTP request::

    $ curl -s localhost:8080/run \
           -d '{"lang": "python", "source": "print(42)", "tests": [{}]}'

Example result:

.. literalinclude:: res/example-result.json
   :language: json


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _isolate: https://github.com/ioi/isolate

.. [#isolatepaper] `MAREŠ, Martin et BLACKHAM, Bernard. A new contest sandbox. Olympiads in Informatics, 2012, vol. 6, p.  100 <http://mj.ucw.cz/papers/isolate.pdf>`_.
