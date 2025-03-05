========================================
ECIES Routers
========================================
.. meta::
    :author: zzz, orignal
    :created: 2020-09-01
    :thread: http://zzz.i2p/topics/2950
    :lastupdated: 2025-03-05
    :status: Closed
    :target: 0.9.51

.. contents::


Note
====
Network deployment and testing in progress.
Subject to revision.
Status:

- ECIES Routers implemented as of 0.9.48, see [Common]_.
- Tunnel building implemented as of 0.9.48, see [Tunnel-Creation-ECIES]_.
- Encrypted messages to ECIES routers implemented as of 0.9.49, see [ECIES-ROUTERS]_.
- New tunnel build messages implemented as of 0.9.51.




Overview
========


Summary
-------

Router Identities currently contain an ElGamal encryption key.
This has been the standard since the beginnings of I2P.
ElGamal is slow and needs to be replaced in all places it is used.

The proposals for LS2 [Prop123]_ and ECIES-X25519-AEAD-Ratchet [Prop144]_
(now specified in [ECIES]_) defined the replacement of ElGamal with ECIES
for Destinations.

This proposal defines the replacement of ElGamal with ECIES-X25519 for routers.
This proposal provides an overview of the changes required.
Most of the details are in other proposals and specifications.
See the reference section for links.


Goals
-----

See [Prop152]_ for additional goals.

- Replace ElGamal with ECIES-X25519 in Router Identities
- Reuse existing cryptographic primitives
- Improve tunnel build message security where possible while maintaining compatibility
- Support tunnels with mixed ElGamal/ECIES peers
- Maximize compatibility with current network
- Do not require "flag day" upgrade to entire network
- Gradual rollout to minimize risk
- New, smaller tunnel build message


Non-Goals
-----------

See [Prop152]_ for additional non-goals.

- No requirement for dual-key routers
- Layer encryption changes, for that see [Prop153]_


Design
======


Key Location and Crypto Type
-------------------------------

For Destinations, the key is in the leaseset, not in the Destination, and
we support multiple encryption types in the same leaseset.

None of that is required for routers. The router's encryption key
is in its Router Identity. See the common structures spec [Common]_.

For routers, we will replace the 256 byte ElGamal key in the Router Identity
with a 32 byte X25519 key and 224 bytes of padding.
This will be indicated by the crypto type in the key certificate.
The crypto type (same as used in the LS2) is 4.
This indicates a little-endian 32-byte X25519 public key.
This is the standard construction as defined in the common structures spec [Common]_.

This is identical to the method proposed for ECIES-P256
for crypto types 1-3 in proposal 145 [Prop145]_.
While this proposal was never adopted, the Java implementation developers prepared for
crypto types in Router Identity key certificates by adding checks in several
places in the code base. Most of this work was done in mid-2019.


Tunnel Build Message
-----------------------

Several changes to the tunnel creation specification [Tunnel-Creation]_
are required to use ECIES instead of ElGamal.
In addition, we will make improvements to the tunnel build messages
to increase security.

In phase 1, we will change the format and encryption of the
Build Request Record and Build Response Record for ECIES hops.
These changes will be compatible with existing ElGamal routers.
These changes are defined in proposal 152 [Prop152]_.

In phase 2, we will add a new version of the
Build Request Message, Build Reply Message,
Build Request Record and Build Response Record.
The size will be reduced for efficiency.
These changes must be supported by all hops in a tunnel, and all hops must be ECIES.
These changes are defined in proposal 157 [Prop157]_.



End-to-End Encryption
-----------------------

History
```````````

In the original design of Java I2P, there was a single ElGamal Session Key Manager (SKM)
shared by the router and all its local Destinations.
As a shared SKM could leak information and allow correlation by attackers,
the design was changed to support separate ElGamal SKMs for the router and each Destination.
The ElGamal design supported only anonymous senders;
the sender sent ephemeral keys only, not a static key.
The message was not bound to the sender's identity.

Then, we designed the ECIES Ratchet SKM in
ECIES-X25519-AEAD-Ratchet [Prop144]_,  now specified in [ECIES]_.
This design was specified using the Noise "IK" pattern, which included the sender's
static key in the first message. This protocol is used for ECIES (type 4) Destinations.
The IK pattern does not allow for anonymous senders.

Therefore, we included in the proposal a way to also send anonymous messages
to a Ratchet SKM, using a zero-filled static key. This simulated a Noise "N" pattern,
but in a compatible way, so a ECIES SKM could receive both anonymous and non-anonymous messages.
The intent was to use zero-key for ECIES routers.


Use Cases and Threat Models
```````````````````````````````

