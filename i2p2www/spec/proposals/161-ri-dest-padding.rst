========================================
RI and Destination Padding
========================================
.. meta::
    :author: zzz
    :created: 2022-09-28
    :thread: http://zzz.i2p/topics/3279
    :lastupdated: 2023-01-02
    :status: Open
    :target: 0.9.57

.. contents::


Status
========

Implemented in 0.9.57.
Leaving this proposal open so we may enhance and discuss the ideas in the "Future Planning" section.


Overview
========


Summary
-------

The ElGamal public key in Destinations has been unused since release 0.6 (2005).
While our specifications do say that it is unused, they do NOT say that implementations can avoid
generating an ElGamal key pair and simply fill the field with random data.

We propose changing the specifications to say that
the field is ignored and that implementations MAY fill the field with random data.
This change is backward-compatible. There is no known implementation that validates
the ElGamal public key.

Additionally, this proposal offers guidance to implementers on how to generate the
random data for Destination AND Router Identity padding so that it is compressible while
still being secure, and without having Base 64 representations appear to be corrupt or insecure.
This provides most of the benefits of removing the padding fields without any
disruptive protocol changes.
Compressible Destinations reduces streaming SYN and repliable datagram size;
compressible Router Identities reduce Database Store Messages, SSU2 Session Confirmed messages,
and reseed su3 files.

Finally, the proposal discusses possibilities for new Destination and Router Identity formats
that would eliminate the padding altogether. There is also a brief discussion of post-quantum
crypto and how that may affect future planning.



Goals
-----

- Eliminate requirement to generate ElGamal keypair for Destinations
- Recommend best practices so Destinations and Router Identities are highly compressible,
  yet do not display obvious patterns in Base 64 representations.
- Encourage adoption of best practices by all implementations so
  the fields are not distinguishable
- Reduce streaming SYN size
- Reduce repliable datagram size
- Reduce SSU2 RI block size
- Reduce SSU2 Session Confirmed size and fragmentation frequency
- Reduce Database Store Message (with RI) size
- Reduce reseed file size
- Maintain compatibility in all protocols and APIs
- Update specifications
- Discuss alternatives for new Destination and Router Identity formats

By eliminating the requirement to generate ElGamal keys, implementations may
be able to completely remove ElGamal code, subject to backward-compatibility considerations
in other protocols.



Design
======

Strictly speaking, the 32-byte signing public key alone (in both Destinations and Router Identities)
and the 32-byte encryption public key (in Router Identities only) is a random number
that provides all the entropy necessary for the SHA-256 hashes of these structures
to be cryptographically strong and randomly distributed in the network database DHT.

However, out of an abundance of caution, we recommend a minimum of 32 bytes of random data
be used in the ElG public key field and padding. Additionally, if the fields were all zeros,
Base 64 destinations would contain long runs of AAAA characters, which may cause alarm
or confusion to users.

For Ed25519 signature type and X25519 encryption type:
Destinations will contain 11 copies (352 bytes) of the random data.
Router Identities will contain 10 copies (320 bytes) of the random data.



Estimated Savings
---------------------

Destinations are included in every streaming SYN [Streaming]_
and repliable datagram [Datagram]_.
Router Infos (containing Router Identities) are included in Database Store Messages [I2NP]_
and in the Session Confirmed messages in [NTCP2]_ and [SSU2]_.

NTCP2 does not compress the Router Info.
RIs in Database Store Messages and SSU2 Session Confirmed messages are gzipped.
Router Infos are zipped in reseed SU3 files.

Destinations in Database Store Messages are not compressed.
Streaming SYN messages are gzipped at the I2CP layer.

For Ed25519 signature type and X25519 encryption type,
estimated savings:

===============  ===========   =============  ====================   ==================  ===========  =============
Data Type        Total Size    Keys and Cert  Uncompressed Padding   Compressed Padding  Size         Savings
===============  ===========   =============  ====================   ==================  ===========  =============
Destination      391           39             352                    32                  71           320 bytes (82%)
Router Identity  391           71             320                    32                  103          288 bytes (74%)
Router Info      1000 typ.     71             320                    32                  722 typ.     288 bytes (29%)
===============  ===========   =============  ====================   ==================  ===========  =============

Notes: Assumes 7-byte certificate is not compressible, zero additional gzip overhead.
Neither is true, but effects will be small.
Ignores other compressible parts of the Router Info.



Specification
=============

Proposed changes to our current specifications are documented below.


Common Structures
------------------
Change the common structures specification [COMMON]_
to specify that the 256-byte Destination public key field is ignored and may
contain random data.

Add a section to the common structures specification [COMMON]_
recommending best practice for the Destination public key field and the
padding fields in the Destination and Router Identity, as follows:

