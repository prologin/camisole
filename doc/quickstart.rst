.. _quickstart:

Quickstart
----------

This introduction assumes that there already exists a running |project| server.
See :ref:`installation` to install |project|.

.. highlight:: shell

Once the |project| server is running, you can query it with an HTTP client like
``curl``::

    $ curl localhost:8080/run -d \
        '{"lang": "python", "source": "print(42)"}'

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

