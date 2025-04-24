===================================
Post-Quantum Crypto Protocols
===================================
.. meta::
    :author: zzz, orignal, drzed, eyedeekay
    :created: 2025-01-21
    :thread: http://zzz.i2p/topics/3294
    :lastupdated: 2025-04-23
    :status: Open
    :target: 0.9.80

.. contents::






Overview
========

While research and competition for suitable post-quantum (PQ)
cryptography have been proceeding for a decade, the choices
have not become clear until recently.

We started looking at the implications of PQ crypto
in 2022 [FORUM]_.

TLS standards added hybrid encryption support in the last two years and it now
is used for a significant portion of encrypted traffic on the internet
due to support in Chrome and Firefox [CLOUDFLARE]_.

NIST recently finalized and published the recommended algorithms
for post-quantum cryptography [NIST-PQ]_.
Several common cryptography libraries now support the NIST standards
or will be releasing support in the near future.

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
- Define multiple variants
- Select best variants after implementation, testing, analysis, and research
- Add support incrementally and with backward compatibility


Non-Goals
=========

- Don't change one-way (Noise N) encryption protocols
- Don't move away from SHA256, not threatened near-term by PQ
- Don't select the final preferred variants at this time


Threat Model
============

- Routers at the OBEP or IBGW, possibly colluding,
  storing garlic messages for later decryption (forward secrecy)
- Network observers
  storing transport messages for later decryption (forward secrecy)
- Network participants forging signatures for RI, LS, streaming, datagrams,
  or other structures


Affected Protocols
==================

We will modify the following protocols, roughly in order
of development. The overall rollout will probably be from late 2025 through mid-2027.
See the Priorities and Rollout section below for details.


==================================  ======
Protocol / Feature                  Status
==================================  ======
Hybrid EncTypes 5-7                 Preliminary, final hash choices pending
Hybrid Dests, Ratchet               Tested on live net, no net upgrade required
Select preferred combo              Probably 6,4
Combo Hybrid/X25519 Dests, Ratchet
Combo Hybrid/X25519 NTCP2
Combo Hybrid/X25519 SSU2
Hybrid Routers, Dests, Ratchet
MLDSA SigTypes 12-14                Probably final
MLDSA Dests                         Tested on live net, requires net upgrade for floodfill support
Hybrid SigTypes 15-17               Preliminary
Hybrid Dests
==================================  ======



Design
======

We will support the NIST FIPS 203 and 204 standards [FIPS203]_ [FIPS204]_
which are based on, but NOT compatible with,
CRYSTALS-Kyber and CRYSTALS-Dilithium (versions 3.1, 3, and older).



Key Exchange
-------------

We will support hybrid key exchange in the following protocols:

=======  ==========  ================  ===============
Proto    Noise Type  Support PQ only?  Support Hybrid?
=======  ==========  ================  ===============
NTCP2       XK       no                yes
SSU2        XK       no                yes
Ratchet     IK       no                yes
TBM          N       no                no
NetDB        N       no                no
=======  ==========  ================  ===============

PQ KEM provides ephemeral keys only, and does not directly support
static-key handshakes such as Noise XK and IK.

Noise N does not use a two-way key exchange and so it is not suitable
for hybrid encryption.

So we will support hybrid encryption only, for NTCP2, SSU2, and Ratchet.
We will define the three ML-KEM variants as in [FIPS203]_,
for 3 new encryption types total.
Hybrid types will only be defined in combination with X25519.

The new encryption types are:

================  ====
  Type            Code
================  ====
MLKEM512_X25519     5
MLKEM768_X25519     6
MLKEM1024_X25519    7
================  ====

Overhead will be substantial. Typical message 1 and 2 sizes (for XK and IK)
are currently around 100 bytes (before any additional payload).
This will increase by 8x to 15x depending on algorithm.


Signatures
-----------

We will support PQ and hybrid signatures in the following structures:

==========================  ================  ===============
Type                        Support PQ only?  Support Hybrid?
==========================  ================  ===============
RouterInfo                  yes               yes
LeaseSet                    yes               yes
Streaming SYN/SYNACK/Close  yes               yes
Repliable Datagrams         yes               yes
Datagram2 (prop. 163)       yes               yes
I2CP create session msg     yes               yes
SU3 files                   yes               yes
X.509 certificates          yes               yes
Java keystores              yes               yes
==========================  ================  ===============


So we will support both PQ-only and hybrid signatures.
We will define the three ML-DSA variants as in [FIPS204]_,
three hybrid variants with Ed25519,
and three PQ-only variants with prehash for SU3 files only,
for 9 new signature types total.
Hybrid types will only be defined in combination with Ed25519.
We will use the standard ML-DSA, NOT the pre-hash variants (HashML-DSA),
except for SU3 files.

We will use the "hedged" or randomized signing variant,
not the "determinstic" variant, as defined in [FIPS204]_ section 3.4.
This ensures that each signature is different, even when over the same data,
and provides additional protection against side-channel attacks.
See the implementation notes section below for additional details
about algorithm choices including encoding and context.


The new signature types are:

============================  ====
        Type                  Code
============================  ====
MLDSA44                        12
MLDSA65                        13
MLDSA87                        14
MLDSA44_EdDSA_SHA512_Ed25519   15
MLDSA65_EdDSA_SHA512_Ed25519   16
MLDSA87_EdDSA_SHA512_Ed25519   17
MLDSA44ph                      18
MLDSA65ph                      19
MLDSA87ph                      20
============================  ====

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



