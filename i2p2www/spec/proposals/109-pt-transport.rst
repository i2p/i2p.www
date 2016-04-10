============
PT Transport
============
.. meta::
    :author: zzz
    :created: 2014-01-09
    :thread: http://zzz.i2p/topics/1551
    :lastupdated: 2014-09-28
    :status: Draft

.. contents::


Introduction
============

The general idea is to use Pluggable Transports (PTs) as an I2P transport for
communication between routers. It would be an easy way to experiment with
alternative protocols, and get ready for I2P blocking resistance.


Thoughts
========

There are a few potential layers of implementation:

1. A generic PT that implements SOCKS and ExtORPort and configures and forks the
   in and out processes, and registers with the comm system. This layer knows
   nothing about NTCP, and it may or may not use NTCP. Good for testing.

2. Building on 1), a generic NTCP PT that builds on the NTCP code and funnels
   NTCP to 1).

3. Building on 2), a specific NTCP-xxxx PT configured to run a given external in
   and out process.
