========================================
ECIES Routers
========================================
.. meta::
    :author: zzz, orignal
    :created: 2020-09-01
    :thread: http://zzz.i2p/topics/2950
    :lastupdated: 2020-09-01
    :status: Open
    :target: 0.9.51

.. contents::



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

This proposal defines the replacement of ElGamal with ECIES for routers.
This proposal provides an overview of the changes required.
Most of the details are in other proposals and specifications.
See the reference section for links.


Goals
-----

- Replace ElGamal with ECIES-X25519
- Reuse existing cryptographic primitives
- Improve tunnel build message security where possible while maintaining compatibility
- Support tunnels with mixed ElGamal/ECIES peers
- Maximize compatibility with current network
- Do not require "flag day" upgrade to entire network
- Gradual rollout to minimize risk


Non-Goals
-----------

- No requirement for dual-key routers



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


Tunnel Build Message
-----------------------

Several changes to the tunnel creation specification [Tunnel-Creation]_
are required to use ECIES instead of ElGamal.
In addition, we will make improvements to the tunnel build messages
to increase security.

These changes are defined in proposal 152 [Prop152]_.
Proposal 152 is preliminary and has not been fully reviewed.
It will require significant corrections and cleanup.



End-to-End Encryption
-----------------------

When sending encrypted messages to routers, usually database lookups and stores,
they will be encrypted with
ECIES-X25519-AEAD-Ratchet [Prop144]_,  now specified in [ECIES]_.

Generally, these will be New Session messages and will be sent with a zero static key
(no binding or session), as the sender of the message is anonymous.

This mode of the protocol is not currently used for Destinations
and may need to be implemented and debugged for this use case.

Replies to lookups will be encrypted with a ratchet tag if requested in the lookup.
This is as documented in [Prop154]_,  now specified in [I2NP]_.

The design should enable the router to have a single ECIES Session Key Manager.
There should be no need to run "dual key" Session Key Managers as
described in [ECIES]_ for Destinations.

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
As of this date, approximately 80% of the network is 0.9.46 or higher.



Specification
=============

X25519: See [ECIES]_.

Router Identity and Key Certificate: See [Common]_.

Tunnel Building: See [Prop152]_.

End-to-End Encryption: See [ECIES]_.



Justification
=============

This design maximizes reuse of existing cryptographic primitives, protocols, and code.

This design minimizes risk.




Implementation Notes
=====================




Issues
======





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
This should be possible now, but ensure there's nothing in the code bases
that blacklists non-ElGamal routers or prevents point-to-point connections.

Until later phases:

- Ensure that tunnel builds are not attempted by ElGamal routers through ECIES routers.
- Ensure that encrypted ElGamal messages are not sent by ElGamal routers to ECIES floodfill routers.
- Ensure that encrypted ECIES messages are not sent by ECIES routers to ElGamal floodfill routers.
- Ensure that ECIES routers are not floodfill.

Target release, if changes required: 0.9.48


NetDB Compatibility
---------------------

Ensure that ECIES router infos may be stored to and retrieved from ElGamal floodfills.
This should be possible now, but ensure there's nothing in the code bases
that blacklists non-ElGamal routers.

Target release, if changes required: 0.9.48


Tunnel Building
-------------------

Implement tunnel building as defined in proposal 152 [Prop152]_.
Start with having an ECIES router build tunnels with all ElGamal hops;
use its own build request record for an inbound tunnel to test and debug.

Then test and support ECIES routers building tunnels with a mix of
ElGamal and ECIES hops.

Then enable tunnel building through ECIES routers.

Target release: 0.9.49 or 0.9.50, early-mid 2021


Ratchet messages to ECIES floodfills
----------------------------------------

Implement and test reception of ECIES messages (with zero static key) by ECIES floodfills.
Enable auto-floodfill by ECIES routers.

Target release: 0.9.49 or 0.9.50, early-mid 2021


Rekeying
------------

Gradually rekey all routers to minimize risk and disruption to the network.
Use existing code that did the rekeying for sig type migration years ago.
This code gives each router a small random chance of rekeying at each restart.
After several restarts, a router will probably have rekeyed to ECIES.

Rekeying may take several releases.

Probably start rekeying mid-2021.

Target release: TBD


ECIES for New Installs
--------------------------

New installs are ECIES routers.

Target release: TBD
Probably mid-late 2021.



Rekeying Complete
----------------------

At this point, routers older than some version TBD will
not be able to build tunnels through most peers.

Target release: TBD
Probably early-mid 2022.



References
==========

.. [Common]
    {{ spec_url('common-structures') }}

.. [ECIES]
   {{ spec_url('ecies') }}

.. [I2NP]
    {{ spec_url('i2np') }}

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

.. [Tunnel-Creation]
    {{ spec_url('tunnel-creation') }}

