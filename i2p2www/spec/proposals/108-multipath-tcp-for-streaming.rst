===========================
Multipath TCP for Streaming
===========================
.. meta::
    :author: hottuna
    :created: 2012-08-26
    :thread: http://zzz.i2p/topics/1221
    :lastupdated: 2012-08-26
    :status: Draft

.. contents::


Overview
========

This proposal is about extending streaming to use multiple tunnels per
connection, similar to multipath TCP.


Motivation
==========

Client tunnels are used by the streaming lib in a fairly standard TCP manner.

It would be preferable to allow a multipath TCP-like solution, where client
tunnels are used based on individual characteristics like:

- Latency
- Capacity
- Availability


Design
======

TBD
