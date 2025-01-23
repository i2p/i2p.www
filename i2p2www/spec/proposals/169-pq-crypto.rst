===================================
Post-Quantum Crypto Protocols
===================================
.. meta::
    :author: zzz
    :created: 2025-01-21
    :thread: http://zzz.i2p/topics/3294
    :lastupdated: 2025-01-23
    :status: Open
    :target: 0.9.80

.. contents::






Overview
========

While research and competition for suitable post-quantum (PQ)
cryptography has been proceeding for a decade, the choices
have not become clear until recently.

We started looking at the implications of PQ crypto
in 2022 [FORUM]_.

SSL added hybrid encryption support in the last two years and it now
is used for a significant portion of encrypted traffic on the internet [CLOUDFLARE]_.

NIST recently finalized and published the recommended algorithms
for post-quantum cryptography [NIST-PQ]_.

Both [CLOUDFLARE]_ and [NIST-PQ]_ recommend that migration start immediately.
See also the 2022 NSA PQ FAQ [NSA-PQ]_.
I2P should be a leader in security and cryptography.
Now is the time to implement the recommended algorithms.
Using our flexible crypto type and signature type system,
we will add types for hybrid crypto, and for PQ and hybrid signatures.


Goals
=====

- Select PQ-resistant algorithms
- Add PQ-only and hybrid algorithms to I2P protocols where appropriate
- Select best variants after implementation, testing, analysis, and research
- Add support incrementally and with backward compatibility


Non-Goals
=========

TBD



Design
======

We will support the NIST FIPS 203 and 204 standards [FIPS203]_ [FIPS204]_
which are based on, but NOT compatible with,
CRYSTALS-Kyber and CRYSTALS-Dilithium (versions 3.1, 3, and older).



Key Exchange
-------------

We will support key exchange in the following protocols:

=======  ==========  ==============  ===============
Proto    Noise Type  Support PQ?     Support Hybrid?
=======  ==========  ==============  ===============
NTCP2       XK       no              yes
SSU2        XK       no              yes
Ratchet     IK       no              yes
TBM          N       no              no
NetDB        N       no              no
=======  ==========  ==============  ===============

PQ KEM provides ephemeral keys only, and does not directly support
static-key handshakes such as Noise XK and IK.
While there is some recent research [PQ-WIREGUARD]_ on adapting Wireguard (IK)
for pure PQ crypto, there are several open questions, and
this approach is unproven.

Noise N does not use a two-way key exchange and so it is not suitable
for hybrid encryption.

So we will support hybrid encryption only, for NTCP2, SSU2, and Ratchet.
We will define the three ML-KEM variants as in [FIPS203]_,
for 3 new encryption types total.
Hybrid types will only be defined in combination with X25519.

The new encryption types are:

================
  Type          
================
MLKEM512_X25519 
MLKEM768_X25519 
MLKEM1024_X25519
================

Overhead will be substantial. Typical message 1 and 2 sizes (for XK and IK)
are currently around 100 bytes (before any additional payload).
This will increase by 8x to 15x depending on algorithm.


Signatures
-----------

We will support PQ and hybrid signatures in the following structures:

==========================  ==============  ===============
Type                        Support PQ?     Support Hybrid?
==========================  ==============  ===============
RouterInfo                  yes             yes
LeaseSet                    yes             yes
Streaming SYN/SYNACK/Close  yes             yes
Repliable Datagrams         yes             yes
I2CP create session msg     yes             yes
SU3 files                   yes             yes
X.509 certificates          yes             yes
Java keystores              yes             yes
==========================  ==============  ===============


So we will support both PQ-only and hybrid signatures.
We will define the three ML-DSA variants as in [FIPS204]_,
for 6 new signature types total.
Hybrid types will only be defined in combination with Ed25519.
We will use the standard ML-DSA, NOT the pre-hash variants (HashML-DSA).

The new signature types are:

============================
        Type                
============================
MLDSA44_EdDSA_SHA512_Ed25519
MLDSA65_EdDSA_SHA512_Ed25519
MLDSA87_EdDSA_SHA512_Ed25519
MLDSA44                     
MLDSA65                     
MLDSA87                     
============================

X.509 certificates and other DER encodings will use the
composite structures and OIDs defined in [COMPOSITE-SIGS]_.

Overhead will be substantial. Typical Ed25519 destination and router identity
sizes are 391 bytes.
These will increase by 3.5x to 6.8x depending on algorithm.
Ed25519 signatures are 64 bytes.
These will increase by 38x to 76x depending on algorithm.
Typical signed RouterInfo, LeaseSet, repliable datagrams, and signed streaming messages are about 1KB.
These will increase by 3x to 8x depending on algorithm.

As the new destination and router identity types will not contain padding,
they will not be compressible. Sizes of destinations and router identities
that are gzipped in-transit will increase by 12x - 38x depending on algorithm.

