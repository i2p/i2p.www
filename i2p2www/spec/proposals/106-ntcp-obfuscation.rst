================
NTCP Obfuscation
================
.. meta::
    :author: zzz
    :created: 2010-11-23
    :thread: http://zzz.i2p/topics/774
    :lastupdated: 2014-01-03
    :status: Rejected
    :supercededby: 111

.. contents::


Overview
========

This proposal is about overhauling the NTCP transport to improve its resistance
to automated identification.


Motivation
==========

NTCP data is encrypted after the first message (and the first message appears to
be random data), thus preventing protocol identification through "payload
analysis". It is still vulnerable to protocol identification through "flow
analysis". That's because the first 4 messages (i.e. the handshake) are fixed
length (288, 304, 448, and 48 bytes).

By adding random amounts of random data to each of the messages, we can make it
a lot harder.


Modifications to NTCP
=====================

This is fairly heavyweight but it prevents any detection by DPI equipment.

The following data will be added to the end of the 288-byte message 1:

- A 514-byte ElGamal encrypted block
- Random padding

The ElG block is encrypted to Bob's public key. When decrypted to 222 bytes, it
contains:
- 214 bytes random padding
- 4 bytes 0 reserved
- 2 bytes padding length to follow
- 2 bytes protocol version and flags

In messages 2-4, the last two bytes of the padding will now indicate the length
of more padding to follow.

Note that the ElG block does not have perfect forward secrecy but there's
nothing interesting in there.

We could modify our ElG library so it will encrypt smaller data sizes if we
think 514 bytes is way too much? Is ElG encryption for each NTCP setup too much?

Support for this would be advertised in the netdb RouterAddress with the option
"version=2". If only 288 bytes are received in Message 1, Alice is assumed to be
version 1 and no padding is sent in subsequent messages. Note that communication
could be blocked if a MITM fragmented IP to 288 bytes (very unlikely according
to Brandon).
