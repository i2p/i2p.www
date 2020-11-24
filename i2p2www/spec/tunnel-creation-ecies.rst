=============================
ECIES-X25519 Tunnel Creation
=============================

.. meta::
    :category: Protocols
    :lastupdated: 2020-11
    :accuratefor: 0.9.48

.. contents::

Overview
========

This document specifies Tunnel Build message encryption
using crypto primitives introduced by [ECIES-X25519]_.
It is a portion of the overall proposal
[Prop156]_ for converting routers from ElGamal to ECIES-X25519 keys.
This specification is implemented as of release 0.9.48.

For the purposes of transitioning the network from ElGamal + AES256 to ECIES + ChaCha20,
tunnels with mixed ElGamal and ECIES routers are necessary.
Specifications for handling mixed tunnel hops are provided.
No changes will be made to the format, processing, or encryption of ElGamal hops.

ElGamal tunnel creators will generate ephemeral X25519 keypairs per-hop, and
follow this spec for creating tunnels containing ECIES hops.

This document specifies ECIES-X25519 Tunnel Building.
For an overview of all changes required for ECIES routers, see proposal 156 [Prop156]_.
For additional background on the development of this specification, see proposal 152 [Prop152]_.

This format maintains the same size for tunnel build records,
as required for compatibility. Smaller build records and messages will be
implemented later - see [Prop157]_.


Cryptographic Primitives
------------------------

The primitives required to implement this specification are:

- AES-256-CBC as in [Cryptography]_
- STREAM ChaCha20/Poly1305 functions:
  ENCRYPT(k, n, plaintext, ad) and DECRYPT(k, n, ciphertext, ad) - as in [NTCP2]_ [ECIES-X25519]_ and [RFC-7539]_
- X25519 DH functions - as in [NTCP2]_ and [ECIES-X25519]_
- HKDF(salt, ikm, info, n) - as in [NTCP2]_ and [ECIES-X25519]_

Other Noise functions defined elsewhere:

- MixHash(d) - as in [NTCP2]_ and [ECIES-X25519]_
- MixKey(d) - as in [NTCP2]_ and [ECIES-X25519]_



Design
======

Noise Protocol Framework
------------------------

This specification provides the requirements based on the Noise Protocol Framework
[NOISE]_ (Revision 34, 2018-07-11).
In Noise parlance, Alice is the initiator, and Bob is the responder.

It is based on the Noise protocol Noise_N_25519_ChaChaPoly_SHA256.
This Noise protocol uses the following primitives:

- One-Way Handshake Pattern: N
  Alice does not transmit her static key to Bob (N)

- DH Function: X25519
  X25519 DH with a key length of 32 bytes as specified in [RFC-7748]_.

- Cipher Function: ChaChaPoly
  AEAD_CHACHA20_POLY1305 as specified in [RFC-7539]_ section 2.8.
  12 byte nonce, with the first 4 bytes set to zero.
  Identical to that in [NTCP2]_.

- Hash Function: SHA256
  Standard 32-byte hash, already used extensively in I2P.


Handshake Patterns
------------------

Handshakes use [Noise]_ handshake patterns.

The following letter mapping is used:

- e = one-time ephemeral key
- s = static key
- p = message payload

The build request is identical to the Noise N pattern.
This is also identical to the first (Session Request) message in the XK pattern used in [NTCP2]_.


.. raw:: html

  {% highlight lang='dataspec' %}
<- s
  ...
  e es p ->

{% endhighlight %}


Request encryption
-----------------------

Build request records are created by the tunnel creator and asymmetrically encrypted to the individual hop.
This asymmetric encryption of request records is currently ElGamal as defined in [Cryptography]_
and contains a SHA-256 checksum. This design is not forward-secret.

The ECIES design uses the one-way Noise pattern "N" with ECIES-X25519 ephemeral-static DH, with an HKDF, and
ChaCha20/Poly1305 AEAD for forward secrecy, integrity, and authentication.
Alice is the tunnel build requestor. Each hop in the tunnel is a Bob.



Reply encryption
-----------------------

Build reply records are created by the hops creator and symmetrically encrypted to the creator.
This symmetric encryption of ElGamal reply records is AES with a prepended SHA-256 checksum.
and contains a SHA-256 checksum. This design is not forward-secret.

ECIES replies use ChaCha20/Poly1305 AEAD for integrity, and authentication.



Specification
=========================