Legal Combinations
------------------

For Destinations, the new signature types are supported with all encryption
types in the leaseset. Set the encryption type in the key certificate to NONE (255).

For RouterIdentities, ElGamal encryption type is deprecated.
The new signature types are supported with X25519 (type 4) encryption only.
The new encryption types will be indicated in the RouterAddresses.
The encryption type in the key certificate will continue to be type 4.



New Crypto Required
-------------------

- ML-KEM (formerly CRYSTALS-Kyber) [FIPS203]_
- ML-DSA (formerly CRYSTALS-Dilithium) [FIPS204]_
- SHA3-128 (formerly Keccak-256) [FIPS202]_ Used only for SHAKE128
- SHA3-256 (formerly Keccak-512) [FIPS202]_
- SHAKE128 and SHAKE256 (XOF extensions to SHA3-128 and SHA3-256) [FIPS202]_

Test vectors for SHA3-256, SHAKE128, and SHAKE256 are at [NIST-VECTORS]_.

Note that the Java bouncycastle library supports all the above.
C++ library support will be in OpenSSL 3.5 [OPENSSL]_.


Alternatives
-------------

We will not support [FIPS205]_ (Sphincs+), it is much much slower and bigger than ML-DSA.
We will not support the upcoming FIPS206 (Falcon), it is not yet standardized.
We will not support NTRU or other PQ candidates that were not standardized by NIST.


Rosenpass
`````````

There is some research [PQ-WIREGUARD]_ on adapting Wireguard (IK)
for pure PQ crypto, but there are several open questions in that paper.
Later, this approach was implemented as Rosenpass [Rosenpass]_ [Rosenpass-Whitepaper]_
for PQ Wireguard.

Rosenpass uses a Noise KK-like handshake with preshared Classic McEliece 460896 static keys
(500 KB each) and Kyber-512 (essentially MLKEM-512) ephemeral keys.
As the Classic McEliece ciphertexts are only 188 bytes, and the Kyber-512
public keys and ciphertexts are reasonable, both handshake messages fit in a standard UDP MTU.
The output shared key (osk) from the PQ KK handshake is used as the input preshared key (psk)
for the standard Wireguard IK handshake.
So there are two complete handshakes in total, one pure PQ and one pure X25519.

We can't do any of this to replace our XK and IK handshakes because:

- We can't do KK, Bob doesn't have Alice's static key
- 500KB static keys are far too big
- We don't want an extra round-trip

There is a lot of good information in the whitepaper,
and we will review it for ideas and inspiration. TODO.



Specification
=============

Common Structures
-----------------

Update the sections and tables in the common structures document [COMMON]_ as follows:


PublicKey
````````````````

The new Public Key types are:

================    ================= ======  =====
  Type              Public Key Length Since   Usage
================    ================= ======  =====
MLKEM512_X25519               32      0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM768_X25519               32      0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM1024_X25519              32      0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM512                     800      0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM768                    1184      0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM1024                   1568      0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM512_CT                  768      0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM768_CT                 1088      0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM1024_CT                1568      0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
NONE                           0      0.9.xx  See proposal 169, for destinations with PQ sig types only, not for RIs or Leasesets
================    ================= ======  =====

Hybrid public keys are the X25519 key.
KEM public keys are the ephemeral PQ key sent from Alice to Bob.
Encoding and byte order are defined in [FIPS203]_.

MLKEM*_CT keys are not really public keys, they are the "ciphertext" sent from Bob to Alice in the Noise handshake.
They are listed here for completeness.



PrivateKey
````````````````

The new Private Key types are:

================    ================== ======  =====
  Type              Private Key Length Since   Usage
================    ================== ======  =====
MLKEM512_X25519               32       0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM768_X25519               32       0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM1024_X25519              32       0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM512                    1632       0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM768                    2400       0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
MLKEM1024                   3168       0.9.xx  See proposal 169, for handshakes only, not for Leasesets, RIs or Destinations
================    ================== ======  =====

Hybrid private keys are the X25519 keys.
KEM private keys are for Alice only.
KEM encoding and byte order are defined in [FIPS203]_.




SigningPublicKey
````````````````

The new Signing Public Key types are:

============================   ==============  ======  =====
         Type                  Length (bytes)  Since   Usage
============================   ==============  ======  =====
MLDSA44                              1312      0.9.xx  See proposal 169
MLDSA65                              1952      0.9.xx  See proposal 169
MLDSA87                              2592      0.9.xx  See proposal 169
MLDSA44_EdDSA_SHA512_Ed25519         1344      0.9.xx  See proposal 169
MLDSA65_EdDSA_SHA512_Ed25519         1984      0.9.xx  See proposal 169
MLDSA87_EdDSA_SHA512_Ed25519         2624      0.9.xx  See proposal 169
MLDSA44ph                            1344      0.9.xx  Only for SU3 files, not for netdb structures
MLDSA65ph                            1984      0.9.xx  Only for SU3 files, not for netdb structures
MLDSA87ph                            2624      0.9.xx  Only for SU3 files, not for netdb structures
============================   ==============  ======  =====

Hybrid signing public keys are the Ed25519 key followed by the PQ key, as in [COMPOSITE-SIGS]_.
Encoding and byte order are defined in [FIPS204]_.


SigningPrivateKey
`````````````````

