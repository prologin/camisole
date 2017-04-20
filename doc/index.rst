camisole's documentation
========================

|project| is a **secure online judge** for code compilation and execution. You
give some untrusted source code and a test suite, and |project| compiles the
code and runs it against the test suite.

It uses isolate_ as a backend to safely compile and execute source codes using
linux kernel features such as namespaces, cgroups, chroot and resources limits.

|project| is aimed at:

- Computer science teachers who want to **grade their students** or provide
  them with an online tool to check their own code.
- Programming contests who want to grade the submissions of the contestants
  with an **online judge**.
- Programming websites who want to have an interactive demo where people can
  **run arbitrary code**.
- Online compiler/interpreter websites.

|project| handles all major languages, and can be easily extended to support
more. The current supported languages are:

.. camisole-language-list::

Communication with the |project| engine relies on a simple HTTP/JSON REST API.

You can contribute to the project development on GitHub_ by reporting issues,
making suggestions or opening pull requests.

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   commands
   usage
   extending
   faq
   dev

Quickstart
----------

.. highlight:: shell

Once the |project| server is running, you can query it with an HTTP client like
``curl``::

    $ curl camisole/run -d '{"lang": "python", "source": "print(42)"}'

Result:

.. literalinclude:: res/001-python-42.out.json
   :language: json

You can easily limit, on a global or per-test basis, the maximum execution time
(user and wall), the available memory, the number of processes…

Those options are available both for the compilation and the tests.

Input:

.. literalinclude:: res/002-ocaml-simple.in.json
   :language: json

Output:

.. literalinclude:: res/002-ocaml-simple.out.json
   :language: json

You can give a full testsuite with different inputs and constraints, and you
will get a separate result for each test:

.. literalinclude:: res/003-python-testsuite.in.json
   :language: json

Output:

.. literalinclude:: res/003-python-testsuite.out.json
   :language: json


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _isolate: https://github.com/ioi/isolate
.. _GitHub: https://github.com/prologin/camisole

.. [#isolatepaper] `MAREŠ, Martin et BLACKHAM, Bernard. A new contest sandbox. Olympiads in Informatics, 2012, vol. 6, p.  100 <http://mj.ucw.cz/papers/isolate.pdf>`_.
