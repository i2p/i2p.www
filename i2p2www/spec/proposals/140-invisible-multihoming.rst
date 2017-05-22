=====================
Invisible Multihoming
=====================
.. meta::
    :author: str4d
    :created: 2017-05-22
    :thread: http://zzz.i2p/topics/2335
    :lastupdated: 2017-05-22
    :status: Open

.. contents::


Overview
========

This proposal outlines a design for a protocol enabling an I2P client or service
to transparently use multiple routers to host a single [Destination]_.

The proposal currently does not specify a concrete implementation. It could be
implemented as an extension to [I2CP]_, or as a new protocol.


Motivation
==========

Multihoming is where multiple routers are used to host the same Destination.
The current way to multihome with I2P is to run the same Destination on each
router independently; the router that gets used by clients at any particular
time is the last one to publish a LeaseSet.

This is a hack and presumably won't work for large websites at scale. Say we had
100 multihoming routers (edges) each with 16 tunnels. That's 1600 LeaseSet
publishes every 10 minutes, or almost 3 per second. The floodfills would get
overwhelmed and throttles would kick in. And that's before we even mention the
lookup traffic.

[Prop120]_ solves this problem with a meta-LeaseSet, which lists the 100 real
[LeaseSet]_ hashes. A lookup becomes a two-stage process: first looking up the
meta-LeaseSet, and then one of the named LeaseSets. This is a good solution to
the lookup traffic issue, but on its own it creates a significant privacy leak:
It is possible to determine which multihoming routers are online by monitoring
the published meta-LeaseSet, because each real LeaseSet has corresponds to a
single edge.

We need a way for an I2P client or service to spread a single Destination across
multiple edge routers, in a way that is indistinguishable to using a single
router (from the perspective of the LeaseSet itself).


Design
======

High-level overview
-------------------

Imagine the following desired configuration:

- A client application with one Destination.
- Four edge routers, each managing three tunnels.
- All twelve tunnels should be published in a single LeaseSet.

