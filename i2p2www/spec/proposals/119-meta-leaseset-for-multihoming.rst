=============================
Meta-LeaseSet for Multihoming
=============================
.. meta::
    :author: zzz
    :created: 2016-01-09
    :thread: http://zzz.i2p/topics/2045
    :lastupdated: 2016-01-11
    :status: Draft

.. contents::


Introduction
============

Multihoming is a hack and presumably won't work for e.g. facebook.i2p at scale.
Say we had 100 multihomes each with 16 tunnels, that's 1600 LS publishes every
10 minutes, or almost 3 per second. The floodfills would get overwhelmed and
throttles would kick in. And that's before we even mention the lookup traffic.

We need some sort of meta-LS, where the LS lists the 100 real LS hashes. This
would be long-lived, a lot longer than 10 minutes. So it's a two-stage lookup
for the LS, but the first stage could be cached for hours.


Format
======

::

  - Destination
  - Published Time stamp
  - Expiration
  - Flags
  - Properties
  - Number of entries
  - Number of revocations

  - Entries. Each entry contains:
    - Hash
    - Flags
    - Expiration
    - Cost (priority)
    - Properties

  - Revocations. Each revocation contains:
    - Hash
    - Flags
    - Expiration

  - Signature

Flags and properties are included for maximum flexibility.


Comments
========

This could then be generalized to be a service lookup of any type. The service
identifier is a SHA256 hash.

For even more massive scalability, we could have multiple levels, i.e. a meta-LS
could point to other meta-LSes.
