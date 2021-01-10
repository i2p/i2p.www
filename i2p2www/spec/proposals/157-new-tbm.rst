========================================
Smaller Tunnel Build Messages
========================================
.. meta::
    :author: zzz, orignal
    :created: 2020-10-09
    :thread: http://zzz.i2p/topics/2957
    :lastupdated: 2021-01-10
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

This proposal defines new request and reply records and new Build Request and Build Reply messages.


Goals
-----

See [Prop152]_ and [Prop156]_ for additional goals.

- Smaller records and messages
- Maintain sufficient space for future options, as in [Prop152]_
- Fit in one tunnel message for the reverse path
- Support ECIES hops only
- Maintain improvements implemented in [Prop152]_
- Maximize compatibility with current network
- Hide inbound build messages from the OBGW
- Hide outbound build reply messages from the IBEP
- Do not require "flag day" upgrade to entire network
- Gradual rollout to minimize risk
- Reuse existing cryptographic primitives


Non-Goals
-----------

See [Prop156]_ for additional non-goals.

- No requirement for mixed ElGamal/ECIES tunnels
- Layer encryption changes, for that see [Prop153]_
- No speedups of crypto operations. It's assumed that ChaCha20 and AES are similar,
  even with AESNI, at least for the small data sizes in question.


Design
======


Records
-------------------------------

See appendix for calculations.

Encrypted request and reply records will be 236 bytes, compared to 528 bytes now.

The plaintext request records will be 172 bytes,
compared to 222 bytes for ElGamal records,
and 464 bytes for ECIES records as defined in [Prop152]_.

The plaintext response records will be 172 bytes,
compared to 496 bytes for ElGamal records,
and 512 bytes for ECIES records as defined in [Prop152]_.

The reply encryption will be ChaCha20 (NOT ChaCha20/Poly1305),
so the plaintext records do not need to be a multiple of 16 bytes.

Request records will be made smaller by using HKDF to create the
layer and reply keys, so they do not need to be explicitly included in the request.


Tunnel Build Messages
-----------------------

Both will be "variable" with a one-byte number of records field,
as with the existing Variable messages.

ShortTunnelBuild: Type 25
Typical length (with 4 records): 945 bytes

OutboundTunnelBuildReply: Type 26
We define a new OutboundTunnelBuildReply message.
This is used for outbound tunnel builds only.
The purpose is to hide outbound build reply messages from the IBEP.
It must be garlic encrypted by the OBGW, targeting the originator
(delivery instructions TUNNEL).
The OBEP decrypts the tunnel build message,
constructs a OutboundTunnelBuildReply message,
and puts the reply into the cleartext field.
The other records go into the other slots.
It then garlic encrypts the message to originator with the derived symmetric keys.


Additionally, we define a new InboundTunnelBuild message, Type 27.
This is used for inbound tunnel builds only.
The purpose is to hide inbound build messages from the OBGW.
It must be garlic encrypted by the originator, targeting the inbound gateway
(delivery instructions ROUTER).
The IBGW decrypts the message,
constructs a ShortTunnelBuild message,
and puts the reply into the correct slot specified.
The other records go into the other slots.
It then sends the ShortTunnelBuildMessage to the next hop.
As the ShortTunnelBuild message is garlic encrypted,
the build record for the IBGW does not need to be encrypted again.


Message Flow
------------------

.. raw:: html

  {% highlight %}
STBM: Short tunnel build message (type 25)
  OTBRM: Outbound tunnel build reply message (type 26)
  ITBM: Inbound tunnel build message (type 27)

  Outbound Build A-B-C
  Reply through existing inbound D-E-F


           STBM      STBM      STBM
  Creator ------> A ------> B ------> C ---\
                                     OBEP   \
                                            | Garlic wrapped
                                            | OTBRM
                                            | (TUNNEL delivery)
                                            | from OBEP to
                                            | creator
                                            /
  Creator <-------F---------E-------- D <--/
                                     IBGW



  Inbound Build D-E-F
  Sent through existing outbound A-B-C


  Creator ------> A ------> B ------> C ---\
                                    OBEP    \
                                            | Garlic wrapped
                                            | ITBM
                                            | (ROUTER delivery)
                                            | from creator
                                            | to IBGW
            STBM      STBM      STBM        /
  Creator <------ F <------ E <------ D <--/
                                     IBGW



{% endhighlight %}



Record Encryption
------------------

Request and reply record encryption: as defined in [Prop152]_.

Reply record encryption for other slots: ChaCha20.


Layer Encryption
------------------

