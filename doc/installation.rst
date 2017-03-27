Installation
============

VM image
--------

TODO

Manual install
--------------

TODO

Core dependencies
*****************

The |project| core depends on:

* Python_ ≥3.6
* aiohttp_ (HTTP server)
* isolate_ (isolation backend)

Per-language dependencies
*************************

In order to actually compile and execution code in languages other than Python,
it is necessary to install each language compiler and/or runtime.

Below is a list of built-in languages supported by upstream |project| along
with the binaries needed to compile/run programs written in said language.

.. camisole-language-table::

.. _Python: https://python.org
.. _aiohttp: https://aiohttp.readthedocs.io
.. _isolate: https://github.com/ioi/isolate
