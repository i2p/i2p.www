=============
GOST Sig Type
=============
.. meta::
    :author: orignal
    :created: 2017-02-18
    :thread: http://zzz.i2p/topics/2239
    :lastupdated: 2017-03-31
    :status: Open

.. contents::


Overview
========

Elliptic curve signature  GOST R 34.10 used by officials and businesses in Russia.
Supporting it could simplify integration of existing apps (usually CryptoPro based).
Hash function is GOST R 34.11 of 32 or 64 bytes.
Basially works the same way as EcDSA, signature and public key size is 64 or 128 bytes.


Motivation
==========

Elliptic curve cryptography was never been trusted completely and produce a lot of speculation about possible backdoors. 
Hence there is no ultimate signature type trusted by everybody.
Adding one more signature type will give people more choice what they trust more.


Design
======

GOST R 34.10 uses standard ellicptic curve with own parameters sets.
Existing groups's math can be reused.
However signing and verification is different and must be implemented.
See RFC: https://www.rfc-editor.org/rfc/rfc7091.txt
GOST R 34.10 is supposed to work together with GOST R 34.11 hash.
We will use GOST R 34.10-2012 (aka steebog) either 256 or 512 bits.
See RFC: https://tools.ietf.org/html/rfc6986

GOST R 34.10 doesn't specify parameters however there are some good parameters sets used by everybody.
GOST R 34.10-2012 with 64 bytes public keys inherits CryptoPro's parameter sets from GOST R 34.10-2001
See RFC: https://tools.ietf.org/html/rfc4357

However newer parameter sets for 128 bytes keys are created by specical technical committee tc26 (tc26.ru).
See RFC: https://www.rfc-editor.org/rfc/rfc7836.txt

Openssl-based implementation in i2pd shows it faster than P256 and slower than 25519.

Specification
=============

Only GOST R 34.10-2012 and GOST R 34.11-2012 are supported.
Two new signature types:
9 - GOSTR3410_GOSTR3411_256_CRYPTO_PRO_A stands for public key and signture type of 64 bytes, hash size of 32 bytes and parameters set CryptoProA (aka CryptoProXchA)
10 - GOSTR3410_GOSTR3411_512_TC26_A stands for public key and signature type of 128 bytes, hash size of 64 bytes and parameters set A from TC26.

Migration
=========

These signature types are supposed to be used as optional signature type only.
No migration is required. i2pd supports it already.