The new Signing Private Key types are:

============================   ==============  ======  =====
         Type                  Length (bytes)  Since   Usage
============================   ==============  ======  =====
MLDSA44                              2560      0.9.xx  See proposal 169
MLDSA65                              4032      0.9.xx  See proposal 169
MLDSA87                              4896      0.9.xx  See proposal 169
MLDSA44_EdDSA_SHA512_Ed25519         2592      0.9.xx  See proposal 169
MLDSA65_EdDSA_SHA512_Ed25519         4064      0.9.xx  See proposal 169
MLDSA87_EdDSA_SHA512_Ed25519         4928      0.9.xx  See proposal 169
MLDSA44ph                            2592      0.9.xx  Only for SU3 files, not for netdb structuresSee proposal 169
MLDSA65ph                            4064      0.9.xx  Only for SU3 files, not for netdb structuresSee proposal 169
MLDSA87ph                            4928      0.9.xx  Only for SU3 files, not for netdb structuresSee proposal 169
============================   ==============  ======  =====

Hybrid signing private keys are the Ed25519 key followed by the PQ key, as in [COMPOSITE-SIGS]_.
Encoding and byte order are defined in [FIPS204]_.


Signature
``````````

The new Signature types are:

============================   ==============  ======  =====
         Type                  Length (bytes)  Since   Usage
============================   ==============  ======  =====
MLDSA44                              2420      0.9.xx  See proposal 169
MLDSA65                              3309      0.9.xx  See proposal 169
MLDSA87                              4627      0.9.xx  See proposal 169
MLDSA44_EdDSA_SHA512_Ed25519         2484      0.9.xx  See proposal 169
MLDSA65_EdDSA_SHA512_Ed25519         3373      0.9.xx  See proposal 169
MLDSA87_EdDSA_SHA512_Ed25519         4691      0.9.xx  See proposal 169
MLDSA44ph                            2484      0.9.xx  Only for SU3 files, not for netdb structuresSee proposal 169
MLDSA65ph                            3373      0.9.xx  Only for SU3 files, not for netdb structuresSee proposal 169
MLDSA87ph                            4691      0.9.xx  Only for SU3 files, not for netdb structuresSee proposal 169
============================   ==============  ======  =====

Hybrid signatures are the Ed25519 signature followed by the PQ signature, as in [COMPOSITE-SIGS]_.
Hybrid signatures are verified by verifying both signatures, and failing
if either one fails.
Encoding and byte order are defined in [FIPS204]_.



Key Certificates
````````````````

The new Signing Public Key types are:

============================  ===========  =======================  ======  =====
        Type                  Type Code    Total Public Key Length  Since   Usage
============================  ===========  =======================  ======  =====
MLDSA44                           12                 1312           0.9.xx  See proposal 169
MLDSA65                           13                 1952           0.9.xx  See proposal 169
MLDSA87                           14                 2592           0.9.xx  See proposal 169
MLDSA44_EdDSA_SHA512_Ed25519      15                 1344           0.9.xx  See proposal 169
MLDSA65_EdDSA_SHA512_Ed25519      16                 1984           0.9.xx  See proposal 169
MLDSA87_EdDSA_SHA512_Ed25519      17                 2624           0.9.xx  See proposal 169
MLDSA44ph                         18                  n/a           0.9.xx  Only for SU3 files
MLDSA65ph                         19                  n/a           0.9.xx  Only for SU3 files
MLDSA87ph                         20                  n/a           0.9.xx  Only for SU3 files
============================  ===========  =======================  ======  =====



The new Crypto Public Key types are:

================    ===========  ======================= ======  =====
  Type              Type Code    Total Public Key Length Since   Usage
================    ===========  ======================= ======  =====
MLKEM512_X25519          5                 32            0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM768_X25519          6                 32            0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
MLKEM1024_X25519         7                 32            0.9.xx  See proposal 169, for Leasesets only, not for RIs or Destinations
NONE                   255                  0            0.9.xx  See proposal 169
================    ===========  ======================= ======  =====


Hybrid key types are NEVER included in key certificates; only in leasesets.

For destinations with Hybrid or PQ signature types,
use NONE (type 255) for the encryption type,
but there is no crypto key, and the
entire 384-byte main section is for the signing key.


Destination sizes
``````````````````

Here are lengths for the new Destination types.
Enc type for all is NONE (type 255) and the encryption key length is treated as 0.
The entire 384-byte section is used for the first part of the signing public key.
NOTE: This is different than the spec for the ECDSA_SHA512_P521
and the RSA signature types, where we maintained the 256-byte ElGamal
key in the destination even though it was unused.

No padding.
Total length is 7 + total key length.
Key certificate length is 4 + excess key length.

Example 1319-byte destination byte stream for MLDSA44:

skey[0:383] 5 (932 >> 8) (932 & 0xff) 00 12 00 255 skey[384:1311]



============================  ===========  =======================  ======  ======  =====
        Type                  Type Code    Total Public Key Length  Main    Excess  Total Dest Length
============================  ===========  =======================  ======  ======  =====
MLDSA44                           12                 1312           384      928    1319
MLDSA65                           13                 1952           384     1568    1959
MLDSA87                           14                 2592           384     2208    2599
MLDSA44_EdDSA_SHA512_Ed25519      15                 1344           384      960    1351
MLDSA65_EdDSA_SHA512_Ed25519      16                 1984           384     1600    1991
MLDSA87_EdDSA_SHA512_Ed25519      17                 2624           384     2240    2631
============================  ===========  =======================  ======  ======  =====



