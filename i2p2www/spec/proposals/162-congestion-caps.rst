============================
Congestion Caps
============================
.. meta::
    :author: dr|z3d, idk, orignal, zzz
    :created: 2023-01-24
    :thread: http://zzz.i2p/topics/3516
    :lastupdated: 2023-02-01
    :status: Open
    :target: 0.9.59

.. contents::



Overview
========

Add congestion indicators to the published Router Info (RI).




Motivation
==========

Bandwidth "caps" (capabilities) indicate share bandwidth limits and reachability but not congestion state.
A congestion indicator will help routers avoid attempting to build through a congested router,
which contributes to more congestion and reduced tunnel build success.



Design
======

Define new caps to indicate various levels of congestion or capacity issues.
These will go in the top-level RI caps, not the address caps.


Congestion Definition
----------------------

Congestion, in general, means that the peer is unlikely to
receive and accept a tunnel build request.
How to define or classify congestion levels is implementation-specific.

Implementations may consider one or more of the following:

- At or near bandwidth limits
- At or near max participating tunnels
- At or near max connections on one or more transports
- Over threshold for queue depth, latency, or CPU usage; internal queue overflow
- Base platform / OS CPU and memory capabilities
- Perceived network congestion
- Network state such as firewalled or symmetric NAT or hidden or proxied
- Configured not to accept tunnels

Congestion state should be based on an average of conditions
over several minutes, not an instantaneous measurement.



Specification
=============

Update [NETDB]_ as follows:


.. raw:: html

  {% highlight %}
D: Medium congestion, or a low-performance router (e.g. Android, Raspberry Pi)
     Other routers should downgrade or limit this router's
     apparent tunnel capacity in the profile.

  E: High congestion, this router is near or at some limit,
     and is rejecting or dropping most tunnel requests.
     If this RI was published in the last 15 minutes, other routers
     should severely downgrade or limit this router's capacity.
     If this RI is older than 15 minutes, treat as 'D'.

  G: This router is temporarily or permanently rejecting all tunnels.
     Do not attempt to build a tunnel through this router,
     until a new RI is received without the 'G'.
{% endhighlight %}

For consistency, implementations should add any congestion cap
at the end (after R or U).



Security Analysis
=================

Any published peer information cannot be trusted.
Caps, like anything else in the Router Info, may be spoofed.
We never use anything in the Router Info to up-rate a router's perceived capacity.

Publishing congestion indicators, telling peers to avoid this router, is inherently
much more secure than permissive or capacity indicators solicting more tunnels.

The current bandwidth capacity indicators (L-P, X) are trusted only to avoid
very low-bandwidth routers. The "U" (unreachable) cap has a similar effect.

Any published congestion indicator should have the same effect as
rejecting or dropping a tunnel build request, with similar security properties.



Notes
=====

Peers must not to completely avoid 'D' routers, only derate them.

Care must be taken not to completely avoid 'E' routers,
so when the whole network is in congestion and publishing 'E',
things don't completely break.

Routers may use different strategies for what types of tunnels to build through 'D' and 'E' routers,
for example exploratory vs. client, or high vs. low bandwidth client tunnels.

Routers should probably not publish a congestion cap at startup or shutdown by default,
even if their network state is unknown, to prevent restart detection by peers.




Compatibility
===============

No issues, all implementations ignore unknown caps.


Migration
=========

Implementations may add support at any time, no coordination needed.

Preliminary plan:
Publish caps in 0.9.58 (April 2023);
act on published caps in 0.9.59 (July 2023).



References
==========

.. [NETDB]
    {{ site_url('docs/how/network-database', True) }}
