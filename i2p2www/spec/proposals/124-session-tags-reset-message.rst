=========================================
Reset Message for ElGamal/AES+SessionTags
=========================================
.. meta::
    :author: orignal
    :created: 2016-01-24
    :thread: http://zzz.i2p/topics/2056
    :lastupdated: 2016-01-26
    :status: Draft

.. contents::


Introduction
============

Imagine some destination has bunch of confirmed tags to another destination. But
that destination got restarted or lost these tags some other way. First
destination keeps sending message with tags and second destination can't
decrypt. Second destination should have a way to tell first destination to reset
(start from scratch) through an additional garlic clove same way as it sends
updated LeaseSet.


Proposed Message
================

This new clove must contain delivery type "destination" with a new I2NP message
called like "Tags reset" and containing sender's ident hash. It should include
timestamp and signature.

Can be sent at any time if a destination can't decrypt messages.


Usage
=====

If I restart my router and try to connect another destination, I send a clove
with my new LeaseSet, and I would send additional clove with this message
containing my address. A remote destination receives this message, delete all
outgoing tags to me and start from ElGamal. 

There is pretty common case that a destination is in communication with one
remote destination only. In case of restart it should send this message to
everybody together with first streaming or datagram message.
