=========================================
OBEP Delivery to 1-of-N or N-of-N Tunnels
=========================================
.. meta::
    :author: zzz, str4d
    :created: 2016-03-10
    :thread: http://zzz.i2p/topics/2099
    :lastupdated: 2017-04-07
    :status: Open

.. contents::


Overview
========

This proposal covers two improvements for improving network performance:

- Delegating IBGW selection to the OBEP by providing it with a list of
  alternatives instead of a single option.

- Enabling multicast packet routing at the OBEP.


Motivation
==========

In the direct connection case, the idea is to reduce connection congestion, by
giving the OBEP flexibility in how it connects to IBGWs. The ability to specify
multiple tunnels also enables us to implement multicast at the OBEP (by
delivering the message to all specified tunnels).

An alternative to the delegation part of this proposal would be to send through
a [LeaseSet]_ hash, similar to the existing ability to specify a target
[RouterIdentity]_ hash. This would result in a smaller message and a potentially
newer LeaseSet. However:

1. It would force the OBEP to do a lookup

2. The LeaseSet may not be published to a floodfill, so the lookup would fail.

3. The LeaseSet may be encrypted, so the OBEP couldn't get the leases.

4. Specifying a LeaseSet reveals to the OBEP the [Destination]_ of the message,
   which they could otherwise only discover by scraping all the LeaseSets in the
   network and looking for a Lease match.


Design
======

The originator (OBGW) would place some (all?) of the target [Leases]_ in the
delivery instructions [TUNNEL-DELIVERY]_ instead of picking just one.

The OBEP would select one of those to deliver to. The OBEP would select, if
available, one that it is already connected to, or already knows about. This
would make the OBEP-IBGW path faster and more reliable, and reduce overall
network connections.

We have one unused delivery type (0x03) and two remaining bits (0 and 1) in the
flags for [TUNNEL-DELIVERY]_, which we can leverage to implement these features.


Security Implications
=====================

This proposal does not change the amount of information leaked about the OBGW's
target Destination or their view of the NetDB:

- An adversary that controls the OBEP and is scraping LeaseSets from the NetDB
  can already determine whether a message is being sent to a particular
  Destination, by searching for the [TunnelId]_ / [RouterIdentity]_ pair. At
  worst, the presence of multiple Leases in the TMDI might make it faster to
  find a match in the adversary's database.

- An adversary that is operating a malicious Destination can already gain
  information about a connecting victim's view of the NetDB, by publishing
  LeaseSets containing different inbound tunnels to different floodfills, and
  observing which tunnels the OBGW connects through. From their point of view,
  the OBEP selecting which tunnel to use is functionally identical to the OBGW
  making the selection.

The multicast flag leaks the fact that the OBGW is multicasting to the OBEPs.
This creates a performance vs. privacy trade-off that should be considered when
implementing higher-level protocols. Being an optional flag, users can make
the appropriate decision for their application. There may be benefits to this
being the default behaviour for compatible applications, however, as wide-spread
usage by a variety of applications would reduce the information leakage about
which particular application a message is from.


Specification
=============

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |flag|  Tunnel ID (opt)  |              |
  +----+----+----+----+----+              +
  |                                       |
  +                                       +
  |         To Hash (optional)            |
  +                                       +
  |                                       |
  +                        +----+----+----+
  |                        |dly | Message  
  +----+----+----+----+----+----+----+----+
   ID (opt) |extended opts (opt)|cnt | (o)
  +----+----+----+----+----+----+----+----+
   Tunnel ID N   |                        |
  +----+----+----+                        +
  |                                       |
  +                                       +
  |         To Hash N (optional)          |
  +                                       +
  |                                       |
  +              +----+----+----+----+----+
  |              | Tunnel ID N+1 (o) |    |
  +----+----+----+----+----+----+----+    +
  |                                       |
  +                                       +
  |         To Hash N+1 (optional)        |
  +                                       +
  |                                       |
  +                                  +----+
  |                                  | sz
  +----+----+----+----+----+----+----+----+
       |
  +----+

  flag ::
         1 byte
         Bit order: 76543210
         bits 6-5: delivery type
                   0x03 = TUNNELS
         bit 0: multicast? If 0, deliver to one of the tunnels
                           If 1, deliver to all of the tunnels
                           Set to 0 for compatibility with future uses if
                           delivery type is not TUNNELS

  Count ::
         1 byte
         Optional, present if delivery type is TUNNELS
         2-255 - Number of id/hash pairs to follow

  Tunnel ID :: `TunnelId`
  To Hash ::
         36 bytes each
         Optional, present if delivery type is TUNNELS
         id/hash pairs

  Total length: Typical length is:
         75 bytes for count 2 TUNNELS delivery (unfragmented tunnel message);
         79 bytes for count 2 TUNNELS delivery (first fragment)

  Rest of delivery instructions unchanged
{% endhighlight %}


Compatibility
=============

The only peers that need to be understand the new specification are the OBGWs
and the OBEPs. We can therefore make this change compatible with the existing
network by making its use conditional on the target I2P version [VERSIONS]_:

* The OBGWs must select compatible OBEPs when building outbound tunnels, based
  on the I2P version advertised in their [RouterInfo]_.

* Peers that advertise the target version must support parsing the new flags,
  and must not reject the instructions as invalid.


References
==========

.. [Destination]
    {{ ctags_url('Destination') }}

.. [Leases]
    {{ ctags_url('Lease') }}

.. [LeaseSet]
    {{ ctags_url('LeaseSet') }}

.. [RouterIdentity]
    {{ ctags_url('RouterIdentity') }}

.. [RouterInfo]
    {{ ctags_url('RouterInfo') }}

.. [TUNNEL-DELIVERY]
    {{ ctags_url('TunnelMessageDeliveryInstructions') }}

.. [TunnelId]
    {{ ctags_url('TunnelId') }}

.. [VERSIONS]
    {{ spec_url('i2np') }}#protocol-versions
