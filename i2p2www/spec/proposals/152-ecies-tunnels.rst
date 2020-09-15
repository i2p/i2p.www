=============
ECIES Tunnels
=============

.. meta::
    :author: chisana, zzz, orignal
    :created: 2019-07-04
    :thread: http://zzz.i2p/topics/2737
    :lastupdated: 2020-09-15
    :status: Open
    :target: 0.9.51

.. contents::

Overview
========

This document proposes changes to Tunnel Build message encryption
using crypto primitives introduced by [ECIES-X25519]_.
It is a portion of the overall proposal
[Prop156]_ for converting routers from ElGamal to ECIES-X25519 keys.

For the purposes of transitioning the network from ElGamal + AES256 to ECIES + ChaCha20,
tunnels with mixed ElGamal and ECIES routers are necessary.
Specifications for handling mixed tunnel hops are provided.
No changes will be made to the format, processing, or encryption of ElGamal hops.

ElGamal tunnel creators will need create ephemeral X25519 keypairs per-hop, and
follow this spec for creating tunnels containing ECIES hops.

This proposal specifies changes needed for ECIES-X25519 Tunnel Building.
For an overview of all changes required for ECIES routers, see proposal 156 [Prop156]_.



Cryptographic Primitives
------------------------

No new cryptographic primitives are introduced. The primitives required to implement this proposal are:

- AES-256-CBC as in [Cryptography]_
- STREAM ChaCha20/Poly1305 functions:
  ENCRYPT(k, n, plaintext, ad) and DECRYPT(k, n, ciphertext, ad) - as in [NTCP2]_ [ECIES-X25519]_ and [RFC-7539]_
- X25519 DH functions - as in [NTCP2]_ and [ECIES-X25519]_
- HKDF(salt, ikm, info, n) - as in [NTCP2]_ and [ECIES-X25519]_

Other Noise functions defined elsewhere:

- MixHash(d) - as in [NTCP2]_ and [ECIES-X25519]_
- MixKey(d) - as in [NTCP2]_ and [ECIES-X25519]_


Goals
-----

- Increase speed of crypto operations
- Replace ElGamal + AES256/CBC with ECIES primitives for tunnel BuildRequestRecords and BuildReplyRecords.
- No change to size of encrypted BuildRequestRecords and BuildReplyRecords (528 bytes) for compatibility
- No new I2NP messages
- Maintain encrypted build record size for compatibility
- Add forward secrecy for Tunnel Build Messages.
- Add authenticated encryption
- Detect hops reordering BuildRequestRecords
- Increase resolution of timestamp so that Bloom filter size may be reduced
- Add field for tunnel expiration so that varying tunnel lifetimes will be possible (all-ECIES tunnels only)
- Add extensible options field for future features
- Reuse existing cryptographic primitives
- Improve tunnel build message security where possible while maintaining compatibility
- Support tunnels with mixed ElGamal/ECIES peers
- Improve defenses against "tagging" attacks on build messages
- Hops do not need to know the encryption type of the next hop before processing the build message,
  as they may not have the next hop's RI at that time
- Maximize compatibility with current network
- No change to tunnel build AES request/reply encryption for ElGamal routers
- No change to tunnel AES "layer" encryption, for that see [Prop153]_
- Continue to support both 8-record TBM/TBRM and variable-size VTBM/VTBRM
- Do not require "flag day" upgrade to entire network


Non-Goals
-----------

- Complete redesign of tunnel build messages requiring a "flag day".
- Shrinking tunnel build messages (requires all-ECIES hops and a new proposal)
- Use of tunnel build options as defined in [Prop143]_, only required for small messages
- Bidirectional tunnels - for that see [Prop119]_


Threat Model
==============

Design Goals
-------------

- No hops are able to determine the originator of the tunnel.

- Middle hops must not be able to determine the direction of the tunnel
  or their position in the tunnel.

- No hops can read any contents of other request or reply records, except
  for truncated router hash and ephemeral key for next hop

- No member of reply tunnel for outbound build can read any reply records.

- No member of outbound tunnel for inbound build can read any request records,
  except that OBEP can see truncated router hash and ephemeral key for IBGW




Tagging Attacks
----------------

A major goal of the tunnel building design is to make it harder
for colluding routers X and Y to know that they are in a single tunnel.
If router X is at hop m and router Y is at hop m+1, they obviously will know.
But if router X is at hop m and router Y is at hop m+n for n>1, this should be much harder.