RouterIdent sizes
``````````````````

Here are lengths for the new Destination types.
Enc type for all is X25519 (type 4).
The entire 352-byte section after the X28819 public key is used for the first part of the signing public key.
No padding.
Total length is 39 + total key length.
Key certificate length is 4 + excess key length.

Example 1351-byte router identity byte stream for MLDSA44:

enckey[0:31] skey[0:351] 5 (960 >> 8) (960 & 0xff) 00 12 00 4 skey[352:1311]



============================  ===========  =======================  ======  ======  =====
        Type                  Type Code    Total Public Key Length  Main    Excess  Total RouterIdent Length
============================  ===========  =======================  ======  ======  =====
MLDSA44                           12                 1312           352      960    1351
MLDSA65                           13                 1952           352     1600    1991
MLDSA87                           14                 2592           352     2240    2631
MLDSA44_EdDSA_SHA512_Ed25519      15                 1344           352      992    1383
MLDSA65_EdDSA_SHA512_Ed25519      16                 1984           352     1632    2023
MLDSA87_EdDSA_SHA512_Ed25519      17                 2624           352     2272    2663
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

The following modifications to XK and IK for hybrid forward secrecy (hfs) are
as specified in [Noise-Hybrid]_ section 5:

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




Noise Handshake KDF
---------------------

Issues
``````

- Should we change the handshake hash function? See [Choosing-Hash]_.
  SHA256 is not vulnerable to PQ, but if we do want to upgrade
  our hash function, now is the time, while we're changing other things.
  The current IETF SSH proposal [SSH-HYBRID]_ is to use MLKEM768
  with SHA256, and MLKEM1024 with SHA384. That proposal includes
  a discussion of the security considerations.
- Should we stop sending 0-RTT ratchet data (other than the LS)?
- Should we switch ratchet from IK to XK if we don't send 0-RTT data?


Overview
````````

This section applies to both IK and XK protocols.

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


Defined ML-KEM Operations
`````````````````````````

We define the following functions corresponding to the cryptographic building blocks used
as defined in [FIPS203]_.

(encap_key, decap_key) = PQ_KEYGEN()
    Alice creates the encapsulation and decapsulation keys
    The encapsulation key is sent in message 1.
    encap_key and decap_key sizes vary based on ML-KEM variant.

(ciphertext, kem_shared_key) = ENCAPS(encap_key)
    Bob calculates the ciphertext and shared key,
    using the ciphertext received in message 1.
    The ciphertext is sent in message 2.
    ciphertext size varies based on ML-KEM variant.
    The kem_shared_key is always 32 bytes.

kem_shared_key = DECAPS(ciphertext, decap_key)
    Alice calculates the shared key,
    using the ciphertext received in message 2.
    The kem_shared_key is always 32 bytes.

Note that both the encap_key and the ciphertext are encrypted inside ChaCha/Poly
blocks in the Noise handshake messages 1 and 2.
They will be decrypted as part of the handshake process.

The kem_shared_key is mixed into the chaining key with MixHash().
See below for details.


Alice KDF for Message 1
`````````````````````````

For XK: After the 'es' message pattern and before the payload, add:

OR

For IK: After the 'es' message pattern and before the 's' message pattern, add:

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


Bob KDF for Message 1
`````````````````````````

For XK: After the 'es' message pattern and before the payload, add:

OR

For IK: After the 'es' message pattern and before the 's' message pattern, add:

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


Bob KDF for Message 2
`````````````````````````

For XK: After the 'ee' message pattern and before the payload, add:

OR

For IK: After the 'ee' message pattern and before the 'se' message pattern, add:

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


Alice KDF for Message 2
`````````````````````````

After the 'ee' message pattern (and before the 'ss' message pattern for IK), add:

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


KDF for Message 3 (XK only)
```````````````````````````
unchanged


KDF for split()
```````````````
unchanged



Ratchet
---------

Update the ECIES-Ratchet specification [ECIES]_ as follows:


Noise identifiers
`````````````````

- "Noise_IKhfselg2_25519+MLKEM512_ChaChaPoly_SHA256"
- "Noise_IKhfselg2_25519+MLKEM768_ChaChaPoly_SHA256"
- "Noise_IKhfselg2_25519+MLKEM1024_ChaChaPoly_SHA256"



