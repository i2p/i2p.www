===================================
Streaming Updates
===================================
.. meta::
    :author: zzz
    :created: 2023-01-24
    :thread: http://zzz.i2p/topics/3541
    :lastupdated: 2023-10-23
    :status: Closed
    :target: 0.9.58
    :implementedin: 0.9.58

.. contents::



Overview
========

Java I2P and i2pd routers older than API 0.9.58 (released March 2023)
are vulnerable to a streaming SYN packet replay attack.
This is a protocol design issue, not an implementation bug.

SYN packets are signed, but the signature of the initial SYN packet sent from Alice to Bob
is not bound to Bob's identity, so Bob may store and replay that packet,
sending it to some victim Charlie. Charlie will think that the packet came from
Alice and respond to her. In most cases, this is harmless, but
the SYN packet may contain initial data (such as a GET or POST) that
Charlie will process immediately.




Design
======

The fix is for Alice to include Bob's destination hash in the signed SYN data.
Bob verifies on reception that that hash matches his hash.

Any potential attack victim Charlie
checks this data and rejects the SYN if it does not match his hash.

By using the NACKs option field in the SYN to store the hash,
the change is backward-compatible, because NACKs are not expected to be included
in the SYN packet and are currently ignored.

All options are covered by the signature, as usual, so Bob may not
rewrite the hash.

If Alice and Charlie are API 0.9.58 or newer, any replay attempt by Bob will be rejected.



Specification
=============

Update [STREAMING]_ to add the following section:

Replay prevention
-----------------

To prevent Bob from using a replay attack by storing a valid signed SYNCHRONIZE packet
received from Alice and later sending it to a victim Charlie,
Alice must include Bob's destination hash in the SYNCHRONIZE packet as follows:

.. raw:: html

  {% highlight lang='dataspec' %}
Set NACK count field to 8
  Set the NACKs field to Bob's 32-byte destination hash

{% endhighlight %}

Upon reception of a SYNCHRONIZE, if the NACK count field is 8,
Bob must interpret the NACKs field as a 32-byte destination hash,
and must verify that it matches his destination hash.
He must also verify the signature of the packet as usual,
as that covers the entire packet including the NACK count and NACKs fields.
If the NACK count is 8 and the NACKs field does not match,
Bob must drop the packet.

This is required for versions 0.9.58 and higher.
This is backward-compatible with older versions,
because NACKs are not expected in a SYNCHRONIZE packet.
Destinations do not and cannot know what version the other end is running.

No change is necessary for the SYNCHRONIZE ACK packet sent from Bob to Alice;
do not include NACKs in that packet.


Security Analysis
=================

This issue has been present in the streaming protocol since it was created in 2004.
It was discovered internally by I2P developers.
We have no evidence that the issue was ever been exploited.
Actual chance of exploitation success may vary widely depending
on the application-layer protocol and service.
Peer-to-peer applications are probably more likely to be affected
than client/server applications.


Compatibility
===============

No issues. All known implementations currently ignore the NACKs field in the SYN packet.
And even if they did not ignore it, and attempted to interpret it
as NACKs for 8 different messages, those messages would not be outstanding
during the SYNCHRONIZE handshake and the NACKs would not make any sense.



Migration
=========

Implementations may add support at any time, no coordination is needed.
Java I2P and i2pd routers implemented this in API 0.9.58 (released March 2023).



References
==========

.. [STREAMING]
    {{ spec_url('streaming') }}
