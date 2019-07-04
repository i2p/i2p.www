=======================================
Tunnels under ECIES-X25519-AEAD-Ratchet
=======================================

.. meta::
    :author: chisana
    :created: 2019-07-04
    :thread: http://zzz.i2p/topics/2737
    :lastupdated: 2019-07-04
    :status: Open

.. contents::

Overview
========

This document is a specification proposal for changes to Tunnel encryption and message processing
using crypto primitives introduced by [Prop144]_: ECIES-X25519-AEAD-Ratchet.

For the purposes of transitioning the network from ElGamal + AES256 to ECIES + ChaCha20,
tunnels with mixed ElGamal and ECIES routers are necessary.

Specifications for how to handle mixed tunnel hops are provided.

No changes will be made to the format, processing, or encryption of ElGamal hops.
All ElGamal routers are treated as though running without changes from this document.

Tunnel Request Records for ECIES Hops
=====================================

Request Record Spec Unencrypted (ElGamal)
-----------------------------------------

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
---------------------------------------

.. raw:: html

  {% highlight lang='dataspec' %}
bytes     0-3: tunnel ID to receive messages as, nonzero
  bytes    4-35: local router identity hash
  bytes   36-39: next tunnel ID, nonzero
  bytes   40-71: next router identity hash
  byte       72: flags
  bytes   73-76: request time (in hours since the epoch, rounded down)
  bytes   77-80: next message ID

{% endhighlight %}

Request Record Spec Encrypted (ECIES)
-------------------------------------

.. raw:: html

  {% highlight lang='dataspec' %}
bytes    0-15: hop's truncated identity hash
  bytes   16-31: sender's ephemeral public key
  bytes  32-112: ChaChaPoly AEAD encrypted build request record
  bytes 113-128: Poly1305 MAC
  bytes 129-527: Random padding

{% endhighlight %}

**IMPORTANT**: The first 129 bytes of ECIES encrypted build request records cannot cross tunnel message fragments (breaks AEAD encryption).

TBD if it is safe for the following random padding to cross tunnel message fragments.

After full transition to ECIES records, bytes 129-527 can be a range of included padding.

When ranged padding is used, first two bytes of padding can be used to indicate padding length.
For symmetric encryption by other hops, it's necessary to know full record length (w/ padding) without asymetric decryption.

Flag Changes for Mixed Tunnels
------------------------------

.. raw:: html

  {% highlight lang='dataspec' %}
Bit order: 76543210 (bit 7 is MSB)
  bit 7: if set, allow messages from anyone
  bit 6: if set, allow messages to anyone, and send the reply to the
         specified next hop in a Tunnel Build Reply Message
  bit 5: if set, ChaCha20 reply encryption selected (ECIES build record),
         also indicates next hop is ECIES
         AES256/CBC (ElGamal) otherwise
  bits 4-0: Undefined, must set to 0 for compatibility with future options

{% endhighlight %}

Tunnel Reply Records for ECIES
==============================

Reply Record Spec Unencrypted (ECIES)
-------------------------------------

.. raw:: html

  {% highlight lang='dataspec' %}
bytes      0: reply byte

{% endhighlight %}

Reply flags for ECIES reply records should use the following values to avoid fingerprinting:

- 0x00 (accept)
- 30 (TUNNEL_REJECT_BANDWIDTH)

Reply Record Spec Encrypted (ECIES)
-----------------------------------

.. raw:: html

  {% highlight lang='dataspec' %}
bytes       0: ChaChaPoly AEAD encrypted build reply record
  bytes    1-16: Poly1305 MAC
  bytes  49-527: Random padding

{% endhighlight %}

**IMPORTANT**: The first 17 bytes of ECIES encrypted build request records cannot cross tunnel message fragments (breaks AEAD encryption).

TBD if it is safe for the following random padding to cross tunnel message fragments.

After full transition to ECIES records, ranged padding rules are the same as for request records.

Symmetric Encryption of Asymmetrically Encrypted Records
========================================================

Mixed tunnels are allowed, and necessary, for full network transition from ElGamal to ECIES.
During the transitionary period, a statistically increasing number of routers will be keyed under ECIES keys.

Symmetric cryptography preprocessing will run in the same way:

- "encryption":
  * cipher run in decryption mode
  * request records preemptively decrypted in preprocessing (concealing encrypted request records)