1b) New session format (with binding)
`````````````````````````````````````

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
  Type              Type Code  X len  Msg 1 len  Msg 1 Enc len  Msg 1 Dec len  PQ key len  pl len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     96+pl        64+pl             pl           --       pl
MLKEM512_X25519          5       32    912+pl       880+pl         800+pl          800       pl
MLKEM768_X25519          6       32   1296+pl      1360+pl        1184+pl         1184       pl
MLKEM1024_X25519         7       32   1680+pl      1648+pl        1568+pl         1568       pl
================    =========  =====  =========  =============  =============  ==========  =======

Note that the payload must contain a DateTime block, so the minimum payload size is 7.
The minimum message 1 sizes may be caculated accordingly.



1g) New Session Reply format
````````````````````````````

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
  Type              Type Code  Y len  Msg 2 len  Msg 2 Enc len  Msg 2 Dec len  PQ CT len   opt len
================    =========  =====  =========  =============  =============  ==========  =======
X25519                   4       32     72+pl        32+pl             pl           --       pl
MLKEM512_X25519          5       32    856+pl       816+pl         768+pl          768       pl
MLKEM768_X25519          6       32   1176+pl      1136+pl        1088+pl         1088       pl
MLKEM1024_X25519         7       32   1656+pl      1616+pl        1568+pl         1568       pl
================    =========  =====  =========  =============  =============  ==========  =======

Note that while message 2 will normally have a nonzero payload,
the ratchet specification [ECIES]_ does not require it, so the minimum payload size is 0.
The minimum message 2 sizes may be caculated accordingly.



NTCP2
------

Update the NTCP2 specification [NTCP2]_ as follows:


Noise identifiers
`````````````````

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
  |   ChaChaPoly frame (MLKEM)            |
  +      (see table below for length)     +
  |   k defined in KDF for message 1      |
  +   n = 0                               +
  |   see KDF for associated data         |
  ~   n = 0                               ~
  +----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   ChaChaPoly frame (options)          |
  +         32 bytes                      +
  |   k defined in KDF for message 1      |
  +   n = 0                               +
  |   see KDF for associated data         |
  +----+----+----+----+----+----+----+----+
  |     unencrypted authenticated         |
  ~         padding (optional)            ~
  |     length defined in options block   |
  +----+----+----+----+----+----+----+----+

  Same as before except add a second ChaChaPoly frame


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
  |           ML-KEM encap_key            |
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
MLKEM512_X25519          5       32    880+pad      848             816          800         16
MLKEM768_X25519          6       32   1264+pad     1232            1200         1184         16
MLKEM1024_X25519         7       32   1648+pad     1616            1584         1568         16
================    =========  =====  =========  =============  =============  ==========  =======

Note: Type codes are for internal use only. Routers will remain type 4,
and support will be indicated in the router addresses.


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
  |   ChaChaPoly frame (MLKEM)            |
  +   Encrypted and authenticated data    +
  -      (see table below for length)     -
  +   k defined in KDF for message 2      +
  |   n = 0; see KDF for associated data  |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |   ChaChaPoly frame (options)          |
  +   Encrypted and authenticated data    +
  -           32 bytes                    -
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

  Same as before except add a second ChaChaPoly frame

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
MLKEM512_X25519          5       32    848+pad      816             784          768         16
MLKEM768_X25519          6       32   1136+pad     1104            1104         1088         16
MLKEM1024_X25519         7       32   1616+pad     1584            1584         1568         16
================    =========  =====  =========  =============  =============  ==========  =======

Note: Type codes are for internal use only. Routers will remain type 4,
and support will be indicated in the router addresses.



3) SessionConfirmed
```````````````````

Unchanged


Key Derivation Function (KDF) (for data phase)
``````````````````````````````````````````````

Unchanged




SSU2
----

Update the SSU2 specification [SSU2]_ as follows:


Noise identifiers
`````````````````

- "Noise_XKhfschaobfse+hs1+hs2+hs3_25519+MLKEM512_ChaChaPoly_SHA256"
- "Noise_XKhfschaobfse+hs1+hs2+hs3_25519+MLKEM768_ChaChaPoly_SHA256"
- "Noise_XKhfschaobfse+hs1+hs2+hs3_25519+MLKEM1024_ChaChaPoly_SHA256"


Long Header
`````````````
The long header is 32 bytes. It is used before a session is created, for Token Request, SessionRequest, SessionCreated, and Retry.
It is also used for out-of-session Peer Test and Hole Punch messages.

TODO: We could internally use the version field and use 3 for MLKEM512 and 4 for MLKEM768.
Do we only do that for types 0 and 1 or for all 6 types?


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
         TODO We could internally use the version field and use 3 for MLKEM512 and 4 for MLKEM768.

  id :: 1 byte, the network ID (currently 2, except for test networks)

  flag :: 1 byte, unused, set to 0 for future compatibility

  Source Connection ID :: 8 bytes, unsigned big endian integer

  Token :: 8 bytes, unsigned big endian integer

{% endhighlight %}


Short Header
`````````````
unchanged


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
  |   ChaCha20 encrypted data (MLKEM)     |
  +          (length varies)              +
  |  k defined in KDF for Session Request |
  +  n = 0                                +
  |  see KDF for associated data          |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   ChaCha20 encrypted data (payload)   |
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
  |           ML-KEM encap_key            |
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
MLKEM512_X25519          5       32    896+pl       832+pl         800+pl        800         pl
MLKEM768_X25519          6       32   1280+pl      1216+pl        1184+pl       1184         pl
MLKEM1024_X25519         7      n/a   too big
================    =========  =====  =========  =============  =============  ==========  =======

Note: Type codes are for internal use only. Routers will remain type 4,
and support will be indicated in the router addresses.

Minimum MTU for MLKEM768_X25519:
About 1316 for IPv4 and 1336 for IPv6.



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
  |   ChaCha20 data (MLKEM)               |
  +   Encrypted and authenticated data    +
  |  length varies                        |
  +  k defined in KDF for Session Created +
  |  n = 0; see KDF for associated data   |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |   ChaCha20 data (payload)             |
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
MLKEM512_X25519          5       32    864+pl       800+pl         768+pl        768         pl
MLKEM768_X25519          6       32   1184+pl      1118+pl        1088+pl       1088         pl
MLKEM1024_X25519         7      n/a   too big
================    =========  =====  =========  =============  =============  ==========  =======

