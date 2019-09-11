=============
ECIES Tunnels
=============

.. meta::
    :author: chisana
    :created: 2019-07-04
    :thread: http://zzz.i2p/topics/2737
    :lastupdated: 2019-09-11
    :status: Open

.. contents::

Overview
========

This document is a specification proposal for changes to Tunnel encryption and message processing
using crypto primitives introduced by [ECIES-X25519]_.

For the purposes of transitioning the network from ElGamal + AES256 to ECIES + ChaCha20,
tunnels with mixed ElGamal and ECIES routers are necessary.

Specifications for how to handle mixed tunnel hops are provided.

No changes will be made to the format, processing, or encryption of ElGamal hops.

ElGamal tunnel creators will need to create ephemeral X25519 keypairs per-hop, and
follow this spec for creating tunnels containing ECIES hops.

This proposal specifies changes needed for ECIES-X25519 Tunnel Building.

Cryptographic Primitives
------------------------

- ChaCha20(msg, nonce, key) - as in [RFC-7539]_
- ChaCha20Poly1305(msg, nonce, AD, key) - as in [NTCP2]_ and [ECIES-X25519]_
- X25519(privateKey, publicKey) - as in [NTCP2]_ and [ECIES-X25519]_
- HKDF(rootKey, sharedSecret, CONTEXT, keylen) - as in [NTCP2]_ and [ECIES-X25519]_

ECIES for Tunnel Building
=========================

Goals
-----

Replace ElGamal + AES256/CBC with ECIES primitives for tunnel BuildRequestRecords and BuildReplyRecords.

Tunnel Request Records for ECIES Hops
-------------------------------------

Request Record Spec Unencrypted (ElGamal)
`````````````````````````````````````````

.. raw:: html

  {% highlight lang='dataspec' %}

bytes     0-3: tunnel ID to receive messages as, nonzero
  bytes    4-35: local router identity hash
  bytes   36-39: next tunnel ID, nonzero
  bytes   40-71: next router identity hash
  bytes  72-103: AES-256 tunnel layer key
  bytes 104-135: AES-256 tunnel IV key
  bytes 136-167: AES-256 reply key
  bytes 168-183: AES-256 reply IV
  byte      184: flags
  bytes 185-188: request time (in hours since the epoch, rounded down)
  bytes 189-192: next message ID
  bytes 193-221: uninterpreted / random padding
  bytes 222-253: Sha256 of the preceding data

{% endhighlight %}

Request Record Spec Unencrypted (ECIES)
```````````````````````````````````````

.. raw:: html

  {% highlight lang='dataspec' %}

bytes     0-3: tunnel ID to receive messages as, nonzero
  bytes    4-35: local router identity hash
  bytes   36-39: next tunnel ID, nonzero
  bytes   40-71: next router identity hash
  byte       72: flags
  bytes   73-76: request time (in minutes since the epoch, rounded down)
  bytes   77-80: request expiration (in minutes since creation, rounded down)
  bytes   81-84: next message ID
  bytes  85-463: tunnel build options / random padding

{% endhighlight %}

The tunnel build options block will be defined by [Tunnel-Build-Options]_, but may be
defined within this spec, TBD.

Request Record Spec Encrypted (ECIES)
`````````````````````````````````````

.. raw:: html

  {% highlight lang='dataspec' %}

bytes    0-15: Hop's truncated identity hash
  bytes   16-47: Sender's ephemeral public key
  bytes  48-511: ChaChaPoly AEAD encrypted BuildRequestRecord
  bytes 512-527: Poly1305 MAC

{% endhighlight %}

After full transition to ECIES records, random padding can be a range if variable sized records
are supported, TBD.

Ranged random padding will be formatted using the Padding block structure from [ECIES-X25519]_ and [NTCP2]_.

Tunnel Reply Records for ECIES
------------------------------

Reply Record Spec Unencrypted (ECIES)
`````````````````````````````````````

.. raw:: html

  {% highlight lang='dataspec' %}

bytes  0-510: Tunnel Build Options / Random padding
  bytes    511: Reply byte

{% endhighlight %}

For options formatting refer to the [Tunnel-Build-Options]_ spec.

Reply flags for ECIES reply records should use the following values to avoid fingerprinting:

- 0x00 (accept)
- 30 (TUNNEL_REJECT_BANDWIDTH)

