========================================
Smaller Tunnel Build Messages
========================================
.. meta::
    :author: zzz, orignal
    :created: 2020-10-09
    :thread: http://zzz.i2p/topics/2957
    :lastupdated: 2020-10-09
    :status: Open
    :target: 0.9.51

.. contents::



Overview
========


Summary
-------

The current size of the encrypted tunnel Build Request and Response records is 528.
For typical Variable Tunnel Build and Variable Tunnel Build Reply messages,
the total size is 2113 bytes. This message is fragmented into 1KB three tunnel
messages for the reverse path.

Changes to the 528-byte record format for ECIES-X25519 routers are specified in [Prop152]_.
For a mix of ElGamal and ECIES-X25519 routers in a tunnel, the record size must remain
528 bytes. However, if all routers in a tunnel are ECIES-X25519, a new, smaller
build record is possible, because ECIES-X25519 encryption has much less overhead
than ElGamal.

Smaller messages would save bandwidth. Also, if the messages could fit in a
single tunnel message, the reverse path would be three times more efficient.

This proposal defines new request and reply records and new Buid Request and Build Reply messages.


Goals
-----

See [Prop152]_ and [Prop156]_ for additional goals.

- Smaller records and messages
- Maintain sufficient space for future options, as in [Prop152]_
- Fit in one tunnel message for the reverse path
- Support ECIES hops only
- Maintain improvements implemented in [Prop152]_
- Maximize compatibility with current network
- Do not require "flag day" upgrade to entire network
- Gradual rollout to minimize risk
- Reuse existing cryptographic primitives


Non-Goals
-----------

See [Prop156]_ for additional non-goals.

- No requirement for mixed ElGamal/ECIES tunnels
- Layer encryption changes, for that see [Prop153]_
- No speedups of crypto operations. It's assumed that ChaCha20 and AES are similar.


Design
======


Records
-------------------------------

See appendix for calculations.

Encrypted request and reply records will be 236 bytes, compared to 528 bytes now.

The plaintext request records will be either 160 or 172 bytes,
compared to 222 bytes for ElGamal records,
and 464 bytes for ECIES records as defined in [Prop152]_.

The plaintext response records will be either 160 or 172 bytes,
compared to 496 bytes for ElGamal records,
and 512 bytes for ECIES records as defined in [Prop152]_.

If we use AES for reply encryption, records must be a multiple of 16.
If we use ChaCha20 (NOT ChaCha20/Poly1305), they can be 172 bytes.
TBD.

Request records will be made smaller by using HKDF to create the
layer and reply keys, so they do not need to be explicitly included in the request.


Tunnel Build Messages
-----------------------

Both will be "variable" with a one-byte number of records field,
as with the existing Variable messages.

Build: Type 25

Reply: Type 26

Total length: 641 or 689 bytes


Record Encryption
------------------

Request and reply record encryption: as defined in [Prop152]_.

Reply record encryption for other slots: AES or ChaCha20?



Specification
=============


Request Record
-----------------------

TBD


Response Record
-----------------------

TBD


KDF
-----------------------

TBD


Tunnel Build Messages
-----------------------

TBD


Justification
=============

This design maximizes reuse of existing cryptographic primitives, protocols, and code.

This design minimizes risk.




Implementation Notes
=====================




Issues
======

- HKDF details
- AES or ChaCha for reply encryption?
- Should we do additional hiding from the paired OBEP or IBGW? Garlic?


Migration
=========

The implementation, testing, and rollout will take several releases
and approximately one year. The phases are as follows. Assignment of
each phase to a particular release is TBD and depends on
the pace of development.

Details of the implementation and migration may vary for
each I2P implementation.

Tunnel creator must ensure that all hops are ECIES-X25519, AND are at least version TBD.
The tunnel creator does NOT have to be ECIES-X25519; it can be ElGamal.
However, if the creator is ElGamal, it reveals to the closest hop that it is the creator.
So, in practice, these tunnels should only be created by ECIES routers.

It should NOT be necessary for the paired-tunnel OBEP or IBGW is ECIES or
of any particular version, because they SHOULD support
relaying of unknown message types.
This should be verified in testing.

Phase 1: Implementation, not enabled by default

Phase 2 (next release): Enable by default


Appendix
==========


.. raw:: html

  {% highlight lang='text' %}
Current 4-slot size: 4 * 528 + overhead = 3 tunnel messages

  4-slot build message to fit in one tunnel message, ECIES-only:

  1024
  - 21 fragment header
  ----
  1003
  - 39 unfragmented instructions
  ----
  964
  - 16 I2NP header
  ----
  948
  - 1 number of slots
  ----
  947
  / 4 slots
  ----
  236 New encrypted build record size (vs. 528 now)
  - 16 trunc. hash
  - 32 eph. key
  - 16 MAC
  ----
  172 cleartext build record max (vs. 222 now)

  Current build record cleartext size before unused padding: 193

  Removal of full router hash and HKDF generation of keys/IVs would free up plenty of room for future options.
  If everything is HKDF, required cleartext space is about 82 bytes (without any options)



{% endhighlight %}


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

.. [Prop156]
    {{ proposal_url('156') }}

.. [Tunnel-Creation]
    {{ spec_url('tunnel-creation') }}

