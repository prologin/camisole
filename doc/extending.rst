Extending camisole
==================

Camisole is built to be modular: adding support for a new language can be as
simple as three lines of code.

Add a custom or new language
----------------------------

To support a new language or customize a built-in one, you have to describe the
way the language is compiled and/or executed. This is done by subclassing the
``camisole.models.Lang`` class and defining some attributes or, for more
esoteric compilers & interpreters, overriding some methods.

Add an interpreted language
***************************

.. highlight:: console

In this example we will add support for a specific implementation of the
LOLCODE_ language. It is an interpreted language, meaning it does not need a
compilation step. Its interpreter can be found `on Github`_ and is used as
follows::

    $ /usr/bin/lci program.lol

.. _LOLCODE: https://en.wikipedia.org/wiki/LOLCODE
.. _`on Github`: https://github.com/justinmeza/lci

With that in mind, create a new Python script that defines a subclass of
``camisole.models.Lang``:

.. code-block:: python
   :caption: ~/lolcode.py
   :name: lolcode.py

   from camisole.models import Lang, Program

   class Lolcode(Lang):
       source_ext = '.lol'
       interpreter = Program('lci')
       reference_source = r'HAI 1.2, VISIBLE "42", KTHXBYE'

* ``source_ext`` is the extension used by the language source files;
  if that's not relevant, just use an empty string
* ``interpreter`` is a Program representing the interpreter binary
* ``reference_source`` is the source, written in the target language, of a
  program that shall output the string ``42\n`` (including the newline).
  This *reference program* will be used to test for working languages, eg. when
  calling :ref:`commands-test`, so it is important to get it right.

By simply creating this class and making it known to |project|, you'll be able
to submit jobs written in LOLCODE. By default, the name of the newly defined
language is the lowercase version of its class name, so in that case,
``lolcode``.

.. highlight:: python

If you like, you can overwrite the language name::

    class Lolcode(Lang, name="roflcode"):

.. highlight:: console

To check if |project| recognizes your new language, add the path to
``lolcode.py`` to ``CAMISOLE_LANGS`` and run :ref:`commands-test`::

    $ export CAMISOLE_LANGS=~/lolcode.py
    $ camisole test
    lolcode ..... OK