Note: Type codes are for internal use only. Routers will remain type 4,
and support will be indicated in the router addresses.

Minimum MTU for MLKEM768_X25519:
About 1316 for IPv4 and 1336 for IPv6.


SessionConfirmed (Type 2)
`````````````````````````
unchanged



KDF for data phase
```````````````````
unchanged



Relay and Peer Test
```````````````````

Relay blocks, Peer Test blocks, and Peer Test messages all contain signatures.
Unfortunately, PQ signatures are larger than the MTU.
There is no current mechanism to fragment Relay or Peer Test blocks or messages
across multiple UDP packets.
The protocol must be extended to support fragmentation.
This will be done in a separate proposal TBD.
Until that is completed, Relay and Peer Test will not be supported.


Issues
``````

We could internally use the version field and use 3 for MLKEM512 and 4 for MLKEM768.

For messages 1 and 2, MLKEM768 would increase packet sizes beyond the 1280 minimum MTU.
Probably would just not support it for that connection if the MTU was too low.

For messages 1 and 2, MLKEM1024 would increase packet sizes beyond 1500 maximum MTU.
This would require fragmenting messages 1 and 2, and it would be a big complication.
Probably won't do it.

Relay and Peer Test: See above


Streaming
---------

TODO: Is there a more efficient way to define signing/verification
to avoid copying the signature?



SU3 Files
---------

TODO

[MLDSA-OIDS]_ section 8.1 disallows HashML-DSA in X.509 certificates
and does not assign OIDs for HashML-DSA, because of implementation
complexities and reduced security.

For PQ-only signatures of SU3 files,
use the OIDs defined in [MLDSA-OIDS]_ of the non-prehash variants for the certificates.
We do not define hybrid signatures of SU3 files,
because we may have to hash the files twice (although HashML-DSA and X2559 use the same
hash function SHA512). Also, concatenating two keys and signatures in
a X.509 certificate would be completely nonstandard.

Note that we disallow Ed25519 signing of SU3 files,
and while we have defined Ed25519ph signing, we have never agreed on an OID for it,
or used it.

The normal sig types are disallowed for SU3 files; use the ph (prehash) variants.



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


Preliminary test results in Java:

====================  ===================  ============  ======
  Type                Relative DH/encaps   DH/decaps     keygen
====================  ===================  ============  ======
X25519                     baseline        baseline      baseline
MLKEM512                   29x faster      22x faster    17x faster
MLKEM768                   17x faster      14x faster    9x faster
MLKEM1024                  12x faster      10x faster    6x faster
====================  ===================  ============  ======


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
MLDSA44                         1312   2420   3732     1351    1319   +3316     +3284
MLDSA65                         1952   3309   5261     1991    1959   +5668     +5636
MLDSA87                         2592   4627   7219     2631    2599   +7072     +7040
MLDSA44_EdDSA_SHA512_Ed25519    1344   2484   3828     1383    1351   +3412     +3380
MLDSA65_EdDSA_SHA512_Ed25519    1984   3373   5357     2023    1991   +5668     +5636
MLDSA87_EdDSA_SHA512_Ed25519    2624   4691   7315     2663    2631   +7488     +7456
============================  =======  ====  =======  ======  ======  ========  =====

Speed:

Speeds as reported by [CLOUDFLARE]_:

====================  ===================  ======
  Type                Relative speed sign  verify
====================  ===================  ======
EdDSA_SHA512_Ed25519        baseline       baseline
MLDSA44                     5x slower      2x faster
MLDSA65                       ???          ???
MLDSA87                       ???          ???
====================  ===================  ======

Preliminary test results in Java:

====================  ===================  ============  ======
  Type                Relative speed sign  verify        keygen
====================  ===================  ============  ======
EdDSA_SHA512_Ed25519       baseline        baseline      baseline
MLDSA44                    4.6x slower     1.7x faster   2.6x faster
MLDSA65                    8.1x slower     same          1.5x faster
MLDSA87                    11.1x slower    1.5x slower   same
====================  ===================  ============  ======




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


Signatures
----------
This proposal defines both hybrid and PQ-only signature types.
MLDSA44 hybrid is preferable to MLDSA65 PQ-only.
The keys and sig sizes for MLDSA65 and MLDSA87 are probably too big for us, at least at first.

NIST security categories [FIPS204]_ :

=========  ========
Algorithm  Security Category
=========  ========
MLDSA44       2
MLKEM67       3
MLKEM87       5
=========  ========


Type Preferences
=================

While we will define and implement 3 crypto and 9 signature types, we
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

Library Support
---------------

Bouncycastle, BoringSSL, and WolfSSL libraries support MLKEM and MLDSA now.
OpenSSL support will be in their 3.5 release scheduled for April 8, 2025 [OPENSSL]_.
3.5-alpha will be availabe March 11, 2025.

The southernstorm.com Noise library adapted by Java I2P contained preliminary support for
hybrid handshakes, but we removed it as unused; we will have to add it back
and update it to match [Noise-Hybrid]_.

Signing Variants
----------------

We will use the "hedged" or randomized signing variant,
not the "determinstic" variant, as defined in [FIPS204]_ section 3.4.
This ensures that each signature is different, even when over the same data,
and provides additional protection against side-channel attacks.
While [FIPS204]_ specifies that the "hedged" variant is the default,
this may or may not be true in various libraries.
Implementors must ensure that the "hedged" variant is used for signing.

We use the normal signing process (called Pure ML-DSA Signature Generation)
which encodes the message internally as 0x00 || len(ctx) || ctx || message,
where ctx is some optional value of size 0x00..0xFF.
We are not using any optional context. len(ctx) == 0.
This process is defined in [FIPS204]_ Algorithm 2 step 10 and Algorithm 3 step 5.
Note that some published test vectors may require setting a mode
where the message is not encoded.



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

Shared Tunnels
``````````````

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

We may not attempt to support multiple MLKEM algorithms
(for example, MLKEM512_X25519 and MLKEM_768_X25519)
on the same destination. Pick just one; however, that depends on us
selecting a preferred MLKEM variant, so HTTP client tunnels can use one.
Implementation-dependent.

We MAY attempt to support three algorithms (for example X25519, MLKEM512_X25519, and MLKEM769_X25519)
on the same destination. The classification and retry strategy may be too complex.
The configuration and configuration UI may be too complex.
Implementation-dependent.

We will probably NOT attempt to support ElGamal and hybrid algorithms on the same destination.
ElGamal is obsolete, and ElGamal + hybrid only (no X25519) doesn't make much sense.
Also, ElGamal and Hybrid New Session Messages are both large, so
classification strategies would often have to try both decryptions,
which would be inefficient.
Implementation-dependent.

Clients may use the same or different X25519 static keys for the X25519
and the hybrid protocols on the same tunnels, implementation-dependent.


Forward Secrecy
```````````````
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
````````````````
MLKEM, MLDSA, or both on the same destination, will dramatically increase
the size of the New Session Message, as described above.
This may significantly decrease the reliability of New Session Message
delivery through tunnels, where they must be fragmented into
multiple 1024 byte tunnel messages. Delivery success is
proportional to the exponential number of fragments.
Implementations may use various strategies to limit the size of the message,
at the expense of 0-RTT delivery.
Implementation-dependent.


