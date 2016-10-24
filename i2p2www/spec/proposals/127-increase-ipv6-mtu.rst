=================
Increase IPv6 MTU
=================
.. meta::
    :author: zzz
    :created: 2016-08-23
    :thread: http://zzz.i2p/topics/2181
    :lastupdated: 2016-08-23
    :status: Open

.. contents::


Overview
========

This proposal is to increase the max SSU IPv6 MTU from 1472 to 1488.


Motivation
==========

IPv4 MTU must be a multiple of 16, + 12. IPv6 MTU must be a multiple of 16.


When IPv6 support was first added years ago, we set the max IPv6 MTU to 1472, less than the
IPv4 MTU of 1484. This was to keep things simple and ensure the IPv6 MTU was less
than the existing IPv4 MTU. Now that IPv6 support is stable, we should be able to
set the IPv6 MTU higher than the IPv4 MTU.

The typical interface MTU is 1500, so we can reasonably increase the IPv6 MTU by 16 to 1488.


Design
======

Change the max from 1472 to 1488.


Specification
=============

In the "Router Address" and "MTU" sections of the SSU overview,
change the max IPv6 MTU from 1472 to 1488.


Migration
=========

We expect that routers will set the connection MTU as the minimum of the local and remote
MTU, as usual. No version check should be required.

If we determine that a version check is required, we will set a minimum version
level of 0.9.28 for this change.
