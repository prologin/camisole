For Developers
==============

Tests
-----

.. highlight:: console

Run tests (and coverage) with::

    $ pip install -r requirements-dev.txt
    $ pytest --cov=camisole

You can then generate an HTML report (browse to http://localhost:8000/)::

    $ coverage html
    $ ( cd htmlcov && python -m http.server )
