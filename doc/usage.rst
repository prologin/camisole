Usage
=====

Camisole exposes a HTTP/JSON REST API. Once the HTTP server of camisole is
running, you can query it with any HTTP client using a POST request.

The body of your request should contain a JSON describing the request you want
to execute. Camisole will return the response as a JSON, always including a
flag `"success"` that indicates whether the request was successful or not.

Simple request
--------------

The main endpoint of camisole used to compile and execute code is ``/run``. You
always have to provide two mandatory parameters:

 - ``lang``: the language of your input
 - ``source``: the source code to compile and execute.

Example with an intepreted language:

.. literalinclude:: res/001-python-42.in.json
   :language: json


Result:

.. literalinclude:: res/001-python-42.out.json
   :language: json

Adding limits and quotas
------------------------

The compilation and execution of the program are sandboxed by default, which
means the process won't be able to access to any of the files in the root
filesystem except ``/usr``, ``/bin`` and ``/lib`` in readonly, it won't be able
to interact with any other process on the system or to use the network devices.

That said, the **resources** of the process aren't limited by default, which
means if you don't add limits and quotas, the process can consume all your
memory or your disk space and will never stop running.

You can put global resource limitations in the ``compile`` and ``execute`` bloc
for the compilation and the execution, respectively.

There are a lot of ways you can limit the resources of both the compilation and
the execution of your program:

- ``time``: limit the user time of the process (seconds)
- ``wall-time``: limit the wall time of the process (seconds)
- ``mem``: limit the available memory of the process (kilobytes)
- ``stack``: limit the stack size of the program (kilobytes)
- ``processes``: limit the number of processes and/or threads
- ``fsize``: limit the size of files created by the program (kilobytes)
- ``quota``: limit the disk quota to a number of blocks and inodes (separate
  both numbers by a comma)

This example demonstrates the use of resource limitations for both the
compilation and execution:

.. literalinclude:: res/004-ocaml-limits.in.json
   :language: json

To get more information about the different options, visit the `documentation
of isolate <https://github.com/ioi/isolate/blob/master/isolate.1.txt>`_, the
isolation backend, where they are described in detail.


Sending a test suite
--------------------

If you want to execute your program on multiple inputs, you shouldn't send one
request per input, as this would recompile the source code every time. You can
send a list of tests to camisole, and the compiled program will get executed
once per test.

To send a test suite, add a ``tests`` field in your input that contains a list
of tests. A text is a (possibly empty) object that can have the following
attributes:

- ``name``: the name of the test (defaults to an autoincremetal ``testXXX``)
- ``stdin``: the input that will be given to the program during this test
- Any additional test-specific resource limit. These resource limits, when
  specified, will override the global ones specified in the ``execute`` bloc.
- ``fatal``: a boolean indicating whether the test is fatal or not. If the test
  is fatal and its execution fails, the other tests won't be executed.

Note that you can also add the boolean ``all_fatal`` in your main request if
you want the tests to always be fatal.

Example input:

.. literalinclude:: res/003-python-testsuite.in.json
   :language: json

Output:

.. literalinclude:: res/003-python-testsuite.out.json
   :language: json

If you don't specify a test suite, Camisole will only execute a single test
named ``test000`` with an empty input.


Response format
---------------

Here is an example response:

.. literalinclude:: res/002-ocaml-simple.out.json
   :language: json

The three fields of the response are:

- the ``success`` flag indicating whether the request was performed
  successfully or if an exception occured.
- the ``compile`` object containing the compilation report
- the ``tests`` list containing all the executed tests, their names and
  reports.

A *report* is an object containing three fields:

- ``stdout``: the standard output of the program
- ``stderr``: the standard error output of the program
- ``exitcode``: the exit code of isolate. This is **not** the exit code of the
  program, but it is advised to use it as if it was the case.
  The difference is that if the program returns 0 but is killed or violates
  a resource limitation policy, or if ``isolate`` crashes, the exitcode flag
  will report an error even if the program in itself didn't return 0.
- ``meta``: the meta object of the report.

Execution metadata
------------------

The meta object contains metadata about the execution of the program and
reports information about what happened to it. The fields are:

- ``cg-mem``: Memory used by the control group (kilobytes)
- ``csw-forced``: Number of context switches forced by the kernel
- ``csw-voluntary``: Number of context switches caused by the process
- ``exitcode``: The actual exit code of the program
- ``exitsig``: The code of the fatal signal received by the process
- ``killed``: True if the program was killed by the sandbox
- ``max-rss``: Maximum resident size of the process (kilobytes)
- ``message``: Status message
- ``status``: Status code
- ``time``: User time of the process (seconds)
- ``wall-time``: Wall time of the process (seconds)

The status code can be one of the following:

- ``OK``: the program ran and exited successfuly
- ``RUNTIME_ERROR``: the program exited with a non-zero exit code
- ``TIMED_OUT``: the program timed out
- ``SIGNALED``: the program received a fatal signal
- ``INTERNAL_ERROR``: the sandbox crashed because of an internal error

Once again, to get more information about the meta object, visit the
`documentation of isolate
<https://github.com/ioi/isolate/blob/master/isolate.1.txt>`_.

Versions and options
--------------------

There is a way to retrieve some information about the languages enabled in
camisole: the endpoint ``/languages`` give you information about the versions
of the compilers, interpreters and runtimes and their options.

.. literalinclude:: res/languages.json
   :language: json


System information
------------------

You can also get information about the system where camisole is running by
doing a request to the ``/system`` endpoint.

.. literalinclude:: res/system.json
   :language: json