.. raw:: html

  {% highlight lang='text' %}
                -{ [Tunnel 1]===\
                 |-{ [Tunnel 2]====[Edge Router 1]-----
                 |-{ [Tunnel 3]===/                    \
                 |                                      \
                 |-{ [Tunnel 4]===\                      \
  [Destination]  |-{ [Tunnel 5]====[Edge Router 2]-----   \
    \            |-{ [Tunnel 6]===/                    \   \
     [LeaseSet]--|                                    [Client]
                 |-{ [Tunnel 7]===\                    /   /
                 |-{ [Tunnel 8]====[Edge Router 3]-----   /
                 |-{ [Tunnel 9]===/                      /
                 |                                      /
                 |-{ [Tunnel 10]==\                    /
                 |-{ [Tunnel 11]===[Edge Router 4]-----
                  -{ [Tunnel 12]==/
{% endhighlight %}

To create and manage this configuration, the client needs the following new
functionality beyond what is currently provided by [I2CP]_:

- Tell a router to build tunnels, without creating a LeaseSet for them.
- Get a list of the current tunnels in the inbound pool.

Additionally, the following functionality would enable significant flexibility
in how the client manages its tunnels:

- Get the contents of a router's fast tier.
- Tell a router to build an inbound or outbound tunnel using a given list of
  peers.

General client process
``````````````````````
- Load or generate a Destination.

- Open up a session with each edge router, tied to the Destination.

- Periodically (around every ten minutes, but more or less based on tunnel
  liveness):

  - Obtain the fast tier from each edge.

  - Use the superset of peers to build tunnels to/from each edge.

    - By default, tunnels to/from a particular edge router will use peers from
      that router's fast tier, but this is not enforced by the protocol.

  - Collect the set of active inbound tunnels from all active edges, and create a
    LeaseSet.

  - Publish the LeaseSet through one or more of the edges.

Protocol outline
----------------

.. raw:: html

  {% highlight %}
         Client                           Edge Router

                    --------------------->  Create Session
   Session Status  <---------------------
                    --------------------->  Get Fast Tier
        Peer List  <---------------------
                    --------------------->  Create Tunnel
    Tunnel Status  <---------------------
                    --------------------->  Get Tunnel Pool
      Tunnel List  <---------------------
                    --------------------->  Publish LeaseSet
                    --------------------->  Send Packet
      Send Status  <---------------------
  Packet Received  <---------------------
{% endhighlight %}

Messages
````````
    Create Session
        Create a session for the given Destination.

    Session Status
        Confirmation that the session has been set up, and the client can now
        start building tunnels.

    Get Fast Tier
        Request a list of the peers that the router currently would consider
        building tunnels through.

    Peer List
        A list of peers known to the router.

    Create Tunnel
        Request that the router build a new tunnel through the specified peers.

    Tunnel Status
        The result of a particular tunnel build, once it is available.

    Get Tunnel Pool
        Request a list of the current tunnels in the inbound or outbound pool
        for the Destination.

    Tunnel List
        A list of tunnels for the requested pool.

    Publish LeaseSet
        Request that the router publish the provided LeaseSet through one of the
        outbound tunnels for the Destination. No reply status is needed; the
        router should continue re-trying until it is satisfied that the LeaseSet
        has been published.

    Send Packet
        An outgoing packet from the client. Optionally specifies an outbound
        tunnel through which the packet must (should?) be sent.

    Send Status
        Informs the client of the success or failure of sending a packet.

    Packet Received
        An incoming packet for the client. Optionally specifies the inbound
        tunnel through which the packet was received(?)


Security implications
=====================

From the perspective of the edge routers, this design is functionally equivalent
to the status quo. The edge router still builds all tunnels, maintains its own
peer profiles, and enforces separation between router and client operations. In
the default configuration is completely identical, because tunnels for that edge
are built from its own fast tier.

From the perspective of the netDB, a single LeaseSet created via this protocol
is identical to the status quo, because it leverages pre-existing functionality.
However, for larger LeaseSets approaching 16 Leases, it may be possible for an
observer to determine that the LeaseSet is multihomed:

- The current maximum size of the fast tier is 75 peers. The Inbound Gateway
  (IBGW, the node published in a Lease) is selected from a fraction of the tier
  (partitioned randomly per-tunnel pool by hash, not count):

      1 hop
          The whole fast tier

      2 hops
          Half of the fast tier
          (the default until mid-2014)

      3+ hops
          A quarter of the fast tier
          (3 being the current default)

  That means on average the IBGWs will be from a set of 20-30 peers.

- In a single-homed setup, a full 16-tunnel LeaseSet would have 16 IBGWs
  randomly selected from a set of up to (say) 20 peers.

- In a 4-edge multihomed setup using the default configuration, a full 16-tunnel
  LeaseSet would have 16 IBGWs randomly-selected from a set of at most 80 peers,
  though there are likely to be a fraction of common peers between edge nodes.

Thus with the default configuration, it may be possible through statistical
analysis to figure out that a LeaseSet is being generated by this protocol. It
might also be possible to figure out how many edge nodes there are, although the
effect of churn on the fast tiers would reduce the effectiveness of this
analysis.

As the client has full control over which peers it selects, this information
leakage could be reduced or eliminated by selecting IBGWs from a reduced set of
peers.


Compatibility
=============

This design is completely backwards-compatible with the network, because there
are no changes to the [LeaseSet]_ format. All edge routers would need to be
aware of the new protocol, but this is not a concern as they would all be
controlled by the same entity.


Performance and scalability notes
=================================

The upper limit of 16 [Leases]_ per LeaseSet is unaltered by this proposal. For
Destinations that require more tunnels than this, there are two possible network
modifications:

- Increase the upper limit on the size of LeaseSets. This would be the simplest
  to implement (though it would still require pervasive network support before
  it could be widely used), but could result in slower lookups due to the larger
  packet sizes. The maximum feasible LeaseSet size is defined by the MTU of the
  underlying transports, and is therefore around 16kB.

- Implement [Prop120]_ for tiered LeaseSets. In combination with this proposal,
  the Destinations for the sub-LeaseSets could be spread across multiple edges,
  effectively acting like multiple IP addresses for a clearnet service.


Acknowledgements
================

Thanks to psi for the discussion that led to this proposal.


References
==========

.. [Destination]
    {{ ctags_url('Destination') }}

.. [I2CP]
    {{ site_url('docs/protocol/i2cp', True) }}

.. [Leases]
    {{ ctags_url('Lease') }}

.. [LeaseSet]
    {{ ctags_url('LeaseSet') }}

.. [Prop120]
    {{ proposal_url('120') }}
