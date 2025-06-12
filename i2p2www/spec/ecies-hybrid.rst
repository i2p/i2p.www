===================================
PQ Hybrid ECIES-X25519-AEAD-Ratchet
===================================
.. meta::
    :category: Protocols
    :lastupdated: 2025-06
    :accuratefor: 0.9.67

.. contents::


Note
====

Implementation, testing, and rollout in progress in the various
router implementations. Check the documentation of those implementations for status.


Overview
========

This is the PQ Hybrid variant of the ECIES-X25519-AEAD-Ratchet protocol [ECIES]_.
It is the first phase of the overall PQ proposal [Prop169]_
to be approved. See that proposal for overall goals, threat models,
analysis, alternatives, and additional information.

This specification contains only the differences from standard [ECIES]_
and must be read in conjunction with that specification.


Design
======

We use the NIST FIPS 203 standard [FIPS203]_
which is based on, but not compatible with,
CRYSTALS-Kyber (versions 3.1, 3, and older).

Hybrid handshakes are as specified in [Noise-Hybrid]_.


Key Exchange
-------------

We define a hybrid key exchange for Ratchet.
PQ KEM provides ephemeral keys only, and does not directly support
static-key handshakes such as Noise IK.

We define the three ML-KEM variants as in [FIPS203]_,
for 3 new encryption types total.
Hybrid types are only defined in combination with X25519.

The new encryption types are:

================  ====
  Type            Code
================  ====
MLKEM512_X25519     5
MLKEM768_X25519     6
MLKEM1024_X25519    7
================  ====

Overhead will be substantial. Typical message 1 and 2 sizes (for IK)
are currently around 100 bytes (before any additional payload).
This will increase by 8x to 15x depending on algorithm.


New Crypto Required
-------------------

- ML-KEM (formerly CRYSTALS-Kyber) [FIPS203]_
- SHA3-128 (formerly Keccak-256) [FIPS202]_ Used only for SHAKE128
- SHA3-256 (formerly Keccak-512) [FIPS202]_
- SHAKE128 and SHAKE256 (XOF extensions to SHA3-128 and SHA3-256) [FIPS202]_

Test vectors for SHA3-256, SHAKE128, and SHAKE256 are at [NIST-VECTORS]_.

Note that the Java bouncycastle library supports all the above.
C++ library support is in OpenSSL 3.5 [OPENSSL]_.



Specification
=============

Common Structures
-----------------

See the common structures specification [COMMON]_ for key lengths and identifiers.



Handshake Patterns
------------------

Handshakes use [Noise]_ handshake patterns.

The following letter mapping is used:

- e = one-time ephemeral key
- s = static key
- p = message payload
- e1 = one-time ephemeral PQ key, sent from Alice to Bob
- ekem1 = the KEM ciphertext, sent from Bob to Alice

The following modifications to XK and IK for hybrid forward secrecy (hfs) are
as specified in [Noise-Hybrid]_ section 5:

.. raw:: html

  {% highlight lang='dataspec' %}

IK:                       IKhfs:
  <- s                      <- s
  ...                       ...
  -> e, es, s, ss, p       -> e, es, e1, s, ss, p
  <- tag, e, ee, se, p     <- tag, e, ee, ekem1, se, p
  <- p                     <- p
  p ->                     p ->

  e1 and ekem1 are encrypted. See pattern definitions below.
  NOTE: e1 and ekem1 are different sizes (unlike X25519)

{% endhighlight %}

The e1 pattern is defined as follows, as specified in [Noise-Hybrid]_ section 4:

.. raw:: html

  {% highlight lang='dataspec' %}

For Alice:
  (encap_key, decap_key) = PQ_KEYGEN()

  // EncryptAndHash(encap_key)
  ciphertext = ENCRYPT(k, n, encap_key, ad)
  n++
  MixHash(ciphertext)

  For Bob:

  // DecryptAndHash(ciphertext)
  encap_key = DECRYPT(k, n, ciphertext, ad)
  n++
  MixHash(ciphertext)


{% endhighlight %}


The ekem1 pattern is defined as follows, as specified in [Noise-Hybrid]_ section 4:

.. raw:: html

  {% highlight lang='dataspec' %}

For Bob:

  (kem_ciphertext, kem_shared_key) = ENCAPS(encap_key)

  // EncryptAndHash(kem_ciphertext)
  ciphertext = ENCRYPT(k, n, kem_ciphertext, ad)
  MixHash(ciphertext)

  // MixKey
  MixKey(kem_shared_key)


  For Alice:

  // DecryptAndHash(ciphertext)
  kem_ciphertext = DECRYPT(k, n, ciphertext, ad)
  MixHash(ciphertext)

  // MixKey
  kem_shared_key = DECAPS(kem_ciphertext, decap_key)
  MixKey(kem_shared_key)


