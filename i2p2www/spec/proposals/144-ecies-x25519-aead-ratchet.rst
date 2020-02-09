=========================
ECIES-X25519-AEAD-Ratchet
=========================
.. meta::
    :author: zzz, chisana
    :created: 2018-11-22
    :thread: http://zzz.i2p/topics/2639
    :lastupdated: 2020-02-09
    :status: Open

.. contents::


Overview
========

This is a proposal for the first new end-to-end encryption type
since the beginning of I2P, to replace ElGamal/AES+SessionTags.

It relies on previous work as follows:

- Common structures spec
- I2NP spec
- ElGamal/AES+Session Tags spec http://i2p-projekt.i2p/en/docs/how/elgamal-aes
- http://zzz.i2p/topics/1768 new asymmetric crypto overview
- Low-level crypto overview https://geti2p.net/spec/cryptography
- ECIES http://zzz.i2p/topics/2418
- [NTCP2]_ [Prop111]_
- 123 New netDB Entries
- 142 New Crypto Template
- [Signal]_ double ratchet algorithm

The goal is to support new encryption for end-to-end,
destination-to-destination communication.

All references to Signal and Noise in this proposal are for background information only.
Knowledge of Signal and Noise protocols is not required to either understand
or implement this proposal.


Current ElGamal Uses
--------------------

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

- In a LS2
  This is the destination's encryption key.



EncTypes in Key Certs
---------------------

As a review,
we added support for encryption types when we added support for signature types.
The encryption type field is always zero, both in Destinations and RouterIdentities.
Whether to ever change that is TBD.
Reference the common structures specification.




Asymmetric Crypto Uses
----------------------

As a review, we use ElGamal for:

1) Tunnel Build messages (key is in RouterIdentity)
   Replacement is not covered in this proposal.
   See proposal 152.

2) Router-to-router encryption of netdb and other I2NP msgs (Key is in RouterIdentity)
   Depends on this proposal.
   Requires a proposal for 1) also, or putting the key in the RI options.

3) Client End-to-end ElGamal+AES/SessionTag (key is in LeaseSet, the Destination key is unused)
   Replacement IS covered in this proposal.

4) Ephemeral DH for NTCP1 and SSU
   Replacement is not covered in this proposal.
   See proposal 111 for NTCP2.
   No current proposal for SSU2.


Goals
-----

- Backwards compatible
- Requires and builds on LS2 (proposal 123)
- Leverage new crypto or primitives added for NTCP2 (proposal 111)
- No new crypto or primitives required for support
- Maintain decoupling of crypto and signing; support all current and future versions
- Enable new crypto for destinations
- Enable new crypto for routers, but only for garlic messages - tunnel building would
  be a separate proposal
- Don't break anything that relies on 32-byte binary destination hashes, e.g. bittorrent
- Maintain 0-RTT message delivery using ephemeral-static DH
- Do not require buffering / queueing of messages at this protocol layer;
  continue to support unlimited message delivery in both directions without waiting for a response
- Upgrade to ephemeral-ephemeral DH after 1 RTT
- Maintain handling of out-of-order messages
- Maintain 256-bit security
- Add forward secrecy
- Add authentication (AEAD)
- Much more CPU-efficient than ElGamal
- Don't rely on Java jbigi to make DH efficient
- Minimize DH operations
- Much more bandwidth-efficient than ElGamal (514 byte ElGamal block)
- Eliminate several problems with session tags, including:

   * Inability to use AES until the first reply
   * Unreliability and stalls if tag delivery assumed
   * Bandwidth inefficient, especially on first delivery
   * Huge space inefficiency to store tags
   * Huge bandwidth overhead to deliver tags
   * Highly complex, difficult to implement
   * Difficult to tune for various use cases
     (streaming vs. datagrams, server vs. client, high vs. low bandwidth)
   * Memory exhaustion vulnerabilities due to tag delivery

- Support new and old crypto on same tunnel if desired
- Recipient is able to efficiently distinguish new from old crypto coming down
  same tunnel
- Others cannot distinguish new from old crypto
- Eliminate new vs. Existing Session length classification (support padding)
- No new I2NP messages required
- Replace SHA-256 checksum in AES payload with AEAD
- (Optimistic) Add extensions or hooks to support multicast
- Support binding of transmit and receive sessions so that
  acknowledgements may happen within the protocol, rather than solely out-of-band.
  This will also allow replies to have forward secrecy immediately.
- Enable end-to-end encryption of certain messages (RouterInfo stores)
  that we currently don't due to CPU overhead.
- Do not change the I2NP Garlic Message
  or Garlic Message Delivery Instructions format.
- Eliminate unused or redundant fields in the Garlic Clove Set and Clove formats.


Non-Goals / Out-of-scope
------------------------

- LS2 format (see proposal 123)
- New DHT rotation algorithm or shared random generation
- New encryption for tunnel building.
  See proposal 152.
- New encryption for tunnel layer encryption.
  See proposal 153.
- Methods of encryption, transmission, and reception of I2NP DLM / DSM / DSRM messages.
  Not changing.
- No LS1-to-LS2 or ElGamal/AES-to-this-proposal communication is supported.
  This proposal is a bidirectional protocol.
  Destinations may handle backward compatibility by publishing two leasesets
  using the same tunnels, or put both encryption types in the LS2.
- Threat model changes
- Implementation details are not discussed here and are left to each project.



Justification
-------------

ElGamal/AES+SessionTag has been our sole end-to-end protocol for about 15 years,
essentially without modifications to the protocol.
There are now cryptographic primitives that are faster.
We need to enhance the security of the protocol.
We have also developed heuristic strategies and workarounds to minimize the
memory and bandwidth overhead of the protocol, but those strategies
are fragile, difficult to tune, and render the protocol even more prone
to break, causing the session to drop.

For about the same time period, the ElGamal/AES+SessionTag specification and related
documentation have described how bandwidth-expensive it is to deliver session tags,
and have proposed replacing session tag delivery with a "synchronized PRNG".
A synchronized PRNG deterministically generates the same tags at both ends,
derived from a common seed.
A synchronized PRNG can also be termed a "ratchet".
This proposal (finally) specifies that ratchet mechanism, and eliminates tag delivery.

By using a ratchet (a synchronized PRNG) to generate the
session tags, we eliminate the overhead of sending session tags
in the New Session message and subsequent messages when needed.
For a typical tag set of 32 tags, this is 1KB.
This also eliminates the storage of session tags on the sending side,
thus cutting the storage requirements in half.

A full two-way handshake, similar to Noise IK pattern, is needed to avoid Key Compromise Impersonation (KCI) attacks.
See the Noise "Payload Security Properties" table in [NOISE]_.
For more information on KCI, see the paper https://www.usenix.org/system/files/conference/woot15/woot15-paper-hlauschek.pdf



Threat Model
------------

The threat model is somewhat different than for NTCP2 (proposal 111).
The MitM nodes are the OBEP and IBGW and are assumed to have full view of
the current or historical global NetDB, by colluding with floodfills.

The goal is to prevent these MitMs from classifying traffic as
new and Existing Session messages, or as new crypto vs. old crypto.



Detailed Proposal
=================

This proposal defines a new end-to-end protocol to replace ElGamal/AES+SessionTags.


Summary of Cryptographic Design
-------------------------------

There are five portions of the protocol to be redesigned:


- 1) The new and Existing Session container formats
  are replaced with new formats.
- 2) ElGamal (256 byte public keys, 128 byte private keys) is be replaced
  with ECIES-X25519 (32 byte public and private keys)
- 3) AES is be replaced with
  AEAD_ChaCha20_Poly1305 (abbreviated as ChaChaPoly below)
- 4) SessionTags will be replaced with ratchets,
  which is essentially a cryptographic, synchronized PRNG.
- 5) The AES payload, as defined in the ElGamal/AES+SessionTags specification,
  is replaced with a block format similar to that in NTCP2.

Each of the five changes has its own section below.


New Cryptographic Primitives for I2P
------------------------------------

Existing I2P router implementations will require implementations for
the following standard cryptographic primitives,
which are not required for current I2P protocols:

- ECIES (but this is essentially X25519)
- Elligator2

Existing I2P router implementations that have not yet implemented [NTCP2]_ ([Prop111]_)
will also require implementations for:

- X25519 key generation and DH
- AEAD_ChaCha20_Poly1305 (abbreviated as ChaChaPoly below)
- HKDF


Crypto Type
-----------

The crypto type (used in the LS2) is 4.
This indicates a 32-byte X25519 public key,
and the end-to-end protocol specified here.

Crypto type 0 is ElGamal.
Crypto types 1-3 are reserved for ECIES-ECDH-AES-SessionTag, see proposal 145.


Noise Protocol Framework
------------------------

This proposal provides the requirements based on the Noise Protocol Framework
[NOISE]_ (Revision 34, 2018-07-11).
Noise has similar properties to the Station-To-Station protocol
[STS]_, which is the basis for the [SSU]_ protocol.  In Noise parlance, Alice
is the initiator, and Bob is the responder.

This proposal is based on the Noise protocol Noise_IK_25519_ChaChaPoly_SHA256.
(The actual identifier for the initial key derivation function
is "Noise_IKelg2_25519_ChaChaPoly_SHA256"
to indicate I2P extensions - see KDF 1 section below)
This Noise protocol uses the following primitives:

- Interactive Handshake Pattern: IK
  Alice immediately transmits her static key to Bob (I)
  Alice knows Bob's static key already (K)

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

This proposal defines the following enhancements to
Noise_XK_25519_ChaChaPoly_SHA256.  These generally follow the guidelines in
[NOISE]_ section 13.

1) Cleartext ephemeral keys are encoded with [Elligator2]_.

2) The reply is prefixed with a cleartext tag.

3) The payload format is defined for messages 1, 2, and the data phase.
   Of course, this is not defined in Noise.

All messages include an [I2NP]_ Garlic Message header.
The data phase uses encryption similar to, but not compatible with, the Noise data phase.


Handshake Patterns
------------------

Handshakes use [Noise]_ handshake patterns.

The following letter mapping is used:

- e = one-time ephemeral key
- s = static key
- p = message payload

One-time and Unbound sessions are similar to the Noise N pattern.

.. raw:: html

  {% highlight lang='dataspec' %}
<- s
  ...
  e es p ->

{% endhighlight %}

Bound sessions are similar to the Noise IK pattern.

.. raw:: html

  {% highlight lang='dataspec' %}
<- s
  ...
  e es s ss p ->
  <- tag e ee se
  <- p
  p ->

{% endhighlight %}


Sessions
--------

The current ElGamal/AES+SessionTag protocol is unidirectional.
At this layer, the receiver doesn't know where a message is from.
Outbound and inbound sessions are not associated.
Acknowledgements are out-of-band using a DeliveryStatusMessage
(wrapped in a GarlicMessage) in the clove.

There is substantial inefficiency in a unidirectional protocol.
Any reply must also use an expensive 'New Session' message.
This causes higher bandwidth, CPU, and memory usage.