Currently there is no plan to change layer encryption for tunnels built with
this specification; it would remain AES, as currently used for all tunnels.

Changing layer encryption to ChaCha20 is a topic for additional research.



New Tunnel Data Message
-------------------------

Currently there is no plan to change the 1KB Tunnel Data Message used for tunnels built with
this specification.

It may be useful to introduce a new I2NP message that is larger or variable-sized, concurrent with this proposal,
for use over these tunnels.
This would reduce overhead for large messages.
This is a topic for additional research.




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



.. _msg-ShortTunnelBuild:

ShortTunnelBuild
-------------------
I2NP Type 25

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | num| ShortBuildRequestRecords...
  +----+----+----+----+----+----+----+----+

  num ::
         1 byte `Integer`
         Valid values: 1-8

  record size: 236 bytes
  total size: 1+$num*236
{% endhighlight %}

Notes
`````
* Typical number of records is 4, for a total size of 945.



.. _msg-OutboundTunnelBuildReply:

OutboundTunnelBuildReply
---------------------------
I2NP Type 26

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | num| ShortBuildReplyRecords...
  +----+----+----+----+----+----+----+----+
                                          |
  +----+----+----+----+----+----+----+----+
  |slot| length  |   Cleartext
  +----+----+----+----+----+----+----+----+
              BuildReplyRecord            |
  +----+----+----+----+----+----+----+----+

  num ::
         Number of encrypted records to follow
         1 byte `Integer`
         Valid values: 0-7

  slot ::
         Slot for the plaintext record to follow
         1 byte `Integer`
         Valid values: 0-7

  length ::
         Length of the plaintext record to follow
         2 byte `Integer`
         Valid values: TBD-172

  BuildReplyRecord ::
         Plaintext record for OBEP
         length: TBD-172

  encrypted record size: 236 bytes
  cleartext record size: 236 bytes
  total size: varies
{% endhighlight %}

Notes
`````
* The Cleartext BuildReplyRecord does NOT contain padding after
  the properties field. It does not need to be fixed length.
  This hopefully allows the garlic encrypted message to fit in
  one tunnel message. Calculation TBD.
* This message MUST be garlic encrypted.




.. _msg-InboundTunnelBuild:

InboundTunnelBuild
-------------------
I2NP Type 27

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | num| ShortBuildRequestRecords...
  +----+----+----+----+----+----+----+----+
                                          |
  +----+----+----+----+----+----+----+----+
  |slot| length  |   Cleartext
  +----+----+----+----+----+----+----+----+
              BuildRequestRecord          |
  +----+----+----+----+----+----+----+----+

  num ::
         Number of encrypted records to follow
         1 byte `Integer`
         Valid values: 0-7

  slot ::
         Slot for the plaintext record to follow
         1 byte `Integer`
         Valid values: 0-7

  length ::
         Length of the plaintext record to follow
         2 byte `Integer`
         Valid values: TBD-172

  BuildRequestRecord ::
         Plaintext record for IBGW
         length: TBD-172

  encrypted record size: 236 bytes
  cleartext record size: 236 bytes
  total size: varies
{% endhighlight %}

Notes
`````
* The Cleartext BuildRequestRecord does NOT contain padding after
  the properties field. It does not need to be fixed length.
  This hopefully allows the garlic encrypted message to fit in
  one tunnel message. Calculation TBD.
* This message MUST be garlic encrypted.




Justification
=============

This design maximizes reuse of existing cryptographic primitives, protocols, and code.

This design minimizes risk.

ChaCha20 is slightly faster than AES for small records, in Java testing.
ChaCha20 avoids a requirement for data size multiples of 16.


Implementation Notes
=====================

- As with the existing variable tunnel build message,
  messages smaller than 4 records are not recommended.
  The typical default is 3 hops.
  Inbound tunnels must be built with an extra record for
  the originator, so the last hop does not know it is last.
  So that middle hops don't know if a tunnel is inbound or outbound,
  outbound tunnels should be built with 4 records also.



Issues
======

- HKDF details
- Layer encryption changes?

 Should we do additional hiding from the paired OBEP or IBGW? Garlic?
- For an IB build, the build message could be garlic encrypted to the IBGW,
  but then it would be larger.
- We could do this for IB now for existing build messages if desired,
  but it's more expensive for ElGamal.
- Is it worth it, or does the size of the message (much larger than
  typical database lookup, but maybe not database store) plus the
  delivery instructions make it obvious anyway?
- For an OB build, the build reply message would have to be garlic encrypted
  by the OBEP to the originator, but that would not be anonymous.
  Is there another way? probably not.


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