Build Request Records
-------------------------------------

Encrypted BuildRequestRecords are 528 bytes for both ElGamal and ECIES, for compatibility.




Request Record Unencrypted
```````````````````````````````````````

This is the specification of the tunnel BuildRequestRecord for ECIES-X25519 routers.
Summary of changes:

- Remove unused 32-byte router hash
- Change request time from hours to minutes
- Add expiration field for future variable tunnel time
- Add more space for flags
- Add Mapping for additional build options
- AES-256 reply key and IV are not used for the hop's own reply record
- Unencrypted record is longer because there is less encryption overhead


The request record does not contain any ChaCha reply keys.
Those keys are derived from a KDF. See below.

All fields are big-endian.

Unencrypted size: 464 bytes

.. raw:: html

  {% highlight lang='dataspec' %}

bytes     0-3: tunnel ID to receive messages as, nonzero
  bytes     4-7: next tunnel ID, nonzero
  bytes    8-39: next router identity hash
  bytes   40-71: AES-256 tunnel layer key
  bytes  72-103: AES-256 tunnel IV key
  bytes 104-135: AES-256 reply key
  bytes 136-151: AES-256 reply IV
  byte      152: flags
  bytes 153-155: more flags, unused, set to 0 for compatibility
  bytes 156-159: request time (in minutes since the epoch, rounded down)
  bytes 160-163: request expiration (in seconds since creation)
  bytes 164-167: next message ID
  bytes   168-x: tunnel build options (Mapping)
  bytes     x-x: other data as implied by flags or options
  bytes   x-463: random padding

{% endhighlight %}

The flags field is the same as defined in [Tunnel-Creation]_ and contains the following::

 Bit order: 76543210 (bit 7 is MSB)
 bit 7: if set, allow messages from anyone
 bit 6: if set, allow messages to anyone, and send the reply to the
        specified next hop in a Tunnel Build Reply Message
 bits 5-0: Undefined, must set to 0 for compatibility with future options

Bit 7 indicates that the hop will be an inbound gateway (IBGW).  Bit 6
indicates that the hop will be an outbound endpoint (OBEP).  If neither bit is
set, the hop will be an intermediate participant.  Both cannot be set at once.

The request exipration is for future variable tunnel duration.
For now, the only supported value is 600 (10 minutes).

The tunnel build options is a Mapping structure as defined in [Common]_.
This is for future use. No options are currently defined.
If the Mapping structure is empty, this is two bytes 0x00 0x00.
The maximum size of the Mapping (including the length field) is 296 bytes,
and the maximum value of the Mapping length field is 294.



Request Record Encrypted
`````````````````````````````````````

All fields are big-endian except for the ephemeral public key which is little-endian.

Encrypted size: 528 bytes

.. raw:: html

  {% highlight lang='dataspec' %}

bytes    0-15: Hop's truncated identity hash
  bytes   16-47: Sender's ephemeral X25519 public key
  bytes  48-511: ChaCha20 encrypted BuildRequestRecord
  bytes 512-527: Poly1305 MAC

{% endhighlight %}



Build Reply Records
-------------------------------------

Encrypted BuildReplyRecords are 528 bytes for both ElGamal and ECIES, for compatibility.


Reply Record Unencrypted
`````````````````````````````````````
This is the specification of the tunnel BuildRequestRecord for ECIES-X25519 routers.
Summary of changes:

- Add Mapping for build reply options
- Unencrypted record is longer because there is less encryption overhead

ECIES replies are encrypted with ChaCha20/Poly1305.

All fields are big-endian.

Unencrypted size: 512 bytes

.. raw:: html

  {% highlight lang='dataspec' %}

bytes    0-x: Tunnel Build Reply Options (Mapping)
  bytes    x-x: other data as implied by options
  bytes  x-510: Random padding
  byte     511: Reply byte

{% endhighlight %}

The tunnel build reply options is a Mapping structure as defined in [Common]_.
This is for future use. No options are currently defined.
If the Mapping structure is empty, this is two bytes 0x00 0x00.
The maximum size of the Mapping (including the length field) is 511 bytes,
and the maximum value of the Mapping length field is 509.

The reply byte is one of the following values
as defined in [Tunnel-Creation]_ to avoid fingerprinting:

- 0x00 (accept)
- 30 (TUNNEL_REJECT_BANDWIDTH)


Reply Record Encrypted
```````````````````````````````````