There are also security weaknesses in a unidirectional protocol.
All sessions are based on ephemeral-static DH.
Without a return path, there is no way for Bob to "ratchet" his static key
to an ephemeral key.
Without knowing where a message is from, there's no way to use
the received ephemeral key for outbound messages,
so the initial reply also uses ephemeral-static DH.

For this proposal, we define two mechanisms to create a bidirectional protocol -
"pairing" and "binding".
These mechanisms provide increased efficiency and security.


Session Context
```````````````

As with ElGamal/AES+SessionTags, all inbound and outbound sessions
must be in a given context, either the router's context or
the context for a particular local destination.
In Java I2P, this context is called the Session Key Manager.

Sessions must not be shared among contexts, as that would
allow correlation among the various local destinations,
or between a local destination and a router.

When a given destination supports both ElGamal/AES+SessionTags
and this proposal, both types of sessions may share a context.
See section 1c) below.



Pairing Inbound and Outbound Sessions
`````````````````````````````````````

When an outbound session is created at the originator (Alice),
a new inbound session is created and paired with the outbound session,
unless no reply is expected (e.g. raw datagrams).

A new inbound session is always paired with a new outbound session,
unless no reply is requested (e.g. raw datagrams).

If a reply is requested and bound to a far-end destination or router,
that new outbound session is bound to that destination or router,
and replaces any previous outbound session to that destination or router.

Pairing inbound and outbound sessions provides a bidirectional protocol
with the capability of ratcheting the DH keys.



Binding Sessions and Destinations
`````````````````````````````````

There is only one outbound session to a given destination or router.
There may be several current inbound sessions from a given destination or router.
Generally, when a new inbound session is created, and traffic is received
on that session (which serves as an ACK), any others will be marked
to expire relatively quickly, within a minute or so.
The previous messages sent (PN) value is checked, and if there are no
unreceived messages (within the window size) in the previous inbound session,
the previous session may be deleted immediately.


When an outbound session is created at the originator (Alice),
it is bound to the far-end Destination (Bob),
and any paired inbound session will also be bound to the far-end Destination.
As the sessions ratchet, they continue to be bound to the far-end Destination.

When an inbound session is created at the receiver (Bob),
it may be bound to the far-end Destination (Alice), at Alice's option.
If Alice includes binding information (her static key) in the New Session message,
the session will be bound to that destination,
and a outbound session will be created and bound to same Destination.
As the sessions ratchet, they continue to be bound to the far-end Destination.


Benefits of Binding and Pairing
```````````````````````````````

For the common, streaming case, we expect Alice and Bob to use the protocol as follows:

- Alice pairs her new outbound session to a new inbound session, both bound to the far-end destination (Bob).
- Alice includes the binding information and signature, and a reply request, in the
  New Session message sent to Bob.
- Bob pairs his new inbound session to a new outbound session, both bound to the far-end destination (Alice).
- Bob sends a reply (ack) to Alice in the paired session, with a ratchet to a new DH key.
- Alice ratchets to a new outbound session with Bob's new key, paired to the existing inbound session.

By binding an inbound session to a far-end Destination, and pairing the inbound session
to an outbound session bound to the same Destination, we achieve two major benefits:

1) The initial reply from Bob to Alice uses ephemeral-ephemeral DH

2) After Alice receives Bob's reply and ratchets, all subsequent messages from Alice to Bob
use ephemeral-ephemeral DH.


Message ACKs
````````````

In ElGamal/AES+SessionTags, when a LeaseSet is bundled as a garlic clove,
or tags are delivered, the sending router requests an ACK.
This is a separate garlic clove containing a DeliveryStatus Message.
For additional security, the DeliveryStatus Message is wrapped in a Garlic Message.
This mechanism is out-of-band from the perspective of the protocol.

In the new protocol, since the inbound and outbound sessions are paired,
we can have ACKs in-band. No separate clove is required.

An explicit ACK is simply an Existing Session message with no I2NP block.
However, in most cases, an explict ACK can be avoided, as there is reverse traffic.
It may be desirable for implementations to wait a short time (perhaps a hundred ms)
before sending an explicit ACK, to give the streaming or application layer time to respond.

Implementations will also need to defer any ACK sending until after the
I2NP block is processed, as the Garlic Message may contain a Database Store Message
with a lease set. A recent lease set will be necessary to route the ACK,
and the far-end destination (contained in the lease set) will be necessary to
verify the binding static key.


Session Timeouts
````````````````

Outbound sessions should always expire before inbound sessions.
One an outbound session expires, and a new one is created, a new paired inbound
session will be created as well. If there was an old inbound session,
it will be allowed to expire.


Multicast
---------

TBD


Definitions
-----------
We define the following functions corresponding to the cryptographic building blocks used.

ZEROLEN
    zero-length byte array

CSRNG(n)
    n-byte output from a cryptographically-secure random number generator.

H(p, d)
    SHA-256 hash function that takes a personalization string p and data d, and
    produces an output of length 32 bytes.
    As defined in [NOISE]_.
    || below means append.

    Use SHA-256 as follows::

        H(p, d) := SHA-256(p || d)

MixHash(d)
    SHA-256 hash function that takes a previous hash h and new data d,
    and produces an output of length 32 bytes.
    || below means append.

    Use SHA-256 as follows::

        MixHash(d) := h = SHA-256(h || d)

STREAM
    The ChaCha20/Poly1305 AEAD as specified in [RFC-7539]_.
    S_KEY_LEN = 32 and S_IV_LEN = 12.

    ENCRYPT(k, n, plaintext, ad)
        Encrypts plaintext using the cipher key k, and nonce n which MUST be unique for
        the key k.
        Associated data ad is optional.
        Returns a ciphertext that is the size of the plaintext + 16 bytes for the HMAC.

        The entire ciphertext must be indistinguishable from random if the key is secret.

    DECRYPT(k, n, ciphertext, ad)
        Decrypts ciphertext using the cipher key k, and nonce n.
        Associated data ad is optional.
        Returns the plaintext.

DH
    X25519 public key agreement system. Private keys of 32 bytes, public keys of 32
    bytes, produces outputs of 32 bytes. It has the following
    functions:

    GENERATE_PRIVATE()
        Generates a new private key.

    DERIVE_PUBLIC(privkey)
        Returns the public key corresponding to the given private key.

    GENERATE_PRIVATE_ELG2()
        Generates a new private key that maps to a public key suitable for Elligator2 encoding.
        Note that half of the randomly-generated private keys will not be suitable and must be discarded.

    ENCODE_ELG2(pubkey)
        Returns the Elligator2-encoded public key corresponding to the given public key (inverse mapping).
        Encoded keys are little endian.
        Encoded key must be 256 bits indistinguishable from random data.
        See Elligator2 section below for specification.

    DECODE_ELG2(pubkey)
        Returns the public key corresponding to the given Elligator2-encoded public key.
        See Elligator2 section below for specification.

    DH(privkey, pubkey)
        Generates a shared secret from the given private and public keys.

HKDF(salt, ikm, info, n)
    A cryptographic key derivation function which takes some input key material ikm (which
    should have good entropy but is not required to be a uniformly random string), a salt
    of length 32 bytes, and a context-specific 'info' value, and produces an output
    of n bytes suitable for use as key material.

    Use HKDF as specified in [RFC-5869]_, using the HMAC hash function SHA-256
    as specified in [RFC-2104]_. This means that SALT_LEN is 32 bytes max.

MixKey(d)
    Use HKDF() with a previous chainKey and new data d, and
    sets the new chainKey and k.
    As defined in [NOISE]_.

    Use HKDF as follows::

        MixKey(d) := output = HKDF(chainKey, d, "", 64)
                     chainKey = output[0:31]
                     k = output[32:63]


Issues
------

- Use Blake2b instead of SHA256?


1) Message format
-----------------


Review of Current Message Format
````````````````````````````````

The Garlic Message as specified in [I2NP]_ is as follows.
As a design goal is that intermediate hops cannot distinguish new from old crypto,
this format cannot change, even though the length field is redundant.
The format is shown with the full 16-byte header, although the
actual header may be in a different format, depending on the transport used.

When decrypted the data contains a series of Garlic Cloves and additional
data, also known as a Clove Set.

See [I2NP]_ for details and a full specification.


.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |type|      msg_id       |  expiration
  +----+----+----+----+----+----+----+----+
                           |  size   |chks|
  +----+----+----+----+----+----+----+----+
  |      length       |                   |
  +----+----+----+----+                   +
  |          encrypted data               |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

{% endhighlight %}


Review of Encrypted Data Format
````````````````````````````````

The current message format, used for over 15 years,
is ElGamal/AES+SessionTags.
In ElGamal/AES+SessionTags, there are two message formats:

1) New session:
- 514 byte ElGamal block
- AES block (128 bytes minimum, multiple of 16)

2) Existing session:
- 32 byte Session Tag
- AES block (128 bytes minimum, multiple of 16)

The minimum padding to 128 is as implemented in Java I2P but is not enforced on reception.

These messages are encapsulated in a I2NP garlic message, which contains
a length field, so the length is known.

Note that there is no padding defined to a non-mod-16 length,
so the New Session is always (mod 16 == 2),
and an Existing Session is always (mod 16 == 0).
We need to fix this.

The receiver first attempts to look up the first 32 bytes as a Session Tag.
If found, he decrypts the AES block.
If not found, and the data is at least (514+16) long, he attempts to decrypt the ElGamal block,
and if successful, decrypts the AES block.


New Session Tags and Comparison to Signal
`````````````````````````````````````````

In Signal Double Ratchet, the header contains:

- DH: Current ratchet public key
- PN: Previous chain message length
- N: Message Number

By using a session tag, we can eliminate most of that.

In New Session, we put only the public key in the unencrytped header.

In Existing Session, we use a session tag for the header.
The session tag is associated with the current ratchet public key,
and the message number.

In both new and Existing Session, PN and N are in the encrypted body.

In Signal, things are constantly ratcheting. A new DH public key requires the
receiver to ratchet and send a new public key back, which also serves
as the ack for the received public key.
This would be far too many DH operations for us.
So we separate the ack of the received key and the transmission of a new public key.
Any message using a session tag generated from the new DH public key constitutes an ACK.
We only transmit a new public key when we wish to rekey.

The maximum number of messages before the DH must ratchet is 65535.

When delivering a session key, we derive the "Tag Set" from it,
rather than having to deliver session tags as well.
A Tag Set can be up to 65536 tags.
However, receivers should implement a "look-ahead" strategy, rather
than generating all possible tags at once.
Only generate at most N tags past the last good tag received.
N might be at most 128, but 32 or even less may be a better choice.



1a) New session format
----------------------

New Session One Time Public key (32 bytes)
Encrypted data and MAC (remaining bytes)

The New Session message may or may not contain the sender's static public key.
If it is included, the reverse session is bound to that key.
The static key should be included if replies are expected,
i.e. for streaming and repliable datagrams.
It should not be included for raw datagrams.

The New Session message is similar to the one-way Noise [NOISE]_ pattern
"N" (if the static key is not sent),
or the two-way pattern "IK" (if the static key is sent).



1b) New session format (with binding)
-------------------------------------

Length is 96 + payload length.
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
  +         Static Key                    +
  |       ChaCha20 encrypted data         |
  +            32 bytes                   +
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

  Public Key :: 32 bytes, little endian, Elligator2, cleartext

  Static Key encrypted data :: 32 bytes

  Payload Section encrypted data :: remaining data minus 16 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}


New Session Ephemeral Key
`````````````````````````

