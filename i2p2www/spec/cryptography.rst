====================================
Low-level Cryptography Specification
====================================
.. meta::
    :category: Design
    :lastupdated: April 2020
    :accuratefor: 0.9.46

.. contents::


Overview
========

This page specifies the low-level details of the cryptography in I2P.

There are several cryptographic algorithms in use within I2P.
In I2P's original design, there was only one of each type - one symmetric algorithm,
one asymmetric algorithm, one signing algorithm, and one hashing algorithm.
There was no provision to add more algorithms or migrate to
ones with more security.

In recent years we have added a framework to support multiple
primitives and combinations in a backward-compatible way.
Numerous signature algorithms, with varying key and signature lengths,
are defined by "signature types".
End-to-end encryption schemes, using a combination of asymmetric and symmetric encryption,
and with varying key lengths, are defined by "encryption types".

Various protocols and data structures in I2P include fields to
specify the signature type and/or encryption type.
These fields, together with the type definitions, define the key and signature
lengths and the cryptographic primitives required to use them.
The definitions of the signature and encryption types
is in the Common Structures specification [Common]_.

The original I2P protocols NTCP, SSU, and ElGamal/AES+SessionTags use a combination
of ElGamal asymmetric encryption and AES symmetric encryption.
Newer protocols NTCP2 and ECIES-X25519-AEAD-Ratchet
use a combination of X25519 key exchange and ChaCha20/Poly1305 symmetric encryption.

- NTCP2 has replaced NTCP.
- ECIES-X25519-AEAD-Ratchet design and implementation are complete,
  and will replace ElGamal/AES+SessionTags in late 2020.
- SSU2, using X25519 and ChaCha20/Poly1305, is scheduled for design in late 2020
  to replace SSU in 2021.


Asymmetric Encryption
=====================

The original asymmetric encryption algorithm in I2P is ElGamal.
The newer algorithm, used in several places, is ECIES X25519 DH key exchange.

We are in the process of migrating all ElGamal usage to X25519.

NTCP (with ElGamal) was migrated to NTCP2 (with X25519).
ElGamal/AES+SessionTag is being migrated to ECIES-X25519-AEAD-Ratchet.


X25519
------

For the details of X25519 usage see [NTCP2]_ and [ECIES]_.


ElGamal
-------

ElGamal is used in several places in I2P:

* To encrypt router-to-router [TunnelBuild]_ messages

* For end-to-end (destination-to-destination) encryption as a part of
  ElGamal/AES+SessionTag [ELG-AES]_ using the encryption key in the [LeaseSet]_

* For encryption of some netDb stores and queries sent to floodfill routers
  [NETDB-DELIVERY]_ as a part of ElGamal/AES+SessionTag [ELG-AES]_
  (destination-to-router or router-to-router).

We use common primes for 2048 ElGamal encryption and decryption, as given by
IETF [RFC-3526]_.  We currently only use ElGamal to encrypt the IV and session
key in a single block, followed by the AES encrypted payload using that key and
IV.

The unencrypted ElGamal contains: 

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |nonz|           H(data)                |
  +----+                                  +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +    +----+----+----+----+----+----+----+
  |    |  data...
  +----+----+----+-//
{% endhighlight %}

The H(data) is the SHA256 of the data that is encrypted in the ElGamal block,
and is preceded by a random nonzero byte.  This byte is actually random as of 0.9.28;
prior to that it was always 0xFF.  It could possibly be used for flags in the
future.  The data encrypted in the block may be up to 222 bytes long.  As the
encrypted data may contain a substantial number of zeros if the cleartext is
smaller than 222 bytes, it is recommended that higher layers pad the cleartext
to 222 bytes with random data.  Total length: typically 255 bytes.

The encrypted ElGamal contains: 

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |  zero padding...       |              |
  +----+----+----+-//-+----+              +
  |                                       |
  +                                       +
  |       ElG encrypted part 1            |
  ~                                       ~
  |                                       |
  +    +----+----+----+----+----+----+----+
  |    |   zero padding...      |         |
  +----+----+----+----+-//-+----+         +
  |                                       |
  +                                       +
  |       ElG encrypted part 2            |
  ~                                       ~
  |                                       |
  +         +----+----+----+----+----+----+
  |         +
  +----+----+
{% endhighlight %}

