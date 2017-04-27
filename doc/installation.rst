Installation
============

Camisole should always be run in a virtual machine. In theory, the sandboxed
programs have no way to interact with the machine. In practice, some
configuration errors on your side, or even some kernel bugs might be exploited.
To limit the attack surface of your instance, you shouldn't run it on a
production machine.

VM image
--------

The best and easiest way to install Camisole is to download a Virtualbox
export here:

`Download camisole-latest.ova (~1 GB)
<https://camisole.prologin.org/ova/camisole-latest.ova>`_

`Archive of releases
<https://camisole.prologin.org/ova>`_

You can then import it in Virtualbox, (File / Import Appliance), click on the
"Start" or "Headless Start" button, and you should then have your Camisole
instance running on port 42920. Test your installation by visiting this URL::

    curl http://localhost:42920/


Manual install
--------------

Camisole has mainly been tested on Archlinux, but it should work on other
platforms. That said, it requires some cutting edge versions that you might
have some trouble installing in other distributions.

Core dependencies
*****************

The |project| core depends on:

* Python_ ≥3.6
* aiohttp_ (HTTP server)
* jsonschema_ (validate the JSON inputs)
* isolate_ (isolation backend)

On Archlinux, install those with::

    pacaur -S python-aiohttp python-jsonschema isolate-git

Per-language dependencies
*************************

In order to actually compile and execution code in languages other than Python,
it is necessary to install each language compiler and/or runtime.

Below is a list of built-in languages supported by upstream |project| along
with the binaries needed to compile/run programs written in said language.

.. camisole-language-table::

The Arch User Repository already have a meta-package depending on all the
languages supported by the upstream::

    pacaur -S camisole-languages

Build and install
*****************

After installing all the required dependancies, you can build and install
Camisole.

For Archlinux, you can install the ``camisole-git`` package in the Arch User
Repository::

    pacaur -S camisole-git

If you want to install and run it manually::

    git clone https://github.com/prologin/camisole
    cd camisole
    python3 setup.py build
    sudo python3 setup.py install

    python3 -m camisole serve

Be aware that you need to have the rights to run ``isolate``. In Archlinux,
you will need to add your user to the ``isolate`` group.


.. _Python: https://python.org
.. _aiohttp: https://aiohttp.readthedocs.io
.. _jsonschema: http://json-schema.org
.. _isolate: https://github.com/ioi/isolate
