=====================
B32 for Encrypted LS2
=====================
.. meta::
    :author: zzz
    :created: 2019-03-13
    :thread: http://zzz.i2p/topics/2682
    :lastupdated: 2019-03-15
    :status: Open

.. contents::


Overview
========

Standard Base 32 ("b32") addresses contain the hash of the destination.
This will not work for encrypted ls2 (proposal 123).

You can't use a traditional base 32 address for an encrypted LS2 (proposal 123),
as it contains only the hash of the destination. It does not provide the non-blinded public key.
Clients must know the destination's public key, sig type,
the blinded sig type, and an optional secret or private key
to fetch and decrypt the leaseset.
Therefore, a base 32 address alone is insufficient.
The client needs either the full destination (which contains the public key),
or the public key by itself.
If the client has the full destination in an address book, and the address book
supports reverse lookup by hash, then the public key may be retrieved.

So we need a new format that puts the public key instead of the hash into
a base32 address. This format must also contain the signature type of the
public key, and the signature type of the blinding scheme.

This proposal documents a new b32 format for these addresses.
While we have referred to this new format during discussions
as a "b33" address, the actual new format retains the usual ".b32.i2p" suffix.

Goals
=====

- Include both unblinded and blinded sigtypes to support future blinding schemes
- Support pubkeys larger than 32 bytes
- Ensure b32 chars are all or mostly random, especially at the beginning
  (don't want all addresses to start with the same chars)
- Parseable
- Support "private" links that include blinding secret and/or per-client key
- Add checksum to detect typos
- Minimize length, maintain DNS label length less than 63 chars for normal usage
- Retain the usual ".b32.i2p" suffix.



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
    bit 1: 0 for no secret, 1 for appended secret
    bit 2: 0 for no per-client auth, 1 for appended per-client privkey
    bits 7-3: Unused, set to 0

  public key sigtype (1 or 2 bytes as indicated in flags)
    If 1 byte, the upper byte is assumed zero

  blinded key sigtype (1 or 2 bytes as indicated in flags)
    If 1 byte, the upper byte is assumed zero

  public key
    Number of bytes as implied by sigtype

  optional secret (only if secret flag is set)
    length of secret (1 byte)
    secret (UTF-8 encoded)

  optional auth private key (only if auth flag is set)
    auth type (1 byte)
    length of private key (1 byte)
    private key
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
  parse the remainder based on the flags to get the public key,
  optional secret, and optional auth privkey
{% endhighlight %}


Justification
=============

- XORing first 3 bytes with the hash provides a limited checksum capability,
  and ensures that all base32 chars at the beginning are randomized.
  Only a few flag and sigtype combinations are valid, so any typo is likely to create an invalid combination and will be rejected.
- In the usual case (1 byte sigtypes, no secret, no per-client auth),
  the hostname will be {56 chars}.b32.i2p, decoding to 35 bytes, same as Tor.
- Tor 2-byte checksum has a 1/64K false negative rate. With 3 bytes, minus a few ignored bytes,
  ours is approaching 1 in a million, since most flag/sigtype combinations are invalid.
- Adler-32 is a poor choice for small inputs, and for detecting small changes [ADLER32]_.
  Use CRC-32 instead. CRC-32 is fast and is widely available.

Caching
=======

While outside the scope of this proposal, routers and/or clients must remember and cache
(probably persistently) the mapping of public key to destination, and vice versa.



Notes
=====

- Distinguish old from new flavors by length. Old b32 addresses are always {52 chars}.b32.i2p. New ones are {56+ chars}.b32.i2p
- Tor discussion thread: https://lists.torproject.org/pipermail/tor-dev/2017-January/011816.html
- Don't expect 2-byte sigtypes to ever happen, we're only up to 13. No need to implement now.
- Hostnames with secret and/or privkeys are for private sharing only and are low-security.
- New format can be used in jump links (and served by jump servers) if desired, just like b32.


Issues
======

- Is a checksum required? If we don't have a checksum, we still must xor the leading bytes with something to randomize the b32 chars.
- Any secret, private key, or public key longer than 32 bytes would
  exceed the DNS max label length of 63 chars. Browsers probably do not care?


Migration
=========

No backward compatibility issues. Longer b32 addresses will fail to be converted
to 32-byte hashes in old software.




References
==========

.. [ADLER32]
    https://en.wikipedia.org/wiki/CRc-32
    https://tools.ietf.org/html/rfc3309