TODO: Add RSA4096 hybrid types for su3?


New Crypto Required
-------------------

- ML-KEM (formerly CRYSTALS-Kyber) [FIPS203]_
- ML-DSA (formerly CRYSTALS-Dilithium) [FIPS204]_
- SHA3-128 (formerly Keccak-256) [FIPS202]_ Used only for SHAKE128
- SHA3-256 (formerly Keccak-512) [FIPS202]_
- SHAKE128 and SHAKE256 (XOF extensions to SHA3-128 and SHA3-256) [FIPS202]_

Test vectors for SHA3-256, SHAKE128, and SHAKE256 are at [NIST-VECTORS]_.



Alternatives
-------------

We will not support [FIPS205]_ (Sphincs+), it is much much slower and bigger than ML-DSA.
We will not support the upcoming FIPS206 (Falcon), it is not yet standardized.



Specification
=============

Common Structures
-----------------

PublicKey
````````````````

================    ================= ======  =====
  Type              Public Key Length Since   Usage
================    ================= ======  =====
MLKEM512_X25519               32      0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM768_X25519               32      0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM1024_X25519              32      0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM512                     800      0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM768                    1184      0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM1024                   1568      0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
NULL                           0      0.9.xx  See proposal 169, for destinations with PQ sig types only, not for RIs or Leasesets
================    ================= ======  =====

Hybrid public keys are the X25519 key.
KEM public keys are the ephemeral PQ key sent from Alice to Bob.


PrivateKey
````````````````

================    ================== ======  =====
  Type              Private Key Length Since   Usage
================    ================== ======  =====
MLKEM512_X25519               32       0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM768_X25519               32       0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM1024_X25519              32       0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM512                    1632       0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM768                    2400       0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM1024                   3168       0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
NULL                           0       0.9.xx  See proposal 169, for destinations with PQ sig types only, not for RIs or Leasesets
================    ================== ======  =====

Hybrid private keys are the X25519 key followed by the PQ key.
KEM private keys are the ciphertext sent from Bob to Alice.




SigningPublicKey
````````````````


============================   ==============  ======  =====
         Type                  Length (bytes)  Since   Usage
============================   ==============  ======  =====
MLDSA44_EdDSA_SHA512_Ed25519         1344      0.9.xx  See proposal 169
MLDSA65_EdDSA_SHA512_Ed25519         1984      0.9.xx  See proposal 169
MLDSA87_EdDSA_SHA512_Ed25519         2616      0.9.xx  See proposal 169
MLDSA44                              1312      0.9.xx  See proposal 169
MLDSA65                              1952      0.9.xx  See proposal 169
MLDSA87                              2592      0.9.xx  See proposal 169
============================   ==============  ======  =====

Hybrid signing public keys are the Ed25519 key followed by the PQ key.