Generate 32 bytes of random data using a strong cryptographic pseudo-random number generator (PRNG)
and repeat those 32 bytes as necessary to fill the public key field (for Destinations)
and the padding field (for Destinations and Router Identities).

Private Key File
--------------------
The private key file (eepPriv.dat) format is not an official part of our specifications
but it is documented in the Java I2P javadocs [PKF]_
and other implementations do support it.
This enables portability of private keys to different implementations.
Add a note to that javadoc that the encryption public key may be random padding
and the encryption private key may be all zeros or random data.

SAM
------
Note in [SAM]_ that the encryption private key is unused and may be ignored.
Any random data may be returned by the client.
The SAM Bridge may send random data on creation (with DEST GENERATE or SESSION CREATE DESTINATION=TRANSIENT)
rather than all zeros, so the Base 64 representation does not have a string of AAAA characters
and look broken.


I2CP
------
No changes required to [I2CP]_. The private key for the encryption public key in the Destination
is not sent to the router.


Future Planning
==================


Protocol Changes
------------------

At a cost of protocol changes and a lack of backward compatibility, we could
change our protocols and specifications to eliminate the padding field in
the Destination, Router Identity, or both.

This proposal bears some similarity to the "b33" encrypted leaseset format,
containing only a key and a type field.

To maintain some compatibility, certain protocol layers could "expand" the padding field
with all zeros to present to other protocol layers.

For Destinations, we could also remove the encryption type field in the key certificate,
at a savings of two bytes.
Alternatively, Destinations could get a new encryption type in the key certificate,
indicating a zero public key (and padding).

If compatibility conversion between old and new formats is not included at some protocol layer,
the following specifications, APIs, protocols, and applications would be affected:

- Common structures spec
- I2NP
- I2CP
- NTCP2
- SSU2
- Ratchet
- Streaming
- SAM
- Bittorrent
- Reseeding
- Private Key File
- Java core and router API
- i2pd API
- Third-party SAM libraries
- Bundled and third-party tools
- Several Java plugins
- User interfaces
- P2P applications e.g. MuWire, bitcoin, monero
- hosts.txt, addressbook, and subscriptions

If conversion is specified at some layer, the list would be reduced.

The costs and benefits of these changes are not clear.

Specific proposals TBD:





PQ Keys
------------------

Post-Quantum (PQ) encryption public keys, for any anticipated algorithm,
are larger than 256 bytes. This would eliminate any padding and any savings from proposed
changes above, for Router Identities.

In a "hybrid" PQ approach, like what SSL is doing, the PQ keys would be ephemeral only,
and would not appear in the Router Identity.

PQ signing keys are not viable,
and Destinations do not contain encryption public keys.
Static keys for ratchet are in the Lease Set, not the Destination.
so we may eliminate Destinations from the following discussion.

So PQ only affects Router Infos, and only for PQ static (not ephemeral) keys, not for PQ hybrid.
This would be for a new encryption type and would affect NTCP2, SSU2, and
encrypted Database Lookup Messages and replies.
Estimated time frame for design, development, and rollout of that would be ????????
But would be after hybrid or ratchet ????????????

For further discussion see [PQ]_.




Issues
======

It may be desirable to rekey the network at a slow rate, to provide cover for new routers.
"Rekeying" could mean simply changing the padding, not really changing the keys.

It is not possible to rekey existing Destinations.

Should Router Identities with padding in the public key field be identified with a different
encryption type in the key certificate? This would cause compatibility issues.




Migration
=========

No backward compatibility issues for replacing the ElGamal key with padding.

Rekeying, if implemented, would be similar to that done
in three previous router identity transitions:
From DSA-SHA1 to ECDSA signatures, then to
EdDSA signatures, then to X25519 encryption.

Subject to backward compatibility issues, and after disabling SSU,
implementations may remove ElGamal code completely.
Approximately 14% of routers in the network are ElGamal encryption type, including many floodfills.

A draft merge request for Java I2P is at [MR]_.


References
==========

.. [Common]
    {{ spec_url('common-structures') }}

.. [Datagram]
    {{ spec_url('datagrams') }}

.. [I2CP]
    {{ spec_url('i2cp') }}

.. [I2NP]
    {{ spec_url('i2np') }}

.. [MR]
    http://git.idk.i2p/i2p-hackers/i2p.i2p/-/merge_requests/66

.. [NTCP2]
    {{ spec_url('ntcp2') }}

.. [PKF]
    http://{{ i2pconv('idk.i2p/javadoc-i2p') }}/net/i2p/data/PrivateKeyFile.html

.. [PQ]
    http://zzz.i2p/topics/3294

.. [SAM]
    {{ site_url('docs/api/samv3') }}

.. [SSU2]
    {{ spec_url('ssu2') }}

.. [Streaming]
    {{ spec_url('streaming') }}
