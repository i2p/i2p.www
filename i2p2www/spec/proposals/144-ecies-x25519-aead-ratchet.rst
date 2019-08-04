=========================
ECIES-X25519-AEAD-Ratchet
=========================
.. meta::
    :author: zzz, chisana
    :created: 2018-11-22
    :thread: http://zzz.i2p/topics/2639
    :lastupdated: 2019-08-04
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
- 111 NTCP2
- 123 New netDB Entries
- 142 New Crypto Template
- Signal double ratchet algorithm https://signal.org/docs/specifications/doubleratchet/

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
   No proposal yet.

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
- Eliminate new vs. existing session length classification (support padding)
- No new I2NP messages required
- Replace SHA-256 checksum in AES payload with AEAD
- (Optimistic) Add extensions or hooks to support multicast
- Support binding of transmit and receive sessions so that
  acknowledgements may happen within the protocol, rather than solely out-of-band.
  This will also allow replies to have forward secrecy immediately.
- Enable end-to-end encryption of certain messages (RouterInfo stores)
  that we currently don't due to CPU overhead.
- Do not change the I2NP Garlic Message, Garlic Message Clove,
  or Garlic Message Delivery Instructions format.


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


Threat Model
------------

The threat model is somewhat different than for NTCP2 (proposal 111).
The MitM nodes are the OBEP and IBGW and are assumed to have full view of
the current or historical global NetDB, by colluding with floodfills.

The goal is to prevent these MitMs from classifying traffic as
new and existing session messages, or as new crypto vs. old crypto.



Detailed Proposal
=================

This proposal defines a new end-to-end protocol to replace ElGamal/AES+SessionTags.


Summary of Cryptographic Design
-------------------------------

There are five portions of the protocol to be redesigned:


- 1) The new and existing session container formats
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

Existing I2P router implementations that have not yet implemented NTCP2 (Proposal 111)
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



Sessions
--------

The current ElGamal/AES+SessionTag protocol is unidirectional.
At this layer, the receiver doesn't know where a message is from.
Outbound and inbound sessions are not associated.
Acknowledgements are out-of-band using a DeliveryStatusMessage
(wrapped in a GarlicMessage) in the clove.

There is substantial inefficiency in a unidirectional protocol.
Any reply must also use an expensive 'new session' message.
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
If Alice includes binding information (her static key) in the new session message,
the session will be bound to that destination,
and a outbound session will be created and bound to same Destination.
As the sessions ratchet, they continue to be bound to the far-end Destination.