- "decryption":
  * cipher run in encryption mode
  * request records encrypted (revealing next plaintext request record) by participant hops
- ChaCha20 does not have "modes", so it is simply run three times:
  * once in preprocessing
  * once by the hop
  * once on final reply processing

When mixed routers are hops in the same tunnel, and the current hop is ECIES,
it will check if reply encryption flag is set (indicating ChaCha20).

If the current hop is an ECIES hop, and ChaCha20 reply encryption is selected,
the reply key is used to ChaCha20 "decrypt" its reply and other records.

If the current hop is an ElGamal hop, the reply encryption bit is ignored,
and the reply key is used to AES256/CBC "decrypt" its reply and other records.

This means later hops in the tunnel are preprocessed using a mix of ChaCha20
and AES256/CBC, using the reply key of preceding hops.

On the reply path, the endpoint (sender) will need to undo the multiple
encryption, using each hop's reply key.

Multiple encryption: https://en.wikipedia.org/wiki/Multiple_encryption

As a clarifying example, let's look at an outbound tunnel w/ ECIES surrounded by ElGamal:

- Sender (OBGW) -> ElGamal (H1) -> ECIES (H2) -> ElGamal (H3)

All records are in their encrypted state (using ElGamal or ECIES).

AES256/CBC cipher, when used, is still used for each record, without chaining across multiple records.

The request records are preprocessed by the Sender (OBGW):

- H3's record is "encrypted" using:
  * H2's reply key (AES256/CBC)
  * H1's reply key (AES256/CBC)
- H2's record is "encrypted" using:
  * H1's reply key (AES256/CBC)
- H1's record goes out without symmetric encryption

Only H2 checks the reply encryption flag, and sees its followed by AES256/CBC.

H3 checks the flags, sees it is an OBEP (bit 6 set), and ignores the reply encryption bit.

After being processed by each hop, the records are in a "decrypted" state:

- H3's record is "decrypted" using:
  * H3's reply key (AES256/CBC)
- H2's record is "decrypted" using:
  * H3's reply key (AES256/CBC)
  * H2's reply key (AES256/CBC)
- H1's record is "decrypted" using:
  * H3's reply key (AES256/CBC)
  * H2's reply key (AES256/CBC)
  * H1's reply key (AES256/CBC)

When there are no inbound tunnels at startup, the Sender (IBEP) postprocesses the reply:

- H3's record is "encrypted" using:
  * H3's reply key (AES256/CBC)
- H2's record is "encrypted" using:
  * H3's reply key (AES256/CBC)
  * H2's reply key (AES256/CBC)
- H1's record is "encrypted" using:
  * H3's reply key (AES256/CBC)
  * H2's reply key (AES256/CBC)
  * H1's reply key (AES256/CBC)

If H3 (OBEP) is an ECIES hop, it checks the reply encryption flag for
ChaCha20 (bit 5 set) or AES256/CBC (bit 5 unset).

H2 would also see that the reply encryption flag is set, and "decrypt" its reply
and other records using ChaCha20.

So our example changes to the following hops:

- Sender (OBGW) -> ElGamal (H1) -> ECIES (H2) -> ECIES (H3)

The request records are preprocessed by the Sender (OBGW):

- H3's record is "encrypted" using:
  * H2's reply key (ChaCha20)
  * H1's reply key (AES256/CBC)
- H2's record is "encrypted" using:
  * H1's reply key (AES256/CBC)
- H1's record goes out without symmetric encryption

After being processed by each hop, the records are in a "decrypted" state:

- H3's record is "decrypted" using:
  * H3's reply key (ChaCha20)
- H2's record is "decrypted" using:
  * H3's reply key (ChaCha20)
  * H2's reply key (ChaCha20)
- H1's record is "decrypted" using:
  * H3's reply key (ChaCha20)
  * H2's reply key (ChaCha20)
  * H1's reply key (AES256/CBC)

When there are no inbound tunnels at startup, the Sender (IBEP) postprocesses the reply:

- H3's record is "encrypted" using:
  * H3's reply key (ChaCha20)
- H2's record is "encrypted" using:
  * H3's reply key (ChaCha20)
  * H2's reply key (ChaCha20)
- H1's record is "encrypted" using:
  * H3's reply key (ChaCha20)
  * H2's reply key (ChaCha20)
  * H1's reply key (AES256/CBC)

