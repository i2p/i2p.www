=================
IPv6 Peer Testing
=================
.. meta::
    :author: zzz
    :created: 2016-05-02
    :thread: http://zzz.i2p/topics/2119
    :lastupdated: 2016-05-02
    :status: Open

.. contents::


Overview
========

This proposal is to implement SSU Peer Testing for IPv6.


Motivation
==========

We cannot reliably determine and track if our IPv6 address is firewalled.

When we added IPv6 support years ago, we assumed that IPv6 was never firewalled.

More recently, in 0.9.20 (May 2015), we split up v4/v6 reachability status internally (ticket #1458).
See that ticket for extensive info and links.

If you have both v4 and v6 firewalled, you can just force firewalled in the TCP configuration section on /confignet.

We don't have peer testing for v6. It's prohibited in the SSU spec.
If we can't regularly test v6 reachability, we can't sensibly transition from/to the v6 reachable state.
What we're left with is guessing that we are reachable if we get an inbound conn,
and guessing that we aren't if we haven't gotten an inbound conn in a while.
The problem is that once you declare unreachable, you don't publish your v6 IP,
and then you won't get any more (after the RI expires in everybody's netdb).


Design
======

Implement Peer Testing for IPv6.


Specification
=============

TBD, but basically, allow IPv6 addresses and connections in the Peer Testing protocol.