The ephemeral key is 32 bytes, encoded with Elligator2.
This key is never reused; a new key is generated with
each message, including retransmissions.

Static Key
``````````

When decryptied, Alice's X25519 static key, 32 bytes.


Payload
```````

Encrypted length is the remainder of the data.
Decrypted length is 16 less than the encrypted length.
Payload must contain a DateTime block and will usually contain one or more Garlic Clove blocks.
See the payload section below for format and additional requirements.



1c) New session format (without binding)
----------------------------------------

If no reply is required, no static key is sent.


Length is 96 + payload length.
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
  +           Flags Section               +
  |       ChaCha20 encrypted data         |
  +            32 bytes                   +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +         (MAC) for above section       +
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

  Public Key :: 32 bytes, little endian, Elligator2, cleartext

  Flags Section encrypted data :: 32 bytes

  Payload Section encrypted data :: remaining data minus 16 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}

New Session Ephemeral Key
`````````````````````````

Alice's ephemeral key.
The ephemeral key is 32 bytes, encoded with Elligator2, little endian.
This key is never reused; a new key is generated with
each message, including retransmissions.


Flags Section Decrypted data
````````````````````````````

The Flags section contains nothing.
It is always 32 bytes, because it must be the same length
as the static key for New Session messages with binding.
Bob determines whether it's a static key or a flags section
by testing if the 32 bytes are all zeros.

TODO any flags needed here?

Payload
```````

Encrypted length is the remainder of the data.
Decrypted length is 16 less than the encrypted length.
Payload must contain a DateTime block and will usually contain one or more Garlic Clove blocks.
See the payload section below for format and additional requirements.




1d) One-time format (no binding or session)
-------------------------------------------

If only a single message is expected to be sent,
no session setup or static key is required.


Length is 96 + payload length.
Encrypted format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |       Ephemeral Public Key            |
  +             32 bytes                  +
  |     Encoded with Elligator2           |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +           Flags Section               +
  |       ChaCha20 encrypted data         |
  +            32 bytes                   +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +         (MAC) for above section       +
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

  Public Key :: 32 bytes, little endian, Elligator2, cleartext

  Flags Section encrypted data :: 32 bytes

  Payload Section encrypted data :: remaining data minus 16 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}


New Session One Time Key
````````````````````````

The one time key is 32 bytes, encoded with Elligator2, little endian.
This key is never reused; a new key is generated with
each message, including retransmissions.


Flags Section Decrypted data
````````````````````````````````

The Flags section contains nothing.
It is always 32 bytes, because it must be the same length
as the static key for New Session messages with binding.
Bob determines whether it's a static key or a flags section
by testing if the 32 bytes are all zeros.

TODO any flags needed here?

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |                                       |
  +             All zeros                 +
  |              32 bytes                 |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+

  zeros:: All zeros, 32 bytes.

{% endhighlight %}


Payload
```````

Encrypted length is the remainder of the data.
Decrypted length is 16 less than the encrypted length.
Payload must contain a DateTime block and will usually contain one or more Garlic Clove blocks.
See the payload section below for format and additional requirements.



1f) KDFs for New Session Message
--------------------------------

KDF for Initial ChainKey
````````````````````````

This is standard [NOISE]_ for IK with a modified protocol name.
Note that we use the same initializer for both the IK pattern (bound sessions)
and for N pattern (unbound sessions).

The protocol name is modified for two reasons.
First, to indicate that the ephemeral keys are encoded with Elligator2,
and second, to indicate that MixHash() is called before the second message
to mix in the tag value.

.. raw:: html

  {% highlight lang='text' %}
This is the "e" message pattern:

  // Define protocol_name.
  Set protocol_name = "Noise_IKelg2+hs2_25519_ChaChaPoly_SHA256"
   (40 bytes, US-ASCII encoded, no NULL termination).

  // Define Hash h = 32 bytes
  h = SHA256(protocol_name);

  Define ck = 32 byte chaining key. Copy the h data to ck.
  Set chainKey = h

  // MixHash(null prologue)
  h = SHA256(h);

  // up until here, can all be precalculated by Alice for all outgoing connections

{% endhighlight %}


KDF for Flags/Static Key Section Encrypted Contents
```````````````````````````````````````````````````

.. raw:: html

  {% highlight lang='text' %}
This is the "e" message pattern:

  // Bob's X25519 static keys
  // bpk is published in leaseset
  bsk = GENERATE_PRIVATE()
  bpk = DERIVE_PUBLIC(bsk)

  // Bob static public key
  // MixHash(bpk)
  // || below means append
  h = SHA256(h || bpk);

  // up until here, can all be precalculated by Bob for all incoming connections

  // Alice's X25519 ephemeral keys
  aesk = GENERATE_PRIVATE_ELG2()
  aepk = DERIVE_PUBLIC(aesk)

  // Alice ephemeral public key
  // MixHash(aepk)
  // || below means append
  h = SHA256(h || aepk);

  // h is used as the associated data for the AEAD in the New Session Message
  // Retain the Hash h for the New Session Reply KDF
  // eapk is sent in cleartext in the
  // beginning of the New Session message
  elg2_aepk = ENCODE_ELG2(aepk)
  // As decoded by Bob
  aepk = DECODE_ELG2(elg2_aepk)

  End of "e" message pattern.

  This is the "es" message pattern:

  // Noise es
  sharedSecret = DH(aesk, bpk) = DH(bsk, aepk)

  // MixKey(DH())
  //[chainKey, k] = MixKey(sharedSecret)
  // ChaChaPoly parameters to encrypt/decrypt
  keydata = HKDF(chainKey, sharedSecret, "", 64)
  chainKey = keydata[0:31]

  // AEAD parameters
  k = keydata[32:64]
  n = 0
  ad = h
  ciphertext = ENCRYPT(k, n, flags/static key section, ad)

  End of "es" message pattern.

  This is the "s" message pattern:

  // MixHash(ciphertext)
  // Save for Payload section KDF
  h = SHA256(h || ciphertext)

  // Alice's X25519 static keys
  ask = GENERATE_PRIVATE()
  apk = DERIVE_PUBLIC(ask)

  End of "s" message pattern.


{% endhighlight %}



KDF for Payload Section (with Alice static key)
```````````````````````````````````````````````

.. raw:: html

  {% highlight lang='text' %}
This is the "ss" message pattern:

  // Noise ss
  sharedSecret = DH(ask, bpk) = DH(bsk, apk)

  // MixKey(DH())
  //[chainKey, k] = MixKey(sharedSecret)
  // ChaChaPoly parameters to encrypt/decrypt
  // chainKey from Static Key Section
  Set sharedSecret = X25519 DH result
  keydata = HKDF(chainKey, sharedSecret, "", 64)
  chainKey = keydata[0:31]

  // AEAD parameters
  k = keydata[32:64]
  n = 0
  ad = h
  ciphertext = ENCRYPT(k, n, payload, ad)

  End of "ss" message pattern.

  // MixHash(ciphertext)
  // Save for New Session Reply KDF
  h = SHA256(h || ciphertext)

{% endhighlight %}


KDF for Payload Section (without Alice static key)
``````````````````````````````````````````````````

Note that this is a Noise "N" pattern, but we use the same "IK" initializer
as for bound sessions.

New Session essages can not be identified as containing Alice's static key or not
until the static key is decrypted and inspected to determine if it contains all zeros.
Therefore, the receiver must use the "IK" state machine for all
New Session messages.
If the static key is all zeros, the "ss" message pattern must be skipped.



.. raw:: html

  {% highlight lang='text' %}
chainKey = from Flags/Static key section
  k = from Flags/Static key section
  n = 1
  ad = h from Flags/Static key section
  ciphertext = ENCRYPT(k, n, payload, ad)

{% endhighlight %}



1g) New Session Reply format
----------------------------

One or more New Session Replies may be sent in response to a single New Session message.
Each reply is prepended by a tag, which is generated from a TagSet for the session.

The New Session Reply is in two parts.
The first part is the completion of the Noise IK handshake with a prepended tag.
The length of the first part is 56 bytes.
The second part is the data phase payload.
The length of the second part is 16 + payload length.

Total length is 72 + payload length.
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
  |  Poly1305 Message Authentication Code |
  +  (MAC) for Key Section (no data)      +
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

  Tag :: 8 bytes, cleartext

  Public Key :: 32 bytes, little endian, Elligator2, cleartext

  MAC :: Poly1305 message authentication code, 16 bytes
         Note: The ChaCha20 plaintext data is empty (ZEROLEN)

  Payload Section encrypted data :: remaining data minus 16 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}

Session Tag
```````````
The tag is generated in the Session Tags KDF, as initialized
in the DH Initialization KDF below.
This correlates the reply to the session.
The Session Key from the DH Initialization is not used.


New Session Reply Ephemeral Key
````````````````````````````````

Bob's ephemeral key.
The ephemeral key is 32 bytes, encoded with Elligator2, little endian.
This key is never reused; a new key is generated with
each message, including retransmissions.


Payload
```````
Encrypted length is the remainder of the data.
Decrypted length is 16 less than the encrypted length.
Payload will usually contain one or more Garlic Clove blocks.
See the payload section below for format and additional requirements.