Benefits of Binding and Pairing
```````````````````````````````

For the common, streaming case, we expect Alice and Bob to use the protocol as follows:

- Alice pairs her new outbound session to a new inbound session, both bound to the far-end destination (Bob).
- Alice includes the binding information and signature, and a reply request, in the
  new session message sent to Bob.
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

An explicit ACK is simply an existing session message with no I2NP block.
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

    Use SHA-256 as follows::

        H(p, d) := SHA-256(p || d)

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

    DECODE_ELG2(pubkey)
        Returns the public key corresponding to the given Elligator2-encoded public key.

    DH(privkey, pubkey)
        Generates a shared secret from the given private and public keys.

HKDF(salt, ikm, info, n)
    A cryptographic key derivation function which takes some input key material ikm (which
    should have good entropy but is not required to be a uniformly random string), a salt
    of length 32 bytes, and a context-specific 'info' value, and produces an output
    of n bytes suitable for use as key material.

    Use HKDF as specified in [RFC-5869]_, using the HMAC hash function SHA-256
    as specified in [RFC-2104]_. This means that SALT_LEN is 32 bytes max.


Issues
------

- Use Blake2b instead of SHA256?


1) Message format
-----------------

Review of Current Message Format
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
so the new session is always (mod 16 == 2),
and an existing session is always (mod 16 == 0).
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

In new session, we put only the public key in the unencrytped header.

In existing session, we use a session tag for the header.
The session tag is associated with the current ratchet public key,
and the message number.

In both new and existing session, PN and N are in the encrypted body.

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

The new session message may or may not contain the sender's static public key.
If it is included, the reverse session is bound to that key.
The static key should be included if replies are expected,
i.e. for streaming and repliable datagrams.
It should not be included for raw datagrams.

The new session message is similar to the one-way Noise [NOISE]_ patterns
"N" (if the static key is not sent)
or "X" (if the static key is sent).



1b) New session format (with binding)
-------------------------------------

Encrypted:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   New Session One Time Public Key     |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +        Ephemeral Key Section          +
  |       ChaCha20 encrypted data         |
  +            40 bytes                   +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +         (MAC) for above section       +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +         Static Key Section            +
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

  Ephemeral Key Section encrypted data :: 40 bytes

  Static Key Section encrypted data :: 32 bytes

  Payload Section encrypted data :: remaining data minus 16 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}



1c) New session format (without binding)
----------------------------------------

Encrypted:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   New Session One Time Public Key     |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +        Ephemeral Key Section          +
  |       ChaCha20 encrypted data         |
  +            40 bytes                   +
  |                                       |
  +                                       +
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

  Ephemeral Key Section encrypted data :: 40 bytes

  Payload Section encrypted data :: remaining data minus 16 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}



1d) One-time format (no binding or session)
-------------------------------------------

If only a single message is expected to be sent,
no session setup or ephemeral key is required.


Encrypted:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   New Session One Time Public Key     |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +           Flags Section               +
  |       ChaCha20 encrypted data         |
  +            40 bytes                   +
  |                                       |
  +                                       +
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

  Flags Section encrypted data :: 40 bytes

  Payload Section encrypted data :: remaining data minus 16 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}



1e) New session contents
------------------------


New Session One Time Key
````````````````````````

The one time key is 32 bytes, encoded with Elligator2.
This key is never reused; a new key is generated with
each message, including retransmissions.


Ephemeral Key Section Decrypted data
````````````````````````````````````

The Ephemeral Key section contains flags and a key.
It is always 40 bytes.
When used in the one-time message, the key is all zeroes.


.. raw:: html

  {% highlight lang='dataspec' %}

flags :: 2 bytes
         bit order: 15 14 .. 3210
         bit 0: 1 if ephemeral key is to be used, 0 if not
         bit 1: 1 if Static Key Section follows, 0 if not
         bits 15-2: Unused, set to 0 for future compatibility
  num :: Message number, 2 bytes
  unused :: 4 bytes
  key :: the originator's ephemeral key, 32 bytes.
         All zeros if flags bit 0 is not set
         Set to 0 for future compatibility

{% endhighlight %}


Static Key Section Decrypted data
`````````````````````````````````

The Static Key Section contains the originator's static key, 32 bytes.



Payload Section Decrypted data
``````````````````````````````

See AEAD section below.
Encrypted length is the remainder of the data.
Decrypted length is 16 less than the encrypted length.
All block types are supported.
Typical contents include the following blocks:

==================================  ============= ============
       Payload Block Type            Type Number  Block Length
==================================  ============= ============
DateTime                                  0            7      
I2NP Message                              3         varies    
Options                                   5            9      
Message Number                            6            9      
Next Key                                  7           37      
ACK Request                               9         varies    
Padding                                 254         varies    
==================================  ============= ============


DateTime Message Contents
~~~~~~~~~~~~~~~~~~~~~~~~~

The current time.


I2NP Message Contents
~~~~~~~~~~~~~~~~~~~~~

The I2NP message sent.


Options Contents
~~~~~~~~~~~~~~~~

See the Session Tag Length Analysis section below for more information.

- STL = 8


Message Number Contents
~~~~~~~~~~~~~~~~~~~~~~~

- Key ID = 65535 (0xffff)
- PN = 0
- N starts with 0, incremented with every new session message sent with the same "next key"


Next Key Contents
~~~~~~~~~~~~~~~~~

- Key ID = 0
- Key = Alice's first ratchet public key rapk (See KDF for part 2 below),
  remains constant for every new session message for this session


ACK Request Contents
~~~~~~~~~~~~~~~~~~~~

Delivery instructions for the ack.


Padding Contents
~~~~~~~~~~~~~~~~

As desired.



1f) KDFs for New Session Message
--------------------------------


KDF for Ephemeral Key Section Encrypted Contents
````````````````````````````````````````````````

.. raw:: html

  {% highlight lang='text' %}