{% endhighlight %}



Defined ML-KEM Operations
-------------------------

We define the following functions corresponding to the cryptographic building blocks used
as defined in [FIPS203]_.

(encap_key, decap_key) = PQ_KEYGEN()
    Alice creates the encapsulation and decapsulation keys
    The encapsulation key is sent in the NS message.
    encap_key and decap_key sizes vary based on ML-KEM variant.

(ciphertext, kem_shared_key) = ENCAPS(encap_key)
    Bob calculates the ciphertext and shared key,
    using the ciphertext received in the NS message.
    The ciphertext is sent in the NSR message.
    ciphertext size varies based on ML-KEM variant.
    The kem_shared_key is always 32 bytes.

kem_shared_key = DECAPS(ciphertext, decap_key)
    Alice calculates the shared key,
    using the ciphertext received in the NSR message.
    The kem_shared_key is always 32 bytes.

Note that both the encap_key and the ciphertext are encrypted inside ChaCha/Poly
blocks in the Noise handshake messages 1 and 2.
They will be decrypted as part of the handshake process.

The kem_shared_key is mixed into the chaining key with MixHash().
See below for details.



Noise Handshake KDF
---------------------


Overview
````````

The hybrid handshake is defined in [Noise-Hybrid]_.
The first message, from Alice to Bob, contains e1, the encapsulation key, before the message payload.
This is treated as an additional static key; call EncryptAndHash() on it (as Alice)
or DecryptAndHash() (as Bob).
Then process the message payload as usual.

The second message, from Bob to Alice, contains ekem1, the ciphertext, before the message payload.
This is treated as an additional static key; call EncryptAndHash() on it (as Bob)
or DecryptAndHash() (as Alice).
Then, calculate the kem_shared_key and call MixKey(kem_shared_key).
Then process the message payload as usual.



Noise identifiers
`````````````````

These are the Noise initialization strings:

- "Noise_IKhfselg2_25519+MLKEM512_ChaChaPoly_SHA256"
- "Noise_IKhfselg2_25519+MLKEM768_ChaChaPoly_SHA256"
- "Noise_IKhfselg2_25519+MLKEM1024_ChaChaPoly_SHA256"



Alice KDF for NS Message
`````````````````````````

After the 'es' message pattern and before the 's' message pattern, add:

.. raw:: html

  {% highlight lang='text' %}
This is the "e1" message pattern:
  (encap_key, decap_key) = PQ_KEYGEN()

  // EncryptAndHash(encap_key)
  // AEAD parameters
  k = keydata[32:63]
  n = 0
  ad = h
  ciphertext = ENCRYPT(k, n, encap_key, ad)
  n++

  // MixHash(ciphertext)
  h = SHA256(h || ciphertext)


  End of "e1" message pattern.

  NOTE: For the next section (payload for XK or static key for IK),
  the keydata and chain key remain the same,
  and n now equals 1 (instead of 0 for non-hybrid).

{% endhighlight %}


Bob KDF for NS Message
`````````````````````````

After the 'es' message pattern and before the 's' message pattern, add:

.. raw:: html

  {% highlight lang='text' %}
This is the "e1" message pattern:

  // DecryptAndHash(encap_key_section)
  // AEAD parameters
  k = keydata[32:63]
  n = 0
  ad = h
  encap_key = DECRYPT(k, n, encap_key_section, ad)
  n++

  // MixHash(encap_key_section)
  h = SHA256(h || encap_key_section)

  End of "e1" message pattern.

  NOTE: For the next section (payload for XK or static key for IK),
  the keydata and chain key remain the same,
  and n now equals 1 (instead of 0 for non-hybrid).

{% endhighlight %}


Bob KDF for NSR Message
`````````````````````````

After the 'ee' message pattern and before the 'se' message pattern, add:

.. raw:: html

  {% highlight lang='text' %}
This is the "ekem1" message pattern:

  (kem_ciphertext, kem_shared_key) = ENCAPS(encap_key)

  // EncryptAndHash(kem_ciphertext)
  // AEAD parameters
  k = keydata[32:63]
  n = 0
  ad = h
  ciphertext = ENCRYPT(k, n, kem_ciphertext, ad)

  // MixHash(ciphertext)
  h = SHA256(h || ciphertext)

  // MixKey(kem_shared_key)
  keydata = HKDF(chainKey, kem_shared_key, "", 64)
  chainKey = keydata[0:31]

  End of "ekem1" message pattern.

{% endhighlight %}


