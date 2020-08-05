===========================
B32 for Encrypted Leasesets
===========================
.. meta::
    :lastupdated: 2020-08
    :accuratefor: 0.9.47

.. contents::


Overview
========

Standard Base 32 ("b32") addresses contain the hash of the destination.
This will not work for encrypted ls2 (proposal 123).

We can't use a traditional base 32 address for an encrypted LS2 (proposal 123),
as it contains only the hash of the destination. It does not provide the non-blinded public key.
Clients must know the destination's public key, sig type,
the blinded sig type, and an optional secret or private key
to fetch and decrypt the leaseset.
Therefore, a base 32 address alone is insufficient.
The client needs either the full destination (which contains the public key),
or the public key by itself.
If the client has the full destination in an address book, and the address book
supports reverse lookup by hash, then the public key may be retrieved.

This format puts the public key instead of the hash into
a base32 address. This format must also contain the signature type of the
public key, and the signature type of the blinding scheme.

This document specifies a b32 format for these addresses.
While we have referred to this new format during discussions
as a "b33" address, the actual new format retains the usual ".b32.i2p" suffix.

Design
======

- New format will contain the unblinded public key, unblinded sig type,
  and blinded sig type.
- Optionally contain a secret and/or private key, for private links only
- Use the existing ".b32.i2p" suffix, but with a longer length.
- Add a checksum.
- Addresses for encrypted leasesets are identified by 56 or more encoded characters
  (35 or more decoded bytes), compared to 52 characters (32 bytes) for traditional base 32 addresses.


Specification
=============

Creation and encoding
---------------------

Construct a hostname of {56+ chars}.b32.i2p (35+ chars in binary) as follows:

.. raw:: html

  {% highlight lang='text' %}
flag (1 byte)
    bit 0: 0 for one-byte sigtypes, 1 for two-byte sigtypes
    bit 1: 0 for no secret, 1 if secret is required
    bit 2: 0 for no per-client auth,
           1 if client private key is required
    bits 7-3: Unused, set to 0

  public key sigtype (1 or 2 bytes as indicated in flags)
    If 1 byte, the upper byte is assumed zero

  blinded key sigtype (1 or 2 bytes as indicated in flags)
    If 1 byte, the upper byte is assumed zero

  public key
    Number of bytes as implied by sigtype

{% endhighlight %}

Post-processing and checksum:

.. raw:: html

  {% highlight lang='text' %}
Construct the binary data as above.
  Treat checksum as little-endian.
  Calculate checksum = CRC-32(data[3:end])
  data[0] ^= (byte) checksum
  data[1] ^= (byte) (checksum >> 8)
  data[2] ^= (byte) (checksum >> 16)

  hostname = Base32.encode(data) || ".b32.i2p"
{% endhighlight %}

Any unused bits at the end of the b32 must be 0.
There are no unused bits for a standard 56 character (35 byte) address.


Decoding and Verification
-------------------------

.. raw:: html

  {% highlight lang='text' %}
strip the ".b32.i2p" from the hostname
  data = Base32.decode(hostname)
  Calculate checksum = CRC-32(data[3:end])
  Treat checksum as little-endian.
  flags = data[0] ^ (byte) checksum
  if 1 byte sigtypes:
    pubkey sigtype = data[1] ^ (byte) (checksum >> 8)
    blinded sigtype = data[2] ^ (byte) (checksum >> 16)
  else (2 byte sigtypes) :
    pubkey sigtype = data[1] ^ ((byte) (checksum >> 8)) || data[2] ^ ((byte) (checksum >> 16))
    blinded sigtype = data[3] || data[4]
  parse the remainder based on the flags to get the public key
{% endhighlight %}


Secret and Private Key Bits
---------------------------

The secret and private key bits are used to indicate to clients, proxies, or other
client-side code that the secret and/or private key will be required to decrypt the
leaseset. Particular implementations may prompt the user to supply the
required data, or reject connection attempts if the required data is missing.


Caching
=======

While outside the scope of this specification, routers and/or clients must remember and cache
(probably persistently) the mapping of public key to destination, and vice versa.



Notes
=====

- Distinguish old from new flavors by length. Old b32 addresses are always {52 chars}.b32.i2p. New ones are {56+ chars}.b32.i2p
- Tor discussion thread: https://lists.torproject.org/pipermail/tor-dev/2017-January/011816.html
- Don't expect 2-byte sigtypes to ever happen, we're only up to 13. No need to implement now.
- New format can be used in jump links (and served by jump servers) if desired, just like b32.



References
==========

.. [ADLER32]
    https://en.wikipedia.org/wiki/CRC-32
    https://tools.ietf.org/html/rfc3309
