=================================
Prefer Nearby Routers in Keyspace
=================================
.. meta::
    :author: chisquare
    :created: 2015-04-25
    :thread: http://zzz.i2p/topics/1874
    :lastupdated: 2015-04-25
    :status: Needs-Research

.. contents::


Overview
========

This is a proposal to organize peers so that they prefer connecting to other
peers that are close to them in keyspace.


Motivation
==========

The idea is to improve tunnel build success, by increasing the probability that
a router is already connected to another.


Design
======

Required Changes
----------------

This change would require:

1. Every router prefer connections near them in the keyspace.
2. Every router be aware that every router prefers connections near them in
   the keyspace.


Advantages for Tunnel Building
------------------------------

If you build a tunnel::

    A -long-> B -short-> C -short-> D

(long/random vs short hop in keyspace), you can guess where the tunnel build
probably failed and try a different peer at that point. In addition, it would
allow you to detect denser parts in key space and have routers just not use them
since it may be someone colluding.

If you build a tunnel::

    A -long-> B -long-> C -short-> D

and it fails, you can infer that it was more likely failing at C -> D and you
can choose another D hop.

You can also build tunnels so that the OBEP is closer to the IBGW and use those
tunnels with OBEP that are closer to the given IBGW in a LeaseSet.


Security Implications
=====================

If you randomize the placement of short vs long hops in the keyspace, an
attacker probably won't get much of an advantage.

The biggest downside though is it may make user enumeration a bit easier.