SigningPrivateKey
`````````````````

============================   ==============  ======  =====
         Type                  Length (bytes)  Since   Usage
============================   ==============  ======  =====
MLDSA44_EdDSA_SHA512_Ed25519         2592      0.9.xx  See proposal 169
MLDSA65_EdDSA_SHA512_Ed25519         4064      0.9.xx  See proposal 169
MLDSA87_EdDSA_SHA512_Ed25519         4928      0.9.xx  See proposal 169
MLDSA44                              2560      0.9.xx  See proposal 169
MLDSA65                              4032      0.9.xx  See proposal 169
MLDSA87                              4896      0.9.xx  See proposal 169
============================   ==============  ======  =====

Hybrid signing private keys are the Ed25519 key followed by the PQ key.


Signature
``````````
============================   ==============  ======  =====
         Type                  Length (bytes)  Since   Usage
============================   ==============  ======  =====
MLDSA44_EdDSA_SHA512_Ed25519         2484      0.9.xx  See proposal 169
MLDSA65_EdDSA_SHA512_Ed25519         4096      0.9.xx  See proposal 169
MLDSA87_EdDSA_SHA512_Ed25519         4960      0.9.xx  See proposal 169
MLDSA44                              2420      0.9.xx  See proposal 169
MLDSA65                              4032      0.9.xx  See proposal 169
MLDSA87                              4896      0.9.xx  See proposal 169
============================   ==============  ======  =====

Hybrid signatures are the Ed25519 signature followed by the PQ signature.
Hybrid signatures are verified by verifying both signatures, and failing
if either one fails.



Key Certificates
````````````````

The defined Signing Public Key types are:

============================  ===========  =======================  ======  =====
        Type                  Type Code    Total Public Key Length  Since   Usage
============================  ===========  =======================  ======  =====
MLDSA44_EdDSA_SHA512_Ed25519      12                 1344           0.9.xx  See proposal 169
MLDSA65_EdDSA_SHA512_Ed25519      13                 1984           0.9.xx  See proposal 169
MLDSA87_EdDSA_SHA512_Ed25519      14                 2616           0.9.xx  See proposal 169
MLDSA44                           15                 1312           0.9.xx  See proposal 169
MLDSA65                           16                 1952           0.9.xx  See proposal 169
MLDSA87                           17                 2592           0.9.xx  See proposal 169
============================  ===========  =======================  ======  =====



The defined Crypto Public Key types are:

================    ===========  ======================= ======  =====
  Type              Type Code    Total Public Key Length Since   Usage
================    ===========  ======================= ======  =====
MLKEM512_X25519          5                 32            0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM768_X25519          6                 32            0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM1024_X25519         7                 32            0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
NULL                   255                  0            0.9.xx  See proposal 169, for destinations with PQ sig types only, not for RIs or Leasesets
================    ===========  ======================= ======  =====


Hybrid key types are NEVER included in key certificates; only in leasesets.

The NULL key type is ONLY for destinations or router identities with Hybrid or PQ signature types.
Never in leasesets.
This is used to indicate to KeysAndCert parsers that there is no crypto key, and the
entire 384-byte main section is for the signing key.


Destination sizes
``````````````````

Here are lengths for the new Destination types.
Enc type for all is NULL (255).
The entire 384-byte section is used for the first part of the signing public key.
No padding.
Total length is 7 + total key length.
Key certificate length is 4 + excess key length.

Example 1319-byte destination byte stream for MLDSA44:

skey[0:383] 5 (932 >> 8) (932 & 0xff) 00 12 00 255 skey[384:1311]



============================  ===========  =======================  ======  ======  =====
        Type                  Type Code    Total Public Key Length  Main    Excess  Total Dest Length
============================  ===========  =======================  ======  ======  =====
MLDSA44_EdDSA_SHA512_Ed25519      12                 1344           384      960    1351
MLDSA65_EdDSA_SHA512_Ed25519      13                 1984           384     1600    1991
MLDSA87_EdDSA_SHA512_Ed25519      14                 2616           384     2648    2623
MLDSA44                           15                 1312           384      928    1319
MLDSA65                           16                 1952           384     1568    1959
MLDSA87                           17                 2592           384     2208    2599
============================  ===========  =======================  ======  ======  =====



RouterIdent sizes
``````````````````

Here are lengths for the new Destination types.
Enc type for all is X25519 (4).
The entire 352-byte section after the X28819 public key is used for the first part of the signing public key.
No padding.
Total length is 39 + total key length.
Key certificate length is 4 + excess key length.

Example 1351-byte router identity byte stream for MLDSA44:

enckey[0:31] skey[0:351] 5 (960 >> 8) (960 & 0xff) 00 12 00 4 skey[352:1311]



============================  ===========  =======================  ======  ======  =====
        Type                  Type Code    Total Public Key Length  Main    Excess  Total RouterIdent Length
============================  ===========  =======================  ======  ======  =====
MLDSA44_EdDSA_SHA512_Ed25519      12                 1344           352      992    1383
MLDSA65_EdDSA_SHA512_Ed25519      13                 1984           352     1632    2023
MLDSA87_EdDSA_SHA512_Ed25519      14                 2616           352     2660    2655
MLDSA44                           15                 1312           352      960    1351
MLDSA65                           16                 1952           352     1600    1991
MLDSA87                           17                 2592           352     2240    2631
============================  ===========  =======================  ======  ======  =====



Handshake Patterns
------------------

Handshakes use [Noise]_ handshake patterns.

The following letter mapping is used:

- e = one-time ephemeral key
- s = static key
- p = message payload
- e1 = one-time ephemeral PQ key, sent from Alice to Bob
- ekem1 = the KEM ciphertext, sent from Bob to Alice

The following modifications to XK and IK for hybrid forward secrecy (hfs) are:

.. raw:: html

  {% highlight lang='dataspec' %}

XK:                       XKhfs:
  <- s                      <- s
  ...                       ...
  -> e, es, p               -> e, es, e1, p
  <- e, ee, p               <- e, ee, ekem1, p
  -> s, se                  -> s, se
  <- p                      <- p
  p ->                      p ->

  e1 is encrypted together with the message 1 payload p
  ekem1 is encrypted together with the message 2 payload p


  IK:                       IKhfs:
  <- s                      <- s
  ...                       ...
  -> e, es, s, ss, p       -> e, es, e1, s, ss, p
  <- tag, e, ee, se, p     <- tag, e, ee, ekem1, se, p
  <- p                     <- p
  p ->                     p ->

  e1 is encrypted together with the message 1 alice static key s
  ekem1 is encrypted with the message 2 ee DH result state FIXME

{% endhighlight %}




Noise Handshake KDF
---------------------

The KEM 32-byte shared secret is combined or mixHash()ed or HKDF()ed into the
final Noise shared secret, before split(), for a final 32-byte shared secret.
Not concatenated with the DH shared secret for a 64-byte final shared secret,
which is what TLS does [TLS-HYBRID]_.


Ratchet
---------

Noise identifiers:

- "Noise_IKhfselg2_25519+MLKEM512_ChaChaPoly_SHA256"
- "Noise_IKhfselg2_25519+MLKEM768_ChaChaPoly_SHA256"
- "Noise_IKhfselg2_25519+MLKEM1024_ChaChaPoly_SHA256"



1b) New session format (with binding)
`````````````````````````````````````