Each encrypted part is prepended with zeros to a size of exactly 257 bytes.
Total length: 514 bytes.  In typical usage, higher layers pad the cleartext
data to 222 bytes, resulting in an unencrypted block of 255 bytes.  This is
encoded as two 256-byte encrypted parts, and there is a single byte of zero
padding before each part at this layer.

See the ElGamal code [ElGamalEngine]_.

The shared prime is the Oakley prime for 2048 bit keys [RFC-3526-S3]_::

    2^2048 - 2^1984 - 1 + 2^64 * { [2^1918 pi] + 124476 }

or as a hexadecimal value::

    FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
    29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
    EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
    E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
    EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
    C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
    83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
    670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B
    E39E772C 180E8603 9B2783A2 EC07A28F B5C55DF0 6F4C52C9
    DE2BCBF6 95581718 3995497C EA956AE5 15D22618 98FA0510
    15728E5A 8AACAA68 FFFFFFFF FFFFFFFF

Using 2 as the generator.

.. _exponent:

Short Exponent
``````````````
While the standard exponent size is 2048 bits (256 bytes) and the I2P
[PrivateKey]_ is a full 256 bytes, in some cases we use the short exponent size
of 226 bits (28.25 bytes).  This should be safe for use with the Oakley primes
[vanOorschot1996]_ [BENCHMARKS]_.

Also, [Koshiba2004]_ apparently supports this, according to this sci.crypt
thread [SCI.CRYPT]_.  The remainder of the PrivateKey is padded with zeroes.

Prior to release 0.9.8, all routers used the short exponent.  As of release
0.9.8, 64-bit x86 routers use a full 2048-bit exponent.
All router now use the full exponent except for a small number of routers
on very slow hardware, who continue
to use the short exponent due to concerns about processor load.  The transition
to a longer exponent for these platforms is a topic for further study.

Obsolescence
````````````
The vulnerability of the network to an ElGamal attack and the impact of
transitioning to a longer bit length is to be studied.  It may be quite
difficult to make any change backward-compatible.


Symmetric Encryption
====================

The original symmetric encryption algorithm in I2P is AES.
The newer algorithm, used in several places, is
Autheticated Encryption with Associated Data (AEAD) ChaCha20/Poly1305.

We are in the process of migrating all AES usage to ChaCha20/Poly1305.

NTCP (with AES) was migrated to NTCP2 (with ChaCha20/Poly1305).
ElGamal/AES+SessionTag is being migrated to ECIES-X25519-AEAD-Ratchet.


ChaCha20/Poly1305
-----------------

For the details of ChaCha20/Poly1305 usage see [NTCP2]_ and [ECIES]_.


AES
---

AES is used for symmetric encryption, in several cases:

* For SSU transport encryption (see section "`Transports`_") after DH key exchange

* For end-to-end (destination-to-destination) encryption as a part of
  ElGamal/AES+SessionTag [ELG-AES]_

* For encryption of some netDb stores and queries sent to floodfill routers
  [NETDB-DELIVERY]_ as a part of ElGamal/AES+SessionTag [ELG-AES]_
  (destination-to-router or router-to-router).

* For encryption of periodic tunnel test messages [TUNNEL-TESTING]_ sent from
  the router to itself, through its own tunnels.

We use AES with 256 bit keys and 128 bit blocks in CBC mode.  The padding used
is specified in IETF [RFC-2313]_ (PKCS#5 1.5, section 8.1 (for block type 02)).
In this case, padding exists of pseudorandomly generated octets to match 16
byte blocks.  Specifically, see the CBC code [CryptixAESEngine]_ and the
Cryptix AES implementation [CryptixRijndael_Algorithm]_, as well as the
padding, found in the ElGamalAESEngine.getPadding function [ElGamalAESEngine]_.

.. Believe it or not, we don't do this any more. If we ever did. safeEncode() and safeDecode() are unused.

.. In all cases, we know the size of the data to be sent, and we AES encrypt the following:

.. .. raw:: html

..   % highlight lang='dataspec' %}
.. +----+----+----+----+----+----+----+----+
  |                H(data)                |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |        size       |    data ...       |
  +----+----+----+----+                   +
  |                                       |
  ~                                       ~
  |                                       |
  +                                       +
  |                                       |
  +                        +----//---+----+
  |                        |              |
  +----+----+----//---+----+              +
  |          Padding to 16 bytes          |
  +----+----+----+----+----+----+----+----+

..  H(data) :: 32-byte SHA-256 `Hash` of the data

.. . size :: 4-byte `Integer`, number of data bytes to follow

.. . data :: payload