The use case and threat model for messages sent to routers is very different from
that for end-to-end messages between Destinations.


Destination use case and threat model:

- Non-anonymous from/to destinations (sender includes static key)
- Efficiently support sustained traffic between destinations (full handshake, streaming, and tags)
- Always sent through outbound and inbound tunnels
- Hide all identifying characteristics from OBEP and IBGW, requiring Elligator2 encoding of ephemeral keys.
- Both participants must use the same encryption type


Router use case and threat model:

- Anonymous messages from routers or destinations (sender does not include static key)
- For encrypted Database Lookups and Stores only, generally to floodfills
- Occasional messages
- Multiple messages should not be correlated
- Always sent through outbound tunnel directly to a router. No inbound tunnels used
- OBEP knows that it is forwarding the message to a router and knows its encryption type
- The two participants may have different encryption types
- Database Lookup replies are one-time messages using the reply key and tag in the Database Lookup message
- Database Store confirmations are one-time messages using a bundled Delivery Status message


Router use-case non-goals:

- No need for non-anonymous messages
- No need to send messages through inbound exploratory tunnels (a router does not publish exploratory leasesets)
- No need for sustained message traffic using tags
- No need to run "dual key" Session Key Managers as described in [ECIES]_ for Destinations. Routers only have one public key.


