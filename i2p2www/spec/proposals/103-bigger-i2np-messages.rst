====================
Bigger I2NP Messages
====================
.. meta::
    :author: zzz
    :created: 2009-04-05
    :thread: http://zzz.i2p/topics/258
    :lastupdated: 2009-05-27
    :status: Dead

.. contents::


Overview
========

This proposal is about increasing the size limit on I2NP messages.


Motivation
==========

iMule's use of 12KB datagrams exposed lots of problems. The actual limit today
is more like 10KB.


Design
======

To do:

- Increase NTCP limit - not so easy?

- More session tag quantity tweaks. May hurt max window size? Are there stats to
  look at? Make the number variable based on how many we think they need? Can
  they ask for more? ask for a quantity?

- Investigate increasing SSU max size (by increasing MTU?)

- Lots of testing

- Finally check in the fragmenter improvements? - Need to do comparison testing
  first!