Request Record Key, Reply Key, Tunnel Layer and IV Key KDF (ECIES)
==================================================================

The `recordKey` takes the place of the product of the ElGamal exchange. It is used
to AEAD encrypt request and reply records for ECIES hops.

Below is a description of how to derive the keys previously transmitted in request records.

.. raw:: html

  {% highlight lang='dataspec' %}
// Sender generates an X25519 ephemeral keypair per VTBM (sesk, sepk)
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
  root_key = Sha256(sepk || hop_ident_hash)

  keydata = HKDF(root_key, sharedSecret, "ECIESRequestRcrd", 96)
  root_key = keydata[0:31]  // update the root key
  recordKey = keydata[32:63]  // AEAD key for Request Record encryption
  replyKey = keydata[64:95]  // Hop reply key

  keydata = HKDF(root_key, sharedSecret, "TunnelLayerIVKey", 64)
  layerKey = keydata[0:31]  // Tunnel layer key
  IVKey = keydata[32:63]  // Tunnel IV key

{% endhighlight %}

`replyKey`, `layerKey` and `IVKey` must still be included inside ElGamal records,
and can be generated randomly. The `recordKey` is just the result of ElGamal multiplication.

Keys are omitted from ECIES records (since they can be derived at the hop).

Request Record Preprocessing for ECIES Hops
-------------------------------------------

.. raw:: html

  {% highlight lang='dataspec' %}
// See record key KDF for key generation
  (ciphertext, mac) = ChaCha20-Poly1305(msg = unencrypted record, nonce = 0, AD = Sha256(recordKey), key = recordKey)

  // For subsequent records past the initial hop
  // nonce = one + zero-indexed order of record in the TunnelBuildMessage
  symCiphertext = ChaCha20(msg = ciphertext || MAC || random padding, nonce, key = replyKey of preceding hop)

{% endhighlight %}

Request Record Encryption from ElGamal Tunnel Creators
------------------------------------------------------

No changes are made for how ElGamal routers preprocess and encrypt request records.

This means ECIES hops will behave like ElGamal hops in ElGamal created tunnels.

For ECIES hops to detect ElGamal tunnel creators, trial-decryption is needed.

It will be necessary to first try decrypting the request record as though it came from an ECIES router.

If trial-decryption fails, attempt decryption as though from an ElGamal router.

If the record includes expected fields (keys + IV, flags, etc, and valid Sha256 of preceding data), ElGamal decryption was succesful.

If ElGamal decryption fails, drop the message without reply, or forwarding to next hop.

Reply Record Encryption for ECIES Hops
--------------------------------------

.. raw:: html

  {% highlight lang='dataspec' %}
// See reply key KDF for key generation
  (ciphertext, MAC) = ChaCha20-Poly1305(msg = reply byte, nonce = 0, AD = Sha256(replyKey), key = replyKey)

  If ChaCha20 reply encryption is set in the request record (flags bit 5 set):

  // Advance the nonce to avoid security issues, see [RFC-7539-S4]_ Security Considerations.
  // nonce = one + zero-indexed order of record in the TunnelBuildMessage
  symCiphertext = ChaCha20(msg = ciphertext || MAC || random padding, nonce, key = replyKey) 

  // Other request/reply record encryption
  // Advance the nonce to avoid security issues, see [RFC-7539-S4]_ Security Considerations.
  // nonce = one + number of records + zero-indexed order of record in the TunnelBuildMessage
  symCiphertext = ChaCha20(msg = multiple encrypted record, nonce, key = replyKey)

  If AES256/CBC reply encryption is set in the request record (flag bit 5 unset):

  // Other request/reply record encryption
  msg = multiple encrypted record
  key = replyKey
  IV = Sha256(replyKey || hop static public key)
  symCiphertext = AES256-CBC-Encrypt(msg, key, IV)

{% endhighlight %}

While mixed tunnels are used, reply records are the same size, though the format is different.

After full transition to ECIES, random padding (bytes 49-527) can be a range of included padding.

When ranged padding is used, first two bytes of padding can be used to indicate padding length.
For symmetric encryption by other hops, it's necessary to know full record length (w/ padding) without asymetric decryption.

Reply Record Encryption for ElGamal Hops
----------------------------------------

There are no changes for how ElGamal hops encrypt their replies.