Tagging attacks are where middle-hop router X alters the tunnel build message in such a way that
router Y can detect the alteration when the build message gets there.
The goal is for any altered message is dropped by a router between X and Y before it gets to router Y.
For modifications that are not dropped before router Y, the tunnel creator should detect the corruption in the reply
and discard the tunnel.

Possible attacks:

- Alter a build record
- Replace a build record
- Add or remove a build record
- Reorder the build records





TODO: Does the current design prevent all these attacks?






Design
======

Noise Protocol Framework
------------------------

This proposal provides the requirements based on the Noise Protocol Framework
[NOISE]_ (Revision 34, 2018-07-11).
In Noise parlance, Alice is the initiator, and Bob is the responder.

This proposal is based on the Noise protocol Noise_N_25519_ChaChaPoly_SHA256.
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


Additions to the Framework
``````````````````````````

None.


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

The new design will use the one-way Noise pattern "N" with ECIES-X25519 ephemeral-static DH, with an HKDF, and
ChaCha20/Poly1305 AEAD for forward secrecy, integrity, and authentication.
Alice is the tunnel build requestor. Each hop in the tunnel is a Bob.


(Payload Security Properties)

.. raw:: html

  {% highlight lang='text' %}
N:                      Authentication   Confidentiality
    -> e, es                  0                2

    Authentication: None (0).
    This payload may have been sent by any party, including an active attacker.

    Confidentiality: 2.
    Encryption to a known recipient, forward secrecy for sender compromise
    only, vulnerable to replay.  This payload is encrypted based only on DHs
    involving the recipient's static key pair.  If the recipient's static
    private key is compromised, even at a later date, this payload can be
    decrypted.  This message can also be replayed, since there's no ephemeral
    contribution from the recipient.

    "e": Alice generates a new ephemeral key pair and stores it in the e
         variable, writes the ephemeral public key as cleartext into the
         message buffer, and hashes the public key along with the old h to
         derive a new h.

    "es": A DH is performed between the Alice's ephemeral key pair and the
          Bob's static key pair.  The result is hashed along with the old ck to
          derive a new ck and k, and n is set to zero.


{% endhighlight %}



Reply encryption
-----------------------

Build reply records are created by the hops creator and symmetrically encrypted to the creator.
This symmetric encryption of reply records is currently AES with a prepended SHA-256 checksum.
and contains a SHA-256 checksum. This design is not forward-secret.

The new design will use ChaCha20/Poly1305 AEAD for integrity, and authentication.


Justification
-----------------

The ephemeral public key in the request does not need to be obfuscated with AES
or Elligator2. The previous hop is the only one that can see it, and that hop
knows that the next hop is ECIES.

Reply records do not need full asymmetric encryption with another DH.



Specification
=========================



Build Request Records
-------------------------------------

Encrypted BuildRequestRecords are 528 bytes for both ElGamal and ECIES, for compatibility.


Request Record Unencrypted (ElGamal)
`````````````````````````````````````````

For reference, this is the current specification of the tunnel BuildRequestRecord for ElGamal routers, taken from [I2NP]_.
The unencrypted data is prepended with a nonzero byte and the SHA-256 hash of the data before encryption,
as defined in [Cryptography]_.

All fields are big-endian.

Unencrypted size: 222 bytes

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

{% endhighlight %}


Request Record Encrypted (ElGamal)
`````````````````````````````````````

For reference, this is the current specification of the tunnel BuildRequestRecord for ElGamal routers, taken from [I2NP]_.

Encrypted size: 528 bytes

.. raw:: html

  {% highlight lang='dataspec' %}

bytes    0-15: Hop's truncated identity hash
  bytes  16-528: ElGamal encrypted BuildRequestRecord

{% endhighlight %}




Request Record Unencrypted (ECIES)
```````````````````````````````````````

This is the proposed specification of the tunnel BuildRequestRecord for ECIES-X25519 routers.
Summary of changes:

- Remove unused 32-byte router hash
- Remove reply IV
- Change request time from hours to minutes
- Add expiration field for future variable tunnel time
- Add more space for flags
- Add Mapping for additional build options
- AES-256 reply key and IV are not used for the hop's own reply record
- Unencrypted record is longer because there is less encryption overhead


The request record does not contain any explicit tunnel or reply keys.
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

The tunnel build options is a Mapping structure as defined in [Common]_.
This is for future use. No options are currently defined.
If the Mapping structure is empty, this is two bytes 0x00 0x00.



Request Record Encrypted (ECIES)
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


Reply Record Unencrypted (ElGamal)
`````````````````````````````````````
ElGamal replies are encrypted with AES.