Encrypted size: 528 bytes

.. raw:: html

  {% highlight lang='dataspec' %}

bytes   0-511: ChaCha20 encrypted BuildReplyRecord
  bytes 512-527: Poly1305 MAC

{% endhighlight %}

After full transition to ECIES records, ranged padding rules are the same as for request records.


Symmetric Encryption of Records
--------------------------------------------------------

Mixed tunnels are allowed, and necessary, for the transition from ElGamal to ECIES.
During the transitionary period, an increasing number of routers will be keyed under ECIES keys.

Symmetric cryptography preprocessing will run in the same way:

- "encryption":

  - cipher run in decryption mode
  - request records preemptively decrypted in preprocessing (concealing encrypted request records)

- "decryption":

  - cipher run in encryption mode
  - request records encrypted (revealing next plaintext request record) by participant hops

- ChaCha20 does not have "modes", so it is simply run three times:

  - once in preprocessing
  - once by the hop
  - once on final reply processing

When mixed tunnels are used, tunnel creators will need to base the symmetric encryption
of BuildRequestRecord on the current and previous hop's encryption type.

Each hop will use its own encryption type for encrypting BuildReplyRecords, and the other
records in the VariableTunnelBuildMessage (VTBM).

On the reply path, the endpoint (sender) will need to undo the [Multiple-Encryption]_, using each hop's reply key.

As a clarifying example, let's look at an outbound tunnel w/ ECIES surrounded by ElGamal:

- Sender (OBGW) -> ElGamal (H1) -> ECIES (H2) -> ElGamal (H3)

All BuildRequestRecords are in their encrypted state (using ElGamal or ECIES).

AES256/CBC cipher, when used, is still used for each record, without chaining across multiple records.

Likewise, ChaCha20 will be used to encrypt each record, not streaming across the entire VTBM.

The request records are preprocessed by the Sender (OBGW):

- H3's record is "encrypted" using:

  - H2's reply key (ChaCha20)
  - H1's reply key (AES256/CBC)

- H2's record is "encrypted" using:

  - H1's reply key (AES256/CBC)

- H1's record goes out without symmetric encryption

Only H2 checks the reply encryption flag, and sees its followed by AES256/CBC.

After being processed by each hop, the records are in a "decrypted" state:

- H3's record is "decrypted" using:

  - H3's reply key (AES256/CBC)

- H2's record is "decrypted" using:

  - H3's reply key (AES256/CBC)
  - H2's reply key (ChaCha20-Poly1305)

- H1's record is "decrypted" using:

  - H3's reply key (AES256/CBC)
  - H2's reply key (ChaCha20)
  - H1's reply key (AES256/CBC)

The tunnel creator, a.k.a. Inbound Endpoint (IBEP), postprocesses the reply:

- H3's record is "encrypted" using:

  - H3's reply key (AES256/CBC)

- H2's record is "encrypted" using:

  - H3's reply key (AES256/CBC)
  - H2's reply key (ChaCha20-Poly1305)

- H1's record is "encrypted" using:

  - H3's reply key (AES256/CBC)
  - H2's reply key (ChaCha20)
  - H1's reply key (AES256/CBC)


Request Record Keys
-----------------------------------------------------------------------

These keys are explicitly included in ElGamal BuildRequestRecords.
For ECIES BuildRequestRecords, the tunnel keys and AES reply keys are included,
but the ChaCha reply keys are derived from the DH exchange.
See [Prop156]_ for details of the router static ECIES keys.

Below is a description of how to derive the keys previously transmitted in request records.


KDF for Initial ck and h
````````````````````````

This is standard [NOISE]_ for pattern "N" with a standard protocol name.

.. raw:: html

  {% highlight lang='text' %}
This is the "e" message pattern:

  // Define protocol_name.
  Set protocol_name = "Noise_N_25519_ChaChaPoly_SHA256"
  (31 bytes, US-ASCII encoded, no NULL termination).

  // Define Hash h = 32 bytes
  // Pad to 32 bytes. Do NOT hash it, because it is not more than 32 bytes.
  h = protocol_name || 0

  Define ck = 32 byte chaining key. Copy the h data to ck.
  Set chainKey = h

  // MixHash(null prologue)
  h = SHA256(h);

  // up until here, can all be precalculated by all routers.

{% endhighlight %}


KDF for Request Record
````````````````````````

