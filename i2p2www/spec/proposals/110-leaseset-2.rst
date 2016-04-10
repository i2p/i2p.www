==========
LeaseSet 2
==========
.. meta::
    :author: zzz
    :created: 2014-01-22
    :thread: http://zzz.i2p/topics/1560
    :lastupdated: 2016-04-04
    :status: Draft

.. contents::


Introduction
============

The end-to-end cryptography used through I2P tunnels has separate encryption and
signing keys. The signing keys are in the tunnel Destination, which has already
been extended with KeyCertificates to support newer signature types. However,
the encryption keys are part of the LeaseSet, which doesn't contain any
Certificates. It is therefore necessary to implement a new LeaseSet format, and
add support for storing it in the netDb.

A silver lining is that once LS2 is implemented, all existing Destinations can
make use of more modern encryption types; routers that can fetch and read a LS2
will be guaranteed to have support for any encryption types introduced alongside
it.


Format
======

The basic LS2 format would be like this:

- dest
- published timestamp (8 bytes)
- expires (8 bytes)
- subtype (1 byte) (regular, encrypted, meta, or service)
- flags (2 bytes)

- subtype-specific part:
  - encryption type, encryption key, and leases for regular
  - blob for encrypted
  - properties, hashes, ports, revocations, etc. for service

- signature
