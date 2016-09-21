# TODO

TODO

# FAQ

## Can I run this in Docker/LXC/… or even directly on my server?

Yes, but we don't think it's a good idea for production environments. By using
a VM, you considerably reduce the attack surface and you won't risk getting
your host taken over if an exploit is found in the kernel that could allow an
attacker to exit the chroot or the namespaces in which they are sandboxed and
thus gain privilege escalation.
[This has happened before.](https://lwn.net/Articles/543273/)

## Why is it called *camisole*?

It means *straitjacket*, because we restrain what the programs can do. In
french, « Ça m'isole » means "It isolates me", it's a fun nod to our isolation
backend, [isolate](https://github.com/ioi/isolate)
