================================
IPv6 Transport Enhancements
================================
.. meta::
    :author: zzz, orignal
    :created: 2021-03-19
    :thread: http://zzz.i2p/topics/3060
    :lastupdated: 2021-04-26
    :status: Closed
    :target: 0.9.50

.. contents::


Note
====
Network deployment and testing in progress.
Subject to minor revisions.


Overview
========

This proposal is to implement enhancements to the SSU and NTCP2 transports for IPv6.


Motivation
==========

As IPv6 grows around the world and IPv6-only setups (especially on mobile) becomes more common,
we need to improve our support for IPv6 and remove the assumptions that
all routers are IPv4-capable.



Connectivity Checking
-----------------------

When selecting peers for tunnels, or selecting OBEP/IBGW paths for routing messages,
it helps to calculate whether router A can connect to router B.
In general, this means determining if A has outbound capability for a transport and address type (IPv4/v6)
that matches one of B's advertised inbound addresses.

However, in many cases we don't know A's capabilites and have to make assumptions.
If A is hidden or firewalled, the addresses are not published, and we don't have direct knowledge -
so we assume it's IPv4 capable, and not IPv6 capable.
The solution is adding two new "caps" or capabilities to the Router Info to indicate outbound capability for IPv4 and IPv6.


IPv6 Introducers
----------------------------------

Our specifications [SSU]_ and [SSU-SPEC]_ contain errors and inconsistencies about whether
IPv6 introducers are supported for IPv4 introductions.
In any case, this has never been implemented in either Java I2P or i2pd.
This needs to be corrected.


IPv6 Introdutions
----------------------------------

Our specifications [SSU]_ and [SSU-SPEC]_ make clear that
IPv6 introductions are not supported.
This was under the assumption that IPv6 is never firewalled.
This is clearly not true, and we need to improve support for firewalled IPv6 routers.


Introduction Diagrams
-------------------------

Legend: ----- is IPv4, ====== is IPv6

Current IPv4-only:

.. raw:: html

  {% highlight %}
        Alice                         Bob                  Charlie
    RelayRequest ---------------------->
         <-------------- RelayResponse    RelayIntro ----------->
         <-------------------------------------------- HolePunch
    SessionRequest -------------------------------------------->
         <-------------------------------------------- SessionCreated
    SessionConfirmed ------------------------------------------>
    Data <--------------------------------------------------> Data
{% endhighlight %}


IPv4 introduction, IPv6 introducer

.. raw:: html

  {% highlight %}
Alice                         Bob                  Charlie
    RelayRequest ======================>
         <============== RelayResponse    RelayIntro ----------->
         <-------------------------------------------- HolePunch
    SessionRequest -------------------------------------------->
         <-------------------------------------------- SessionCreated
    SessionConfirmed ------------------------------------------>
    Data <--------------------------------------------------> Data
{% endhighlight %}

IPv6 introduction, IPv6 introducer


.. raw:: html

  {% highlight %}
Alice                         Bob                  Charlie
    RelayRequest ======================>
         <============== RelayResponse    RelayIntro ===========>
         <============================================ HolePunch
    SessionRequest ============================================>
         <============================================ SessionCreated
    SessionConfirmed ==========================================>
    Data <==================================================> Data
{% endhighlight %}

IPv6 introduction, IPv4 introducer

.. raw:: html

  {% highlight %}
Alice                         Bob                  Charlie
    RelayRequest ---------------------->
         <-------------- RelayResponse    RelayIntro ===========>
         <============================================ HolePunch
    SessionRequest ============================================>
         <============================================ SessionCreated
    SessionConfirmed ==========================================>
    Data <==================================================> Data
{% endhighlight %}


Design
======

There are three changes to be implemented.

- Add "4" and "6" capabilities to Router Address capabilities to indicate outbound IPv4 and IPv6 support
- Add support for IPv4 introductions via IPv6 introducers
- Add support for IPv6 introductions via IPv4 and IPv6 introducers



Specification
=============

4/6 Caps
--------

This was originally implemented without a formal proposal, but it is required for
IPv6 introductions, so we include it here.
See also [CAPS]_.


Two new capabilities "4" and "6" are defined.
These new capabilities will be added to the "caps" property in the Router Address, not in the Router Info caps.
We currently don't have a "caps" property defined for NTCP2.
An SSU address with introducers is, by definition, ipv4 right now. We don't support ipv6 introduction at all.
However, this proposal is compatible with a IPv6 introductions. See below.

Additionally, a router may support connectivity via an overlay network such as I2P-over-Yggdrasil,
but does not wish to publish an address, or that address does not have a standard IPv4 or IPv6 format.
This new capability system should be flexible enough to support these networks as well.

We define the following changes:

NTCP2: Add "caps" property

SSU: Add support for a Router Address without a host or introducers, to indicate outbound support
for IPv4, IPv6, or both.

Both transports: Define the following caps values:

- "4": IPv4 support
- "6": IPv6 support

Multiple values may be supported in a single address. See below.
At least one of these caps are mandatory if no "host" value is included in the Router Address.
At most one of these caps is optional if a "host" value is included in the Router Address.
Additional transport caps may be defined in the future to indicate support for overlay networks or other connectivity.