Changes: Current ratchet contained only the static key in the first ChaCha section.
With ML-KEM, the first ChaCha section will also contain the encrypted PQ public key.


Encrypted format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   New Session Ephemeral Public Key    |
  +             32 bytes                  +
  |     Encoded with Elligator2           |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +       ML-KEM key and Static Key       +
  |       ChaCha20 encrypted data         |
  +      (see table below for length)     +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +    (MAC) for Static Key Section       +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +            Payload Section            +
  |       ChaCha20 encrypted data         |
  ~                                       ~
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +         (MAC) for Payload Section     +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+


{% endhighlight %}

Decrypted format:

.. raw:: html

  {% highlight lang='dataspec' %}
Payload Part 1:


  +----+----+----+----+----+----+----+----+
  |                                       |
  +       ML-KEM key                      +
  |                                       |
  +      (see table below for length)     +
  |                                       |
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +       X25519 Static Key               +
  |                                       |
  +      (32 bytes)                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+

  Payload Part 2:

  +----+----+----+----+----+----+----+----+
  |                                       |
  +            Payload Section            +
  |                                       |
  ~                                       ~
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+

{% endhighlight %}

Sizes:

================    =========  =====  =========  =============  =============  ==========  =======
  Type              Type Code  X len  Msg 1 len  Msg 1 Enc len  Msg 1 Dec len  PQ key len  pl len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     96+pl        64+pl             pl           --       pl
MLKEM512_X25519          5       32    896+pl       864+pl         800+pl          800       pl
MLKEM768_X25519          6       32   1280+pl      1344+pl        1184+pl         1184       pl
MLKEM1024_X25519         7       32   1664+pl      1632+pl        1568+pl         1568       pl
================    =========  =====  =========  =============  =============  ==========  =======


1g) New Session Reply format
````````````````````````````

Changes: Current ratchet has an empty payload for the first ChaCha section.
With ML-KEM, the first ChaCha section will contain the encrypted PQ ciphertext.


Encrypted format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |       Session Tag   8 bytes           |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +        Ephemeral Public Key           +
  |                                       |
  +            32 bytes                   +
  |     Encoded with Elligator2           |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   ChaCha20 encrypted PQ ciphertext    |
  +      (see table below for length)     +
  ~                                       ~
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +  (MAC) for Key Section                +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +            Payload Section            +
  |       ChaCha20 encrypted data         |
  ~                                       ~
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +         (MAC) for Payload Section     +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+


{% endhighlight %}

Decrypted format:

.. raw:: html

  {% highlight lang='dataspec' %}
Payload Part 1:


  +----+----+----+----+----+----+----+----+
  |                                       |
  +       ML-KEM ciphertext               +
  |                                       |
  +      (see table below for length)     +
  |                                       |
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  Payload Part 2:

  +----+----+----+----+----+----+----+----+
  |                                       |
  +            Payload Section            +
  |                                       |
  ~                                       ~
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+

{% endhighlight %}

Sizes:

================    =========  =====  =========  =============  =============  ==========  =======
  Type              Type Code  Y len  Msg 2 len  Msg 2 Enc len  Msg 2 Dec len  PQ CT len   opt len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     72+pl        32+pl             pl           --       pl
MLKEM512_X25519          5       32    872+pl       832+pl         800+pl          800       pl
MLKEM768_X25519          6       32   1256+pl      1216+pl        1184+pl         1184       pl
MLKEM1024_X25519         7       32   1664+pl      1600+pl        1568+pl         1568       pl
================    =========  =====  =========  =============  =============  ==========  =======


KDF for Payload Section Encrypted Contents
``````````````````````````````````````````


.. raw:: html

  {% highlight lang='text' %}
// split()
  keydata = HKDF(chainKey, ZEROLEN, "", 64)

  TODO

  k_ab = keydata[0:31]
  k_ba = keydata[32:63]

  rest unchanged
{% endhighlight %}




NTCP2
------

Noise identifiers:

- "Noise_XKhfsaesobfse+hs2+hs3_25519+MLKEM512_ChaChaPoly_SHA256"
- "Noise_XKhfsaesobfse+hs2+hs3_25519+MLKEM768_ChaChaPoly_SHA256"
- "Noise_XKhfsaesobfse+hs2+hs3_25519+MLKEM1024_ChaChaPoly_SHA256"


1) SessionRequest
``````````````````

