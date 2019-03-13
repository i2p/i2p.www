=====================
EdDSA-BLAKE2b-Ed25519
=====================
.. meta::
    :author: zzz
    :created: 2019-03-12
    :thread: http://zzz.i2p/topics/2689
    :lastupdated: 2019-03-13
    :status: Open

.. contents::


Overview
========


This proposal adds two new signature types using BLAKE2b-512 with
personalization strings and salts, to replace SHA-512.
This will eliminate three classes of possible attacks.


Motivation
==========

During discussions and design of NTCP2 (proposal 111) and LS2 (proposal 123),
we briefly considered various attacks that were possible, and how to
prevent them. Three of these attacks are Length Extension Attacks,
Reuse of Signed Data, and Duplicate Message Identification.

For both NTCP2 and LS2, we decided that
these attacks were not directly relevant to the proposals at hand,
and any solutions conflicted with the goal of minimizing new primitives.
Also, we determined that the speed of the hash functions in these protocols
was not an important factor in our decisions.
Therefore, we mostly deferred the solution to a separate proposal.
While we did add some personalization features to the LS2 specification,
we did not require any new hash functions.

Many projects, such as ZCash [ZCASH]_, are using hash functions and
signature algorithms based on newer algorithms that are not vulnerable to
the following attacks.


Length Extension Attacks
------------------------

SHA-256 and SHA-512 are vulnerable to Length Extension Attacks (LEA) [LEA]_.
This is the case when actual data is signed, not the hash of the data.
In most I2P protocols (streaming, datagrams, netdb, and others), the actual
data is signed. One exception is SU3 files, where the hash is signed.
The other exception is signed datagrams for DSA (sig type 0) only,
where the hash is signed.
For other signed datagram sig types, the data is signed.


Reuse of Signed Data
--------------------

Signed data in I2P protocols may be vulnerable to
a Reuse of Signed Data (RSD) due to lack Of domain separation.
This allows an attacker to use data received in one context
(such as a signed datagram) and present it as valid, signed data
in another context (such as streaming or network database).
While it is unlikely that the signed data from one context would be parsed
as valid data in another context, it is difficult or impossible to
analyze all situations to know for sure.
Additionally, in some context, it may be possible for an attacker to
induce a victim to sign specially-crafted data which could be valid data
in another context.
Again, it is difficult or impossible to analyze all situations to know for sure.


Duplicate Message Identification
--------------------------------

I2P protocols may be vulnerable to Duplicate Message Identification (DMI).
This may allow an attacker to identify that two signed messages have the same
content, even if these messages and their signatures are encrypted.
While it is unlikely due to the encryption methods used in I2P,
it is difficult or impossible to analyze all situations to know for sure.
By using a hash function that provides a method to add a random salt,
all signatures will be different even when signing the same data.
While Red25519 as defined in proposal 123 adds a random salt to the hash function,
this does not solve the problem for unencrypted lease sets.


Speed
-----

While not a primary motivation for this proposal,
SHA-512 is relatively slow, and faster hash functions are available.


Goals
=====

- Prevent above attacks
- Minimize use of new crypto primitives
- Use proven, standard crypto primitives
- Use standard curves
- Use faster primitives if available


Design
======

Modify the existing Ed25519 and Red25519 signature types to use BLAKE2b-512
instead of SHA-512. Add unique personalization strings for each use case.
Use the BLAKE2b salt feature for Ed25519.


Justification
=============

- BLAKE2b is not vulnerable to LEA [BLAKE2]_.
- BLAKE2b provides a standard way to add personalization strings for domain separation
- BLAKE2b provides a standard way to add a random salt to prevent DMI.
- BLAKE2b is faster than SHA-256 and SHA-512 (and MD5) on modern hardware,
  according to [BLAKE2]_.
- Ed25519 is still our fastest signature type, much faster than ECDSA, at least in Java.
- Ed25519 [ED25519-REFS]_ requires a 512 bit cryptographic hash function.
  It does not specify SHA-512. BLAKE2b is just as suitable for the hash function.
- BLAKE2b is widely available in libraries for many programming languages, such as Noise.


Specification
=============

Use unkeyed BLAKE2b-512 as in [BLAKE2]_ with salt and personalization.
All uses of BLAKE2b signatures will use a 16-character personalization string.

When used in EdDSA_BLAKE2b_Ed25519 signing,
when hashing the data to calculate r,
set a new BLAKE2b 16-byte random salt for each signature.
When calculating S, reset the salt to the default of all-zeros.