NTCP2
-----
We can set the MSB of the ephemeral key
(key[31] & 0x80) in the session request to indicate that this
is a hybrid connection.
This would allow us to run both standard NTCP and hybrid NTCP
on the same port.
Only one hybrid variant would be supported, and advertised in the router address.
For example, v=2,3 or v=2,4 or v=2,5.

If we don't do that, we need different transport address/port,
and a new protocol name such as "NTCP1PQ1".

Note: Type codes are for internal use only. Routers will remain type 4,
and support will be indicated in the router addresses.

TODO


SSU2
-----
MAY Need different transport address/port,
but hopefully not, we have a header with flags for message 1.
We could internally use the version field and use 3 for MLKEM512 and 4 for MLKEM768.
Maybe just v=2,3,4 in the address would be sufficient.
But we need identifiers for both new algorithms: 3a, 3b?

Check and verify that SSU2 can handle the RI fragmented across
multiple packets (6-8?). i2pd currently supports only 2 fragments max?

Note: Type codes are for internal use only. Routers will remain type 4,
and support will be indicated in the router addresses.

TODO




Router Compatibility
====================

Transport Names
---------------

We will probably not require new transport names,
if we can run both standard and hybrid on the same port,
with version flags.

If we do require new transport names, they would be:


=========  ====
Transport  Type
=========  ====
NTCP2PQ1   MLKEM512_X25519
NTCP2PQ2   MLKEM768_X25519
NTCP2PQ3   MLKEM1024_X25519
SSU2PQ1    MLKEM512_X25519
SSU2PQ2    MLKEM768_X25519
=========  ====

Note that SSU2 cannot support MLKEM1024, it is too big.



Router Enc. Types
-----------------

We have several alternatives to consider:

Type 5/6/7 Routers
``````````````````

Not recommended.
Use only the new transports listed above that match the router type.
Older routers cannot connect, build tunnels through, or send netdb messages to.
Would take several release cycles to debug and ensure support before enabling by default.
Might extend rollout by a year or more over alternatives below.


Type 4 Routers
``````````````

Recommended.
As PQ does not affect the X25519 static key or N handshake protocols,
we could leave the routers as type 4, and just advertise new transports.
Older routers could still connect, build tunnels through, or send netdb messages to.


NTCP2 Alternatives
``````````````````

Type 4 routers could advertise both NTCP2 and NTCP2PQ* addresses.
These could use the same static key and other parameters, or not.
These will probably need to be on different ports;
it would be very difficult to support both NTCP2 and NTCP2PQ* protocols
on the same port, as there is no header or framing that would allow
Bob to classify and frame the incoming Session Request message.

Separate ports and addresses will be difficult for Java but straightforward for i2pd.


SSU2 Alternatives
``````````````````

Type 4 routers could advertise both SSU2 and SSU2PQ* addresses.
With added header flags, Bob could identify the incoming transport
type in the first message. Therefore, we could support
both SSU2 and SSUPQ* on the same port.

These could be published as separate addresses (as i2pd has done
in previous transitions) or in the same address with a parameter
indicating PQ support (as Java i2p has done in previous transitions).

If in the same address, or on the same port in different addresses, these would use the same static key and other parameters.
If in different addresses with different ports, these could use the same static key and other parameters, or not.

Separate ports and addresses will be difficult for Java but straightforward for i2pd.


Recommendations
````````````````

TODO


Router Sig. Types
-----------------

Type 12-17 Routers
``````````````````