Use cases and examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~

SSU:

SSU with host: 4/6 optional, never more than one.
Example: SSU caps="4" host="1.2.3.4" key=... port="1234"

SSU outbound only for one, other is published: Caps only, 4/6.
Example: SSU caps="6"

SSU with introducers: never combined. 4 or 6 is required.
Example: SSU caps="4" iexp0=... ihost0=... iport0=... itag0=... key=...

SSU hidden: Caps only, 4, 6, or 46. Multiple is allowed.
No need for two addresses one with 4 and one with 6.
Example: SSU caps="46"

NTCP2:

NTCP2 with host: 4/6 optional, never more than one.
Example: NTCP2 caps="4" host="1.2.3.4" i=... port="1234" s=... v="2"

NTCP2 outbound only for one, other is published: Caps, s, v only, 4/6/y, multiple is allowed.
Example: NTCP2 caps="6" i=... s=... v="2"

NTCP2 hidden: Caps, s, v only 4/6, multiple is allowed No need for two addresses one with 4 and one with 6.
Example: NTCP2 caps="46" i=... s=... v="2"



IPv6 Introducers for IPv4
----------------------------

The following changes are required to correct errors and inconsistencies in the specs.
We have also described this as "part 1" of the proposal.

Spec Changes
~~~~~~~~~~~~~~~~

[SSU]_ currently says (IPv6 notes):

IPv6 is supported as of version 0.9.8. Published relay addresses may be IPv4 or IPv6, and Alice-Bob communication may be via IPv4 or IPv6.

Add the following:

While the specification was changed as of version 0.9.8, Alice-Bob communication via IPv6 was not actually supported until version 0.9.50.
Earlier versions of Java routers erroneously published the 'C' capability for IPv6 addresses,
even though they did not actually act as an introducer via IPv6.
Therefore, routers should only trust the 'C' capability on an IPv6 address if the router version is 0.9.50 or higher.



[SSU-SPEC]_ currently says (Relay Request):

The IP address is only included if it is be different than the packet's source address and port.
In the current implementation, the IP length is always 0 and the port is always 0,
and the receiver should use the packet's source address and port.
This message may be sent via IPv4 or IPv6. If IPv6, Alice must include her IPv4 address and port.

Add the following:

The IP and port must be included to introduce an IPv4 address when sending this message over IPv6.
This is supported as of release 0.9.50.



IPv6 Introductions
----------------------------

All three of the SSU relay messages (RelayRequest, RelayResponse, and RelayIntro) contain IP length fields
to indicate the length of the (Alice, Bob, or Charlie) IP address to follow.

Therefore, no change to the format of the messages is required.
Only textual changes to the specifications, indicating that 16-byte IP addresses are allowed.

The following changes are required to the specs.
We have also described this as "part 2" of the proposal.


Spec Changes
~~~~~~~~~~~~~~~~

[SSU]_ currently says (IPv6 notes):

Bob-Charlie and Alice-Charlie communication is via IPv4 only.

[SSU-SPEC]_ currently says (Relay Request):

There are no plans to implement relaying for IPv6.

Change to say:

Relaying for IPv6 is supported as of release 0.9.xx

[SSU-SPEC]_ currently says (Relay Response):

Charlie's IP address must be IPv4, as that is the address that Alice will send the SessionRequest to after the Hole Punch.
There are no plans to implement relaying for IPv6.

Change to say:

Charlie's IP address may be IPv4 or, as of release 0.9.xx, IPv6.
That is the address that Alice will send the SessionRequest to after the Hole Punch.
Relaying for IPv6 is supported as of release 0.9.xx

[SSU-SPEC]_ currently says (Relay Intro):

Alice's IP address is always 4 bytes in the current implementation, because Alice is trying to connect to Charlie via IPv4.
This message must be sent via an established IPv4 connection,
as that's the only way that Bob knows Charlie's IPv4 address to return to Alice in the RelayResponse.

Change to say:

For IPv4, Alice's IP address is always 4 bytes, because Alice is trying to connect to Charlie via IPv4.
As of release 0.9.xx, IPv6 is supported, and Alice's IP address may be 16 bytes.

For IPv4, this message must be sent via an established IPv4 connection,
as that's the only way that Bob knows Charlie's IPv4 address to return to Alice in the RelayResponse.
As of release 0.9.xx, IPv6 is supported, and this message may be sent via an established IPv6 connection.

Also add:

As of release 0.9.xx, any SSU address published with introducers must contain "4" or "6" in the "caps" option.


Migration
=========

All old routers should ignore the caps property in NTCP2, and unknown capability characters in the SSU caps property.

Any SSU address with introducers that does not contain a "4" or "6" cap is assumed to be for IPv4 introduction.





References
==========

.. [CAPS]
    http://zzz.i2p/topics/3050

.. [NTCP2]
    {{ spec_url('ntcp2') }}

.. [SSU]
    {{ site_url('docs/transport/ssu', True) }}

.. [SSU-SPEC]
    {{ spec_url('ssu') }}