Established Tunnel Message Processing
=====================================

This section describes changes to:

- Outbound and Inbound Gateway preprocessing + encryption
- Participant encryption + postprocessing
- Outbound and Inbound Endpoint encryption + postprocessing

Changes account for tunnels with mixed routers of non-upgraded-ElGamal and ECIES hops.

For an overview of current tunnel message processing, see the [Tunnel-Implementation]_ spec.

Only changes for ECIES gateways + hops are discussed.

No changes are made for ElGamal routers, meaning ECIES hops will behave
as ElGamal hops in Outbound and Inbound tunnels created by ElGamal routers.

See section on build request records for ECIES hop detection of ElGamal tunnel creators.

Gateway Message Processing
--------------------------

Gateways will fragment and bundle messages in the same way, but must take care when
fragmenting I2NP messages containing AEAD frames.

AEAD frames (including the MAC) must be contained in a single fragment.

This limitation effectively reduces ECIES session messages to the length of a Tunnel Message
payload minus the inner header and wrapping I2NP message header lengths.

TBD if it is safe to fragment a message header from its AEAD frame.

Gateway Encryption
------------------

For mixed tunnels, gateways will still generate an IV for use by ElGamal hops.

For ChaCha20 en/decryption, the IV and tunnel messages are concatenated together.

Inbound tunnels:

- Encrypt the IV and tunnel message(s) using ChaCha20
- Maintain a `tunnelNonce` counter for each set of message(s) received after successful tunnel build
- Destroy tunnel before `tunnelNonce` "rolls over": 2^96 - 1 = 79228162514264337593543950335
  * unlikely to ever occur, given the lifetime of tunnels

.. raw:: html

  {% highlight lang='dataspec' %}
// Gateway generates a random IV
  // Gateway encrypts concatenated IV + preprocessed tunnel messages
  // Increment the nonce for each set of tunnel messages received
  encIV = ChaCha20(msg = IV, nonce = tunnelNonce, key = IVKey)
  encMsg = ChaCha20(msg = tunnel msg(s), nonce = tunnelNonce, key = layerKey)

{% endhighlight %}

Outbound tunnels:

- Iteratively decrypt the IV and tunnel messages based on hop type
  * ECIES hops will encrypt using ChaCha20
  * ElGamal hops will encrypt using AES256/ECB
- Use the same rules for IV and layer nonces as Inbound tunnels

.. raw:: html

  {% highlight lang='dataspec' %}
