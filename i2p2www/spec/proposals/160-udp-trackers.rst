================================
UDP Trackers
================================
.. meta::
    :author: zzz
    :created: 2022-01-03
    :thread: http://zzz.i2p/topics/1634
    :lastupdated: 2022-01-17
    :status: Open
    :target: 0.9.54

.. contents::


Overview
========

This proposal is for implemention of UDP trackers in I2P.


Motivation
==========

As the user base in general and the number of bittorrent users specifically continues to grow,
we need to make trackers and announces more efficient so that trackers are not overwhelemed.

Bittorrent proposed UDP trackers in BEP 15 [BEP15]_ in 2008, and the vast majority
of trackers on clearnet are now UDP-only.

A preliminary proposal for UDP trackers in I2P was posted on our bittorrent spec page [SPEC]_
in May 2014; this predated our formal proposal process, and it was never implemented.
This proposal simplifies the 2014 version.

It is difficult to calculate the bandwidth savings of datagrams vs. streaming protocol.
A repliable request is about the same size as a streaming SYN, but the payload
is about 500 bytes smaller because the HTTP GET has a huge 600 byte
URL parameter string.
The raw reply is much smaller than a streaming SYN ACK, providing significant reduction
for a tracker's outbound traffic.

Additionally, there should be implementation-specific memory reductions,
as datagrams require much less in-memory state than a streaming connection.



Design
============

This proposal uses both repliable and raw datagrams,
as defined in [DATAGRAMS]_.


BEP 15
-------

The message flow in [BEP15]_ is as follows:

.. raw:: html

  {% highlight %}
Client                        Tracker
    Connect Req. ------------->
      <-------------- Connect Resp.
    Announce Req. ------------->
      <-------------- Announce Resp.
    Announce Req. ------------->
      <-------------- Announce Resp.
{% endhighlight %}

The connect phase is required to prevent IP address spoofing.
The tracker returns a connection ID that the client uses in subsequent announces.
This connection ID expires in one minute at the client, and in two minutes at the tracker.
This is not necessary in I2P because of repliable datagrams.

We propose two mechanisms for I2P, compatibility mode and fast mode.


Compatibility Mode
-------------------------

In compatibility mode, we keep the same message flow as BEP 15,
for ease of adoption in existing UDP-capable client code bases:

.. raw:: html

  {% highlight %}
Client                        Tracker
    Connect Req. ------------->       (Repliable)
      <-------------- Connect Resp.   (Raw)
    Announce Req. ------------->      (Raw)
      <-------------- Announce Resp.  (Raw)
    Announce Req. ------------->      (Raw)
      <-------------- Announce Resp.  (Raw)
             ...
{% endhighlight %}

This mode is also useful if the client plans to send multiple announces
within one minute to a single tracker, as only the connect
message must be repliable.


I2P Fast Mode
-------------------------

In fast mode, we omit the connect phase, as it is not required to prevent address spoofing.
This significantly simplifies the client-side implementation.

.. raw:: html

  {% highlight %}
Client                        Tracker
    Announce Req. ------------->      (Repliable)
      <-------------- Announce Resp.  (Raw)
{% endhighlight %}

This mode omits a round-trip, but requires every announce request to be repliable.



Specification
=============

Repliable datagrams use I2CP protocol 17; raw datagrams use I2CP protocol 18.
Requests may be repliable or raw. Responses are always raw.


Connect Request
-----------------

Client to tracker.
16 bytes. Must be repliable. Same as in [BEP15]_.


.. raw:: html

  {% highlight %}
Offset  Size            Name            Value
  0       64-bit integer  protocol_id     0x41727101980 // magic constant
  8       32-bit integer  action          0 // connect
  12      32-bit integer  transaction_id
{% endhighlight %}



Connect Response
-----------------

Tracker to client.
16 bytes. Must be raw. Same as in [BEP15]_.


.. raw:: html

  {% highlight %}
Offset  Size            Name            Value
  0       32-bit integer  action          0 // connect
  4       32-bit integer  transaction_id
  8       64-bit integer  connection_id
{% endhighlight %}

The response MUST be sent to the I2CP "to port" that was received as the request "from port".




Announce Request
-----------------

Client to tracker.
98 bytes. Same as in [BEP15]_ except as noted below.

If preceded by a connect request/response, must be raw,
with the connection_id received in the connect response.


If NOT preceded by a connect request/response, must be repliable,
and the connection_id is ignored.


.. raw:: html

  {% highlight %}
Offset  Size            Name            Value
  0       64-bit integer  connection_id
  8       32-bit integer  action          1 // announce
  12      32-bit integer  transaction_id
  16      20-byte string  info_hash
  36      20-byte string  peer_id
  56      64-bit integer  downloaded
  64      64-bit integer  left
  72      64-bit integer  uploaded
  80      32-bit integer  event           0 // 0: none; 1: completed; 2: started; 3: stopped
  84      32-bit integer  IP address      0 // default
  88      32-bit integer  key
  92      32-bit integer  num_want        -1 // default
  96      16-bit integer  port
  98      TBD             additional data TBD
{% endhighlight %}

Changes from [BEP15]_:

- connection_id is ignored if repliable
- IP address is ignored
- key is ignored
- port is probably ignored
- Explicitly indidate that the protocol is extensible,
  with possible additional data starting at port 98.