KDF for Reply TagSet
`````````````````````

One or more tags are created from the TagSet, which is initialized using
the KDF below, using the chainKey from the New Session message.

.. raw:: html

  {% highlight lang='text' %}
// Generate tagset
  tagsetKey = HKDF(chainKey, ZEROLEN, "SessionReplyTags", 32)
  tagset_nsr = DH_INITIALIZE(chainKey, tagsetKey)

{% endhighlight %}


KDF for Reply Key Section Encrypted Contents
````````````````````````````````````````````

.. raw:: html

  {% highlight lang='text' %}
// Keys from the New Session message
  // Alice's X25519 keys
  // apk and aepk are sent in original New Session message
  // ask = Alice private static key
  // apk = Alice public static key
  // aesk = Alice ephemeral private key
  // aepk = Alice ephemeral public key
  // Bob's X25519 static keys
  // bsk = Bob private static key
  // bpk = Bob public static key

  // Generate the tag
  tagsetEntry = tagset_nsr.GET_NEXT_ENTRY()
  tag = tagsetEntry.SESSION_TAG

  // MixHash(tag)
  h = SHA256(h || tag)

  This is the "e" message pattern:

  // Bob's X25519 ephemeral keys
  besk = GENERATE_PRIVATE_ELG2()
  bepk = DERIVE_PUBLIC(besk)

  // Bob's ephemeral public key
  // MixHash(bepk)
  // || below means append
  h = SHA256(h || bepk);

  // elg2_bepk is sent in cleartext in the
  // beginning of the New Session message
  elg2_bepk = ENCODE_ELG2(bepk)
  // As decoded by Bob
  bepk = DECODE_ELG2(elg2_bepk)

  End of "e" message pattern.

  This is the "ee" message pattern:

  // MixKey(DH())
  //[chainKey, k] = MixKey(sharedSecret)
  // ChaChaPoly parameters to encrypt/decrypt
  // chainKey from original New Session Payload Section
  sharedSecret = DH(aesk, bepk) = DH(besk, aepk)
  keydata = HKDF(chainKey, sharedSecret, "", 32)
  chainKey = keydata[0:31]

  End of "ee" message pattern.

  This is the "se" message pattern:

  // MixKey(DH())
  //[chainKey, k] = MixKey(sharedSecret)
  sharedSecret = DH(ask, bepk) = DH(besk, apk)
  keydata = HKDF(chainKey, sharedSecret, "", 64)
  chainKey = keydata[0:31]

  // AEAD parameters
  k = keydata[32:64]
  n = 0
  ad = h
  ciphertext = ENCRYPT(k, n, ZEROLEN, ad)

  End of "se" message pattern.

  // MixHash(ciphertext)
  h = SHA256(h || ciphertext)

  chainKey is used in the ratchet below.

{% endhighlight %}


KDF for Payload Section Encrypted Contents
``````````````````````````````````````````

This is like the first Existing Session message,
post-split, but without a separate tag.
Additionally, we use the hash from above to bind the
payload to the NSR message.


.. raw:: html

  {% highlight lang='text' %}
// split()
  keydata = HKDF(chainKey, ZEROLEN, "", 64)
  k_ab = keydata[0:31]
  k_ba = keydata[32:63]
  tagset_ab = DH_INITIALIZE(chainKey, k_ab)
  tagset_ba = DH_INITIALIZE(chainKey, k_ba)

  // AEAD parameters for New Session Reply payload
  k = HKDF(k_ba, ZEROLEN, "AttachPayloadKDF", 32)
  n = 0
  ad = h
  ciphertext = ENCRYPT(k, n, payload, ad)
{% endhighlight %}


Notes
-----

Multiple NSR messages may be sent in reply, each with unique ephemeral keys, depending on the size of the response.

Alice and Bob are required to use new ephemeral keys for every NS and NSR message.

Alice must receive one of Bob's NSR messages before sending Existing Session (ES) messages,
and Bob must receive an ES message from Alice before sending ES messages.

The ``chainKey`` and ``k`` from Bob's NSR Payload Section are used
as inputs for the initial ES DH Ratchets (both directions, see DH Ratchet KDF).

Bob must only retain Existing Sessions for the ES messages received from Alice.
Any other created inbound and outbound sessions (for multiple NSRs) should be
destroyed immediately after receiving Alice's first ES message for a given session.



1h) Existing session format
---------------------------

Session tag (8 bytes)
Encrypted data and MAC (see section 3 below)


Format
``````
Encrypted:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |       Session Tag                     |
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
  +              (MAC)                    +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+

  Session Tag :: 8 bytes, cleartext

  Payload Section encrypted data :: remaining data minus 16 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}


Payload
```````
Encrypted length is the remainder of the data.
Decrypted length is 16 less than the encrypted length.
See the payload section below for format and requirements.


KDF
```

.. raw:: html

  {% highlight lang='text' %}
See AEAD section below.

  // AEAD parameters for Existing Session payload
  k = The 32-byte session key associated with this session tag
  n = The message number N in the current chain, as retrieved from the associated Session Tag.
  ad = The session tag, 8 bytes
  ciphertext = ENCRYPT(k, n, payload, ad)
{% endhighlight %}


Justification
`````````````

Notes
`````


Issues
``````



2) ECIES-X25519
---------------


Format
``````

32-byte public and private keys.


Justification
`````````````

Used in [NTCP2]_.



Notes
`````


Issues
``````



2a) Elligator2
--------------

In standard Noise handshakes, the initial handshake messages in each direction start with
ephemeral keys that are transmitted in cleartext.
As valid X25519 keys are distinguishable from random, a man-in-the-middle may distinguish
these messages from Existing Session messages that start with random session tags.
In [NTCP2]_ ([Prop111]_), we used a low-overhead XOR function using the out-of-band static key to obfuscate
the key. However, the threat model here is different; we do not want to allow any MitM to
use any means to confirm the destination of the traffic, or to distinguish
the initial handshake messages from Existing Session messages.

Therefore, [Elligator2]_ is used to transform the ephemeral keys in the New Session and New Session Reply messages
so that they are indistinguishable from uniform random strings.



Format
``````

32-byte public and private keys.
Encoded keys are little endian.

As defined in [Elligator2]_, the encoded keys are indistinguishable from 254 random bits.
We require 256 random bits (32 bytes). Therefore, the encoding and decoding are
defined as follows:

Encoding:

.. raw:: html

  {% highlight lang='text' %}
ENCODE_ELG2() Definition

  // Encode as defined in Elligator2 specification
  encodedKey = encode(pubkey)
  // OR in 2 random bits to MSB
  randomByte = CSRNG(1)
  encodedKey[31] |= (randomByte & 0xc0)
{% endhighlight %}


Decoding:

.. raw:: html

  {% highlight lang='text' %}
DECODE_ELG2() Definition

  // Mask out 2 random bits from MSB
  encodedKey[31] &= 0x3f
  // Decode as defined in Elligator2 specification
  pubkey = decode(encodedKey)
{% endhighlight %}




Justification
`````````````

Required to prevent the OBEP and IBGW from classifying traffic.


Notes
`````

Elligator2 doubles average the key generation time, as half the private keys
result in public keys that are unsuitable for encoding with Elligator2.
Also, the key generation time is unbounded with an exponential distribution,
as the generator must keep retrying utnil a suitable key pair is found.

This overhead may be managed by doing key generation in advance,
in a separate thread, to keep a pool of suitable keys.

The generator does the ENCODE_ELG2() function to determine suitability.
Therefore, the generator should store the result of ENCODE_ELG2()
so it does not have to be calculated again.

Additionally, the unsuitable keys may be added to the pool of keys
used for [NTCP2]_, where Elligator2 is not used.
The security issues of doing so is TBD.




3) AEAD (ChaChaPoly)
--------------------

AEAD using ChaCha20 and Poly1305, same as in [NTCP2]_.
This corresponds to [RFC-7539]_, which is also
used similarly in TLS [RFC-7905]_.



New Session and New Session Reply Inputs
````````````````````````````````````````

Inputs to the encryption/decryption functions
for an AEAD block in a New Session message:

.. raw:: html

  {% highlight lang='dataspec' %}
k :: 32 byte cipher key
       See New Session and New Session Reply KDFs above.

  n :: Counter-based nonce, 12 bytes.
       n = 0

  ad :: Associated data, 32 bytes.
        The SHA256 hash of the preceding data, as output from mixHash()

  data :: Plaintext data, 0 or more bytes

{% endhighlight %}


Existing Session Inputs
```````````````````````

Inputs to the encryption/decryption functions
for an AEAD block in an Existing Session message:

.. raw:: html

  {% highlight lang='dataspec' %}
k :: 32 byte session key
       As looked up from the accompanying session tag.

  n :: Counter-based nonce, 12 bytes.
       Starts at 0 and incremented for each message when transmitting.
       For the receiver, the value
       as looked up from the accompanying session tag.
       First four bytes are always zero.
       Last eight bytes are the message number (n), little-endian encoded.
       Maximum value is 65535.
       Session must be ratcheted when N reaches that value.
       Higher values must never be used.

  ad :: Associated data
        The session tag

  data :: Plaintext data, 0 or more bytes

{% endhighlight %}


Encrypted Format
````````````````

Output of the encryption function, input to the decryption function:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |       ChaCha20 encrypted data         |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +              (MAC)                    +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+

  encrypted data :: Same size as plaintext data, 0 - 65519 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}

Notes
`````
- Since ChaCha20 is a stream cipher, plaintexts need not be padded.
  Additional keystream bytes are discarded.

- The key for the cipher (256 bits) is agreed upon by means of the SHA256 KDF.
  The details of the KDF for each message are in separate sections below.

- ChaChaPoly frames are of known size as they are encapsulated in the I2NP data message.

- For all messages,
  padding is inside the authenticated
  data frame.


AEAD Error Handling
```````````````````

All received data that fails the AEAD verification must be discarded.
No response is returned.


Justification
`````````````

Used in [NTCP2]_.


Notes
`````

We do not use random nonces. If we do need random nonces,
we may need a different AEAD with a larger nonce that's resistant to nonce reuse,
so we can use random nonces. (SIV?)





4) Ratchets
-----------

We still use session tags, as before, but we use ratchets to generate them.
Session tags also had a rekey option that we never implemented.
So it's like a double ratchet but we never did the second one.

Here we define something similar to Signal's Double Ratchet.
The session tags are generated deterministically and identically on
the receiver and sender sides.

By using a symmetric key/tag ratchet, we eliminate memory usage to store session tags on the sender side.
We also eliminate the bandwidth consumption of sending tag sets.
Receiver side usage is still significant, but we can reduce it further
as we will shrink the session tag from 32 bytes to 8 bytes.

We do not use header encryption as specified (and optional) in Signal,
we use session tags instead.

By using a DH ratchet, we acheive forward secrecy, which was never implemented
in ElGamal/AES+SessionTags.

Note: The New Session one-time public key is not part of the ratchet, its sole function
is to encrypt Alice's initial DH ratchet key.