Design Conclusions
```````````````````````

The ECIES Router SKM does not need a full Ratchet SKM as specified in [ECIES]_ for Destinations.
There is no requirement for non-anonymous messages using the IK pattern.
The threat model does not require Elligator2-encoded ephemeral keys.

Therefore, the router SKM will use the Noise "N" pattern, same as specified
in [Prop152]_ for tunnel building.
It will use the same payload format as specified in [ECIES]_ for Destinations.
The zero static key (no binding or session) mode of IK specified in [ECIES]_ will not be used.

Replies to lookups will be encrypted with a ratchet tag if requested in the lookup.
This is as documented in [Prop154]_,  now specified in [I2NP]_.

The design enables the router to have a single ECIES Session Key Manager.
There is no need to run "dual key" Session Key Managers as
described in [ECIES]_ for Destinations.
Routers only have one public key.

An ECIES router does not have an ElGamal static key.
The router still needs an implementation of ElGamal to build tunnels
through ElGamal routers and send encrypted messages to ElGamal routers.

An ECIES router MAY require a partial ElGamal Session Key Manager to
receive ElGamal-tagged messages received as replies to NetDB lookups
from pre-0.9.46 floodfill routers, as those routers do not
have an implementation of ECIES-tagged replies as specified in [Prop152]_.
If not, an ECIES router may not request an encrypted reply from a
pre-0.9.46 floodfill router.

This is optional. Decision may vary in various I2P implementations
and may depend on the amount of the network that has upgraded to
0.9.46 or higher.
As of this date, approximately 85% of the network is 0.9.46 or higher.



Specification
=============

X25519: See [ECIES]_.

Router Identity and Key Certificate: See [Common]_.

Tunnel Building: See [Prop152]_.

New Tunnel Build Message: See [Prop157]_.


Request Encryption
---------------------

The request encryption is the same as that specified in [Tunnel-Creation-ECIES]_ and [Prop152]_,
using the Noise "N" pattern.

Replies to lookups will be encrypted with a ratchet tag if requested in the lookup.
Database Lookup request messages contain the 32-byte reply key and 8-byte reply tag
as specified in [I2NP]_ and [Prop154]_. The key and tag are used to encrypt the reply.

Tag sets are not created.
The zero static key scheme specified in
ECIES-X25519-AEAD-Ratchet [Prop144]_ and [ECIES]_ will not be used.
Ephemeral keys will not be Elligator2-encoded.

Generally, these will be New Session messages and will be sent with a zero static key
(no binding or session), as the sender of the message is anonymous.


KDF for Initial ck and h
````````````````````````

This is standard [NOISE]_ for pattern "N" with a standard protocol name.
This is the same as specified in [Tunnel-Creation-ECIES]_ and [Prop152]_ for tunnel build messages.


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


KDF for Message
````````````````````````

Message creators generate an ephemeral X25519 keypair for each message.
Ephemeral keys must be unique per message.
This is the same as specified in [Tunnel-Creation-ECIES]_ and [Prop152]_ for tunnel build messages.


.. raw:: html

  {% highlight lang='dataspec' %}

// Target router's X25519 static keypair (hesk, hepk) from the Router Identity
  hesk = GENERATE_PRIVATE()
  hepk = DERIVE_PUBLIC(hesk)

  // MixHash(hepk)
  // || below means append
  h = SHA256(h || hepk);

  // up until here, can all be precalculated by each router
  // for all incoming messages

  // Sender generates an X25519 ephemeral keypair
  sesk = GENERATE_PRIVATE()
  sepk = DERIVE_PUBLIC(sesk)

  // MixHash(sepk)
  h = SHA256(h || sepk);

  End of "e" message pattern.

  This is the "es" message pattern:

  // Noise es
  // Sender performs an X25519 DH with receiver's static public key.
  // The target router
  // extracts the sender's ephemeral key preceding the encrypted record.
  sharedSecret = DH(sesk, hepk) = DH(hesk, sepk)

  // MixKey(DH())
  //[chainKey, k] = MixKey(sharedSecret)
  // ChaChaPoly parameters to encrypt/decrypt
  keydata = HKDF(chainKey, sharedSecret, "", 64)
  // Chain key is not used
  //chainKey = keydata[0:31]

  // AEAD parameters
  k = keydata[32:63]
  n = 0
  plaintext = 464 byte build request record
  ad = h
  ciphertext = ENCRYPT(k, n, plaintext, ad)

  End of "es" message pattern.

  // MixHash(ciphertext) is not required
  //h = SHA256(h || ciphertext)

{% endhighlight %}



Payload
````````````````````````

The payload is the same block format as defined in [ECIES]_ and [Prop144]_.
All messages must contain a DateTime block for replay prevention.


Reply Encryption
---------------------

Replies to Database Lookup messages are Database Store or Database Search Reply messages.
They are encrypted as Existing Session messages with
the 32-byte reply key and 8-byte reply tag
as specified in [I2NP]_ and [Prop154]_.


There are no explicit replies to Database Store messages. The sender may bundle its
own reply as a Garlic Message to itself, containing a Delivery Status message.




Justification
=============

This design maximizes reuse of existing cryptographic primitives, protocols, and code.

This design minimizes risk.




Implementation Notes
=====================

Older routers do not check the encryption type of the router and will send ElGamal-encrypted
build records or netdb messages.
Some recent routers are buggy and will send various types of malformed build records.
Some recent routers may send non-anonymous (full ratchet) netdb messages.
Implementers should detect and reject these records and messages
as early as possible, to reduce CPU usage.



Issues
======

Proposal 145 [Prop145]_ may or may not be rewritten to be mostly-compatible with
Proposal 152 [Prop152]_.



Migration
=========

The implementation, testing, and rollout will take several releases
and approximately one year. The phases are as follows. Assignment of
each phase to a particular release is TBD and depends on
the pace of development.

Details of the implementation and migration may vary for
each I2P implementation.



Basic Point-to-Point
---------------------

ECIES routers can connect to and receive connections from ElGamal routers.
This should be possible now, as several checks were added to the Java code base
by mid-2019 in reaction to unfinished proposal 145 [Prop145]_.
Ensure there's nothing in the code bases
that prevents point-to-point connections to non-ElGamal routers.

Code correctness checks:

- Ensure that ElGamal routers do not request AEAD-encrypted replies to DatabaseLookup messages
  (when the reply comes back through an exploratory tunnel to the router)
- Ensure that ECIES routers do not request AES-encrypted replies to DatabaseLookup messages
  (when the reply comes back through an exploratory tunnel to the router)

Until later phases, when specifications and implementations are complete:

- Ensure that tunnel builds are not attempted by ElGamal routers through ECIES routers.
- Ensure that encrypted ElGamal messages are not sent by ElGamal routers to ECIES floodfill routers.
  (DatabaseLookups and DatabaseStores)
- Ensure that encrypted ECIES messages are not sent by ECIES routers to ElGamal floodfill routers.
  (DatabaseLookups and DatabaseStores)
- Ensure that ECIES routers do not automatically become floodfill.

No changes should be required.
Target release, if changes required: 0.9.48


NetDB Compatibility
---------------------

Ensure that ECIES router infos may be stored to and retrieved from ElGamal floodfills.
This should be possible now, as several checks were added to the Java code base
by mid-2019 in reaction to unfinished proposal 145 [Prop145]_.
Ensure there's nothing in the code bases
that prevents storage of non-ElGamal RouterInfos in the network database.

No changes should be required.
Target release, if changes required: 0.9.48


Tunnel Building
-------------------

Implement tunnel building as defined in proposal 152 [Prop152]_.
Start with having an ECIES router build tunnels with all ElGamal hops;
use its own build request record for an inbound tunnel to test and debug.

Then test and support ECIES routers building tunnels with a mix of
ElGamal and ECIES hops.

Then enable tunnel building through ECIES routers.
No minimum version check should be necessary unless incompatible changes
to proposal 152 are made after a release.

Target release: 0.9.48, late 2020


Ratchet messages to ECIES floodfills
----------------------------------------

Implement and test reception of ECIES messages (with zero static key) by ECIES floodfills,
as defined in proposal 144 [Prop144]_.
Implement ant test reception of AEAD replies to DatabaseLookup messages by ECIES routers.

Enable auto-floodfill by ECIES routers.
Then enable sending ECIES messages to ECIES routers.
No minimum version check should be necessary unless incompatible changes
to proposal 152 are made after a release.

Target release: 0.9.49, early 2021.
ECIES routers may automatically become floodfill.


Rekeying and New Installs
---------------------------

New installs will default to ECIES as of release 0.9.49.

Gradually rekey all routers to minimize risk and disruption to the network.
Use existing code that did the rekeying for sig type migration years ago.
This code gives each router a small random chance of rekeying at each restart.
After several restarts, a router will probably have rekeyed to ECIES.

The criterion for starting rekeying is that a sufficient portion of the network,
perhaps 50%, can build tunnels through ECIES routers (0.9.48 or higher).

Before aggressively rekeying the entire network, the vast majority
(perhaps 90% or more) must be able to build tunnels through ECIES routers (0.9.48 or higher)
AND send messages to ECIES floodfills (0.9.49 or higher).
This target will probably be reached for the 0.9.52 release.

Rekeying will take several releases.

Target release:
0.9.49 for new routers to default to ECIES;
0.9.49 to slowly start rekeying;
0.9.50 - 0.9.52 to repeatedly increase the rekeying rate;
late 2021 for the majority of the network to be rekeyed.


New Tunnel Build Message (Phase 2)
------------------------------------

Implement and test the new Tunnel Build Message as defined in proposal 157 [Prop157]_.
Roll the support out in release 0.9.51.
Do additional testing, then enable in release 0.9.52.

Testing will be difficult.
Before this can be widely tested, a good subset of the network must support it.
Before it is broadly useful, a majority of the network must support it.
If specification or implementation changes are required after testing,
that would delay the rollout for an additional release.

Target release: 0.9.52, late 2021.


Rekeying Complete
----------------------

At this point, routers older than some version TBD will
not be able to build tunnels through most peers.

Target release: 0.9.53, early 2022.



References
==========

.. [Common]
    {{ spec_url('common-structures') }}

.. [ECIES]
   {{ spec_url('ecies') }}

.. [ECIES-ROUTERS]
   {{ spec_url('ecies-routers') }}

.. [I2NP]
    {{ spec_url('i2np') }}

.. [NOISE]
    https://noiseprotocol.org/noise.html

.. [Prop123]
    {{ proposal_url('123') }}

.. [Prop144]
    {{ proposal_url('144') }}

.. [Prop145]
    {{ proposal_url('145') }}

.. [Prop152]
    {{ proposal_url('152') }}

.. [Prop153]
    {{ proposal_url('153') }}

.. [Prop154]
    {{ proposal_url('154') }}

.. [Prop157]
    {{ proposal_url('157') }}

.. [Tunnel-Creation]
    {{ spec_url('tunnel-creation') }}

.. [Tunnel-Creation-ECIES]
   {{ spec_url('tunnel-creation-ecies') }}
