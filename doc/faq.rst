Frequently Asked Questions
==========================

Can I run this in Docker/LXC/… or even directly on my server?
-------------------------------------------------------------

Yes, but we don't think it's a good idea for production environments. By using
a VM, you considerably reduce the attack surface and you won't risk getting
your host taken over if an exploit is found in the kernel that could allow an
attacker to exit the chroot or the namespaces in which they are sandboxed and
thus gain privilege escalation. `This has happened before`_.

Can I use this to run multiple source files?
--------------------------------------------

We're not planning on adding this feature. Camisole is designed for "quick and
dirty" source code evaluation. If you're planning to do anything more complex
than "take this source file, compile it and evaluate it", you'd be better off
using isolate_ directly and make it suit your needs better.

Why is it called *camisole*?
----------------------------

It means *straitjacket*, because we restrain what the programs can do. In
french, « Ça m'isole » means "It isolates me", it's a fun nod to our isolation
backend, isolate_.

.. _isolate: https://github.com/ioi/isolate
.. _This has happened before: https://lwn.net/Articles/543273/