Message Numbers
```````````````

The Double Ratchet handles lost or out-of-order messages by including in each message header
the message's number in the sending chain (N=0,1,2,...)
and the length (number of message keys) in the previous sending chain (PN).
This enables the recipient to advance to the relevant message key while storing skipped message keys
in case the skipped messages arrive later.

On receiving a message, if a DH ratchet step is triggered then the received PN
minus the length of the current receiving chain is the number of skipped messages in that receiving chain.
The received N is the number of skipped messages in the new receiving chain (i.e. the chain after the DH ratchet).

If a DH ratchet step isn't triggered, then the received N minus the length of the receiving chain
is the number of skipped messages in that chain.


Sample Implementation
``````````````````````

We define the following data structures and functions to implement these ratchets.

TAGSET_ENTRY
    A single entry in a TAGSET.

    INDEX
        An integer index, starting with 0

    SESSION_TAG
        An identifier to go out on the wire, 8 bytes

    SESSION_KEY
        A symmetric key, never goes on the wire, 32 bytes

TAGSET
    A collection of TAGSET_ENTRIES.

    CREATE(key, n)
        Generate a new TAGSET using initial cryptographic key material of 32 bytes.
        The associated session identifier is provided.
        The initial number of of tags to create is specified; this is generally 0 or 1
        for an outgoing session.
        LAST_INDEX = -1
        EXTEND(n) is called.

    EXTEND(n)
        Generate n more TAGSET_ENTRIES by calling EXTEND() n times.

    EXTEND()
        Generate one more TAGSET_ENTRY, unless the maximum number SESSION_TAGS have
        already been generated.
        If LAST_INDEX is greater than or equal to 65535, return.
        ++ LAST_INDEX
        Create a new TAGSET_ENTRY with the LAST_INDEX value and the calculated SESSION_TAG.
        Calls RATCHET_TAG() and (optionally) RATCHET_KEY().
        For inbound sessions, the calculation of the SESSION_KEY may
        be deferred and calculated in GET_SESSION_KEY().
        Calls EXPIRE()

    EXPIRE()
        Remove tags and keys that are too old, or if the TAGSET size exceeds some limit.

    RATCHET_TAG()
        Calculates the next SESSION_TAG based on the last SESSION_TAG.

    RATCHET_KEY()
        Calculates the next SESSION_KEY based on the last SESSION_KEY.

    SESSION
        The associated session.

    CREATION_TIME
        When the TAGSET was created.

    LAST_INDEX
        The last TAGSET_ENTRY INDEX generated by EXTEND().

    GET_NEXT_ENTRY()
        Used for outgoing sessions only.
        EXTEND(1) is called if there are no remaining TAGSET_ENTRIES.
        If EXTEND(1) did nothing, the max of 65535 TAGSETS have been used,
        and return an error.
        Returns the next unused TAGSET_ENTRY.

    GET_SESSION_KEY(sessionTag)
        Used for incoming sessions only.
        Returns the TAGSET_ENTRY containing the sessionTag.
        If found, the TAGSET_ENTRY is removed.
        If the SESSION_KEY calculation was deferred, it is calculated now.
        If there are few TAGSET_ENTRIES remaining, EXTEND(n) is called.




4a) DH Ratchet
``````````````

Ratchets but not nearly as fast as Signal does.
We separate the ack of the received key from generating the new key.
In typical usage, Alice and Bob will each ratchet (twice) immediately in a New Session,
but will not ratchet again.

Note that a ratchet is for a single direction, and generates a New Session tag / message key ratchet chain for that direction.
To generate keys for both directions, you have to ratchet twice.

You ratchet every time you generate and send a new key.
You ratchet every time you receive a new key.

Alice ratchets once when creating an unbound outbound session, she does not create an inbound session
(unbound is non-repliable).

Bob ratchets once when creating an unbound inbound session, and does not create a corresponding outbound session
(unbound is non-repliable).

Alice continues sending New Session (NS) messages to Bob until receiving one of Bob's New Session Reply (NSR) messages.
She then uses the NSR's Payload Section KDF results as inputs for the session ratchets (see DH Ratchet KDF),
and begins sending Existing Session (ES) messages.

For each NS message received, Bob creates a new inbound session, using the KDF results
of the reply Payload Section for inputs to the new inbound and outbound ES DH Ratchet.

For each reply required, Bob sends Alice a NSR message with the reply in the payload.
It is required Bob use new ephemeral keys for every NSR.

Bob must receive an ES message from Alice on one of the inbound sessions, before creating and sending
ES messages on the corresponding outbound session.

Alice should use a timer for receiving a NSR message from Bob. If the timer expires,
the session should be removed.

To avoid a KCI and/or resource exhaustion attack, where an attacker drops Bob's NSR replies to keep Alice sending NS messages,
Alice should avoid starting New Sessions to Bob after a certain number of retries due to timer expiration.

Alice and Bob each do one DH initialization to create the inbound and outbound Existing Session
session tag and symmetric key ratchet chains, and do a DH ratchet for every Next DH Key block received.

Alice and Bob each do two session tag ratchets and two symmetric keys ratchets after each
DH ratchet. For each new ES message in a given direction, Alice and Bob advance the session
tag and symmtric key ratchets.

The frequency of DH ratchets after the initial handshake is implementation-dependent.
While the protocol places a limit of 65535 messages before a ratchet is required,
more frequent ratcheting (based on message count, elapsed time, or both)
may provide additional security.

After the final handshake KDF on bound sessions, Bob and Alice must run the Noise Split() function on the
resulting CipherState to create independent symmetric and tag chain keys for inbound and outbound sessions.


Issues
~~~~~~


DH INITIALIZATION KDF
~~~~~~~~~~~~~~~~~~~~~~~

This is the definition of DH_INITIALIZE(rootKey, k)
for a single direction. It creates a tagset, and a
root key to be used for a subsequent DH ratchet if necessary.

We use DH initialization in two places. First, we use it
to generate a tag set for the New Session Replies.
Second, we use it to generate two tag sets, one for each direction,
for use in Existing Session messages.

TODO why are we using the chain key after split() ?


.. raw:: html

  {% highlight lang='text' %}
Inputs:
  1) rootKey = chainKey from Payload Section
  2) k from the New Session KDF or split()

  // KDF_RK(rk, dh_out)
  keydata = HKDF(rootKey, k, "KDFDHRatchetStep", 64)

  // Output 1: The next Root Key (KDF input for the next ratchet)
  nextRootKey = keydata[0:31]
  // Output 2: The chain key to initialize the new
  // session tag and symmetric key ratchets
  // for Alice to Bob transmissions
  ck = keydata[32:63]

  // session tag and symmetric key chain keys
  keydata = HKDF(ck, ZEROLEN, "TagAndKeyGenKeys", 64)
  sessTag_ck = keydata[0:31]
  symmKey_ck = keydata[32:63]

{% endhighlight %}


DH RATCHET KDF
~~~~~~~~~~~~~~~

This is used after new DH keys are exchanged, before a tagset
is exhausted.

TODO

.. raw:: html

  {% highlight lang='text' %}

  // See New Session Reply KDF for generating Bob's reply message
  // and first set of ephemeral keys

  Received Next DH Key block:
  // Alice's generates new X25519 ephemeral keys
  rask = GENERATE_PRIVATE()
  rapk = DERIVE_PUBLIC(rask)
  
  rbsk = Bob's current ephemeral private key
  rbpk = DERIVE_PUBLIC(rbsk)

  sharedSecret = DH(rask, rbpk) = DH(rbsk, rapk)

  // KDF_RK(rk, dh_out)
  rootKey = nextRootKey from previous DH Ratchet
  keydata = HKDF(rootKey, sharedSecret, "KDFDHRatchetStep", 64)

  //TODO
  newTagSet = DH_INITIALIZE(rootKey, sharedSecret)

{% endhighlight %}


Notes
~~~~~

Bob may choose to rekey his ephemeral keys on receiving a Next DH Key block from Alice,
but care must be taken to not cause an infinite rekeying loop. Should a flag be included
in Next DH Key blocks for receiver rekey, or a timer be set from last rekey? TBD.

On receiving a Next DH Key block on a bound session, the corresponding outbound session
should be synchronized with the received ephemeral key, and a new ephemeral keypair
(unless recently rekeyed).


4b) Session Tag Ratchet
```````````````````````

Ratchets for every message, as in Signal.
The session tag ratchet is synchronized with the symmetric key ratchet,
but the receiver key ratchet may "lag behind" to save memory.

Transmitter ratchets once for each message transmitted.
No additional tags must be stored.
The transmitter must also keep a counter for 'N', the message number
of the message in the current chain. The 'N' value is included
in the sent message.
See the Message Number block definition.

Receiver must ratchet ahead by the max window size and store the tags in a "tag set",
which is associated with the session.
Once received, the stored tag may be discarded, and if there are no previous
unreceived tags, the window may be advanced.
The receiver should keep the 'N' value associated with each session tag,
and check that the number in the sent message matches this value.
See the Message Number block definition.


KDF
~~~

This is the definition of RATCHET_TAG().

.. raw:: html

  {% highlight lang='text' %}
Inputs:
  1) Session Tag Chain key sessTag_ck
     First time: output from DH ratchet
     Subsequent times: output from previous session tag ratchet

  Generated:
  2) input_key_material = SESSTAG_CONSTANT
     Must be unique for this chain (generated from chain key),
     so that the sequence isn't predictable, since session tags
     go out on the wire in plaintext.

  Outputs:
  1) N (the current session tag number)
  2) the session tag (and symmetric key, probably)
  3) the next Session Tag Chain Key (KDF input for the next session tag ratchet)

  Initialization:
  keydata = HKDF(sessTag_ck, ZEROLEN, "STInitialization", 64)
  // Output 1: Next chain key
  sessTag_chainKey = keydata[0:31]
  // Output 2: The constant
  SESSTAG_CONSTANT = keydata[32:63]

  // KDF_ST(ck, constant)
  keydata_0 = HKDF(sessTag_chainkey, SESSTAG_CONSTANT, "SessionTagKeyGen", 64)
  // Output 1: Next chain key
  sessTag_chainKey_0 = keydata_0[0:31]
  // Output 2: The session tag
  // or more if tag is longer than 8 bytes
  tag_0 = keydata_0[32:39]

  // repeat as necessary to get to tag_n
  keydata_n = HKDF(sessTag_chainKey_(n-1), SESSTAG_CONSTANT, "SessionTagKeyGen", 64)
  // Output 1: Next chain key
  sessTag_chainKey_n = keydata_n[0:31]
  // Output 2: The session tag
  // or more if tag is longer than 8 bytes
  tag_n = keydata_n[32:39]

{% endhighlight %}


