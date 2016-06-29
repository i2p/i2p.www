=================
IPv6 Peer Testing
=================
.. meta::
    :author: zzz
    :created: 2016-05-02
    :thread: http://zzz.i2p/topics/2119
    :lastupdated: 2016-06-29
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

Implement Peer Testing for IPv6,
by removing previous restrictions that peer testing was only allowed for IPv4.
The peer test message already has a field for IP length.


Specification
=============

In the Peer Testing sections of the SSU overview and SSU specification, make the following changes:

IPv6 Notes:
Through release 0.9.26, only testing of IPv4 addresses is supported.
Only testing of IPv4 addresses is supported.
Therefore, all Alice-Bob and Alice-Charlie communication must be via IPv4.
Bob-Charlie communication, however, may be via IPv4 or IPv6.
Alice's address, when specified in the PeerTest message, must be 4 bytes.
As of release 0.9.27, testing of IPv6 addresses is supported, and Alice-Bob and Alice-Charlie communication may be via IPv6.

Alice sends the request to Bob using an existing session over the transport (IPv4 or IPv6) that she wishes to test.
When Bob receives a request from Alice via IPv4, Bob must select a Charlie that advertises an IPv4 address.
When Bob receives a request from Alice via IPv6, Bob must select a Charlie that advertises an IPv6 address.
The actual Bob-Charlie communication may be via IPv4 or IPv6 (i.e., independent of Alice's address type).
