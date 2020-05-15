========================================
Streaming MTU for ECIES Destinations
========================================
.. meta::
    :author: zzz
    :created: 2020-05-06
    :thread: http://zzz.i2p/topics/2886
    :lastupdated: 2020-05-15
    :status: Open
    :target: 0.9.47

.. contents::



Overview
========


Summary
-------

ECIES reduces exisiting session (ES) message overhead by about 90 bytes.
Therefore we can increase the MTU by about 90 bytes for ECIES connections.
See [ECIES]_, [STREAMING-SPEC]_, and [STREAMING-OPTIONS]_.

Without increasing the MTU, in many cases the overhead savings aren't really 'saved',
as the messages will be padded out to use two full tunnel messages anyway.

This proposal does not require any change to the specifications.
It is posted as a proposal solely to facilitate discussion and consensus-building
of the recommended value and of the implementation details.


Goals
-----

- Increase negotiated MTU
- Maximize usage of 1 KB tunnel messages
- Do not change streaming protocol


Design
======

Use the existing MAX_PACKET_SIZE_INCLUDED option and MTU negotiation.
Streaming continues to use the minimum of the sent and received MTU.
The default remains 1730 for all connections, no matter what keys are used.

Implementations are encouraged to include the MAX_PACKET_SIZE_INCLUDED option in all SYN packets, in both directions,
although this is not a requirement.

If a destination is ECIES-only, use the higher value (either as Alice or Bob).
If a destination is dual-key, behavior may vary:

If dual-key client is outside the router (in an external application),
it may not "know" the key being used at the far-end, and Alice may request
a higher value in the SYN, while the max data in the SYN remains 1730.

If dual-key client is inside the router, the information of what key
is being used may or may not be known to the client.
The leaseset may not have been fetched yet, or the internal API interfaces
may not easily make that information available to the client.
If the information is available, Alice may use the higher value;
otherwise, Alice must use the standard value of 1730 until negotiated.

A dual-key client as Bob may send the higher value in response,
even if no value or a value of 1730 was received from Alice;
however, there is no provision for negotiating upwards in streaming,
so the MTU should remain at 1730.


As noted in [STREAMING-OPTIONS]_,
the data in the SYN packets sent from Alice to Bob may exceed Bob's MTU.
This is a weakness in the streaming protocol.
Therefore, dual-key clients must limit the data in the sent SYN packets
to 1730 bytes, while sending a higher MTU option.
Once the higher MTU is received from Bob, Alice may increase the actual maximum
payload sent.


Analysis
----------

As described in [ECIES]_, the ElGamal overhead for existing session messages is
151 bytes, and the Ratchet overhead is 69 bytes.
Therefore, we may increase the MTU for ratchet connections by (151 - 69) = 82 bytes,
from 1730 to 1812.



Specification
=============

Add the following changes and clarifications to the MTU Selection and Negotiation section of [STREAMING-OPTIONS]_.
No changes to [STREAMING-SPEC]_.


The default value of the option i2p.streaming.maxMessageSize remains 1730 for all connections, no matter what keys are used.
Clients must use the minimum of the sent and received MTU, as usual.

There are four related MTU contants and variables:

- DEFAULT_MTU: 1730, unchanged, for all connections
- i2cp.streaming.maxMessageSize: default 1730 or 1812, may be changed by configuration
- ALICE_SYN_MAX_DATA: The maximum data that Alice may include in a SYN packet
- negotiated_mtu: The minimum of Alice's and Bob's MTU, to be used as the max data size
  in the SYN ACK from Bob to Alice, and in all subsequent packets sent in both directions


There are five cases to consider:


1) Alice ElGamal-only
---------------------------------
No change, 1730 MTU in all packets.

- ALICE_SYN_MAX_DATA = 1730
- i2cp.streaming.maxMessageSize default: 1730
- Alice may send MAX_PACKET_SIZE_INCLUDED in SYN, not required unless != 1730


2) Alice ECIES-only
---------------------------------
1812 MTU in all packets.

- ALICE_SYN_MAX_DATA = 1812
- i2cp.streaming.maxMessageSize default: 1812
- Alice must send MAX_PACKET_SIZE_INCLUDED in SYN



3) Alice Dual-Key and knows Bob is ElGamal
----------------------------------------------
1730 MTU in all packets.

- ALICE_SYN_MAX_DATA = 1730
- i2cp.streaming.maxMessageSize default: 1812
- Alice may send MAX_PACKET_SIZE_INCLUDED in SYN, not required unless != 1730



4) Alice Dual-Key and knows Bob is ECIES
------------------------------------------
1812 MTU in all packets.

- ALICE_SYN_MAX_DATA = 1812
- i2cp.streaming.maxMessageSize default: 1812
- Alice must send MAX_PACKET_SIZE_INCLUDED in SYN



5) Alice Dual-Key and Bob key is unknown
------------------------------------------
Send 1812 as MAX_PACKET_SIZE_INCLUDED in SYN packet but limit SYN packet data to 1730.

- ALICE_SYN_MAX_DATA = 1730
- i2cp.streaming.maxMessageSize default: 1812
- Alice must send MAX_PACKET_SIZE_INCLUDED in SYN


For all cases
-----------------

Alice and Bob calculate
negotiated_mtu, the minimum of Alice's and Bob's MTU, to be used as the max data size
in the SYN ACK from Bob to Alice, and in all subsequent packets sent in both directions.




Justification
=============

See [CALCULATION]_ for why the current value is 1730.
See [ECIES]_ for why the ECIES overhead is 82 bytes less than ElGamal.



Implementation Notes
=====================

If streaming is creating messages of optimal size, it's very important that
the ECIES-Ratchet layer does not pad beyond that size.

The optimal Garlic Message size to fit into two tunnel messages,
including the 16 byte Garlic Message I2NP header, 4 byte Garlic Message Length,
8 byte ES tag, and 16 byte MAC, is 1956 bytes.

A recommended padding algorithm in ECIES is as follows:

- If the total length of the Garlic Message would be 1954-1956 bytes,
  do not add a padding block (no room)
- If the total length of the Garlic Message would be 1938-1953 bytes,
  add a padding block to pad to exactly 1956 bytes.
- Otherwise, pad as usual, for example with a random amount 0-15 bytes.

Similar strategies could be used at the optimal one-tunnel-message size (964)
and three-tunnel-message size (2952), although these sizes should be rare in practice.



Issues
======

The 1812 value is preliminary. To be confirmed and possibly adjusted.




Migration
=========

No backward compatibility issues.
This is an existing option and MTU negotiation is already part of the specification.

Older ECIES destinations will support 1730.
Any client receiving a higher value will respond with 1730, and the far-end
will negotiate downward, as usual.



References
==========

.. [CALCULATION]
   https://github.com/i2p/i2p.i2p/blob/master/apps/streaming/java/src/net/i2p/client/streaming/impl/ConnectionOptions.java#L220

.. [ECIES]
   {{ spec_url('ecies') }}#overhead

.. [STREAMING-OPTIONS]
    {{ site_url('docs/api/streaming', True) }}

.. [STREAMING-SPEC]
    {{ spec_url('streaming') }}#flags-and-option-data-fields