4c) Symmetric Key Ratchet
`````````````````````````

Ratchets for every message, as in Signal.
Each symmetric key has an associated message number and session tag.
The session key ratchet is synchronized with the symmetric tag ratchet,
but the receiver key ratchet may "lag behind" to save memory.

Transmitter ratchets once for each message transmitted.
No additional keys must be stored.

When receiver gets a session tag, if it has not already ratcheted the
symmetric key ratchet ahead to the associated key, it must "catch up" to the associated key.
The receiver will probably cache the keys for any previous tags
that have not yet been received.
Once received, the stored key may be discarded, and if there are no previous
unreceived tags, the window may be advanced.

For efficiency, the session tag and symmetric key ratchets are separate so
the session tag ratchet can run ahead of the symmetric key ratchet.
This also provides some additional security, since the session tags go out on the wire.


KDF
~~~

This is the definition of RATCHET_KEY().

.. raw:: html

  {% highlight lang='text' %}
Inputs:
  1) Symmetric Key Chain key symmKey_ck
     First time: output from DH ratchet
     Subsequent times: output from previous symmetric key ratchet

  Generated:
  2) input_key_material = SYMMKEY_CONSTANT = ZEROLEN
     No need for uniqueness. Symmetric keys never go out on the wire.
     TODO: Set a constant anyway?

  Outputs:
  1) N (the current session key number)
  2) the session key
  3) the next Symmetric Key Chain Key (KDF input for the next symmetric key ratchet)

  // KDF_CK(ck, constant)
  SYMMKEY_CONSTANT = ZEROLEN
  // Output 1: Next chain key
  keydata_0 = HKDF(symmKey_ck, SYMMKEY_CONSTANT, "SymmetricRatchet", 64)
  symmKey_chainKey_0 = keydata_0[0:31]
  // Output 2: The symmetric key
  k_0 = keydata_0[32:63]

  // repeat as necessary to get to k[n]
  keydata_n = HKDF(symmKey_chainKey_(n-1), SYMMKEY_CONSTANT, "SymmetricRatchet", 64)
  // Output 1: Next chain key
  symmKey_chainKey_n = keydata_n[0:31]
  // Output 2: The symmetric key
  k_n = keydata_n[32:63]


{% endhighlight %}



5) Payload
----------

This replaces the AES section format defined in the ElGamal/AES+SessionTags specification.

This uses the same block format as defined in the [NTCP2]_ specification.
Individual block types are defined differently.

There are concerns that encouraging implementers to share code
may lead to parsing issues. Implementers should carefully consider
the benefits and risks of sharing code, and ensure that the
ordering and valid block rules are different for the two contexts.




Payload Section Decrypted data
``````````````````````````````

Encrypted length is the remainder of the data.
Decrypted length is 16 less than the encrypted length.
All block types are supported.
Typical contents include the following blocks:

==================================  ============= ============
       Payload Block Type            Type Number  Block Length
==================================  ============= ============
DateTime                                  0            7      
Session ID (debug)                        1            7      
Termination (TBD)                         4          TBD      
Options                                   5            9      
Message Numbers (TBD)                     6          TBD      
Next Key                                  7           37      
Next Key Ack (TBD)                        8          TBD      
ACK Request                               9         varies    
Garlic Clove                             11         varies    
Padding                                 254         varies    
==================================  ============= ============




Unencrypted data
````````````````
There are zero or more blocks in the encrypted frame.
Each block contains a one-byte identifier, a two-byte length,
and zero or more bytes of data.

For extensibility, receivers must ignore blocks with unknown identifiers,
and treat them as padding.

Encrypted data is 65535 bytes max, including a 16-byte authentication header,
so the max unencrypted data is 65519 bytes.

(Poly1305 auth tag not shown):

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |blk |  size   |       data             |
  +----+----+----+                        +
  |                                       |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |blk |  size   |       data             |
  +----+----+----+                        +
  |                                       |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  ~               .   .   .               ~

  blk :: 1 byte
         0 datetime
         1 session id
         2 reserved
         3 reserved
         4 termination
         5 options
         6 message number and previous message number (ratchet)
         7 next session key
         8 ack of reverse session key
         9 reply delivery instructions
         10 reserved
         11 Garlic Clove
         224-253 reserved for experimental features
         254 for padding
         255 reserved for future extension
  size :: 2 bytes, big endian, size of data to follow, 0 - 65516
  data :: the data

  Maximum ChaChaPoly frame is 65535 bytes.
  Poly1305 tag is 16 bytes
  Maximum total block size is 65519 bytes
  Maximum single block size is 65519 bytes
  Block type is 1 byte
  Block length is 2 bytes
  Maximum single block data size is 65516 bytes.

{% endhighlight %}


Block Ordering Rules
````````````````````
In the New Session message,
the DateTime block is required, and must be the first block.

Other allowed blocks:

- Garlic Clove (type 11)
- Options (type 5)
- Padding (type 254)

In the New Session Reply message,
no blocks are required.

Other allowed blocks:

- Garlic Clove (type 11)
- Options (type 5)
- Padding (type 254)

No other blocks are allowed.
Padding, if present, must be the last block.

In the Existing Session message, no blocks are required, and order is unspecified, except for the
following requirements:

Termination, if present, must be the last block except for Padding.
Padding, if present, must be the last block.

There may be multiple Garlic Clove blocks in a single frame.
Multiple Padding blocks are not allowed in a single frame.
Other block types probably won't have multiple blocks in
a single frame, but it is not prohibited.


DateTime
````````
An expiration.
Assists in reply prevention.
Bob must validate that the message is recent, using this timestamp.
Bob must implement a Bloom filter or other mechanism to prevent replay attacks,
if the time is valid.
Generally included in New Session messages only.

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+
  | 0  |    4    |     timestamp     |
  +----+----+----+----+----+----+----+

  blk :: 0
  size :: 2 bytes, big endian, value = 4
  timestamp :: Unix timestamp, unsigned seconds.
               Wraps around in 2106

{% endhighlight %}


Session ID
``````````
This may only be useful for debugging.

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+
  | 1  |    4    |        id         |
  +----+----+----+----+----+----+----+

  blk :: 1
  size :: 2 bytes, big endian, value = 4
  id :: random number

{% endhighlight %}


Garlic Clove
````````````

A single decrypted Garlic Clove as specified in [I2NP]_,
with modifications to remove fields that are unused
or redundant.
Garlic Cloves may not be fragmented across blocks or
across ChaChaPoly frames.

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | 11 |  size   |                        |
  +----+----+----+                        +
  |      Delivery Instructions            |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |type|  Message_ID       | Expiration   
  +----+----+----+----+----+----+----+----+
       |      I2NP Message body           |
  +----+                                  +
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  size :: size of all data to follow

  Delivery Instructions :: As specified in
         the Garlic Clove section of [I2NP]_.
         Length varies but is typically 1, 33, or 37 bytes

  type :: I2NP message type

  Message_ID :: 4 byte `Integer` I2NP message ID

  Expiration :: 4 bytes, seconds since the epoch

{% endhighlight %}

Notes
`````
- Implementers must ensure that when reading a block,
  malformed or malicious data will not cause reads to
  overrun into the next block.

- The Clove Set format specified in [I2NP]_ is not used.
  Each clove is contained in its own block.

- The I2NP message header is 9 bytes, with an identical format
  to that used in [NTCP2]_.

- The Certificate, Message ID, and Expiration from the
  Garlic Message definition in [I2NP]_ are not included.

- The Certificate, Clove ID, and Expiration from the
  Garlic Clove definition in [I2NP]_ are not included.

Justification
`````````````
- The certificates were never used.
- The separate message ID and clove IDs were never used.
- The separate expirations were never used.
- The overall savings compared to the old Clove Set and Clove formats
  is approximately 35 bytes for 1 clove, 54 bytes for 2 cloves,
  and 73 bytes for 3 cloves.
- The block format is extensible and any new fields may be added
  as new block types.


Termination
```````````
Drop the session.
This must be the last non-padding block in the frame.


.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | 4  |  size   |    valid data frames
  +----+----+----+----+----+----+----+----+
      received   | rsn|     addl data     |
  +----+----+----+----+                   +
  ~               .   .   .               ~
  +----+----+----+----+----+----+----+----+

  blk :: 4
  size :: 2 bytes, big endian, value = 9 or more
  valid data frames received :: The number of valid AEAD data phase frames received
                                (current receive nonce value)
                                0 if error occurs in handshake phase
                                8 bytes, big endian
  rsn :: reason, 1 byte:
         0: normal close or unspecified
         1: termination received
  addl data :: optional, 0 or more bytes, for future expansion, debugging,
               or reason text.
               Format unspecified and may vary based on reason code.

{% endhighlight %}

Notes
`````

Not all reasons may actually be used, implementation dependent.
Additional reasons listed are for consistency, logging, debugging, or if policy changes.




Options
```````
Pass updated options.
Options include various parameters for the session.
See the Session Tag Length Analysis section below for more information.

The options block may be variable length,
nine or more bytes, as more_options may be present.


.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | 5  |  size   |STL |OTW |STimeout |MITW|
  +----+----+----+----+----+----+----+----+
  |flg |         more_options             |
  +----+                                  +
  |                                       |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  blk :: 5
  size :: 2 bytes, big endian, size of options to follow, 6 bytes minimum
  STL :: Session tag length (default 8), min and max TBD
  OTW :: Outbound Session tag window (max lookahead)
  STimeout :: Session idle timeout
  MITW :: Max Inbound Session Tag window (max lookahead)
  flg :: 1 byte flags
         bit order: 76543210
         bit 0: 1 to request a ratchet (new key), 0 if not
         bits 7-1: Unused, set to 0 for future compatibility

  more_options :: Format TBD

{% endhighlight %}


Options Notes
`````````````
- Support for non-default session tag length is optional,
  probably not necessary

- The tag window is MAX_SKIP in the Signal documentation.



Options Issues
``````````````
- more_options format is TBD.
- Options negotiation is TBD.
- Padding parameters also?
- Is 255 big enough for max MITW?


Message Numbers
```````````````

The message's number (N) in the current sending chain (N=0,1,2,...)
and the length (number of message keys) in the previous sending chain (PN).
Also contains the public key id, used for acks.


.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | 6  |  size   | key ID |   PN    |  N
 +----+----+----+----+----+----+----+----+
      |
 +----+

  blk :: 6
  size :: 6
  Key ID :: The ID of the current key being used, 2 bytes big endian.
            65535 (0xffff) when in a New Session message.
  PN :: 2 bytes big endian. The number of keys in the previous sending chain.
        i.e. one more than the last 'N' sent in the previous chain.
        Use 0 if there was no previous sending chain.
  N :: 2 bytes big endian. The message number in the current sending chain.
       Starts with 0.

{% endhighlight %}


Notes
``````
- Maximum PN and N is 65535. Do not allow to roll over. Sender must ratchet the DH key, send it,
  and receive an ack, before the sending chain reaches 65535.

- N is not strictly needed in an Existing Session message, as it's associated with the Session Tag

- The definitions of PN and N are identical to that in Signal.
  This is similar to what Signal does, but in Signal, PN and N are in the header.
  Here, they're in the encrypted message body.

- Key ID can be just an incrementing counter.
  It may not be strictly necessary, but it's useful for debugging.
  Also, we use it for explicit ACKs.
  Signal does not use a key ID.




Next DH Ratchet Public Key
``````````````````````````
The next DH ratchet key is in the payload,
and it is optional. We don't ratchet every time.
(This is different than in signal, where it is in the header, and sent every time)
For typical usage patterns, Alice and Bob each ratchet a single time
at the beginning.

For the first ratchet,
Key ID = 0 and
Key = Alice's first ratchet public key rapk (See KDF for part 2),
remains constant for every New Session message for this session


.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | 7  |  size   |  key ID |              |
  +----+----+----+----+----+              +
  |                                       |
  +                                       +
  |     Next DH Ratchet Public Key        |
  +                                       +
  |                                       |
  +                        +----+----+----+
  |                        |
  +----+----+----+----+----+

  blk :: 7
  size :: 34
  key ID :: The key ID of this key. 2 bytes, big endian, used for ack
  Public Key :: The next public key, 32 bytes, little endian


{% endhighlight %}



Notes
``````

- Key ID can be just an incrementing counter.
  It may not be strictly necessary, but it's useful for debugging.
  Also, we use it for explicit ACKs.
  Signal does not use a key ID.


Issues
``````