// Gateway generates a random IV
  // For each hop, decrypt the IV and tunnel message(s) based on hop type
  // Increment the nonce for each set of tunnel message(s) sent
  // For the first hop, the previous decrypted IV will be the randomly generated IV

  // For ECIES hops
  decIV = ChaCha20(msg = prev. decIV, nonce = tunnelNonce, key = hop's IVKey)
  decMsg = ChaCha20(msg = tunnel msg(s), nonce = tunnelNonce, key = hop's layerKey)

  // For ElGamal hops (unchanged)
  decIV = AES256/ECB-Decrypt(msg = prev. decIV, IV = prev. decIV, key = hop's IVKey)
  decMsg = AES256/ECB-Decrypt(msg = tunnel msg(s), IV = decIV, key = hop's layerKey)
  decIV2 = AES256/ECB-Decrypt(msg = decIV, IV = decIV, key = hop's IVKey)

{% endhighlight %}

Participant Processing
----------------------

Participants will track seen messages in the same way, using decaying Bloom filters.

IV double-encryption is no longer necessary for ECIES hops,
since there are no confirmation attacks against ChaCha20.

Use of multiple encryption with ChaCha20 and AES256/ECB also prevents the confirmation attack
against ElGamal hops.

IV double-encryption will still be used for ElGamal hops, since they are considered unchanged.

.. raw:: html

  {% highlight lang='dataspec' %}
// For ECIES hops
  encIV = ChaCha20(msg = received IV, nonce = tunnelNonce, key = IVKey)
  encMsg = ChaCha20(msg = received Msg, nonce = tunnelNonce, key = layerKey)

  // For ElGamal hops (unchanged)
  currentIV = AES256/ECB-Encrypt(msg = received IV, IV = received IV, key = hop's IVKey)
  encMsg = AES256/ECB-Encrypt(msg = tunnel msg(s), IV = currentIV, key = hop's layerKey)
  nextIV = AES256/ECB-Encrypt(msg = currentIV, IV = currentIV, key = hop's IVKey)

{% endhighlight %}

Tunnel Message Overhead for ECIES
=================================

Wrapped I2NP message overhead:

- I2NP Block header: 3 (block type + size) + 9 (I2NP message header) = 12
- New Session Message:
  * 25 (min payload len) + 16 (MAC) = 41
  * 32 (one-time key) + 40 (ephemeral section) + 16 (MAC) + 41 (min payload) = 129 unbound
  * 88 (unbound) + 32 (static section) + 16 (MAC) + 41 (min payload) = 177 bound
- Existing Message: 8 (session tag) + payload len + 16 (MAC) = 24 + payload len

- New session:
  * 12 (I2NP) + 129 (unbound) = 141 + payload
  * 12 (I2NP + 177 (bound) = 189 + payload
- Existing Session: 12 (I2NP) + 24 = 36 + payload
- Build Request Record: 528 (ElGamal, mixed tunnels)
- Build Request Reply: 528 (ElGamal, mixed tunnels)

Tunnel message overhead:

Tunnel IV no longer needed, unused space claimed by trailing 16 byte Poly1305 MAC
Follow-on fragments no longer usable, all messages must fit in a single fragment

- 4 (tunnel ID) + 1 (padding delim) + 4 (checksum) = 9 (header)
- 3 (first, local delivery)
- 35 (first, router delivery)
- 39 (first, tunnel delivery)
- 7 (follow-on)

Number of messages wrapped in a tunnel message with current max (1024 bytes):

- 1024 - 9 (header) =  1015 (max payload length)

Variable Tunnel Build Message:

- For 8 build records, 4 Tunnel Data Messages:
  - 1015 = `39 (tunnel) + 528` + `39 (tunnel) + 445`
  - 1015 = `7 (follow) + 83` + `39 (tunnel) + 528` + `39 (tunnel) + 319`
  - 1015 = `7 (follow) + 209` + `39 (tunnel) + 528` + `39 (tunnel) + 193`
  - 1015 = `7 (follow) + 335` + `39 (tunnel) + 528`

- For 4-5 build records, 3 Tunnel Data Messages:
  - 1015 = `39 (tunnel) + 528` + `39 (tunnel) + 445`
  - 1015 = `7 (follow) + 83` + `39 (tunnel) + 528` + `39 (tunnel) + 319`
  - 1015 = `7 (follow) + 209` + `39 (tunnel) + 528`

- For 2-3 build records, 2 Tunnel Data Messages:
  - 1015 = `39 (tunnel) + 528` + `39 (tunnel) + 445`
  - 1015 = `7 (follow) + 83` + `39 (tunnel) + 528`

Even with fragment messages on the edges, all tunnel messages safely contain the ECIES build
request and reply record AEAD frames.

Additional payloads calculated on average, distributed evenly per message.
Can adjust number of messages to fit bigger payloads per message, these are just examples.

Unbound New Session Message (min payload + addtl. payload):

- 1015 / (3 (local) + 141 + payload) = 7 msgs + 6 bytes per addtl. payload
- 1015 / (35 (router) + 141 + payload) = 5 msgs + 134 bytes per addtl. payload
- 1015 / (39 (tunnel) + 141 + payload) = 5 msgs + 115 bytes per addtl. payload

Bound New Session Message (min payload + addtl. payload):

- 1015 / (3 (local) + 189 + payload) = 5 msgs + 54 bytes per addtl. payload
- 1015 / (35 (router) + 189 + payload) = 4 msgs + 119 bytes per addtl. payload
- 1015 / (39 (tunnel) + 189 + payload) = 4 msgs + 103 bytes per addtl. payload

Existing Session Message (+ payload len):

- 1015 / (3 (local) + 36 + payload) = 17 msgs + 20 bytes per payload
- 1015 / (35 (router) + 36 + payload) = 14 msgs + 21 bytes per payload
- 1015 / (39 (tunnel) + 36 + payload) = 13 msgs + 39 bytes per payload

References
==========

.. [Prop144]
   {{ proposal_url('144') }}

.. [Tunnel-Implementation]
   https://geti2p.net/en/docs/tunnels/implementation

.. [RFC-7539-S4]
   https://tools.ietf.org/html/rfc7539#section-4