Alice KDF for NSR Message
`````````````````````````

After the 'ee' message pattern and before the 'ss' message pattern, add:

.. raw:: html

  {% highlight lang='text' %}
This is the "ekem1" message pattern:

  // DecryptAndHash(kem_ciphertext_section)
  // AEAD parameters
  k = keydata[32:63]
  n = 0
  ad = h
  kem_ciphertext = DECRYPT(k, n, kem_ciphertext_section, ad)

  // MixHash(kem_ciphertext_section)
  h = SHA256(h || kem_ciphertext_section)

  // MixKey(kem_shared_key)
  kem_shared_key = DECAPS(kem_ciphertext, decap_key)
  keydata = HKDF(chainKey, kem_shared_key, "", 64)
  chainKey = keydata[0:31]

  End of "ekem1" message pattern.

{% endhighlight %}



KDF for split()
```````````````
unchanged


Message Format
--------------

NS Format
`````````

Changes: Current ratchet contained the static key in the first ChaCha section,
and the payload in the second section.
With ML-KEM, there are now three sections.
The first section contains the encrypted PQ public key.
The second section contains the static key.
The third section contains the payload.


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
  +           ML-KEM encap_key            +
  |       ChaCha20 encrypted data         |
  +      (see table below for length)     +
  |                                       |
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +    (MAC) for encap_key Section        +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +           X25519 Static Key           +
  |       ChaCha20 encrypted data         |
  +             32 bytes                  +
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
  +       ML-KEM encap_key                +
  |                                       |
  +      (see table below for length)     +
  |                                       |
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  Payload Part 2:

  +----+----+----+----+----+----+----+----+
  |                                       |
  +       X25519 Static Key               +
  |                                       |
  +      (32 bytes)                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+

  Payload Part 3:

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
  Type              Type Code  X len  NS len     NS Enc len     NS Dec len     PQ key len  pl len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     96+pl        64+pl             pl           --       pl
MLKEM512_X25519          5       32    912+pl       880+pl         800+pl          800       pl
MLKEM768_X25519          6       32   1296+pl      1360+pl        1184+pl         1184       pl
MLKEM1024_X25519         7       32   1680+pl      1648+pl        1568+pl         1568       pl
================    =========  =====  =========  =============  =============  ==========  =======

Note that the payload must contain a DateTime block, so the minimum payload size is 7.
The minimum NS sizes may be calculated accordingly.



NSR Format
``````````

Changes: Current ratchet has an empty payload for the first ChaCha section,
and the payload in the second section.
With ML-KEM, there are now three sections.
The first section contains the encrypted PQ ciphertext.
The second section has an empty payload.
The third section contains the payload.


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
  | ChaCha20 encrypted ML-KEM ciphertext  |
  +      (see table below for length)     +
  ~                                       ~
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +  (MAC) for ciphertext Section         +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +  (MAC) for key Section (no data)      +
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

  empty

  Payload Part 3:

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
  Type              Type Code  Y len  NSR len    NSR Enc len    NSR Dec len    PQ CT len   opt len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     72+pl        32+pl             pl           --       pl
MLKEM512_X25519          5       32    856+pl       816+pl         768+pl          768       pl
MLKEM768_X25519          6       32   1176+pl      1136+pl        1088+pl         1088       pl
MLKEM1024_X25519         7       32   1656+pl      1616+pl        1568+pl         1568       pl
================    =========  =====  =========  =============  =============  ==========  =======

Note that while NSR will normally have a nonzero payload,
the ratchet specification [ECIES]_ does not require it, so the minimum payload size is 0.
The minimum NSR sizes may be caculated accordingly.



Overhead Analysis
=================

Key Exchange
-------------

Size increase (bytes):

================    ==============  =============
  Type              Pubkey (NS)     Cipertext (NSR)
================    ==============  =============
MLKEM512_X25519       +816               +784
MLKEM768_X25519      +1200              +1104
MLKEM1024_X25519     +1584              +1584
================    ==============  =============

Speed:

Speeds as reported by [CLOUDFLARE]_:

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


Security Analysis
=================

NIST security categories are summarized in [NIST-PQ-END]_ slide 10.
Preliminary criteria:
Our minimum NIST security category should be 2 for hybrid protocols
and 3 for PQ-only.

========  ======
Category  As Secure As
========  ======
   1      AES128
   2      SHA256
   3      AES192
   4      SHA384
   5      AES256
========  ======


Handshakes
----------
These are all hybrid protocols.
Probably need to prefer MLKEM768; MLKEM512 is not secure enough.

NIST security categories [FIPS203]_ :

=========  ========
Algorithm  Security Category
=========  ========
MLKEM512      1
MLKEM768      3
MLKEM1024     5
=========  ========


Type Preferences
=================


The recommended type for initial support, based on security category and key length, is:

MLKEM768_X25519 (type 6)



Implementation Notes
=====================

Library Support
---------------

Bouncycastle, BoringSSL, and WolfSSL libraries support MLKEM now.
OpenSSL support is be in their 3.5 release April 8, 2025 [OPENSSL]_.


Shared Tunnels
--------------

Auto-classify/detect of multiple protocols on the same tunnels should be possible based
on a length check of message 1 (New Session Message).
Using MLKEM512_X25519 as an example, message 1 length is 816 bytes larger
than current ratchet protocol, and the minimum message 1 size (with only a DateTime payload included)
is 919 bytes. Most message 1 sizes with current ratchet have a payload less than
816 bytes, so they can be classified as non-hybrid ratchet.
Large messages are probably POSTs which are rare.

So the recommended strategy is:

- If message 1 is less than 919 bytes, it's the current ratchet protocol.
- If message 1 is greater than or equal to 919 bytes, it's probably MLKEM512_X25519.
  Try MLKEM512_X25519 first, and if it fails, try the current ratchet protocol.

This should allow us to efficiently support standard ratchet and hybrid ratchet
on the same destination, just as we previously supported ElGamal and ratchet
on the same destination. Therefore, we can migrate to the MLKEM hybrid protocol
much more quickly than if we could not support dual-protocols for the same destination,
because we can add MLKEM support to existing destinations.

The required supported combinations are:

- X25519 + MLKEM512
- X25519 + MLKEM768
- X25519 + MLKEM1024

The following combinations may be complex, and are NOT required to be supported,
but may be, implementation-dependent:

- More than one MLKEM
- ElG + one or more MLKEM
- X25519 + one or more MLKEM
- ElG + X25519 + one or more MLKEM

It is not required to support multiple MLKEM algorithms
(for example, MLKEM512_X25519 and MLKEM_768_X25519)
on the same destination. Pick just one.
Implementation-dependent.

It is not required to support three algorithms (for example X25519, MLKEM512_X25519, and MLKEM769_X25519)
on the same destination. The classification and retry strategy may be too complex.
The configuration and configuration UI may be too complex.
Implementation-dependent.

It is not required to support ElGamal and hybrid algorithms on the same destination.
ElGamal is obsolete, and ElGamal + hybrid only (no X25519) doesn't make much sense.
Also, ElGamal and Hybrid New Session Messages are both large, so
classification strategies would often have to try both decryptions,
which would be inefficient.
Implementation-dependent.

Clients may use the same or different X25519 static keys for the X25519
and the hybrid protocols on the same tunnels, implementation-dependent.


Forward Secrecy
---------------
The ECIES specification allows Garlic Messages in the New Session Message payload,
which allows for 0-RTT delivery of the initial streaming packet,
usually a HTTP GET, together with the client's leaseset.
However, the New Session Message payload does not have forward secrecy.
As this proposal is emphasizing enhanced forward secrecy for ratchet,
implementations may or should defer inclusion of the streaming payload,
or the full streaming message, until the first Existing Session Message.
This would be at the expense of 0-RTT delivery.
Strategies may also depend on traffic type or tunnel type,
or on GET vs. POST, for example.
Implementation-dependent.


New Session Size
----------------
MLKEM will dramatically increase
the size of the New Session Message, as described above.
This may significantly decrease the reliability of New Session Message
delivery through tunnels, where they must be fragmented into
multiple 1024 byte tunnel messages. Delivery success is
proportional to the exponential number of fragments.
Implementations may use various strategies to limit the size of the message,
at the expense of 0-RTT delivery.
Implementation-dependent.





References
==========

.. [CLOUDFLARE]
   https://blog.cloudflare.com/pq-2024/

.. [COMMON]
    {{ spec_url('common-structures') }}

.. [ECIES]
   {{ spec_url('ecies') }}

.. [FORUM]
   http://zzz.i2p/topics/3294

.. [FIPS202]
   https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf

.. [FIPS203]
   https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf

.. [NIST-PQ-END]
   https://www.nccoe.nist.gov/sites/default/files/2023-08/pqc-light-at-the-end-of-the-tunnel-presentation.pdf

.. [NIST-VECTORS]
   https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines/example-values

.. [Noise]
   https://noiseprotocol.org/noise.html

.. [Noise-Hybrid]
   https://github.com/noiseprotocol/noise_hfs_spec/blob/master/output/noise_hfs.pdf

.. [OPENSSL]
   https://openssl-library.org/post/2025-02-04-release-announcement-3.5/

.. [PQ-WIREGUARD]
   https://eprint.iacr.org/2020/379.pdf

.. [Prop169]
    {{ proposal_url('169') }}
