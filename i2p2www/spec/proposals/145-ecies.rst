==========
ECIES-P256
==========
.. meta::
    :author: orignal
    :created: 2019-01-23
    :thread: http://zzz.i2p/topics/2418
    :lastupdated: 2019-01-24
    :status: Open

.. contents::


Motivation
==========

ECIES-P256 is much faster than ElGamal. There are few i2pd eepsites with ECIES-P256 crypto type already and Java should be able to communicate with them and vice-versa. i2pd supports it since release 2.16.0 (0.9.32 Java).

Overview
========

This proposal introduces new crypto type ECIES-P256 that can appear in certiticate part of identity, or as separate encryption key type in LeaseSet2.
Can be used in RouterInfo, LeaseSet1 and LeaseSet2.


ElGamal Key Locations
---------------------

As a review,
ElGamal 256-byte public keys may be found in the following data structures.
Reference the common structures specification.

- In a Router Identity
  This is the router's encryption key.

- In a Destination
  The public key of the destination was used for the old i2cp-to-i2cp encryption
  which was disabled in version 0.6, it is currently unused except for
  the IV for LeaseSet encryption, which is deprecated.
  The public key in the LeaseSet is used instead.

- In a LeaseSet
  This is the destination's encryption key.

In 3 above, ECIES public key still takes 256 bytes, although actual key length is 64 bytes.
The rest must be filled with random padding.

- In a LS2
  This is the destination's encryption key. Key size is 64 bytes.


EncTypes in Key Certs
---------------------

ECIES-P256 uses encryption type 1.
Encryption types 2 and 3 should be reserved for ECIES-P284 and ECIES-P521


Asymmetric Crypto Uses
----------------------

This proposal describes replacement ofElGamal for:

1) Tunnel Build messages (key is in RouterIdentity). ElGamal block is 512 bytes
  
2) Client End-to-end ElGamal+AES/SessionTag (key is in LeaseSet, the Destination key is unused). ElGamal block is 514

3) Router-to-router encryption of netdb and other I2NP msgs. ElGamal block is 514 bytes


Goals
-----

- Backwards compatible
- No changes for existing data structure
- Much more CPU-efficient than ElGamal

Non-Goals
---------

- RouterInfo and LeaseSet1 can't publish ElGamal and ECIES-P256 together

Justification
-------------

ElGamal/AES+SessionTag engine always stuck on lack of tags, that produces dramatic perfomance degradation in I2P communications.
Tunnel build is heaviest operation because originator must run ElGamal encryption 3 times per each tunnel build request.


Cryptographic Primitives required
=================================

1) EC P256 curve key generation and DH

2) AES-CBC-256

3) SHA256


Detailed Proposal
=================

A destination with ECIES-P256 publishes itslef with crypto type 1 in certificate.
First 64 bytes of 256 in identity should be interpreted as ECIES public key and the rest must be ignored.
LeaseSet's separate encryption key is based on key type from identity.

ECIES block for ElGamal/AES+SessionTags
---------------------------------------
ECIES block replaces ElGamal block for For ElGamal/AES+SessionTags. The length in 514 bytes.
Consists of two parts 257 bytes each. 
The first part starts with zero and then P256 ephemeral public key of 64 bytes, the rest 192 bytes is random padding.
The second part starts with zero and then AES-CBC-256 encrypted 256 bytes with the same content as in ElGamal.

ECIES block for tunnel build record
------------------------------------
Tunnel build record is the same, but without leading zeroes in blocks.
A tunnel can be through any combination of routers' crypto types and it's done per record.
Tunnel's originator encrypts records depending on tunnel participant's published crypto type, tunnel participant decrypts based on own crypto type.


AES-CBC-256 key
---------------
This is ECDH shared keys calculation where KDF is SHA256 over x coordinate.
Let Alice as encryptor and Bob as decryptor.
Assume k is Alice's randomly picked ephemeral P256 private key and P is Bob's public key.
S is shared secret S(Sx, Sy)
Alice calculates S by "agreeing" k with P, e.g. S = k*P.

Asssume K is Alice's ephemeral public key and p is Bob's private key.
Bob take K from first block of received message and calculates S = p*K

AES encryption key is SHA256(Sx) and iv is Sy.