.. . padding :: random data, to a multiple of 16 bytes
.. % endhighlight %}

.. After the data comes an application-specified number of randomly generated
 padding bytes.  This application-specified number is rounded up to a multiple
 of 16.  The entire segment (from H(data) through the end of the random bytes)
 is AES encrypted (256 bit CBC w/ PKCS#5). 

.. This code is implemented in the safeEncrypt and safeDecrypt methods of
 AESEngine but it is unused.


Obsolescence
````````````
The vulnerability of the network to an AES attack and the impact of
transitioning to a longer bit length is to be studied.  It may be quite
difficult to make any change backward-compatible.

References
``````````
* [STATUS-AES]_


.. _sig:

Signatures
==========

Numerous signature algorithms, with varying key and signature lengths,
are defined by signature types. It is relatively easy
to add more signature types.

EdDSA-SHA512-Ed25519 is the current default signature algorithm.
DSA, which was the original algorithm before we added support for signature types,
is still in use in the network.

DSA
---

Signatures are generated and verified with 1024 bit [DSA]_ (L=1024, N=160), as
implemented in [DSAEngine]_.  DSA was chosen because it is much faster for
signatures than ElGamal.

SEED
````
160 bit::

    86108236b8526e296e923a4015b4282845b572cc

Counter
```````
::

    33

DSA prime (p)
`````````````
1024 bit::

    9C05B2AA 960D9B97 B8931963 C9CC9E8C 3026E9B8 ED92FAD0
    A69CC886 D5BF8015 FCADAE31 A0AD18FA B3F01B00 A358DE23
    7655C496 4AFAA2B3 37E96AD3 16B9FB1C C564B5AE C5B69A9F
    F6C3E454 8707FEF8 503D91DD 8602E867 E6D35D22 35C1869C
    E2479C3B 9D5401DE 04E0727F B33D6511 285D4CF2 9538D9E3
    B6051F5B 22CC1C93

DSA quotient (q)
````````````````
::

    A5DFC28F EF4CA1E2 86744CD8 EED9D29D 684046B7

DSA generator (g)
`````````````````
1024 bit::

    0C1F4D27 D40093B4 29E962D7 223824E0 BBC47E7C 832A3923
    6FC683AF 84889581 075FF908 2ED32353 D4374D73 01CDA1D2
    3C431F46 98599DDA 02451824 FF369752 593647CC 3DDC197D
    E985E43D 136CDCFC 6BD5409C D2F45082 1142A5E6 F8EB1C3A
    B5D0484B 8129FCF1 7BCE4F7F 33321C3C B3DBB14A 905E7B2B
    3E93BE47 08CBCC82

The [SigningPublicKey]_ is 1024 bits.  The [SigningPrivateKey]_ is 160 bits.

Obsolescence
````````````
[NIST-800-57]_ recommends a minimum of (L=2048, N=224) for usage beyond 2010.
This may be mitigated somewhat by the "cryptoperiod", or lifespan of a given
key.

The prime number was chosen in 2003 [CHOOSING-CONSTANTS]_, and the person that
chose the number (TheCrypto) is currently no longer an I2P developer.  As such,
we do not know if the prime chosen is a 'strong prime'.  If a larger prime is
chosen for future purposes, this should be a strong prime, and we will document
the construction process.

References
``````````
* [MEETING-51]_
* [MEETING-52]_


New Signature Algorithms
========================

As of release 0.9.12, the router supports additional signature algorithms that
are more secure than 1024-bit DSA.  The first usage was for Destinations;
support for Router Identities was added in release 0.9.16.
Existing Destinations cannot be migrated from old to new signatures;
however, there is support for a single tunnel with multiple
Destinations, and this provides a way to switch to newer signature types.
Signature type is encoded in the Destination and Router
Identity, so that new signature algorithms or curves may be added at any time.

The current supported signature types are as follows:

* DSA-SHA1
* ECDSA-SHA256-P256
* ECDSA-SHA384-P384 (not widely used)
* ECDSA-SHA512-P521 (not widely used)
* EdDSA-SHA512-Ed25519 (default as of release 0.9.15)
* RedDSA-SHA512-Ed25519 (as of release 0.9.39)


Additional signature types are used at the application layer only,
primarily for signing and verifying su3 files.
These signature types are as follows:

* RSA-SHA256-2048 (not widely used)
* RSA-SHA384-3072 (not widely used)
* RSA-SHA512-4096
* EdDSA-SHA512-Ed25519ph (as of release 0.9.25; not widely used)


ECDSA
-----

ECDSA uses the standard NIST curves and standard SHA-2 hashes.

We migrated new destinations to ECDSA-SHA256-P256 in the 0.9.16 - 0.9.19
release time frame.  Usage for Router Identities is supported as of release
0.9.16 and migration of existing routers happened in 2015.

RSA
---

Standard RSA PKCS#1 v1.5 (RFC 2313) with the public exponent F4 = 65537.

RSA is now used for signing all out-of-band trusted content, including router
updates, reseeding, plugins, and news.  The signatures are embedded in the
"su3" format [UPDATES]_.  4096-bit keys are recommended and used by all known
signers.  RSA is not used, or planned for use, in any in-network Destinations
or Router Identities.

EdDSA 25519
-----------

Standard EdDSA using curve 25519 and standard 512-bit SHA-2 hashes.

Supported as of release 0.9.15.

Destinations and Router Identities were migrated in late 2015.


RedDSA 25519
------------

Standard EdDSA using curve 25519 and standard 512-bit SHA-2 hashes,
but with different private keys, and minor modifications to signing.
For encrypted leasesets.
See [EncryptedLeaseSet]__ for details.

Supported as of release 0.9.39.


Hashes
======

Hashes are used in signature algorithms and as keys in the network's DHT.

Older signature algorithms use SHA1 and SHA256.
Newer signature algorithms use SHA512.
The DHT uses SHA256.

SHA256
------

DHT hashes within I2P are standard SHA256.

Obsolescence
````````````
The vulnerability of the network to a SHA-256 attack and the impact of
transitioning to a longer hash is to be studied.  It may be quite difficult to
make any change backward-compatible.

References
``````````
* [SHA-2]_


Transports
==========

At the lowest protocol layer, point-to-point inter-router communication is
protected by the transport layer security.

NTCP2 connections use X25519 Diffie-Hellman and ChaCha20/Poly1305 authenticated encryption.

SSU and the obsolete NTCP transports use 256 byte (2048
bit) Diffie-Hellman key exchange using the same shared prime and generator as
specified above for ElGamal_, followed by symmetric AES encryption as described
above.

SSU is planned to be migrated to SSU2 (with X25519 and ChaCha20/Poly1305).

All transports provide perfect forward secrecy [PFS]_ on the transport links.


.. _tcp:

NTCP2 connections
-----------------

NTCP2 connections use X25519 Diffie-Hellman and ChaCha20/Poly1305 authenticated encryption,
and the Noise protocol framework [Noise]_.

See the NTCP2 specification [NTCP2]_ for details and references.

.. _udp:

UDP connections
---------------

SSU (the UDP transport) encrypts each packet with AES256/CBC with both an
explicit IV and MAC (HMAC-MD5-128) after agreeing upon an ephemeral session key
through a 2048 bit Diffie-Hellman exchange, station-to-station authentication
with the other router's DSA key, plus each network message has their own hash
for local integrity checking.

See the SSU specification [SSU-KEYS]_ for details.

WARNING - I2P's HMAC-MD5-128 used in SSU is apparently non-standard.
Apparently, an early version of SSU used HMAC-SHA256, and then it was switched
to MD5-128 for performance reasons, but left the 32-byte buffer size intact.
See HMACGenerator.java and the 2005-07-05 status notes [STATUS-HMAC]_ for
details.

NTCP connections
----------------

NTCP is no longer used, it was replaced by NTCP2.

NTCP connections were negotiated with a 2048 Diffie-Hellman implementation,
using the router's identity to proceed with a station to station agreement,
followed by some encrypted protocol specific fields, with all subsequent data
encrypted with AES (as above).  The primary reason to do the DH negotiation
instead of using ElGamalAES+SessionTag [ELG-AES]_ is that it provides
'(perfect) forward secrecy' [PFS]_, while ElGamalAES+SessionTag does not.

See the NTCP specification [NTCP]_ for details.


References
==========

.. [BENCHMARKS]
    {{ site_url('misc/benchmarks', True) }}

    Crypto++ benchmarks, originally at http://www.eskimo.com/~weidai/benchmarks.html (now dead),
    rescued from http://www.archive.org/, dated Apr 23, 2008.

.. [CHOOSING-CONSTANTS]
    http://article.gmane.org/gmane.comp.security.invisiblenet.iip.devel/343

.. [Common]
    {{ spec_url('common-structures') }}

.. [CryptixAESEngine]
    https://github.com/i2p/i2p.i2p/tree/master/core/java/src/net/i2p/crypto/CryptixAESEngine.java

.. [CryptixRijndael_Algorithm]
    https://github.com/i2p/i2p.i2p/tree/master/core/java/src/net/i2p/crypto/CryptixRijndael_Algorithm.java

.. [DSA]
    http://en.wikipedia.org/wiki/Digital_Signature_Algorithm

.. [DSAEngine]
    https://github.com/i2p/i2p.i2p/tree/master/core/java/src/net/i2p/crypto/DSAEngine.java

.. [ECIES]
    {{ specl_url('ecies') }}

.. [ELG-AES]
    {{ site_url('docs/how/elgamal-aes', True) }}

.. [ElGamalEngine]
    https://github.com/i2p/i2p.i2p/tree/master/core/java/src/net/i2p/crypto/ElGamalEngine.java

.. [ElGamalAESEngine]
    https://github.com/i2p/i2p.i2p/tree/master/core/java/src/net/i2p/crypto/ElGamalAESEngine.java

.. [Koshiba2004]
    Koshiba & Kurosawa. Short Exponent Diffie-Hellman Problems. PKC 2004, LNCS 2947, pp. 173-186

    Available as PDF on Archive.org: https://web.archive.org/web/\*/https://www.iacr.org/archive/pkc2004/29470171/29470171.pdf
    
    http://www.springerlink.com/content/2jry7cftp5bpdghm/

    Full text: http://books.google.com/books?id=cXyiNZ2_Pa0C&amp;lpg=PA173&amp;ots=PNIz3dWe4g&amp;pg=PA173#v=onepage&amp;q&amp;f=false

.. [EncryptedLeaseSet]
    {{ spec_url('encryptedleaseset') }}

.. [LeaseSet]
    {{ ctags_url('LeaseSet') }}

.. [MEETING-51]
    {{ get_url('meetings_show', id=51, _external=True) }}

.. [MEETING-52]
    {{ get_url('meetings_show', id=52, _external=True) }}

.. [NETDB-DELIVERY]
    {{ site_url('docs/how/network-database', True) }}#delivery

.. [NIST-800-57]
    http://csrc.nist.gov/publications/nistpubs/800-57/sp800-57-Part1-revised2_Mar08-2007.pdf

.. [NOISE]
    http://noiseprotocol.org/noise.html

.. [NTCP]
    {{ site_url('docs/transport/ntcp', True) }}

.. [NTCP2]
    {{ site_url('docs/spec/ntcp2', True) }}

.. [PFS]
    http://en.wikipedia.org/wiki/Perfect_forward_secrecy

.. [PrivateKey]
    {{ ctags_url('PrivateKey') }}

.. [RFC-2313]
    http://tools.ietf.org/html/rfc2313

.. [RFC-3526]
    http://tools.ietf.org/html/rfc3526

.. [RFC-3526-S3]
    http://tools.ietf.org/html/rfc3526#section-3

.. [SCI.CRYPT]
    https://groups.google.com/forum/#!topic/sci.crypt/GFWl76dBZnc

.. [SHA-2]
    https://en.wikipedia.org/wiki/SHA-2

.. [SigningPrivateKey]
    {{ ctags_url('SigningPrivateKey') }}

.. [SigningPublicKey]
    {{ ctags_url('SigningPublicKey') }}

.. [SSU-KEYS]
    {{ site_url('docs/transport/ssu', True) }}#keys

.. [STATUS-AES]
    Feb. 7, 2006 Status Notes

    {{ get_url('blog_post', slug='2006/02/07/status', _external=True) }}

.. [STATUS-HMAC]
    Jul. 5, 2005 Status Notes

    {{ get_url('blog_post', slug='2005/07/05/status', _external=True) }}

.. [TunnelBuild]
    {{ ctags_url('TunnelBuild') }}

.. [TUNNEL-TESTING]
    {{ site_url('docs/how/tunnel-routing', True) }}#testing

.. [UPDATES]
    {{ spec_url('updates') }}

.. [vanOorschot1996]
    van Oorschot, Weiner. On Diffie-Hellman Key Agreement with Short Exponents. EuroCrypt '96

    Available as PDF on Archive.org: https://web.archive.org/web/20180101000000\*/https://link.springer.com/content/pdf/10.1007%2F3-540-68339-9_29.pdf

    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.14.5952&rep=rep1&type=pdf
