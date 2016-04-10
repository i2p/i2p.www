==========================
'Encrypted' Streaming Flag
==========================
.. meta::
    :author: orignal
    :created: 2015-01-21
    :thread: http://zzz.i2p/topics/1795
    :lastupdated: 2015-01-21
    :status: Draft

.. contents::


Introduction
============

High-loaded apps can encounter a shortage of ElGamal/AES+SessionTags tags.


Proposal
========

Add a new flag somewhere within the streaming protocol. If a packets comes with
this flag it means payload is AES encrypted by key from private key and peer's
public key. That would allow to eliminated garlic (ElGamal/AES) encryption and
shortage of tags problem.

May be set per packet or per stream through SYN.
