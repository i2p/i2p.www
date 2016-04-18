==================
Encrypted LeaseSet
==================
.. meta::
    :author: zzz
    :created: 2016-01-11
    :thread: http://zzz.i2p/topics/2047
    :lastupdated: 2016-01-12
    :status: Draft

.. contents::


Introduction
============

Current encrypted LS is horrendous and insecure. I can say that, I designed and
implemented it.

Reasons:

- AES CBC encrypted
- Single AES key for everybody
- Lease expirations still exposed
- Encryption pubkey still exposed


Goals
=====

- Make entire thing opaque
- Keys for each recipient


Strategy
========

Do like GPG/OpenPGP does. Asymmetrically encrypt a symmetric key for each
recipient. Data is decrypted with that asymmetric key. See e.g. [RFC-4880-S5.1]_
IF we can find an algo that's small and fast.

LS2 contents
------------

- Destination
- Published timestamp
- Expiration
- Flags
- Length of data
- Encrypted data
- Signature

Encrypted data could be prefixed with some enctype specifier, or not.

Trick is finding an asymmetric encryption that's small and fast. ElGamal at 514
bytes is a little painful here. We can do better.

See e.g. http://security.stackexchange.com/questions/824...

This works for small numbers of recipients (or actually, keys; you can still
distribute keys to multiple people if you like).


References
==========

.. [RFC-4880-S5.1]
    https://tools.ietf.org/html/rfc4880#section-5.1
