camisole's documentation
========================

|project| is a **secure online judge** for code compilation and execution. You
give some untrusted source code and a test suite, and |project| compiles the
code and runs it against the test suite.

It uses isolate_ as a backend to safely compile and execute source codes using
Linux kernel features such as namespaces, cgroups, chroot and resources limits.

|project| is aimed at:

- Computer science teachers who want to **grade their students** or provide
  them with an online tool to check their own code.
- Programming contests who want to grade the submissions of the contestants
  with an **online judge**.
- Programming websites who want to have an interactive demo where people can
  **run arbitrary code**.
- Online compiler/interpreter websites.

|project| handles all major languages, and can be easily extended to support
more. The built-in languages are:

.. camisole-language-list::

Communication with the |project| engine relies on a simple HTTP API with JSON
or MessagePack_ serialization.

You can contribute to the project development on GitHub_ by reporting issues,
making suggestions or opening pull requests.

Check out :ref:`quickstart` for a quick outlook of |project| features and usage.

Contents
--------

.. toctree::
   :maxdepth: 2

   quickstart
   installation
   commands
   usage
   extending
   faq
   dev

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _MessagePack: https://en.wikipedia.org/wiki/MessagePack
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _isolate: https://github.com/ioi/isolate
.. _GitHub: https://github.com/prologin/camisole

.. [#isolatepaper] `MAREŠ, Martin et BLACKHAM, Bernard. A new contest sandbox. Olympiads in Informatics, 2012, vol. 6, p.  100 <http://mj.ucw.cz/papers/isolate.pdf>`_.
