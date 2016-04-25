=================
Restricted Routes
=================
.. meta::
    :author: zzz
    :created: 2008-09-14
    :thread: http://zzz.i2p/topics/114
    :lastupdated: 2008-10-13
    :status: Reserve

.. contents::


Introduction
============


Thoughts
========

- Add a new transport "IND" (indirect) which publishes a leaseSet hash in the
  RouterAddress structure: "IND: [key=aababababababababb]". This transport bids
  the lowest priority when the target router publishes it. To send to a peer via
  this transport, fetch the leaseset from a ff peer as usual, and send it
  directly to the lease.

- A peer advertising IND must build and maintain a set of tunnels to another
  peer. These are not exploratory tunnels and not client tunnels, but a second
  set of router tunnels.

  - 1-hop is sufficient?
  - How to select peers for these tunnels?
  - They need to be "non-restricted" but how do you know that? Reachability
    mapping? Graph theory, algorithms, data structures may help here. Need to
    read up on this. See tunnels TODO.

- If you have IND tunnels then your IND transport must bid (low-priority) to
  send messages out these tunnels.

- How to decide to enable building indirect tunnels

- How to implement and test without blowing cover