Older routers verify RIs and so cannot connect, build tunnels through, or send netdb messages to.
Would take several release cycles to debug and ensure support before enabling by default.
Would be the same issues as the enc. type 5/6/7 rollout;
might extend rollout by a year or more over the type 4 enc. type rollout alternative listed above.

No alternatives.


LS Enc. Types
-----------------

Type 5-7 LS Keys
``````````````````

These may be present in the LS with older type 4 X25519 keys.
Older routers will ignore unknown keys.

Destinations can support multiple key types, but only by doing trial decrypts of
message 1 with each key.
The overhead may be mitigated by maintaining counts of successful decrypts for each key,
and trying the most-used key first.
Java I2P uses this strategy for ElGamal+X25519 on the same destination.


Dest. Sig. Types
-----------------

Type 12-17 Dests
``````````````````

Routers verify leaseset signatures and so cannot connect, or receive leasesets for type 12-17 destinations.
Would take several release cycles to debug and ensure support before enabling by default.

No alternatives.


Priorities and Rollout
======================

The most valuable data are the end-to-end traffic, encrypted with ratchet.
As an external observer between tunnel hops, that's encrypted twice more, with tunnel encryption and transport encryption.
As an external observer between OBEP and IBGW, it's encrypted only once more, with transport encryption.
As a OBEP or IBGW participant, ratchet is the only encryption.
However, as tunnels are unidirectional, capturing both messages in the ratchet handshake
would require colluding routers, unless tunnels were built with the
OBEP and IBGW on the same router.

The most worrisome PQ threat model right now is storing traffic today, for decryption many many years from now (forward secrecy).
A hybrid approach would protect that.

The PQ threat model of breaking the authentication keys in some reasonable period of time
(say a few months) and then impersonating the authentication or decrypting in almost-real-time,
is much farther off? And that's when we'd want to migrate to PQC static keys.

So, the earliest PQ threat model is OBEP/IBGW storing traffic for later decryption.
We should implement hybrid ratchet first.

Ratchet is the highest priority.
Transports are next.
Signatures are the lowest priority.

Signature rollout will also be a year or more later than encryption rollout,
because no backward compatibility is possible.
Also, MLDSA adoption in the industry will be standardized by the CA/Browser Forum
and Certificate Authorities. CAs need hardware security module (HSM) support
first, which is not currently available [CABFORUM]_.
We expect the CA/Browser Forum to drive decisions on specific parameter
choices, including whether to support or require composite signatures [COMPOSITE-SIGS]_.




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

We should be able to just try one-then-the-other, as we did with X25519, to be proven.




Issues
=========

- Noise Hash selection - stay with SHA256 or upgrade?
  SHA256 should be good for another 20-30 years, not threatened by PQ,
  See [NIST-PQ-UPDATE]_ and [NIST-PQ-END]_.
  If SHA256 is broken we have worse problems (netdb).
- NTCP2 separate port, separate router address
- SSU2 relay / peer test
- SSU2 version field
- SSU2 router address version



References
==========

.. [CABFORUM]
   https://cabforum.org/2024/10/10/2024-10-10-minutes-of-the-code-signing-certificate-working-group/

.. [Choosing-Hash]
   https://kerkour.com/fast-secure-hash-function-sha256-sha512-sha3-blake3

.. [CLOUDFLARE]
   https://blog.cloudflare.com/pq-2024/

.. [COMMON]
    {{ spec_url('common-structures') }}

.. [COMPOSITE-SIGS]
   https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/

.. [ECIES]
   {{ spec_url('ecies') }}

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

.. [MLDSA-OIDS]
   https://datatracker.ietf.org/doc/draft-ietf-lamps-dilithium-certificates/

.. [NIST-PQ]
   https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards

.. [NIST-PQ-UPDATE]
   https://csrc.nist.gov/csrc/media/Presentations/2022/update-on-post-quantum-encryption-and-cryptographi/Day%202%20-%20230pm%20Chen%20PQC%20ISPAB.pdf

.. [NIST-PQ-END]
   https://www.nccoe.nist.gov/sites/default/files/2023-08/pqc-light-at-the-end-of-the-tunnel-presentation.pdf

.. [NIST-VECTORS]
   https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines/example-values

.. [Noise]
   https://noiseprotocol.org/noise.html

.. [Noise-Hybrid]
   https://github.com/noiseprotocol/noise_hfs_spec/blob/master/output/noise_hfs.pdf

.. [NSA-PQ]
   https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSI_CNSA_2.0_FAQ\_.PDF

.. [NTCP2]
   {{ spec_url('ntcp2') }}

.. [OPENSSL]
   https://openssl-library.org/post/2025-02-04-release-announcement-3.5/

.. [PQ-WIREGUARD]
   https://eprint.iacr.org/2020/379.pdf

.. [RFC-2104]
    https://tools.ietf.org/html/rfc2104

.. [Rosenpass]
   https://rosenpass.eu/

.. [Rosenpass-Whitepaper]
   https://raw.githubusercontent.com/rosenpass/rosenpass/papers-pdf/whitepaper.pdf

.. [SSH-HYBRID]
   https://datatracker.ietf.org/doc/draft-ietf-sshm-mlkem-hybrid-kex/

.. [SSU2]
   {{ spec_url('ssu2') }}

.. [TLS-HYBRID]
   https://datatracker.ietf.org/doc/draft-ietf-tls-hybrid-design/
