==========================
Transport Network ID Check
==========================
.. meta::
    :author: zzz
    :created: 2019-02-28
    :thread: http://zzz.i2p/topics/2687
    :lastupdated: 2019-03-05
    :status: Open

.. contents::


Overview
========

NTCP2 (proposal 111) does not reject connections from different network IDs
at the Session Request phase.
The connection must currently be rejected at the Session Confirmed phase,
when Bob checks Alice's RI.

Similarly, SSU does not reject connections from different network IDs
at the Session Request phase.
The connection must currently be rejected after the Session Confirmed phase,
when Bob checks Alice's RI.

This proposal changes the Session Request phase of both transports to incorporate the
network ID, in a backwards-compatible way.


Motivation
==========

Connections from the wrong network should be rejected, and the
peer should be blacklisted, as soon as possible.


Design
======

Ideally we would XOR in the network ID somewhere in the Session Request.
Since this must be backwards-compatible, we will XOR in (id - 2)
so it will be a no-op for the current network ID value of 2.


Specification
=============

For NTCP2, XOR (id - 2) into the obfuscated X value in Session Request.

For SSU, replace the XOR of the protocol version (currently 0) with
an XOR of (id - 2) in the HMAC-MD5 calculation.


Notes
=====


Issues
======

- Should we make a similar change to NTCP 1 as well?
- Should we make changes to reseeds to prevent reseeding for the wrong network?


Migration
=========

This is backwards-compatible for the current network ID value of 2.
If any people are running networks (test or otherwise) with a different network ID value,
this change is backwards-incompatible.
However, we are not aware of anybody doing this.
If it's a test network only, it's not an issue, just update all of the routers at once.
