====================================
OBEP Delivery to One-of-Many Tunnels
====================================
.. meta::
    :author: zzz
    :created: 2016-03-10
    :thread: http://zzz.i2p/topics/2099
    :lastupdated: 2016-03-10
    :status: Draft

.. contents::


Introduction
============

To reduce connection congestion, give the OBEP a list of id/hash pairs (i.e.
leases) to deliver the message to rather than just one. The OBEP would select
one of those to deliver to. The OBEP would select, if available, one that it is
already connected to, or already knows about.

The originator (OBGW) would stick some (all?) of the target leases in the
delivery instructions instead of picking just one.

This would make the OBEP-IBGW path faster and more reliable, and reduce overall
network connections.

Proposal
========

We have one unused delivery type (0x03) and two remaining bits 0 and 1) in the
flags. Because we've previously discussed multicast at the OBEP (deliver to all
specified leases), we could plan for that feature as well at the same time.

So the specification proposal is::

  Flag byte:
    Delivery type 0x03: count byte and multiple id/hash pairs follow
  Bit 0: 0 to deliver to one of the tunnels; 1 to deliver to all of the tunnels
  Count byte: 2-255 number of id/hash pairs to follow (36 bytes each)
  That many id/hash pairs (36 bytes each)
  rest of delivery instructions unchanged