Ack
```
This is only if an explicit ack was requested by the far end.
Multiple acks may be present to ack multiple messages.



.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | 8  |  size   |  key id |   N     |    |
  +----+----+----+----+----+----+----+    +
  |             more acks                 |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  blk :: 8
  size :: 4 * number of acks to follow, minimum 1 ack
  for each ack:
  key ID :: 2 bytes, big endian, from the message being acked
  N :: 2 bytes, big endian, from the message being acked


{% endhighlight %}


Notes
``````


Issues
``````



Ack Request
```````````
Delivery instructions for the ack.
To replace the out-of-band DeliveryStatus Message in the Garlic Clove.
Also (optionally) binds the outbound session to the far-end Destination or Router.

If an explicit ack is requested, the current key ID and message number (N)
are returned in an ack block. When a next public key is included,
any message sent to that key constitutes an ack, no explicit ack is required.



.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |  9 |  size   | sessionID         |flg |
  +----+----+----+----+----+----+----+----+
  |  Garlic Clove Delivery Instructions   |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  blk :: 9
  size :: varies, typically 100
  session ID :: reverse session ID, length 4 bytes big endian
  flg :: 1 byte flags
         bit order: 76543210
         bits 7-0: Unused, set to 0 for future compatibility
  Delivery Instructions :: as defined in I2NP spec, 33 bytes for DESTINATION type


{% endhighlight %}


Notes
``````

- When the delivery instructions contains the hash of the destination,
  and the session is not previously bound, this binds the session to the destination.

- After a session is bound, any subsequent destination delivery instructions must contain
  the same hash as previously, or this is an error.

- See ACK section above for more information.


Issues
``````

- Java router must have the actual signing private key, not a dummy,
  see new I2CP Create LeaseSet2 Message in proposal 123.

- For easier processing, LS clove should precede Garlic clove in the message.

- Is the next public key the right thing to sign?

- Use alice's static pubkey instead?



Padding
```````
All padding is inside AEAD frames.
TODO Padding inside AEAD should roughly adhere to the negotiated parameters.
TODO Bob sent his requested tx/rx min/max parameters in message 2.
TODO Alice sent her requested tx/rx min/max parameters in message 3.
Updated options may be sent during the data phase.
See options block information above.

If present, this must be the last block in the frame.



.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |254 |  size   |      padding           |
  +----+----+----+                        +
  |                                       |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  blk :: 254
  size :: 2 bytes, big endian, size of padding to follow
  padding :: random data

{% endhighlight %}

Notes
`````
- Padding strategies TBD.
- Minimum padding TBD.
- Padding-only frames are allowed.
- Padding defaults TBD.
- See options block for padding parameter negotiation
- See options block for min/max padding parameters
- Message size limit is 64KB. If more padding is necessary, send multiple frames.
- Router response on violation of negotiated padding is implementation-dependent.


Other block types
`````````````````
Implementations should ignore unknown block types for
forward compatibility, except in message 3 part 2, where
unknown blocks are not allowed.


Future work
```````````
- The padding length is either to be decided on a per-message basis and
  estimates of the length distribution, or random delays should be added.
  These countermeasures are to be included to resist DPI, as message sizes
  would otherwise reveal that I2P traffic is being carried by the transport
  protocol. The exact padding scheme is an area of future work, Appendix A
  provides more information on the topic.



Typical Usage Patterns
======================


HTTP GET
--------

This is the most typical use case, and most non-HTTP streaming use cases
will be identical to this use case as well.
A small initial message is sent, a reply follows,
and additional messages are sent in both directions.

An HTTP GET generally fits in a single I2NP message.
Alice sends a small request with a single new Session message, bundling a reply leaseset.
Alice includes immediate ratchet to new key.
Includes sig to bind to destination. No ack requested.

Bob ratchets immediately.

Alice ratchets immediately.

Continues on with those sessions.

.. raw:: html

  {% highlight %}
Alice                           Bob

  New Session (1b)     ------------------->
  with ephemeral key 1
  with static key for binding
  with next key
  with bundled HTTP GET
  with bundled LS
  without bundled Delivery Status Message

  any retransmissions, same as above

  following messages may arrive in any order:

  <--------------     New Session Reply (1g)
                      with Bob ephemeral key 1
                      with bundled HTTP reply part 1

  <--------------     New Session Reply (1g)
                      with Bob ephemeral key 2
                      with bundled HTTP reply part 2

  <--------------     New Session Reply (1g)
                      with Bob ephemeral key 3
                      with bundled HTTP reply part 3

  After reception of any of these messages,
  Alice switches to use Existing Session messages,
  creates a new inbound + outbound session pair,
  and ratchets.


  Existing Session     ------------------->
  with bundled streaming ack


  Existing Session     ------------------->
  with bundled streaming ack


  After reception of any of these messages,
  Bob switches to use Existing Session messages.


  <--------------     Existing Session
                      with bundled HTTP reply part 4


  Existing Session     ------------------->
  with bundled streaming ack

  <--------------     Existing Session
                      with bundled HTTP reply part 5

{% endhighlight %}



HTTP POST
---------

Alice has three options:

1) Send the first message only (window size = 1), as in HTTP GET.
   Not recommended.

2) Send up to streaming window, but using same Elligator2-encoded cleartext public key.
   All messages contain same next public key (ratchet).
   This will be visible to OBGW/IBEP because they all start with the same cleartext.
   Things proceed as in 1).
   Not recommended.

3) Recommended implementation.
   Send up to streaming window, but using a different Elligator2-encoded cleartext public key (session) for each.
   All messages contain same next public key (ratchet).
   This will not be visible to OBGW/IBEP because they all start with different cleartext.
   Bob must recognize that they all contain the same next public key,
   and respond to all with the same ratchet.
   Alice uses that next public key and continues.

Option 3 message flow:

.. raw:: html

  {% highlight %}
Alice                           Bob

  New Session (1b)     ------------------->
  with ephemeral key 1
  with static key for binding
  with bundled HTTP POST part 1
  with bundled LS
  without bundled Delivery Status Message


  New Session (1b)     ------------------->
  with ephemeral key 2
  with static key for binding
  with bundled HTTP POST part 2
  with bundled LS
  without bundled Delivery Status Message


  New Session (1b)     ------------------->
  with ephemeral key 3
  with static key for binding
  with bundled HTTP POST part 3
  with bundled LS
  without bundled Delivery Status Message


  following messages can arrive in any order:

  <--------------     New Session Reply (1g)
                      with Bob ephemeral key 1
                      with bundled streaming ack

  <--------------     New Session Reply (1g)
                      with Bob ephemeral key 2
                      with bundled streaming ack

  After reception of any of these messages,
  Alice switches to use Existing Session messages,
  creates a new inbound + outbound session pair,
  and ratchets.


  following messages can arrive in any order:


  Existing Session     ------------------->
  with bundled HTTP POST part 4

  Existing Session     ------------------->
  with next key
  with bundled HTTP POST part 5


  After reception of any of these messages,
  Bob switches to use Existing Session messages.


  <--------------     Existing Session
                      with bundled streaming ack

  After reception of any of this message,
  Alice switches to use Existing Session messages,
  and Alice ratchets.


  Existing Session     ------------------->
  with next key
  with bundled HTTP POST part 4

  after reception of this message, Bob ratchets

  Existing Session     ------------------->
  with next key
  with bundled HTTP POST part 5

  <--------------     Existing Session
                      with bundled streaming ack

{% endhighlight %}



Repliable Datagram
------------------

A single message, with a single reply expected.
Additional messages or replies may be sent.

Similar to HTTP GET, but with smaller options for session tag window size and lifetime.
Maybe don't request a ratchet.

.. raw:: html

  {% highlight %}
Alice                           Bob

  New Session (1b)     ------------------->
  with static key for binding
  with next key
  with bundled repliable datagram
  with bundled LS
  without bundled Delivery Status Message


  <--------------     New Session Reply (1g)
                      with Bob ephemeral key
                      with bundled reply part 1

  <--------------     New Session Reply (1g)
                      with Bob ephemeral key
                      with bundled reply part 2

  After reception of either message,
  Alice switches to use Existing Session messages,
  and ratchets.

  If the Existing Session message arrives first,
  Alice ratchets on the existing inbound and outbound
  sessions.

  When the New Session Reply arrives, Alice
  sets the existing inbound session to expire,
  creates a new inbound and outbound session,
  and sends Existing Session messages on
  the new outbound session.

  Alice keeps the expiring inbound session
  around for a while to process the Existing Session
  message sent to Alice.
  If all expected original Existing Session message replies
  have been processed, Alice can expire the original
  inbound session immediately.

  if there are any other messages:

  Existing Session     ------------------->
  with bundled message

  Existing Session     ------------------->
  with bundled streaming ack

  <--------------     Existing Session
                      with bundled message

{% endhighlight %}



Multiple Raw Datagrams
----------------------

Multiple anonymous messages, with no replies expected.

In this scenario, Alice requests a session, but without binding.
New session message is sent.
No reply LS is bundled.
A reply DSM is bundled (this is the only use case that requires bundled DSMs).
No next key is included. No reply or ratchet is requested.
No ratchet is sent.
Options set session tags window to zero.

.. raw:: html

  {% highlight %}
Alice                           Bob

  New Session (1c)     ------------------->
  with bundled message
  without bundled LS
  with bundled Delivery Status Message 1

  New Session (1c)     ------------------->
  with bundled message
  without bundled LS
  with bundled Delivery Status Message 2

  New Session (1c)     ------------------->
  with bundled message
  without bundled LS
  with bundled Delivery Status Message 3
 
  following messages can arrive in any order:

  <--------------     Delivery Status Message 1

  <--------------     Delivery Status Message 2

  <--------------     Delivery Status Message 3

  After reception of any of these messages,
  Alice switches to use Existing Session messages.

  Existing Session     ------------------->

  Existing Session     ------------------->

  Existing Session     ------------------->

{% endhighlight %}



Single Raw Datagram
-------------------

A single anonymous messages, with no reply expected.

One-time message is sent.
No reply LS or DSM are bundled. No next key is included. No reply or ratchet is requested.
No ratchet is sent.
Options set session tags window to zero.

.. raw:: html

  {% highlight %}
Alice                           Bob

  One-Time Message (1d)   ------------------->
  with bundled message
  without bundled LS
  without bundled Delivery Status Message

{% endhighlight %}



Long-Lived Sessions
-------------------

Long-lived sessions may ratchet, or request a ratchet, at any time,
to maintain forward secrecy from that point in time.
Sessions must ratchet as they approach the limit of sent messages per-session (65535).



Implementation Considerations
=============================

As with the existing ElGamal/AES+SessionTag protocol, implementations must
limit session tag storage and protect against memory exhaustion attacks.

Some recommended strategies include:

- Hard limit on number of session tags stored
- Aggressive expiration of idle inbound sessions when under memory pressure
- Limit on number of inbound sessions bound to a single far-end destination
- Adaptive reduction of session tag window and deletion of old unused tags
  when under memory pressure
- Refusal to ratchet when requested, if under memory pressure



Identification at Receiver
==========================

Following are recommendations for classifying incoming messages.


