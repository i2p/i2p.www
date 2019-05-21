==================
ECDSA key blinding
==================
.. meta::
    :author: orignal
    :created: 2019-05-21
    :lastupdated: 2019-05-21
    :status: Open

.. contents::


Motivation
==========

Some people don't like EdDSA or RedDSA. We should offer some alternatives and let them blind ECDSA signatures.

Overview
========

This proposal descibes key bliding for ECDSA signature types 1, 2, 3.

Proposal
========

Works the same way as RedDSA, but everything is in Big Endian.
Only same signature types are allowed, e.g. 1->1, 2->2, 3->3.

Definitions
-----------

B
    Curve's base point 

L
   Elliptic curve's group order. Property of curve.

DERIVE_PUBLIC(a)
    Convert a private key to public, by muplitpling B over an elliptic curve alpha
    A 32-byte random number known to those who know the destination.

GENERATE_ALPHA(destination, date, secret)
    Generate alpha for the current date, for those who know the destination and the secret.

a
    The unblinded 32-byte signing private key used to sign the destination

A
    The unblinded 32-byte  signing public key in the destination,
    = DERIVE_PUBLIC(a), as in correspoding curve

a'
    The blinded 32-byte  signing private key used to sign the encrypted leaseset
    This is a valid ECDSA private key.

A'
    The blinded 32-byte ECDSA signing public key in the Destination,
    may be generated with DERIVE_PUBLIC(a'), or from A and alpha.
    This is a valid ECDSA public key on the curve

H(p, d)
    SHA-256 hash function that takes a personalization string p and data d, and
    produces an output of length 32 bytes.

    Use SHA-256 as follows::

        H(p, d) := SHA-256(p || d)

HKDF(salt, ikm, info, n)
    A cryptographic key derivation function which takes some input key material ikm (which
    should have good entropy but is not required to be a uniformly random string), a salt
    of length 32 bytes, and a context-specific 'info' value, and produces an output
    of n bytes suitable for use as key material.

    Use HKDF as specified in [RFC-5869], using the HMAC hash function SHA-256
    as specified in [RFC-2104]. This means that SALT_LEN is 32 bytes max.


Blinding Calculations
---------------------

A new secret alpha and blinded keys must be generated each day (UTC).
The secret alpha and the blinded keys are calculated as follows.

GENERATE_ALPHA(destination, date, secret), for all parties:

.. raw:: html

  {% highlight lang='text' %}
// GENERATE_ALPHA(destination, date, secret)

  // secret is optional, else zero-length
  A = destination's signing public key
  stA = signature type of A, 2 bytes big endian (0x0001, 0x0002 or 0x0003)
  stA' = signature type of blinded public key A', 2 bytes big endian, always the same as stA
  keydata = A || stA || stA'
  datestring = 8 bytes ASCII YYYYMMDD from the current date UTC
  secret = UTF-8 encoded string
  seed = HKDF(H("I2PGenerateAlpha", keydata), datestring || secret, "i2pblinding1", 64)
  // treat seed as a 64 byte big-endian value
  alpha = seed mod L
{% endhighlight %}


BLIND_PRIVKEY(), for the owner publishing the leaseset:

.. raw:: html

  {% highlight lang='text' %}
// BLIND_PRIVKEY()

  alpha = GENERATE_ALPHA(destination, date, secret)
  a = destination's signing private key
  // Addition using scalar arithmentic
  blinded signing private key = a' = BLIND_PRIVKEY(a, alpha) = (a + alpha) mod L
  blinded signing public key = A' = DERIVE_PUBLIC(a')
{% endhighlight %}


BLIND_PUBKEY(), for the clients retrieving the leaseset:

.. raw:: html

  {% highlight lang='text' %}
// BLIND_PUBKEY()

  alpha = GENERATE_ALPHA(destination, date, secret)
  A = destination's signing public key
  // Addition using group elements (points on the curve)
  blinded public key = A' = BLIND_PUBKEY(A, alpha) = A + DERIVE_PUBLIC(alpha)
{% endhighlight %}


Both methods of calculating A' yield the same result, as required.

b33 address
===========

ECDSA's public key is (X,Y) pair, so for P256, for example, it's 64 bytes, rather than 32 as for RedDSA.
Either b33 address will be longer, or public key can be stored in compressed format like in bitcoin wallets.


