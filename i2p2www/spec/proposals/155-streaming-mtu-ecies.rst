========================================
Streaming MTU for ECIES Destinations
========================================
.. meta::
    :author: zzz
    :created: 2020-05-06
    :thread: http://zzz.i2p/topics/2886
    :lastupdated: 2020-05-07
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

Implementations are encouraged to include the option in all SYN packets, in both directions,
although this is not a requirement.

If a destination is ECIES-only, send the higher value (either as Alice or Bob).
If a destination is dual-key, behavior may vary:

If dual-key client is outside the router (in an external application),
it may not "know" the key being used at the far-end, and Alice must
send the standard value of 1730.

If dual-key client is inside the router, the information of what key
is being used may or may not be known to the client.
The leaseset may not have been fetched yet, or the internal API interfaces
may not easily make that information available to the client.
If the information is available, Alice may send the higher value;
otherwise, Alice must send the standard value of 1730.

A dual-key client as Bob may send the higher value in response,
even if no value or a value of 1730 was received from Alice;
however, there is no provision for negotiating upwards in streaming,
so the MTU should remain at 1730.



Specification
=============

ECIES and dual-key ECIES destinations may send an MTU of up to 1820.
The default remains 1730 for all connections, no matter what keys are used.
Clients must use the minimum of the sent and received MTU, as usual.

This will be added as a note to [STREAMING-OPTIONS]_. 
No change to [STREAMING-SPEC]_.



Justification
=============

See [CALCULATION]_ for why the current value is 1730.
See [ECIES]_ for why the ECIES overhead is 90 bytes less than ElGamal.



Notes
=====

As noted in [STREAMING-OPTIONS],
the data in the SYN packets sent from Alice to Bob may exceed Bob's MTU.
This is a weakness in the streaming protocol.

It may be advisable, in dual-key clients, to limit the data in the sent SYN packets
to 1730 bytes, while sending an MTU option of 1820.
Once an 1820 MTU is received from Bob, Alice may increase the actual maximum
payload sent.



Issues
======

The 1820 value is preliminary. To be confirmed and possibly adjusted.




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