The response MUST be sent to the I2CP "to port" that was received as the request "from port".
Do not use the port from the announce request.





Announce Response
-----------------

Tracker to client.
20+ bytes. Must be raw. Same as in [BEP15]_ except as noted below.



.. raw:: html

  {% highlight %}
Offset  Size            Name            Value
  0           32-bit integer  action          1 // announce
  4           32-bit integer  transaction_id
  8           32-bit integer  interval
  12          32-bit integer  leechers
  16          32-bit integer  seeders
  20          16-bit integer  count of hashes to follow
  22 + 32 * n 32-byte hash    binary hashes
  ...
  22 + 32 * c TBD             additional data TBD

{% endhighlight %}

Changes from [BEP15]_:

- Add a hash count before the hashes, so that the response format
  is extensible with additional data after the hashes.
- Instead of 6-byte IPv4+port or 18-byte IPv6+port, we return
  a multiple of 32-byte "compact responses" with the SHA-256 binary peer hashes.
  As with TCP compact responses, we do not include a port.
- Explicitly indidate that the protocol is extensible,
  with possible additional data starting after the hashes

The response MUST be sent to the I2CP "to port" that was received as the request "from port".
Do not use the port from the announce request.

I2P datagrams have a very large maximum size of about 16 KB;
however, for reliable delivery, datagrams larger than 4 KB should be avoided.
For bandwidth efficiency, trackers should probably limit the maximum peers
to about 50.


Scrape
----------

Scrape request/response from [BEP15]_ is not required by this proposal,
but may be implemented if desired, no changes required.
The scrape request is always repliable (unless there is a previous connect request/response)
and the scrape response is always raw.


Error Response
------------------

Error response from [BEP15]_ is not required by this proposal,
but may be implemented if desired, no changes required.
The error response is always raw.


Announce URL
------------

As in clearnet, UDP announce URLs are of the form "udp://host:port/path".
The path is ignored and may be empty.
If the ":port" part is omitted, use an I2CP port of 0.



Issues
=======

- Repliable datagrams do not support offline signatures.
  That requires a separate proposal.
- This proposal does not support blinded destinations,
  but may be extended to do so. See below.
- This proposal offers two modes at the client's option.
  An existing clearnet tracker such as "opentracker" would require more modifications
  to support the fast mode. There is no way in the announce URL to indicate
  support for only one mode.
- Compatibility mode may not be necessary, pending feedback from BiglyBT and
  other developers. However, it would still save a lot of bandwidth
  if it is used for several announces within a minute.
  Repliable announces are about 450 bytes larger than raw announces.


Extensions
=============

Extension bits or a version field are not included.
Clients and trackers should not assume packets to be of a certain size.
This way, additional fields can be added without breaking compatibility.

The announce response is modified to include a count of peer hashes,
so that the response may be easily extended with additional information.

If blinded destination support is required, we can either add the
blinded 35-byte address to the end of the announce request, or define a new blinded announce request message.
The set of blinded 35-byte peer addresses could be added to the end of the announce reply.



Implementation guidelines
==========================

Clients
--------

For a given tracker hostname, a client should prefer UDP over HTTP URLs,
and should not announce to both.

Clients wihout existing BEP 15 support should implement
fast mode only, as it is much simpler.
Clients with existing BEP 15 support should require only small modifications.
Evaluate both fast and compatibility modes and choose
whatever is best for the existing code base.

If a client support DHT or other datagram protocols, it should probably
select a different port as the request "from port" so that the replies
come back to that port and are not mixed up with DHT messages.
The client only receives raw datagrams as replies.
Trackers will never send a repliable datagram to the client.

Clients with a default list of opentrackers should update the list to
add UDP URLs after the known opentrackers are known to support UDP.

Clients may or may not implement retransmission of requests.
Retransmissions, if implemented, should use an initial timeout
of at least 15 seconds, and double the timeout for each retransmission
(exponential backoff).


Trackers
---------

Trackers must implement both compatibility mode and fast mode.
Trackers with existing BEP 15 support should require only small modifications.
This proposal differs from the 2014 proposal, in that the tracker
must support reception of repliable and raw datagrams on the same port.

For an integrated application (router and client in one process, for example the ZzzOT Java plugin),
it should be straightforward to implement and route the streaming and datagram traffic separately.

For an external tracker application that currently uses an HTTP server tunnel to receive
announce requests, the implementation could be quite difficult.
A specialized tunnel could be developed to translate datagrams to local HTTP requests/responses.
Or, a specialized tunnel that handles both HTTP requests and datagrams could be designed
that would forward the datagrams to the external process.
These design decisions will depend heavily on the specific router and tracker implementations,
and are outside the scope of this proposal.




Migration
=========

Existing clients do not support UDP announce URLs and ignore them.

Existing trackers do not support reception of repliable or raw datagrams, they will be dropped.

This proposal is completely optional. Neither clients nor trackers are required to implement it at any time.



Rollout
=======

The first implementations are expected to be in ZzzOT and i2psnark.
They will be used for testing and verification of this proposal.

Other implementations will follow as desired after the testing and verification are complete.




References
==========

.. [BEP15]
    http://www.bittorrent.org/beps/bep_0015.html

.. [DATAGRAMS]
    {{ spec_url('datagrams') }}

.. [SPEC]
    {{ site_url('docs/applications/bittorrent', True) }}