ElGamal tunnel creators generate an ephemeral X25519 keypair for each
ECIES hop in the tunnel, and use scheme above for encrypting their BuildRequestRecord.
ElGamal tunnel creators will use the scheme prior to this spec for encrypting to ElGamal hops.

ECIES tunnel creators will need to encrypt to each of the ElGamal hop's public key using the
scheme defined in [Tunnel-Creation]_. ECIES tunnel creators will use the above scheme for encrypting
to ECIES hops.

This means that tunnel hops will only see encrypted records from their same encryption type.

For ElGamal and ECIES tunnel creators, they will generate unique ephemeral X25519 keypairs
per-hop for encrypting to ECIES hops.

**IMPORTANT**:
Ephemeral keys must be unique per ECIES hop, and per build record.
Failing to use unique keys opens an attack vector for colluding hops to confirm they are in the same tunnel.


.. raw:: html

  {% highlight lang='dataspec' %}

// Each hop's X25519 static keypair (hesk, hepk) from the Router Identity
  hesk = GENERATE_PRIVATE()
  hepk = DERIVE_PUBLIC(hesk)

  // MixHash(hepk)
  // || below means append
  h = SHA256(h || hepk);

  // up until here, can all be precalculated by each router
  // for all incoming build requests

  // Sender generates an X25519 ephemeral keypair per ECIES hop in the VTBM (sesk, sepk)
  sesk = GENERATE_PRIVATE()
  sepk = DERIVE_PUBLIC(sesk)

  // MixHash(sepk)
  h = SHA256(h || sepk);

  End of "e" message pattern.

  This is the "es" message pattern:

  // Noise es
  // Sender performs an X25519 DH with Hop's static public key.
  // Each Hop, finds the record w/ their truncated identity hash,
  // and extracts the Sender's ephemeral key preceding the encrypted record.
  sharedSecret = DH(sesk, hepk) = DH(hesk, sepk)

  // MixKey(DH())
  //[chainKey, k] = MixKey(sharedSecret)
  // ChaChaPoly parameters to encrypt/decrypt
  keydata = HKDF(chainKey, sharedSecret, "", 64)
  // Save for Reply Record KDF
  chainKey = keydata[0:31]

  // AEAD parameters
  k = keydata[32:64]
  n = 0
  plaintext = 464 byte build request record
  ad = h
  ciphertext = ENCRYPT(k, n, plaintext, ad)

  End of "es" message pattern.

  // MixHash(ciphertext)
  // Save for Reply Record KDF
  h = SHA256(h || ciphertext)

{% endhighlight %}

``replyKey``, ``layerKey`` and ``layerIV`` must still be included inside ElGamal records,
and can be generated randomly.



Reply Record Encryption
--------------------------------------

The reply record is ChaCha20/Poly1305 encrypted.

.. raw:: html

  {% highlight lang='dataspec' %}

// AEAD parameters
  k = chainkey from build request
  n = 0
  plaintext = 512 byte build reply record
  ad = h from build request

  ciphertext = ENCRYPT(k, n, plaintext, ad)

{% endhighlight %}



Implementation Notes
=====================

* Older routers do not check the encryption type of the hop and will send ElGamal-encrypted
  records. Some recent routers are buggy and will send various types of malformed records.
  Implementers should detect and reject these records prior to the DH operation
  if possible, to reduce CPU usage.



References
==========

.. [Common]
    {{ spec_url('common-structures') }}

.. [Cryptography]
   {{ spec_url('cryptography') }}

.. [ECIES-X25519]
   {{ spec_url('ecies') }}

.. [I2NP]
   {{ spec_url('i2np') }}

.. [NOISE]
    https://noiseprotocol.org/noise.html

.. [NTCP2]
   {{ spec_url('ntcp2') }}

.. [Prop119]
   {{ proposal_url('119') }}

.. [Prop143]
   {{ proposal_url('143') }}

.. [Prop152]
    {{ proposal_url('152') }}

.. [Prop153]
    {{ proposal_url('153') }}

.. [Prop156]
    {{ proposal_url('156') }}

.. [Prop157]
    {{ proposal_url('157') }}

.. [Tunnel-Creation]
   {{ spec_url('tunnel-creation') }}

.. [Multiple-Encryption]
   https://en.wikipedia.org/wiki/Multiple_encryption

.. [RFC-7539]
   https://tools.ietf.org/html/rfc7539

.. [RFC-7748]
   https://tools.ietf.org/html/rfc7748