// Bob's X25519 static keys
  // bpk is published in leaseset
  bsk = GENERATE_PRIVATE()
  bpk = DERIVE_PUBLIC(bsk)

  // Alice's X25519 one-time-use ephemeral keys
  ask = GENERATE_PRIVATE_ELG2()
  apk = DERIVE_PUBLIC(ask)
  // eapk is sent in cleartext in the
  // beginning of the new session message
  eapk = ENCODE_ELG2(apk)
  // As decoded by Bob
  apk = DECODE_ELG2(eapk)

  INITIAL_ROOT_KEY = SHA256("144-ECIES-X25519-AEAD-Ratchet")

  sharedSecret = DH(ask, bpk) = DH(bsk, apk)

  // MixKey(DH())
  // ChaChaPoly parameters to encrypt/decrypt
  keydata = HKDF(INITIAL_ROOT_KEY, sharedSecret, "NewSessionTmpKey", 64)
  chainKey = keydata[0:31]
  k = keydata[32:64]
  n = 0
  ad = SHA-256(eapk)

{% endhighlight %}



KDF for Static Key Section Encrypted Contents
`````````````````````````````````````````````

Only present if indicated in Ephemeral Key Section flags.

TODO we can't really use the chainKey from above, or
else we won't end up with the same key from multiple
new session messages.


.. raw:: html

  {% highlight lang='text' %}
// Bob's X25519 static keys
  // bpk is published in leaseset
  bsk = GENERATE_PRIVATE()
  bpk = DERIVE_PUBLIC(bsk)

  // Alice's X25519 reusable ephemeral keys
  ask = GENERATE_PRIVATE()
  // apk was decrypted in Ephemeral Key Section
  apk = DERIVE_PUBLIC(ask)

  sharedSecret = DH(ask, bpk) = DH(bsk, apk)

  // MixKey(DH())
  // ChaChaPoly parameters to encrypt/decrypt
  // chainKey from Ephemeral Key Section
  keydata = HKDF(chainKey, sharedSecret, "EphemperalPart2x", 64)
  chainKey = keydata[0:31]
  k = keydata[32:64]
  n = 0
  ad = SHA-256(apk)

{% endhighlight %}



KDF for Payload Section (with Alice static key)
```````````````````````````````````````````````

.. raw:: html

  {% highlight lang='text' %}
// Bob's X25519 static keys
  // bpk is published in leaseset
  bsk = GENERATE_PRIVATE()
  bpk = DERIVE_PUBLIC(bsk)

  // Alice's X25519 static keys
  ask = GENERATE_PRIVATE()
  // apk was decrypted in Static Key Section
  apk = DERIVE_PUBLIC(ask)

  sharedSecret = DH(ask, bpk) = DH(bsk, apk)

  // MixKey(DH())
  // ChaChaPoly parameters to encrypt/decrypt
  // chainKey from Static Key Section
  k = HKDF(chainKey, sharedSecret, "Part3StaticKeyHK", 64)
  chainKey = keydata[0:31]
  k = keydata[32:64]
  n = message number from Ephemeral Key Section
  ad = SHA-256(apk)

{% endhighlight %}


KDF for Payload Section (without Alice static key)
``````````````````````````````````````````````````

.. raw:: html

  {% highlight lang='text' %}
// Bob's X25519 static keys
  // bpk is published in leaseset
  bsk = GENERATE_PRIVATE()
  bpk = DERIVE_PUBLIC(bsk)

  // Alice's X25519 ephemeral keys
  ask = GENERATE_PRIVATE()
  // apk was decrypted in Ephemeral Key Section
  apk = DERIVE_PUBLIC(ask)

  sharedSecret = DH(ask, bpk) = DH(bsk, apk)

  // MixKey(DH())
  // ChaChaPoly parameters to encrypt/decrypt
  // chainKey from Ephemeral Key Section
  k = HKDF(chainKey, sharedSecret, "Part3EphemeralHK", 64)
  chainKey = keydata[0:31]
  k = keydata[32:64]
  n = message number from Ephemeral Key Section
  ad = SHA-256(apk)

{% endhighlight %}