All fields are big-endian.

Unencrypted size: 528 bytes

.. raw:: html

  {% highlight lang='dataspec' %}

bytes 0-31   :: SHA-256 Hash of bytes 32-527
  bytes 32-526 :: random data
  byte  527    :: reply

  total length: 528

{% endhighlight %}


Reply Record Unencrypted (ECIES)
`````````````````````````````````````
This is the proposed specification of the tunnel BuildRequestRecord for ECIES-X25519 routers.
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
  bytes    511: Reply byte

{% endhighlight %}

The tunnel build reply options is a Mapping structure as defined in [Common]_.
This is for future use. No options are currently defined.
If the Mapping structure is empty, this is two bytes 0x00 0x00.

The reply byte is one of the following values
as defined in [Tunnel-Creation]_ to avoid fingerprinting:

- 0x00 (accept)
- 30 (TUNNEL_REJECT_BANDWIDTH)


Reply Record Encrypted (ECIES)
```````````````````````````````````

Encrypted size: 528 bytes

.. raw:: html

  {% highlight lang='dataspec' %}

bytes     0-511: ChaCha20 encrypted BuildReplyRecord
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


Request Record Keys (ECIES)
-----------------------------------------------------------------------

These keys are explicitly included in ElGamal BuildRequestRecords.
For ECIES BuildRequestRecords, these keys are derived from the DH exchange.
See [Prop156]_ for details of the router static ECIES keys.

Below is a description of how to derive the keys previously transmitted in request records.


KDF for Initial h
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


Request Record Encryption (ElGamal)
----------------------------------------

As defined in [Tunnel-Creation]_.
There are no changes to encryption for ElGamal hops.




Reply Record Encryption (ECIES)
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



Reply Record Encryption (ElGamal)
----------------------------------------

As defined in [Tunnel-Creation]_.
There are no changes to encryption for ElGamal hops.



Security Analysis
--------------------------------------------------------------

ElGamal does not provide forward secrecy for Tunnel Build Messages.

AES256/CBC is in slightly better standing, only being vulnerable to a theoretical weakening from a
known plaintext `biclique` attack.

The only known practical attack against AES256/CBC is a padding oracle attack, when the IV is known to the attacker.

An attacker would need to break the next hop's ElGamal encryption to gain the AES256/CBC key info (reply key and IV).

ElGamal is significantly more CPU-intensive than ECIES, leading to potential resource exhaustion.

ECIES, used with new ephemeral keys per-BuildRequestRecord or VariableTunnelBuildMessage, provides forward-secrecy.

ChaCha20Poly1305 provides AEAD encryption, allowing the recipient to verify message integrity before attempting decryption.


Justification
=============

This design maximizes reuse of existing cryptographic primitives, protocols, and code.
This design minimizes risk.




Implementation Notes
=====================




Issues
======

* Is an HKDF required for the keys, what's the advantage of doing that vs.
  just including them in the build record as before?

* Make KDFs be similar to those in Noise (NTCP2) and Ratchet

* HKDF output no more than 64 bytes preferred

* In the current Java implementation, the full router hash field in the build
  request record at bytes 4-35 is not checked and does not appear to be necessary.

* Each record is CBC encrypted with the same AES reply key and IV, as with the current design.
  Is this a problem? Can it be fixed?

* In the current Java implementation, the originator leaves one record empty
  for itself. Thus a message of n records can only build a tunnel of n-1 hops.
  This is necessary for inbound tunnels (where the next-to-last hop
  can see the hash prefix for the next hop), but not for outbound tunnels.
  However, if the build message length is different for inbound and outbound
  tunnels, this would allow hops to determine which direction the tunnel was.

* Should we define new, smaller VTBM/VTBRM I2NP messages for all-ECIES tunnels
  now instead of waiting for the rollout?



Migration
=========

See [Prop156]_.




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

.. [Prop153]
    {{ proposal_url('153') }}

.. [Prop156]
    {{ proposal_url('156') }}

.. [Tunnel-Creation]
   {{ spec_url('tunnel-creation') }}

.. [Multiple-Encryption]
   https://en.wikipedia.org/wiki/Multiple_encryption

.. [RFC-7539]
   https://tools.ietf.org/html/rfc7539

.. [RFC-7748]
   https://tools.ietf.org/html/rfc7748



