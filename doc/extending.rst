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

Add a compiled language
***********************

Many languages are compiled to machine code by a compiler, instead of being
executed by an interpreter. C, C++ and Rust are just three examples of such
languages.

To implement a compiled language in |project|, just replace ``interpreter`` with
``compiler`` in the code above. Let's try with Rust, for instance:

.. code-block:: python
   :caption: ~/rust.py
   :name: rust.py

   from camisole.models import Lang, Program

   class Rust(Lang):
       source_ext = '.rs'
       compiler = Program('rustc')
       reference_source = r'fn main() { println!("42"); }'

Of course there are many parameters available to configure the compiler
or interpreter. For languages that require a more complex build or execute
workflow, such as Java or Go, you can also override some methods exposed by the
:class:`Lang` class.

Please read the code of the many built-in languages shipped with |project| for
more examples on how you can tune program options and more broadly the build
pipeline itself.

Making the new langage discoverable
***********************************

.. highlight:: console

You have one or multiple Python files, say ``/tmp/camisole/lolcode.py`` and
``/tmp/camisole/rust.py``, containing language declarations ie. :class:`Lang`
classes. You have to make this file known to |project| in order to use it.

As a Python program, |project| relies on the *Python path* to find modules.
You can either put your files on the default Python path, but this may not be
a good idea as it is usually a system path belonging to root and managed by
your distribution package manager.

Instead, you can put your modules in either:

* ``/usr/share/camisole/languages`` (recommended for system-packaged modules)
* ``~/.local/share/camisole/languages``

You can also customize the ``PYTHONPATH`` environment variable with the
**directories** containing your Python file(s).

Then, add your modules (the Python **file names** without extension) to the
``CAMISOLE_LANGS`` environment variable, separated with semicolons (``:``).
When run, |project| will recognize your module and imports its :class:`Lang`
definitions.

    $ export PYTHONPATH=/tmp/camisole
    $ export CAMISOLE_LANGS=lolcode:rust
    $ camisole test
    lolcode ..... OK
    rust ........ OK

If your newly defined language does not appear, you can troubleshoot issues by
running ``test`` in a very verbose mode::

   $ camisole -l debug test