KDF for Payload Section (one-time format)
`````````````````````````````````````````

.. raw:: html

  {% highlight lang='text' %}
// Bob's X25519 static keys
  // bpk is published in leaseset
  bsk = GENERATE_PRIVATE()
  bpk = DERIVE_PUBLIC(bsk)

  // Alice's X25519 ephemeral keys
  // Alice's decoded one-time keys
  ask = GENERATE_PRIVATE()
  // Alice's decoded one-time public key
  apk = DERIVE_PUBLIC(ask)

  sharedSecret = DH(ask, bpk) = DH(bsk, apk)

  // MixKey(DH())
  // ChaChaPoly parameters to encrypt/decrypt
  k = HKDF(INITIAL_ROOT_KEY, sharedSecret, "Part3OneTimeKeys", 64)
  chainKey = keydata[0:31]
  k = keydata[32:64]
  n = 0
  ad = SHA-256(apk)

{% endhighlight %}




Justification
`````````````

By using a ratchet (a synchronized PRNG) to generate the
session tags, we eliminate the overhead of sending session tags
in the new session message and subsequent messages when needed.
For a typical tag set of 32 tags, this is 1KB.
This also eliminates the storage of session tags on the sending side,
thus cutting the storage requirements in half.


Notes
`````

This allows sending multiple new session messages with the same initial ratchet key,
which is more efficient, e.g. for a POST.
These messages will have a different cleartext (new session) key but contain
the same ratchet key inside the first AEAD block.
New session keys are never reused.
This prevents external observers from identifying a POST sequence through
seeing duplicate cleartext keys. However, these messages may still be
identified as containing keys, so we must use Elligator2.
The first AEAD block will contain a sequence number and/or IV so the second block may
be decrypted correctly.




1g) Existing session format
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
  +                                       +
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

  encrypted data :: Same size as plaintext data, size varies

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}


Decrypted:
  See AEAD section below.


KDF
```

.. raw:: html

  {% highlight lang='text' %}
See message key ratchet below.

  Key: KDF TBD
  IV: KDF TBD
  Nonce: The message number N in the current chain, as retrieved from the associated Session Tag.
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

Used in NTCP2.



Notes
`````


Issues
``````



2a) Elligator2
--------------


Format
``````

32-byte public and private keys.


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

Additionally, the unsuitable keys may be added to the pool of keys
used for NTCP2, where Elligator2 is not used.
The security issues of doing so is TBD.




3) AEAD (ChaChaPoly)
--------------------

AEAD using ChaCha20 and Poly1305, same as in NTCP2.


New Session Inputs
``````````````````

Inputs to the encryption/decryption functions
for an AEAD block in a new session message:

.. raw:: html

  {% highlight lang='dataspec' %}
k :: 32 byte cipher key
       See new session message KDF above.

  n :: Counter-based nonce, 12 bytes.
       n = 0

  ad :: Associated data, 32 bytes.
        The SHA256 hash of the preceding data (public key)

  data :: Plaintext data, 0 or more bytes

{% endhighlight %}


Existing Session Inputs
```````````````````````

Inputs to the encryption/decryption functions
for an AEAD block in an existing session message:

.. raw:: html

  {% highlight lang='dataspec' %}
k :: 32 byte cipher key
       As looked up from the accompanying session tag.

  n :: Counter-based nonce, 12 bytes.
       Starts at 0 and incremented for each message.
       First four bytes are always zero.
       As looked up from the accompanying session tag.
       Last eight bytes are the message number (n), little-endian encoded.
       Maximum value is 2**64 - 2.
       Session must be ratcheted before N reaches that value.
       The value 2**64 - 1 must never be used.

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

For ChaCha20, what is described here corresponds to [RFC-7539]_, which is also
used similarly in TLS [RFC-7905]_.

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

Used in NTCP2.