Reply Record Spec Encrypted (ECIES)
```````````````````````````````````

.. raw:: html

  {% highlight lang='dataspec' %}

bytes     0-511: ChaChaPoly AEAD encrypted BuildReplyRecord
  bytes 512-527: Poly1305 MAC

{% endhighlight %}

After full transition to ECIES records, ranged padding rules are the same as for request records.

Symmetric Encryption of Asymmetrically Encrypted Records
--------------------------------------------------------

Mixed tunnels are allowed, and necessary, for full network transition from ElGamal to ECIES.
During the transitionary period, a statistically increasing number of routers will be keyed under ECIES keys.

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

Each hop will use it's own encryption type for encrypting BuildReplyRecords, and the other
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

Request Record Key, Reply Key, Tunnel Layer Key, and IV Key KDF (ECIES)
-----------------------------------------------------------------------

The ``recordKey`` takes the place of the product of the ElGamal exchange. It is used
to AEAD encrypt request records for ECIES hops.

Below is a description of how to derive the keys previously transmitted in request records.

.. raw:: html

  {% highlight lang='dataspec' %}

// Sender generates an X25519 ephemeral keypair per ECIES hop in the VTBM (sesk, sepk)
  sesk = GENERATE_PRIVATE()
  sepk = DERIVE_PUBLIC(sesk)

  // Each hop's X25519 static keypair (hesk, hepk), generated for NTCP2 RouterInfos and LeaseSet2s
  hesk = GENERATE_PRIVATE()
  hepk = DERIVE_PUBLIC(hesk)

  // Sender performs an X25519 DH with Hop's static public key.
  // Each Hop, finds the record w/ their truncated identity hash,
  // and extracts the Sender's ephemeral key preceding the encrypted record.
  sharedSecret = DH(sesk, hepk) = DH(hesk, sepk)

  // Derive a root key from the Sha256 of Sender's ephemeral key and Hop's full identity hash
  rootKey = Sha256(sepk || hop_ident_hash)

  keydata = HKDF(rootKey, sharedSecret, "RequestReplyGener", 96)
  rootKey = keydata[0:31]  // update the root key
  recordKey = keydata[32:63]  // AEAD key for Request Record encryption
  replyKey = keydata[64:95]  // Hop reply key

  // If AES layer encryption is used
  keydata = HKDF(rootKey, sharedSecret, "TunnelLayerRando", 80)
  layerKey = keydata[0:31]  // Tunnel layer key
  randKey = keydata[32:63]  // Tunnel randomization key
  replyIV = keydata[64:79]  // Reply record IV

  // If ChaCha layer encryption is used
  keydata = HKDF(rootKey, sharedSecret, "TunnelLayerRando", 96)
  layerKey = keydata[0:31]  // Tunnel layer key
  randKey = keydata[32:63]  // Tunnel randomization key
  sendKey = keydata[64:95]  // AEAD send key
{% endhighlight %}

``replyKey``, ``layerKey`` and ``randKey`` must still be included inside ElGamal records,
and can be generated randomly. For ElGamal, the ``recordKey`` is not needed, since the
tunnel creator can directly encrypt to an ElGamal hop's public key.

Keys are omitted from ECIES records (since they can be derived at the hop).

BuildRequestRecord Encryption for ECIES Hops
--------------------------------------------

.. raw:: html

  {% highlight lang='dataspec' %}

// See record key KDF for key generation
  // Repeat for each ECIES hop record in the VTBM
  (ciphertext, mac) = ChaCha20-Poly1305(msg = unencrypted record, nonce = 0, AD = Sha256(hop's recordKey), key = hop's recordKey)
  encryptedRecord = ciphertext || MAC

  For subsequent records past the initial hop, pre-emptively decrypt for each preceding hop in the tunnel

  // If the preceding hop is ECIES:
  nonce = one + number of records + zero-indexed order of record in the VariableTunnelBuildMessage
  key = replyKey of preceding hop
  symCiphertext = ChaCha20(msg = encryptedRecord, nonce, key)

  // If the preceding hop is ElGamal:
  IV = reply IV of preceding hop
  key = reply key of preceding hop
  symCiphertext = AES256/CBC-Decrypt(msg = encryptedRecord, IV, key) 

{% endhighlight %}

Request Record Encryption from ElGamal + ECIES Tunnel Creators
--------------------------------------------------------------

ElGamal tunnel creators will need to generate an ephemeral X25519 keypair for each
ECIES hop in the tunnel, and use scheme above for encrypting their BuildRequestRecord.
ElGamal tunnel creators will use the scheme prior to this spec for encrypting to ElGamal hops.

ECIES tunnel creators will need to encrypt to the ElGamal hop's public key using the
scheme prior to this spec. ECIES tunnel creators will use the above scheme for encrypting
to ECIES hops.

This means that tunnel hops will only see encrypted records from their same encryption type.

For ElGamal and ECIES tunnel creators, they will generate unique ephemeral X25519 keypairs
per-hop for encrypting to ECIES hops.

Ephemeral keys must be unique per ECIES hop, and per build record.

**IMPORTANT**: Failing to use unique keys opens an attack vector for colluding hops to confirm they are in the same tunnel.

.. raw:: html

  {% highlight lang='dataspec' %}

// See reply key KDF for key generation
  // Encrypting an ECIES hop request record
  AD = Sha256(hop static key || hop Identity hash)
  (ciphertext, MAC) = ChaCha20-Poly1305(msg = BuildRequestRecord, nonce = 0, AD, key = hop's recordKey)

  // Encrypting an ElGamal hop request record
  ciphertext = ElGamal-Encrypt(msg = BuildRequestRecord, key = hop's ElGamal public key)

{% endhighlight %}

Reply Record Encryption for ECIES Hops
--------------------------------------

The nonces must be unique per ChaCha20/ChaCha20-Poly1305 invocation using the same key.

See [RFC-7539-S4]_ Security Considerations for more information.

.. raw:: html

  {% highlight lang='dataspec' %}

// See reply key KDF for key generation
  msg = reply byte || build options || random padding
  (ciphertext, MAC) = ChaCha20-Poly1305(msg, nonce = 0, AD = Sha256(replyKey), key = replyKey)

  // Other request/reply record encryption
  // Use a unique nonce per-record
  nonce = one + number of records + zero-indexed order of record in the VariableTunnelBuildMessage
  symCiphertext = ChaCha20(msg = multiple encrypted record, nonce, key = replyKey)

{% endhighlight %}

While mixed tunnels are used, reply records are the same size, though the format is different.

After full transition to ECIES, random padding can be a range of included padding.

When ranged padding is used, random padding will be formatted using the Padding block structure from [ECIES-X25519]_ and [NTCP2]_.

For symmetric encryption by other hops, it's necessary to know full record length (w/ padding) without asymmetric decryption.

When/if records become variable-length, it may become necessary to include an unencrypted Data block header before each record, TBD.

BuildReplyRecord may or may not need to match BuildRequestRecord length if both are preceded by Data block header, TBD.

Reply Record Encryption for ElGamal Hops
----------------------------------------

There are no changes for how ElGamal hops encrypt their replies.

Security Analysis for ECIES + ChaCha20 Tunnel Build Encryption
--------------------------------------------------------------

ElGamal does not provide forward-secrecy for Tunnel Build Messages.

AES256/CBC is in slightly better standing, only being vulnerable to a theoretical weakening from a
known plaintext `biclique` attack.

The only known practical attack against AES256/CBC is a padding oracle attack, when the IV is known to the attacker.

An attacker would need to break the next hop's ElGamal encryption to gain the AES256/CBC key info (reply key and IV).

ElGamal is significantly more CPU-intensive than ECIES, leading to potential resource exhaustion.

ECIES, used with new ephemeral keys per-BuildRequestRecord or VariableTunnelBuildMessage, provides forward-secrecy.

ChaCha20Poly1305 provides AEAD encryption, allowing the recipient to verify message integrity before attempting decryption.

Tunnel Message Overhead for ECIES
=================================

Wrapped I2NP message overhead:

- I2NP Block header: 3 (block type + size) + 9 (I2NP message header) = 12
- New Session Message:

  - 25 (min payload len) + 16 (MAC) = 41
  - 32 (one-time key) + 40 (ephemeral section) + 16 (MAC) + 41 (min payload) = 129 unbound
  - 88 (unbound) + 32 (static section) + 16 (MAC) + 41 (min payload) = 177 bound

- Existing Message: 8 (session tag) + payload len + 16 (MAC) = 24 + payload len

- New session:

  - 12 (I2NP) + 129 (unbound) = 141 + payload
  - 12 (I2NP + 177 (bound) = 189 + payload

- Existing Session: 12 (I2NP) + 24 = 36 + payload
- Build Request Record: 528 (ElGamal, mixed tunnels)
- Build Request Reply: 528 (ElGamal, mixed tunnels)

Tunnel message overhead:

Wrapped I2NP message overhead:

- I2NP Block header: 3 (block type + size) + 9 (I2NP message header) = 12
- New Session Message:

  - 25 (min payload len) + 16 (MAC) = 41
  - 32 (one-time key) + 40 (ephemeral section) + 16 (MAC) + 41 (min payload) = 129 unbound
  - 88 (unbound) + 32 (static section) + 16 (MAC) + 41 (min payload) = 177 bound

- Existing Message: 8 (session tag) + payload len + 16 (MAC) = 24 + payload len

- New session:

  - 12 (I2NP) + 129 (unbound) = 141 + payload
  - 12 (I2NP + 177 (bound) = 189 + payload

- Existing Session: 12 (I2NP) + 24 = 36 + payload
- Build Request Record: 528 (ElGamal, mixed tunnels)
- Build Request Reply: 528 (ElGamal, mixed tunnels)

Tunnel message overhead:

Tunnel layer keys, IV/nonce keys, and reply keys no longer need to be transmitted in ECIES BuildRequest Records.
Unused space claimed by build options, random padding, and the trailing 16 byte Poly1305 MAC.

ECIES session messages will be wrapped in I2NP Data messages, surrounded by a Garlic Clove,
and fragmented in Tunnel Data messages like any other message.

Dropped fragments will result in AEAD decryption failure (fails MAC verification),
resulting in the entire message being dropped.

References
==========

.. [ECIES-X25519]
   {{ proposal_url('144') }}

.. [Tunnel-Build-Options]
   {{ proposal_url('143') }}

.. [NTCP2]
   https://geti2p.net/spec/ntcp2

.. [Tunnel-Implementation]
   https://geti2p.net/en/docs/tunnels/implementation

.. [Multiple-Encryption]
   https://en.wikipedia.org/wiki/Multiple_encryption

.. [RFC-7539]
   https://tools.ietf.org/html/rfc7539

.. [RFC-7539-S4]
   https://tools.ietf.org/html/rfc7539#section-4