Changes: Current NTCP2 contains only the options in the ChaCha section.
With ML-KEM, the ChaCha section will also contain the encrypted PQ public key.


Raw contents:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +        obfuscated with RH_B           +
  |       AES-CBC-256 encrypted X         |
  +             (32 bytes)                +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   ChaChaPoly frame                    |
  +      (see table below for length)     +
  |   k defined in KDF for message 1      |
  +   n = 0                               +
  |   see KDF for associated data         |
  +----+----+----+----+----+----+----+----+
  |     unencrypted authenticated         |
  ~         padding (optional)            ~
  |     length defined in options block   |
  +----+----+----+----+----+----+----+----+

  Same as before except ChaChaPoly frame is bigger


{% endhighlight %}

Unencrypted data (Poly1305 authentication tag not shown):

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |                   X                   |
  +              (32 bytes)               +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |           ML-KEM Public Key           |
  +      (see table below for length)     +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |               options                 |
  +              (16 bytes)               +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |     unencrypted authenticated         |
  +         padding (optional)            +
  |     length defined in options block   |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+



{% endhighlight %}

Sizes:

================    =========  =====  =========  =============  =============  ==========  =======
  Type              Type Code  X len  Msg 1 len  Msg 1 Enc len  Msg 1 Dec len  PQ key len  opt len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     64+pad       32              16           --         16
MLKEM512_X25519          5       32    864+pad      832             816          800         16
MLKEM768_X25519          6       32   1248+pad     1216            1200         1184         16
MLKEM1024_X25519         7       32   1632+pad     1600            1584         1568         16
================    =========  =====  =========  =============  =============  ==========  =======


2) SessionCreated
``````````````````

Changes: Current NTCP2 contains only the options in the ChaCha section.
With ML-KEM, the ChaCha section will also contain the encrypted PQ public key.


Raw contents:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +        obfuscated with RH_B           +
  |       AES-CBC-256 encrypted Y         |
  +              (32 bytes)               +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |   ChaChaPoly frame                    |
  +   Encrypted and authenticated data    +
  -      (see table below for length)     -
  +   k defined in KDF for message 2      +
  |   n = 0; see KDF for associated data  |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |     unencrypted authenticated         |
  +         padding (optional)            +
  |     length defined in options block   |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  Same as before except ChaChaPoly frame is bigger

{% endhighlight %}

Unencrypted data (Poly1305 auth tag not shown):

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |                  Y                    |
  +              (32 bytes)               +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |           ML-KEM Ciphertext           |
  +      (see table below for length)     +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |               options                 |
  +              (16 bytes)               +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |     unencrypted authenticated         |
  +         padding (optional)            +
  |     length defined in options block   |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+

{% endhighlight %}

Sizes:

================    =========  =====  =========  =============  =============  ==========  =======
  Type              Type Code  Y len  Msg 2 len  Msg 2 Enc len  Msg 2 Dec len  PQ CT len   opt len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     64+pad       32              16           --         16
MLKEM512_X25519          5       32    832+pad      800             784          768         16
MLKEM768_X25519          6       32   1120+pad     1088            1104         1088         16
MLKEM1024_X25519         7       32   1600+pad     1568            1584         1568         16
================    =========  =====  =========  =============  =============  ==========  =======



3) SessionConfirmed
```````````````````

Unchanged


Key Derivation Function (KDF) (for data phase)
``````````````````````````````````````````````

The data phase uses a zero-length associated data input.


The KDF generates two cipher keys k_ab and k_ba from the chaining key ck,
using HMAC-SHA256(key, data) as defined in [RFC-2104]_.
This is the Split() function, exactly as defined in the Noise spec.

.. raw:: html

  {% highlight lang='text' %}

ck = from handshake phase

  // k_ab, k_ba = HKDF(ck, zerolen)
  // ask_master = HKDF(ck, zerolen, info="ask")

  // zerolen is a zero-length byte array
  temp_key = HMAC-SHA256(ck, zerolen)

  TODO


  remainder unchanged

{% endhighlight %}




SSU2
----

Noise identifiers:

- "Noise_XKhfschaobfse+hs1+hs2+hs3_25519+MLKEM512_ChaChaPoly_SHA256"
- "Noise_XKhfschaobfse+hs1+hs2+hs3_25519+MLKEM768_ChaChaPoly_SHA256"
- "Noise_XKhfschaobfse+hs1+hs2+hs3_25519+MLKEM1024_ChaChaPoly_SHA256"

Long Header
`````````````
The long header is 32 bytes. It is used before a session is created, for Token Request, SessionRequest, SessionCreated, and Retry.
It is also used for out-of-session Peer Test and Hole Punch messages.

Before header encryption:

.. raw:: html

  {% highlight lang='dataspec' %}