When used in RedDSA_BLAKE2b_Ed25519 signing,
A random salt is allowed, however it is not necessary, as the signature algorithm
adds 80 bytes of random data (see proposal 123).

When used in EdDSA_BLAKE2b_Ed25519 and RedDSA_BLAKE2b_Ed25519 verification,
do not use a random salt, use the default of all-zeros.

The salt and personalization features are not specified in [RFC-7693]_;
use those features as specified in [BLAKE2]_.


Signature Types
---------------

For EdDSA_BLAKE2b_Ed25519, replace the SHA-512 hash function
in EdDSA_SHA512_Ed25519 (signature type 7)
with BLAKE2b-512. No other changes.

For RedDSA_BLAKE2b_Ed25519, replace the SHA-512 hash function
in RedDSA_SHA512_Ed25519 (signature type 11, as defined in proposal 123)
with BLAKE2b-512. No other changes.

We do not need an replacement for
EdDSA_SHA512_Ed25519ph (signature type 8) for su3 files,
because the prehashed version of EdDSA is not vulnerable to LEA.
EdDSA_SHA512_Ed25519 (signature type 7) is not supported for su3 files.


=======================  ===========  ======  =====
        Type             Type Code    Since   Usage
=======================  ===========  ======  =====
EdDSA_BLAKE2b_Ed25519        12        TBD    Router Identities and Destinations
RedDSA_BLAKE2b_Ed25519       13        TBD    For Destinations and encrypted leasesets only; never used for Router Identities
=======================  ===========  ======  =====



Common Structure Data Lengths
-----------------------------

The following applies to both new signature types.


==================================  =============
            Data Type                  Length    
==================================  =============
Hash                                     64      
Private Key                              32      
Public Key                               32      
Signature                                64      
==================================  =============



Personalizations
----------------

To provide domain separation for the various uses of signatures,
we will use the BLAKE2b personalization feature.
The following applies to both new signature types.

All uses of BLAKE2b signatures will use a 16-character personalization string.
Any new uses must be added to the table here, with a unique personalization.

The NTCP 1 and SSU handshake uses below are for the signed data defined in the
handshake itself.
Signed RouterInfos in DatabaseStore Messages will use the NetDb Entry personalization,
just as if stored in the NetDB.


==================================  ==========================
         Usage                      16 Byte Personalization
==================================  ==========================
I2CP SessionConfig                  "I2CP_SessionConf"
NetDB Entries (RI, LS, LS2)         "network_database"
NTCP 1 handshake                    "NTCP_1_handshake"
Signed Datagrams                    "sign_datagramI2P"
Streaming                           "streaming_i2psig"
SSU handshake                       "SSUHandshakeSign"
SU3 Files                           n/a, not supported
==================================  ==========================



Notes
=====



Issues
======




Migration
=========

The same as with the rollout for previous signature types.

We plan to change new routers from type 7 to type 12 as the default.
We plan to eventually migrate existing routers from type 7 to type 12,
using the "rekeying" process used after type 7 was introduced.
We plan to change new destinations from type 7 to type 12 as the default.
We plan to change new encrypted destinations from type 11 to type 13 as the default.

We will support blinding from types 7, 11, 12, and 13 to type 13.
We will not support blinding 12 or 13 to type 11.

New routers could start using the new sig type by default after a few months.
New destinations could start using the new sig type by default after perhaps a year.

For the minimum router version 0.9.TBD, routers must ensure:

- Do not store (or flood) a RI or LS with the new sig types to routers less than version 0.9.TBD.
- When verifying a netdb store, do not fetch a RI or LS with the new sig types from routers less than version 0.9.TBD.
- Routers with a new sig type in their RI may not connect to routers less than version 0.9.TBD,
  either with NTCP, NTCP2, or SSU.
- Streaming connections and signed datagrams won't work to routers less than version 0.9.TBD,
  but there's no way to know that, so these sig types should not be used by default for some period
  of months or years after 0.9.TBD is released.



References
==========

.. [BLAKE2]
   https://blake2.net/blake2.pdf

.. [ED25519-REFS]
    "High-speed high-security signatures" by Daniel
    J. Bernstein, Niels Duif, Tanja Lange, Peter Schwabe, and
    Bo-Yin Yang. http://cr.yp.to/papers.html#ed25519

.. [EDDSA-FAULTS]
   https://news.ycombinator.com/item?id=15414760

.. [LEA]
   https://en.wikipedia.org/wiki/Length_extension_attack

.. [RFC-7693]
   https://tools.ietf.org/html/rfc7693

.. [ZCASH]
   https://github.com/zcash/zips/tree/master/protocol/protocol.pdf