X25519 Only
-----------

On a tunnel that is solely used with this protocol, do identification
as is done currently with ElGamal/AES+SessionTags:

First, treat the initial data as a session tag, and look up the session tag.
If found, decrypt using the stored data associated with that session tag.

If not found, treat the initial data as a DH public key and nonce.
Perform a DH operation and the specified KDF, and attempt to decrypt the remaining data.


X25519 Shared with ElGamal/AES+SessionTags
------------------------------------------

On a tunnel that supports both this protocol and
ElGamal/AES+SessionTags, classify incoming messages as follows:

Due to a flaw in the ElGamal/AES+SessionTags specification,
the AES block is not padded to a random non-mod-16 length.
Therefore, the length of Existing Session messages mod 16 is always 0,
and the length of New Session messages mod 16 is always 2 (since the
ElGamal block is 514 bytes long).

If the length mod 16 is not 0 or 2,
treat the initial data as a session tag, and look up the session tag.
If found, decrypt using the stored data associated with that session tag.

If not found, and the length mod 16 is not 0 or 2,
treat the initial data as a DH public key and nonce.
Perform a DH operation and the specified KDF, and attempt to decrypt the remaining data.
(based on the relative traffic mix, and the relative costs of X25519 and ElGamal DH operations,
ths step may be done last instead)

Otherwise, if the length mod 16 is 0,
treat the initial data as a ElGamal/AES session tag, and look up the session tag.
If found, decrypt using the stored data associated with that session tag.

If not found, and the data is at least 642 (514 + 128) bytes long,
and the length mod 16 is 2,
treat the initial data as a ElGamal block.
Attempt to decrypt the remaining data.

Note that if the ElGamal/AES+SessionTag spec is updated to allow
non-mod-16 padding, things will need to be done differently.




Analysis
========


Bandwidth overhead estimate
----------------------------

Message overhead for the first two messages in each direction are as follows.
This assumes only one message in each direction before the ACK,
or that any additional messages are sent speculatively as Existing Session messages.
If there is no speculative acks of delivered session tags, the
overhead or the old protocol is much higher.

No padding is assumed for the new protocol.


For ElGamal/AES+SessionTags
```````````````````````````

New session message, same each direction:


.. raw:: html

  {% highlight lang='text' %}
ElGamal block:
  514 bytes

  AES block:
  - 2 byte tag count
  - 1024 bytes of tags (32 typical)
  - 4 byte payload size
  - 32 byte hash of payload
  - 1 byte flags
  - 8 byte (average) padding to 16 bytes
  1071 total

  Total:
  1585 bytes
{% endhighlight %}

Existing session messages, same each direction:

.. raw:: html

  {% highlight lang='text' %}
AES block:
  - 32 byte session tag
  - 2 byte tag count
  - 4 byte payload size
  - 32 byte hash of payload
  - 1 byte flags
  - 8 byte (average) padding to 16 bytes
  79 total

  Four message total (two each direction)
  3328 bytes
{% endhighlight %}


For ECIES-X25519-AEAD-Ratchet
`````````````````````````````

TODO update this section after proposal is stable.

Alice-Bob New Session message:

.. raw:: html

  {% highlight lang='text' %}
- 32 byte public key
  - 8 byte nonce
  - 6 byte message ID block
  - 7 byte options block
  - 37 byte next key ratchet block
  - 103 byte ack request block
  - 3 byte I2NP block overhead ?
  - 16 byte Poly1305 tag

  Total:
  212 bytes
{% endhighlight %}

Bob-Alice Existing Session message:

.. raw:: html

  {% highlight lang='text' %}
- 8 byte session tag
  - 6 byte message ID block
  - 7 byte options block
  - 37 byte next key ratchet block
  - 4 byte ack request block
  - 3 byte I2NP block overhead ?
  - 16 byte Poly1305 tag

  Total:
  81 bytes
{% endhighlight %}

Existing session messages, same each direction:

.. raw:: html

  {% highlight lang='text' %}
- 8 byte session tag
  - 6 byte message ID block
  - 3 byte I2NP block overhead ?
  - 16 byte Poly1305 tag

  Total:
  33 bytes
{% endhighlight %}

Four message total (two each direction):

.. raw:: html

  {% highlight lang='text' %}
359 bytes
  89% (approx. 10x) reduction compared to ElGamal/AEs+SessionTags
{% endhighlight %}


Processing overhead estimate
----------------------------

TODO update this section after proposal is stable.

The following cryptographic operations are required by each party to initiate
a New Session and do the first ratchet:

- HMAC-SHA256: 3 per HKDF, total TBD
- ChaChaPoly: 2 each
- X25519 key generation: 2 Alice, 1 Bob
- X25519 DH: 3 each
- Signature verification: 1 (Bob)

Alice calculates 5 ECDHs per-bound-session (minimum), 2 for each NS message to Bob,
and 3 for each of Bob's NSR messages.

Bob also calculates 6 ECDHs per-bound-session, 3 for each of Alice's NS messages, and 3 for each of his NSR messages.

The following cryptographic operations are required by each party for each data phase message:

- ChaChaPoly: 1



Session Tag Length Analysis
---------------------------

Current session tag length is 32 bytes.
We have not yet found any justification for that length, but we are continuing to research the archives.
The proposal above defines the new tag length as 8 bytes.
This decision is preliminary.
The analysis justifying an 8 byte tag is as follows:

The session tag ratchet is assumed to generate random, uniformly distributed tags.
There is no cryptographic reason for a particular session tag length.
The session tag ratchet is synchronized to, but generates an independent output from,
the symmetric key ratchet. The outputs of the two ratchets may be different lengths.

Therefore, the only concern is session tag collision.
It is assumed that implementations will not attempt to handle collisions
by trying to decrypt with both sessions;
implementations will simply associate the tag with either the previous or new
session, and any message received with that tag on the other session
will be dropped after the decryption fails.

The goal is to select a session tag length that is large enough
to minimize the risk of collisions, while small enough
to minimize memory usage.

This assumes that implementations limit session tag storage to
prevent memory exhaustion attacks. This also will greatly reduce the chances that an attacker
can create collisions. See the Implementation Considerations section below.

For a worst case, assume a busy server with 64 new inbound sessions per second.
Assume 15 minute inbound session tag lifetime (same as now, probably should be reduced).
Assume inbound session tag window of 32.
64 * 15 * 60 * 32 =  1,843,200 tags
Current Java I2P max inbound tags is 750,000 and has never been hit as far as we know.

A target of 1 in a million (1e-6) session tag collisions is probably sufficient.
The probability of dropping a message along the way due to congestion is far higher than that.

Ref: https://en.wikipedia.org/wiki/Birthday_paradox
Probability table section.

With 32 byte session tags (256 bits) the session tag space is 1.2e77.
The probability of a collision with probability 1e-18 requires 4.8e29 entries.
The probability of a collision with probability 1e-6 requires 4.8e35 entries.
1.8 million tags of 32 bytes each is about 59 MB total.

With 16 byte session tags (128 bits) the session tag space is 3.4e38.
The probability of a collision with probability 1e-18 requires 2.6e10 entries.
The probability of a collision with probability 1e-6 requires 2.6e16 entries.
1.8 million tags of 16 bytes each is about 30 MB total.

With 8 byte session tags (64 bits) the session tag space is 1.8e19.
The probability of a collision with probability 1e-18 requires 6.1 entries.
The probability of a collision with probability 1e-6 requires 6.1e6 (6,100,000) entries.
1.8 million tags of 8 bytes each is about 15 MB total.

6.1 million active tags is over 3x more than our worst-case estimate of 1.8 million tags.
So the probability of collision would be less than one in a million.
We therefore conclude that 8 byte session tags are sufficient.
This results in a 4x reduction of storage space,
in addition to the 2x reduction because transmit tags are not stored.
So we will have a 8x reduction in session tag memory usage compared to ElGamal/AES+SessionTags.

To maintain flexibility should these assumptions be wrong,
we will include a session tag length field in the options,
so that the default length may be overridden on a per-session basis.
We do not expect to implement dynamic tag length negotiation
unless absolutely necessary.

Implementations should, at a minimum, recognize session tag collisions,
handle them gracefully, and log or count the number of collisions.
While still extremely unlikely, they will be much more likely than
they were for ElGamal/AES+SessionTags, and could actually happen.


Alternate analysis
``````````````````

Using twice the sessions per second (128) and twice the tag window (64),
we have 4 times the tags (7.4 million). Max for one in a million
chance of collision is 6.1 million tags.
12 byte (or even 10 byte) tags would add a huge margin.

However, is the one in a million chance of collision a good target?
Much larger than the chance of being dropped along the way is not much use.
The false-positive target for Java's DecayingBloomFilter is roughly
1 in 10,000, but even 1 in 1000 isn't of grave concern.
By reducing the target to 1 in 10,000, there's plenty of margin
with 8 byte tags.




Common Structures Spec Changes Required
=======================================

TODO


Key Certificates
----------------



Encryption Spec Changes Required
================================

TODO



I2NP Changes Required
=====================

TODO



I2CP Changes Required
=====================

I2CP Options
------------

This section is copied from proposal 123.

New options in SessionConfig Mapping:

::

  i2cp.leaseSetEncType=nnn  The encryption type to be used.
                            0: ElGamal
                            1-3: See proposal 145
                            4: This proposal.
                            Other values to be defined in future proposals.


Create Leaseset2 Message
------------------------

See proposal 123 for specification.


SAM Changes Required
====================

TODO



BOB Changes Required
====================

TODO




Publishing, Migration, Compatibility
====================================

TODO



References
==========

.. [Elligator2]
    https://elligator.cr.yp.to/elligator-20130828.pdf
    https://www.imperialviolet.org/2013/12/25/elligator.html
    See also OBFS4 code

.. [GARLICSPEC]
    {{ site_url('docs/how/garlic-routing', True) }}

.. [I2NP]
    {{ spec_url('i2np') }}

.. [NTCP2]
    {{ spec_url('ntcp2') }}

.. [NOISE]
    http://noiseprotocol.org/noise.html

.. [Prop111]
    {{ proposal_url('111') }}

.. [Prop123]
    {{ proposal_url('123') }}

.. [Prop142]
    {{ proposal_url('142') }}

.. [RFC-2104]
    https://tools.ietf.org/html/rfc2104

.. [RFC-5869]
    https://tools.ietf.org/html/rfc5869

.. [RFC-7539]
    https://tools.ietf.org/html/rfc7539

.. [RFC-7748]
    https://tools.ietf.org/html/rfc7748

.. [RFC-7905]
    https://tools.ietf.org/html/rfc7905

.. [RFC-4880-S5.1]
    https://tools.ietf.org/html/rfc4880#section-5.1

.. [Signal]
    https://signal.org/docs/specifications/doubleratchet/

.. [SSU]
    {{ site_url('docs/transport/ssu', True) }}

.. [STS]
    Diffie, W.; van Oorschot P. C.; Wiener M. J., Authentication and
    Authenticated Key Exchanges