+----+----+----+----+----+----+----+----+
  |      Destination Connection ID        |
  +----+----+----+----+----+----+----+----+
  |   Packet Number   |type| ver| id |flag|
  +----+----+----+----+----+----+----+----+
  |        Source Connection ID           |
  +----+----+----+----+----+----+----+----+
  |                 Token                 |
  +----+----+----+----+----+----+----+----+

  Destination Connection ID :: 8 bytes, unsigned big endian integer

  Packet Number :: 4 bytes, unsigned big endian integer

  type :: The message type = 0, 1, 7, 9, 10, or 11

  ver :: The protocol version, equal to 2

  id :: 1 byte, the network ID (currently 2, except for test networks)

  flag :: 1 byte, unused, set to 0 for future compatibility

  Source Connection ID :: 8 bytes, unsigned big endian integer

  Token :: 8 bytes, unsigned big endian integer

{% endhighlight %}


SessionRequest (Type 0)
```````````````````````

Changes: Current SSU2 contains only the block data in the ChaCha section.
With ML-KEM, the ChaCha section will also contain the encrypted PQ public key.


Raw contents:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |  Long Header bytes 0-15, ChaCha20     |
  +  encrypted with Bob intro key         +
  |    See Header Encryption KDF          |
  +----+----+----+----+----+----+----+----+
  |  Long Header bytes 16-31, ChaCha20    |
  +  encrypted with Bob intro key n=0     +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +       X, ChaCha20 encrypted           +
  |       with Bob intro key n=0          |
  +              (32 bytes)               +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   ChaCha20 encrypted data             |
  +          (length varies)              +
  |  k defined in KDF for Session Request |
  +  n = 0                                +
  |  see KDF for associated data          |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +        Poly1305 MAC (16 bytes)        +
  |                                       |
  +----+----+----+----+----+----+----+----+


{% endhighlight %}

Unencrypted data (Poly1305 authentication tag not shown):

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |      Destination Connection ID        |
  +----+----+----+----+----+----+----+----+
  |   Packet Number   |type| ver| id |flag|
  +----+----+----+----+----+----+----+----+
  |        Source Connection ID           |
  +----+----+----+----+----+----+----+----+
  |                 Token                 |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |                   X                   |
  +              (32 bytes)               +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |           ML-KEM Public Key           |
  +      (see table below for length)     +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |     Noise payload (block data)        |
  +          (length varies)              +
  |     see below for allowed blocks      |
  +----+----+----+----+----+----+----+----+


{% endhighlight %}

Sizes, not including IP overhead:

================    =========  =====  =========  =============  =============  ==========  =======
  Type              Type Code  X len  Msg 1 len  Msg 1 Enc len  Msg 1 Dec len  PQ key len  pl len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     80+pl        16+pl             pl         --         pl
MLKEM512_X25519          5       32    880+pl       816+pl         800+pl        800         pl
MLKEM768_X25519          6       32   1264+pl      1200+pl        1184+pl       1184         pl
MLKEM1024_X25519         7      n/a   too big
================    =========  =====  =========  =============  =============  ==========  =======

Minimum MTU for MLKEM768_X25519:
About 1300 for IPv4 and 1320 for IPv6.



SessionCreated (Type 1)
````````````````````````
Changes: Current SSU2 contains only the block data in the ChaCha section.
With ML-KEM, the ChaCha section will also contain the encrypted PQ public key.


Raw contents:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |  Long Header bytes 0-15, ChaCha20     |
  +  encrypted with Bob intro key and     +
  | derived key, see Header Encryption KDF|
  +----+----+----+----+----+----+----+----+
  |  Long Header bytes 16-31, ChaCha20    |
  +  encrypted with derived key n=0       +
  |  See Header Encryption KDF            |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +       Y, ChaCha20 encrypted           +
  |       with derived key n=0            |
  +              (32 bytes)               +
  |       See Header Encryption KDF       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |   ChaCha20 data                       |
  +   Encrypted and authenticated data    +
  |  length varies                        |
  +  k defined in KDF for Session Created +
  |  n = 0; see KDF for associated data   |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +        Poly1305 MAC (16 bytes)        +
  |                                       |
  +----+----+----+----+----+----+----+----+


{% endhighlight %}

Unencrypted data (Poly1305 auth tag not shown):

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |      Destination Connection ID        |
  +----+----+----+----+----+----+----+----+
  |   Packet Number   |type| ver| id |flag|
  +----+----+----+----+----+----+----+----+
  |        Source Connection ID           |
  +----+----+----+----+----+----+----+----+
  |                 Token                 |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |                  Y                    |
  +              (32 bytes)               +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |           ML-KEM Ciphertext           |
  +      (see table below for length)     +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |     Noise payload (block data)        |
  +          (length varies)              +
  |      see below for allowed blocks     |
  +----+----+----+----+----+----+----+----+

{% endhighlight %}

Sizes, not including IP overhead:

================    =========  =====  =========  =============  =============  ==========  =======
  Type              Type Code  Y len  Msg 2 len  Msg 2 Enc len  Msg 2 Dec len  PQ CT len   pl len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     80+pl        16+pl             pl         --         pl
MLKEM512_X25519          5       32    880+pl       816+pl         800+pl        800         pl
MLKEM768_X25519          6       32   1264+pl      1200+pl        1184+pl       1184         pl
MLKEM1024_X25519         7      n/a   too big
================    =========  =====  =========  =============  =============  ==========  =======

Minimum MTU for MLKEM768_X25519:
About 1300 for IPv4 and 1320 for IPv6.


SessionConfirmed (Type 2)
`````````````````````````
unchanged



