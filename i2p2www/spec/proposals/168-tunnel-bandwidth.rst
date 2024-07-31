===================================
Tunnel Bandwidth Parameters
===================================
.. meta::
    :author: zzz
    :created: 2024-07-31
    :thread: http://zzz.i2p/topics/3652
    :lastupdated: 2024-07-31
    :status: Open
    :target: 0.9.65

.. contents::



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

This proposal addresses the issue by adding bandwidth parameters to
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

The following two options may be set in the tunnel build options mapping field of the record:
A requesting router may include either or both.

- m := minimum bandwidth required for this tunnel (KBps positive integer as a string)
- r := requested bandwidth for this tunnel (KBps positive integer as a string)

The participating router should reject the tunnel if "m" is specified and it cannot
provide at least that much bandwidth.


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

Implementations may use available bandwidth or any other data, algorithm, local policy,
or local configuration to calculate the bandwidth value returned in the
build response. Not specified by this proposal.

This proposal does not require participating hops to implement per-tunnel or global
throttling of any type, or specify a particular algorithm or implementation, if any.

This proposal also does not require client routers to throttle traffic
to the limit returned by the participating hop, and depending on application,
that may not be possible, particularly for inbound tunnels.



Security Analysis
=================

Client fingerprinting based on requests.
The client (originating) router may wish to randomize the "m" and "r" values instead of sending
the same value to each hop; or send a limited set values that represent bandwidth "buckets",
or some conbination of both.

Avoid over-allocation ddos.




Compatibility
===============

No issues. All known implementations currently ignore the mapping field in build messages,
and correctly skip over a non-empty options field.


Migration
=========

Implementations may add support at any time, no coordination is needed.



References
==========

.. [Tunnel-Creation-ECIES]
    {{ spec_url('tunnel-creation-ecies') }}
