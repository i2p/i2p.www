============================
Opt-in Statistics Collection
============================
.. meta::
    :author: zab
    :created: 2015-11-04
    :thread: http://zzz.i2p/topics/1981
    :lastupdated: 2015-11-04
    :status: Draft

.. contents::


Overview
========

This proposal is about an opt-in automated reporting system for network
statistics.


Motivation
==========

Currently there are several network parameters which have been determined by
educated guessing. It is suspected that some of those can be tweaked to improve
the overall performance of the network in terms of speed, reliability and so on.
However, changing them without proper research is very risky.


Design
======

The router supports vast collection of stats which can be used to analyze
network-wide properties. What we need is an automated reporting system which
collects those stats in a centralized place. Naturally, this would be opt-in as
it pretty much destroys anonymity. (The privacy-friendly stats are already
reported to stats.i2p) As a ballpark figure, for a network of size 30,000 a
sample of 300 reporting routers should be representative enough.
