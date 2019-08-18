==========================
Transport Network ID Check
==========================
.. meta::
    :author: zzz
    :created: 2019-02-28
    :thread: http://zzz.i2p/topics/2687
    :lastupdated: 2019-08-13
    :status: Closed
    :target: 0.9.42
    :implementedin: 0.9.42

.. contents::


Overview
========

NTCP2 (proposal 111) does not reject connections from different network IDs
at the Session Request phase.
The connection must currently be rejected at the Session Confirmed phase,
when Bob checks Alice's RI.

Similarly, SSU does not reject connections from different network IDs
at the Session Request phase.
The connection must currently be rejected after the Session Confirmed phase,
when Bob checks Alice's RI.

This proposal changes the Session Request phase of both transports to incorporate the
network ID, in a backwards-compatible way.


Motivation
==========

Connections from the wrong network should be rejected, and the
peer should be blacklisted, as soon as possible.


Goals
=====

- Prevent cross-contamination of testnets and forked networks

- Add network ID to NTCP2 and SSU handshake

- For NTCP2,
  the receiver (incoming connection) should be able to identify that the network ID is different,
  so it can blacklist the peer's IP.

- For SSU,
  the receiver (incoming connection) cannot blacklist at the session request phase, because
  the incoming IP could be spoofed. It is sufficient to change the cryptography of the handshake.

- Prevent reseeding from the wrong network

- Must be backward-compatible


Non-Goals
=========

- NTCP 1 is no longer in use, so it will not be changed.


Design
======

For NTCP2,
XORing in a value would just cause the encryption to fail, and the
receiver would not have enough information to blacklist the originator,
so that approach is not preferred.

For SSU,
we will XOR in the network ID somewhere in the Session Request.
Since this must be backwards-compatible, we will XOR in (id - 2)
so it will be a no-op for the current network ID value of 2.



Specification
=============

Documentation
-------------

Add the following specification for valid network id values:


==================================  ==============
       Usage                         NetID Number
==================================  ==============
Reserved                                   0
Reserved                                   1
Current Network (default)                  2
Reserved Future Networks               3 - 15
Forks and Test Networks               16 - 254
Reserved                                 255
==================================  ==============


The Java I2P configuration to change the default is "router.networkID=nnn".
Document this better and encourage forks and test networks to add this setting to their configuration.
Encourage other implementations to implement and document this option.


NTCP2
-----

Use the first reserved byte of the options (byte 0) in the Session Request message to contain the network ID, currently 2.
It contains the network ID.
If nonzero, the receiver shall check it against the least significant byte of the local network ID.
If they do not match, receiver shall immediately disconnect and blacklist the originator's IP.


SSU
---

For SSU, add an XOR of ((netid - 2) << 8) in the HMAC-MD5 calculation.

Existing:

.. raw:: html

  {% highlight lang='dataspec' %}
HMAC-MD5(encryptedPayload + IV + (payloadLength ^ protocolVersion), macKey)

  '+' means append and '^' means exclusive-or.
  payloadLength is a 2 byte unsigned integer
  protocolVersion is one byte 0x00

{% endhighlight %}

New:

.. raw:: html

  {% highlight lang='dataspec' %}
HMAC-MD5(encryptedPayload + IV + (payloadLength ^ protocolVersion ^ ((netid - 2) << 8)), macKey)

  '+' means append, '^' means exclusive-or, '<<' means left shift.
  payloadLength is a two byte unsigned integer, big endian
  protocolVersion is two bytes 0x0000, big endian
  netid is a two byte unsigned integer, big endian, legal values are 2-254


{% endhighlight %}


Reseeding
---------

Add a parameter ?netid=nnn to the fetch of the reseed su3 file.
Update reseed software to check for the netid. If it is present and not equal to "2",
the fetch should be rejected with an error code, perhaps 403.
Add configuration option to reseed software so that an alternate netid may be configured
for test or forked networks.


Notes
=====

We cannot force test networks and forks to change the network ID.
The best we can do is documentation and communication.
If we do discover cross-contamination with other networks, we should attempt to
contact the developers or operators to explain the importance of changing the network ID.


Issues
======



Migration
=========

This is backwards-compatible for the current network ID value of 2.
If any people are running networks (test or otherwise) with a different network ID value,
this change is backwards-incompatible.
However, we are not aware of anybody doing this.
If it's a test network only, it's not an issue, just update all of the routers at once.
