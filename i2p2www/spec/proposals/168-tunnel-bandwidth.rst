===================================
Tunnel Bandwidth Parameters
===================================
.. meta::
    :author: zzz
    :created: 2024-07-31
    :thread: http://zzz.i2p/topics/3652
    :lastupdated: 2024-12-10
    :status: Closed
    :target: 0.9.65

.. contents::



NOTE
====

This proposal was approved and is now in the
[Tunnel-Creation-ECIES]_ specification as of API 0.9.65.
There are no known implementations yet; implementation dates / API versions are TBD.



Overview
========

As we have increased the performance of the network over the last several years
with new protocols, encryption types, and congestion control improvements,
faster applications such as video streaming are becoming possible.
These applications require high bandwidth at each hop in their client tunnels.

Participating routers, however, do not have any information about how much
bandwidth a tunnel will use when they get a tunnel build message.
They can only accept or reject a tunnel based on the current total bandwidth
used by all participating tunnels and the total bandwidth limit for participating tunnels.

Requesting routers also do not have any information on how much bandwidth
is available at each hop.

Also, routers currently have no way to limit inbound traffic on a tunnel.
This would be quite useful during times of overload or DDoS of a service.

This proposal addresses these issues by adding bandwidth parameters to
the tunnel build request and reply messages.



Design
======

Add bandwidth parameters to the records in ECIES tunnel build messages [Tunnel-Creation-ECIES]_
in the tunnel build options mapping field. Use short parameter names since the space available
for the options field is limited.
Tunnel build messages are fixed-size so this does not increase the
size of the messages.



Specification
=============

Update the ECIES tunnel build message specification [Tunnel-Creation-ECIES]_
as follows:

For both long and short ECIES build records:

Build Request Options
---------------------------

The following three options may be set in the tunnel build options mapping field of the record:
A requesting router may include any, all, or none.

- m := minimum bandwidth required for this tunnel (KBps positive integer as a string)
- r := requested bandwidth for this tunnel (KBps positive integer as a string)
- l := limit bandwidth for this tunnel; only sent to IBGW (KBps positive integer as a string)

Constraint: m <= r <= l

The participating router should reject the tunnel if "m" is specified and it cannot
provide at least that much bandwidth.

Request options are sent to each participant in the corresponding encrypted build request record,
and are not visible to other participants.


Build Reply Option
---------------------------

The following option may be set in the tunnel build reply options mapping field of the record,
when the response is ACCEPTED:

- b := bandwidth available for this tunnel (KBps positive integer as a string)

The participating router should include this if either "m" or "r" was specified
in the build request. The value should be at least that of the "m" value if specified,
but may be less or more than the "r" value if specified.

The participating router should attempt to reserve and provide at least this
much bandwidth for the tunnel, however this is not guaranteed.
Routers cannot predict conditions 10 minutes into the future, and
participating traffic is lower-priority than a router's own traffic and tunnels.

Routers may also over-allocate available bandwidth if necessary, and this is
probably desirable, as other hops in the tunnel could reject it.

For these reasons, the participating router's reply should be treated
as a best-effort commitment, but not a guarantee.

Reply options are sent to the requesting router in the corresponding encrypted build reply record,
and are not visible to other participants.


Implementation Notes
=====================

Bandwidth parameters are as seen at the participating routers at the tunnel layer,
i.e. the number of fixed-size 1 KB tunnel messages per second.
Transport (NTCP2 or SSU2) overhead is not included.

This bandwidth may be much more or less than the bandwidth seen at the client.
Tunnel messages contain substantial overhead, including overhead from higher layers
including ratchet and streaming. Intermittent small messages such as streaming acks
will be expanded to 1 KB each.
However, gzip compression at the I2CP layer may substantially reduce bandwidth.

The simplest implementation at the requesting router is to use
the average, minimum, and/or maximum bandwidths of current tunnels in the pool
to calculate the values to put in the request.
More complex algorithms are possible and are up to the implementer.

There are no current I2CP or SAM options defined for the client to tell the
router what bandwidth is required, and no new options are proposed here.
Options may be defined at a later date if necessary.

Implementations may use available bandwidth or any other data, algorithm, local policy,
or local configuration to calculate the bandwidth value returned in the
build response. Not specified by this proposal.

This proposal requires inbound gateways to implement per-tunnel
throttling if requested by the "l" option.
It does not require other participating hops to implement per-tunnel or global
throttling of any type, or specify a particular algorithm or implementation, if any.

This proposal also does not require client routers to throttle traffic
to the "b" value returned by the participating hop, and depending on application,
that may not be possible, particularly for inbound tunnels.

This proposal only affects tunnels created by the originator. There is no
method defined to request or allocate bandwidth for "far-end" tunnels created
by the the owner of the other end of an end-to-end connection.



Security Analysis
=================

Client fingerprinting or correlation may be possible based on requests.
The client (originating) router may wish to randomize the "m" and "r" values instead of sending
the same value to each hop; or send a limited set values that represent bandwidth "buckets",
or some combination of both.

Over-allocation DDoS: While it may be possible to DDoS a router now by building and
using a large number of tunnels through it, this proposal arguably makes it much easier,
by simply requesting one or more tunnels with large bandwidth requests.

Implementations can and should use one or more of the following strategies
to mitigate this risk:

- Overallocation of available bandwidth
- Limit per-tunnel allocation to some percentage of available bandwidth
- Limit rate of increase in allocated bandwidth
- Limit rate of increase in used bandwidth
- Limit allocated bandwidth for a tunnel if not used early in a tunnel's lifetime (use it or lose it)
- Tracking average bandwidth per tunnel
- Tracking requested vs. actual bandwidth used per tunnel


Compatibility
===============

No issues. All known implementations currently ignore the mapping field in build messages,
and correctly skip over a non-empty options field.


Migration
=========

Implementations may add support at any time, no coordination is needed.

As there is currently no API version defined where support for this proposal is required,
routers should check for a "b" response to confirm support.



References
==========

.. [Tunnel-Creation-ECIES]
    {{ spec_url('tunnel-creation-ecies') }}