Notes
`````


Issues
``````

Avoid using random nonces. If we do need random nonces,
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

Note: The new session one-time public key is not part of the ratchet, its sole function
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



4a) DH Ratchet
``````````````

Ratchets but not nearly as fast as Signal does.
We separate the ack of the received key from generating the new key.
In typical usage, Alice and Bob will each ratchet (twice) immediately in a new session,
but will not ratchet again.

Note that a ratchet is for a single direction, and generates a new session tag / message key ratchet chain for that direction.
To generate keys for both directions, you have to ratchet twice.

You ratchet every time you generate and send a new key.
You ratchet every time you receive a new key.

Alice ratchets once when she initiates a new outbound session and creates the corresponding inbound session.
Bob ratchets twice when he receives the inbound session and creates the corresponding outbound session,
once for the new key received, and once for the new key generated.
Alice ratchets once when she receives the new key on the inbound session and replaces the corresponding outbound session.
So each side ratchets twice total, in the typical case.

The frequency of ratchets after the initial handshake is implementation-dependent.
While the protocol places a limit of 65535 messages before a ratchet is required,
more frequent ratcheting (based on message count, elapsed time, or both)
may provide additional security.


KDF
~~~

.. raw:: html

  {% highlight lang='text' %}
Inputs:
  1) Root key
  2) sharedSecret (the DH result from the new session message)

  First time:
  // Alice generates her first ephemeral DH key pair
  // Alice's first ratchet X25519 ephemeral keys
  rask = GENERATE_PRIVATE()
  // rapk is sent encrypted in the new session message
  rapk = DERIVE_PUBLIC(rask)

  // Bob's X25519 static keys
  // bpk is published in Bob's leaseset
  bsk = GENERATE_PRIVATE()
  bpk = DERIVE_PUBLIC(bsk)

  INITIAL_ROOT_KEY = SHA256("144-ECIES-X25519-AEAD-Ratchet")

  sharedSecret = DH(rask, bpk) = DH(bsk, rapk)

  // KDF_RK(rk, dh_out)
  keydata = HKDF(INITIAL_ROOT_KEY, sharedSecret, "KDFDHRatchetStep", 64)
  // Output 1: The next Root Key (KDF input for the next ratchet)
  nextRootKey = keydata[0:31]
  // Output 2: The chain key to initialize the new
  // session tag and symmetric key ratchets
  // for Bob to Alice transmissions
  ck = keydata[32:63]
  keydata = HKDF(ck, ZEROLEN, "TagAndKeyGenKeys", 64)
  sessTag_ck = keydata[0:31]
  symmKey_ck = keydata[32:63]


  Second time:
  // Bob generates his first ephemeral DH key pair
  // Alice's first ratchet X25519 ephemeral keys
  rbsk = GENERATE_PRIVATE()
  // rbpk is sent encrypted in the reply
  rbpk = DERIVE_PUBLIC(rbsk)

  // Alice's first ratchet X25519 ephemeral keys
  // from new session message
  rask = As generated for new session message
  rapk = from new session message

  sharedSecret = DH(rask, rbpk) = DH(rbsk, rapk)

  // KDF_RK(rk, dh_out)
  rootKey = nextRootKey
  keydata = HKDF(rootKey, sharedSecret, "KDFDHRatchetStep", 64)
  // Output 1: The next Root Key (KDF input for the next ratchet)
  nextRootKey = keydata[0:31]
  // Output 2: The chain key to initialize the new
  // session tag and symmetric key ratchets
  // for Alice to Bob transmissions
  ck = keydata[32:63]
  keydata = HKDF(ck, ZEROLEN, "TagAndKeyGenKeys", 64)
  sessTag_ck = keydata[0:31]
  symmKey_ck = keydata[32:63]



{% endhighlight %}




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

.. raw:: html

  {% highlight lang='text' %}
Inputs:
  1) Session Tag Chain key sessTag_ck
     First time: output from DH ratchet
     Subsequent times: output from previous session tag ratchet

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

.. raw:: html

  {% highlight lang='text' %}
Inputs:
  1) Symmetric Key Chain key symmKey_ck
     First time: output from DH ratchet
     Subsequent times: output from previous symmetric key ratchet
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

This uses the same block format as defined in the NTCP2 specification.
Individual block types are defined differently.

There are concerns that encouraging implementers to share code
may lead to parsing issues. Implementers should carefully consider
the benefits and risks of sharing code, and ensure that the
ordering and valid block rules are different for the two contexts.



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
         1-2 reserved
         3 I2NP message (Garlic Message only)
         4 termination
         5 options
         6 message number and previous message number (ratchet)
         7 next session key
         8 ack of reverse session key
         9 reply delivery instructions
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
In the new session message,
the following blocks are required, in the following order:

- DateTime (type 0)
- Options (type 5)
- Message Number (type 6)

Other allowed blocks:

- I2NP message (type 3)
- Padding (type 254)

No other blocks are allowed.

In the existing session message, order is unspecified, except for the
following requirements:
TBD
Padding, if present, must be the last block.
Termination, if present, must be the last block except for Padding.

There may be multiple I2NP blocks in a single frame.
Multiple Padding blocks are not allowed in a single frame.
Other block types probably won't have multiple blocks in
a single frame, but it is not prohibited.



DateTime
````````
Timestamp for replay prevention:

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



I2NP Message
````````````

An single I2NP message with a modified header.
I2NP messages may not be fragmented across blocks or
across ChaChaPoly frames.

This uses the first 9 bytes from the standard NTCP I2NP header,
and removes the last 7 bytes of the header, as follows:
truncate the expiration from 8 to 4 bytes,
remove the 2 byte length (use the block size - 9),
and remove the one-byte SHA256 checksum.


.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | 3  |  size   |type|    msg id         |
  +----+----+----+----+----+----+----+----+
  |   short exp       |     message       |
  +----+----+----+----+                   +
  |                                       |
  ~               .   .   .               ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  blk :: 3
  size :: 2 bytes, big endian, size of type + msg id + exp + message to follow
          I2NP message body size is (size - 9).
  type :: 1 byte, I2NP msg type, see I2NP spec
  msg id :: 4 bytes, big endian, I2NP message ID
  short exp :: 4 bytes, big endian, I2NP message expiration, Unix timestamp, unsigned seconds.
               Wraps around in 2106
  message :: I2NP message body

{% endhighlight %}

Notes
`````
- Implementers must ensure that when reading a block,
  malformed or malicious data will not cause reads to
  overrun into the next block.



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
            65535 (0xffff) when in a new session message.
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