KDF for data phase
```````````````````

The data phase uses the header for associated data.

The KDF generates two cipher keys k_ab and k_ba from the chaining key ck,
using HMAC-SHA256(key, data) as defined in [RFC-2104]_.
This is the split() function, exactly as defined in the Noise spec.

.. raw:: html

  {% highlight lang='text' %}
// split()
  // chainKey = from handshake phase
  keydata = HKDF(chainKey, ZEROLEN, "", 64)

  TODO


  k_ab = keydata[0:31]
  k_ba = keydata[32:63]

  Remainder unchanged


{% endhighlight %}



Issues
``````

For messages 1 and 2, MLKEM768 would increase packet sizes beyond the 1280 minimum MTU.
Probably would just not support it for that connection if the MTU was too low.

For messages 1 and 2, MLKEM1024 would increase packet sizes beyond 1500 maximum MTU.
This would require fragmenting messages 1 and 2, and it would be a big complication.
Probably won't do it.

Other Specs
-----------

The new maximum Destination size will be 2599 (3468 in base 64).

Update other documents that give guidance on Destination sizes, including:

- SAMv3
- Bittorrent
- Developer guidelines
- Naming / addressbook / jump servers
- Other docs


Overhead Analysis
=================

Key Exchange
-------------

Size increase (bytes):

================    ==============  =============
  Type              Pubkey (Msg 1)  Cipertext (Msg 2)
================    ==============  =============
MLKEM512_X25519       +800               +768
MLKEM768_X25519      +1184              +1088
MLKEM1024_X25519     +1568              +1568
================    ==============  =============

Speed:

================    ==============
  Type              Relative speed
================    ==============
X25519 DH/keygen    baseline
MLKEM512            2.25x faster
MLKEM768            1.5x faster
MLKEM1024           1x (same)
XK                  4x DH (keygen + 3 DH)
MLKEM512_X25519     4x DH + 2x PQ (keygen + enc/dec) = 4.9x DH = 22% slower
MLKEM768_X25519     4x DH + 2x PQ (keygen + enc/dec) = 5.3x DH = 32% slower
MLKEM1024_X25519    4x DH + 2x PQ (keygen + enc/dec) = 6x DH = 50% slower
================    ==============

Speeds as reported by [CLOUDFLARE]_.


Signatures
-----------

Size:

Typical key, sig, RIdent, Dest sizes or size increases (Ed25519 included for reference)
assuming X25519 encryption type for RIs.
Added size for a Router Info, LeaseSet, repliable datagrams, and each of the two streaming (SYN and SYN ACK) packets listed.
Current Destinations and Leasesets contain repeated padding and are compressible in-transit.
New types do not contain padding and will not be compressible,
resulting in a much higher size increase in-transit.
See design section above.


============================  =======  ====  =======  ======  ======  ========  =====
        Type                  Pubkey   Sig   Key+Sig  RIdent  Dest    RInfo     LS/Streaming/Datagram (each msg)
============================  =======  ====  =======  ======  ======  ========  =====
EdDSA_SHA512_Ed25519              32     64     96      391     391   baseline  baseline
MLDSA44_EdDSA_SHA512_Ed25519    1344   2484   3828     1383    1351   +3412     +3380
MLDSA65_EdDSA_SHA512_Ed25519    1984   4096   5357     2023    1991   +5668     +5632
MLDSA87_EdDSA_SHA512_Ed25519    2616   4960   7315     2655    2673   +7160     +7128
MLDSA44                         1312   2420   3732     1351    1319   +3316     +3284
MLDSA65                         1952   4032   5261     1991    1959   +5668     +5636
MLDSA87                         2592   4896   7219     2631    2599   +7072     +7040
============================  =======  ====  =======  ======  ======  ========  =====

Speed:

====================  ===================  ======
  Type                Relative speed sign  verify
====================  ===================  ======
EdDSA_SHA512_Ed25519        baseline       baseline
MLDSA44                     5x slower      2x faster
MLDSA65                       ???          ???
MLDSA87                       ???          ???
====================  ===================  ======


Speeds as reported by [CLOUDFLARE]_.





Security Analysis
=================

Handshakes
----------
Probably need to prefer MLKEM768; MLKEM512 is not secure enough.




Signatures
----------
MLDSA44 hybrid is preferable to MLDSA65 PQ-only.
The keys and sig sizes for MLDSA65 and MLDSA87 are probably too big for us, at least at first.



Type Preferences
=================

While we will define and implement 3 crypto and 6 signature types, we
plan to measure performance during development, and further analyze
the effects of increased structure sizes. We will also continue
to research and monitor developments in other projects and protocols.

After a year or more of development we will attempt to settle on
a preferred type or default for each use case.
Selection will require making tradeoffs of bandwidth, CPU, and estimated security level.
All types may not be suitable or allowed for all use cases.


Preliminary preferences are as follows, subject to change:

Encryption: MLKEM768_X25519

Signatures: MLDSA44_EdDSA_SHA512_Ed25519

Preliminary restrictions are as follows, subject to change:

Encryption: MLKEM1024_X25519 not allowed for SSU2

Signatures: MLDSA87 and hybrid variant probably too large;
MLDSA65 and hybrid variant may be too large



Implementation Notes
=====================

Reliability
-----------

Size increase will result in much more tunnel fragmentation
for NetDB stores, streaming handshakes, and other messages.
Check for performance and reliability changes.


Structure Sizes
---------------

Find and check any code that limits the byte size of router infos and leasesets.


NetDB
-----

Review and possibly reduce maximum LS/RI stored in RAM or on disk,
to limit storage increase.
Increase minimum bandwidth requirements for floodfills?


Ratchet
--------
Auto-classify/detect on same tunnels?
If not, destinations would be hybrid-only, no support for regular ratchet.

TODO


NTCP2
-----
Need different transport address/port,
would be hard to run both on the same port, we have no header or flags
for message 1, it is fixed size (before padding).
So probably a protocol name such as "PQTCP".

TODO


SSU2
-----
MAY Need different transport address/port,
but hopefully not, we have a header with flags for message 1.
Maybe just v=2,3 in the address would be sufficient.
But we need identifiers for all 3 new flavors: 3a, 3b, 3c?

Check and verify that SSU2 can handle the RI fragmented across
multiple packets (6-8?)

TODO




Compatibility
===============

TODO


Priorities and Rollout
======================

The most valuable data are the end-to-end traffic, encrypted with ratchet.
As an external observer between tunnel hops, that's encrypted twice more, with tunnel encryption and transport encryption.
As an external observer between OBEP and IBGW, it's encrypted only once more, with transport encryption.
As a OBEP or IBGW participant, ratchet is the only encryption.

The most worrisome PQ threat model right now is storing traffic today, for decryption many many years from now.
A hybrid approach would protect that.

The PQ threat model of breaking the authentication keys in some reasonable period of time
(say a few months) and then impersonating the authentication or decrypting in almost-real-time,
is much farther off? And that's when we'd want to migrate to PQC static keys.

So, the earliest PQ threat model is OBEP/IBGW storing traffic for later decryption.
We should implement hybrid ratchet first.

Ratchet is the highest priority.
Transports are next.
Signatures are the lowest priority.


======================   ====
Milestone                Target
======================   ====
Ratchet beta             Late 2025
Select best enc type     Early 2026
NTCP2 beta               Early 2026
SSU2 beta                Mid 2026
Ratchet production       Mid 2026
Ratchet default          Late 2026
Signature beta           Late 2026
NTCP2 production         Late 2026
SSU2 production          Early 2027
Select best sig type     Early 2027
NTCP2 default            Early 2027
SSU2 default             Mid 2027
Signature production     Mid 2027
======================   ====



Migration
=========

If we can't support both old and new ratchet protocols on the same tunnels,
migration will be much more difficult.

TODO




Issues
=========

TODO




References
==========


.. [CLOUDFLARE]
   https://blog.cloudflare.com/pq-2024/

.. [COMPOSITE-SIGS]
   https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/

.. [FORUM]
   http://zzz.i2p/topics/3294

.. [FIPS202]
   https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf

.. [FIPS203]
   https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf

.. [FIPS204]
   https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf

.. [FIPS205]
   https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf

.. [NIST-PQ]
   https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards

.. [NIST-VECTORS]
   https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines/example-values

.. [Noise]
   https://noiseprotocol.org/noise.html

.. [Noise-Hybrid]
   https://github.com/noiseprotocol/noise_hfs_spec/blob/master/output/noise_hfs.pdf

.. [NSA-PQ]
   https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSI_CNSA_2.0_FAQ\_.PDF

.. [PQ-WIREGUARD]
   https://eprint.iacr.org/2020/379.pdf

.. [RFC-2104]
    https://tools.ietf.org/html/rfc2104

.. [TLS-HYBRID]
   https://www.ietf.org/archive/id/draft-tls-westerbaan-xyber768d00-03.html
