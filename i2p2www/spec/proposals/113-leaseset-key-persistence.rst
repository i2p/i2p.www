========================
LeaseSet Key Persistence
========================
.. meta::
    :author: zzz
    :created: 2014-12-13
    :thread: http://zzz.i2p/topics/1770
    :lastupdated: 2016-12-02
    :status: Closed

.. contents::


Overview
========

This proposal is about persisting additional data in the LeaseSet that is
currently ephemeral.
Implemented in 0.9.18.


Motivation
==========

In 0.9.17 persistence was added for the netDb slicing key, stored in
i2ptunnel.config. This helps prevent some attacks by keeping the same slice
after restart, and it also prevents possible correlation with a router restart.

There's two other things that are even easier to correlate with router restart:
the leaseset encryption and signing keys. These are not currently persisted.


Proposed Changes
================

Private keys are stored in i2ptunnel.config, as i2cp.leaseSetPrivateKey and i2cp.leaseSetSigningPrivateKey.