- N is not strictly needed in an existing session message, as it's associated with the Session Tag

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
  with static key for binding
  with next key
  with bundled HTTP GET
  with bundled LS
  without bundled Delivery Status Message

  any retransmissions, same as above


  following messages may arrive in any order:

  <--------------     Existing Session
                      with next key
                      with bundled HTTP reply part 1

  <--------------     Existing Session
                      with next key
                      with bundled HTTP reply part 2

  <--------------     Existing Session
                      with next key
                      with bundled HTTP reply part 3

  After reception of any of these messages,
  Alice switches to use existing session messages,
  and ratchets.


  Existing Session     ------------------->
  with next key
  with bundled streaming ack

  after reception of this message, Bob ratchets


  Existing Session     ------------------->
  with bundled streaming ack

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
  with static key for binding
  with next key
  with bundled HTTP POST part 1
  with bundled LS
  without bundled Delivery Status Message


  New Session (1b)     ------------------->
  with static key for binding
  with next key
  with bundled HTTP POST part 2
  with bundled LS
  without bundled Delivery Status Message


  New Session (1b)     ------------------->
  with static key for binding
  with next key
  with bundled HTTP POST part 3
  with bundled LS
  without bundled Delivery Status Message



  <--------------     Existing Session
                      with next key
                      with bundled streaming ack

  After reception of any of this message,
  Alice switches to use existing session messages,
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


  <--------------     Existing Session
                      with next key
                      with bundled reply

  After reception of this message,
  Alice switches to use existing session messages,
  and ratchets.

  if there are any other messages:

  Existing Session     ------------------->
  with next key
  with bundled message

  after reception of this message, Bob ratchets


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
 
  following messages can come in any order:

  <--------------     Delivery Status Message 1

  <--------------     Delivery Status Message 2

  <--------------     Delivery Status Message 3

  After reception of any of these messages,
  Alice switches to use existing session messages.

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
Therefore, the length of existing session messages mod 16 is always 0,
and the length of new session messages mod 16 is always 2 (since the
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
or that any additional messages are sent speculatively as existing session messages.
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

Alice-Bob new session message:

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

Bob-Alice existing session message:

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
a new session and do the first ratchet:

- HMAC-SHA256: 3 per HKDF, total TBD
- ChaChaPoly: 2 each
- X25519 key generation: 2 Alice, 1 Bob
- X25519 DH: 3 each
- Signature verification: 1 (Bob)


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
