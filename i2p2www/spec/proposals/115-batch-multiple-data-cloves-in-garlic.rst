====================================
Batch Multiple Data Cloves in Garlic
====================================
.. meta::
    :author: orignal
    :created: 2015-01-22
    :thread: http://zzz.i2p/topics/1797
    :lastupdated: 2015-01-22
    :status: Needs-Research

.. contents::


Overview
========

This proposal is about sending multiple Data Garlic Cloves inside an end-to-end
Garlic Message, instead of just one.


Motivation
==========

Not clear.


Required Changes
================

The changes would be in OCMOSJ and related helper classes, and in
ClientMessagePool. As there is no queue now, a new queue and some delay would be
necessary. Any batching would have to honor a max garlic size to minimize
dropping. Perhaps 3KB? Would want to instrument things first to measure how
often this would get used.


Thoughts
========

It is unclear whether this will have any useful effect, as streaming already
does batching and selects optimum MTU. Batching would increase message size and
exponential drop probability.

The exception is uncompressed content, gzipped at the I2CP layer. But HTTP
traffic is already compressed at higher layer, and Bittorrent data is usually
uncompressible. What does this leave? I2pd doesn't currently do the x-i2p-gzip
compression so it may help there a lot more. But stated goal of not running out
of tags is better fixed with proper windowing implementation in his streaming
library.


Compatibility
=============

This is backward-compatible, as the garlic receiver will already process all
cloves it receives.
