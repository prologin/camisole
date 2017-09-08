.. _installation:

Installation
============

.. highlight:: console

|project| should always be run in a virtual machine. In theory, the sandboxed
programs have no way to interact with the machine. In practice, some
configuration errors on your side, or even some kernel bugs might be exploited.
Refer to :ref:`why-vm` for more explanations.

VM image
--------

The easiest way to install |project| is to download the Virtualbox image:

* `Download camisole-latest.ova
  <https://camisole.prologin.org/ova/camisole-latest.ova>`_  (~1 GB)
* `Old releases <https://camisole.prologin.org/ova>`_

You can then import it in Virtualbox, (File / Import Appliance), click on the
"Start" or "Headless Start" button, and you should then have your Camisole
instance running on port 42920. Test your installation by visiting this URL::

   $ curl http://localhost:42920/

Archlinux packages
------------------

Using you preferred AUR helper (eg. pacaur), install ``camisole-git``. You can
also install the ``camisole-languages`` meta-package_ to install the
dependencies for all the built-in languages supported by |project|::

   $ pacaur -S camisole-git camisole-languages

.. _meta-package: https://aur.archlinux.org/packages/camisole-languages/

Manual install
--------------

|project| has mainly been tested on Archlinux, but it should work on other
platforms. That said, it requires some cutting edge versions that you might
have some trouble installing in other distributions.

The |project| core program depends on:

* a modern Linux kernel
* isolate_ (isolation backend)
* Python_ ≥3.6
* Python aiohttp_ (HTTP server)
* Python MessagePack_ (alternative to JSON)
* Python PyYAML_ (configuration)
* Python `JSON Schema`_ (user input validation)

On Archlinux, install those with your favorite AUR helper, eg. pacaur::

   $ pacaur -S isolate-git python-aiohttp python-msgpack python-yaml \
               python-jsonschema

Per-language dependencies
*************************

In order to actually compile and execution code in languages other than Python,
it is necessary to install each language compiler and/or runtime.

Below is a list of built-in languages supported by upstream |project| along
with the binaries needed to compile/run programs written in said language.

.. camisole-language-table::

Build and install
*****************

After installing all the required dependencies, you can build and install
|project|::

   $ git clone https://github.com/prologin/camisole
   $ cd camisole
   $ python3 setup.py build
   $ sudo python3 setup.py install

   $ python3 -m camisole serve

Be aware that you need to have the rights to run ``isolate``. In Archlinux,
you will need to add your user to the ``isolate`` group.

.. _Python: https://python.org
.. _aiohttp: https://aiohttp.readthedocs.io
.. _JSON Schema: http://json-schema.org
.. _isolate: https://github.com/ioi/isolate
.. _MessagePack: https://pypi.python.org/pypi/msgpack-python
.. _PyYAML: http://pyyaml.org/
