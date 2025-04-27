================================
UDP Trackers
================================
.. meta::
    :author: zzz
    :created: 2022-01-03
    :thread: http://zzz.i2p/topics/1634
    :lastupdated: 2025-04-27
    :status: Open
    :target: 0.9.68

.. contents::


Overview
========

This proposal is for implemention of UDP trackers in I2P.


Change History
--------------

A preliminary proposal for UDP trackers in I2P was posted on our bittorrent spec page [SPEC]_
in May 2014; this predated our formal proposal process, and it was never implemented.
This proposal was created in early 2022 and simplifies the 2014 version.

As this proposal relies on repliable datagrams, it was put on hold once we
started working on the Datagram2 proposal [Prop163]_ in early 2023.
That proposal was approved in April 2025.

The 2023 version of this proposal specified two modes, "compatibility" and "fast".
Further analysis revealed that the fast mode would be insecure, and would also
be inefficient for clients with a large number of torrents.
Further, BiglyBT indicated a preference for compatibility mode.
This mode will be easier to implement for any tracker or client supporting
standard [BEP15]_.

While the compatibility mode is more complex to implement from-scratch
on the client size, we do have preliminary code for it started in 2023.

Therefore, the current version here is further simplified to remove fast mode,
and remove the term "compatibility". The current version switches to
the new Datagram2 format, and adds references to the UDP announce extenstion
protocol [BEP41]_.

Also, a connection ID lifetime field is added to the connect response,
to extend the efficiency gains of this protocol.


Motivation
==========

As the user base in general and the number of bittorrent users specifically continues to grow,
we need to make trackers and announces more efficient so that trackers are not overwhelemed.

Bittorrent proposed UDP trackers in BEP 15 [BEP15]_ in 2008, and the vast majority
of trackers on clearnet are now UDP-only.

It is difficult to calculate the bandwidth savings of datagrams vs. streaming protocol.
A repliable request is about the same size as a streaming SYN, but the payload
is about 500 bytes smaller because the HTTP GET has a huge 600 byte
URL parameter string.
The raw reply is much smaller than a streaming SYN ACK, providing significant reduction
for a tracker's outbound traffic.

Additionally, there should be implementation-specific memory reductions,
as datagrams require much less in-memory state than a streaming connection.

Post-Quantum encryption and signatures as envisioned in [Prop169]_ will substantially
increase the overhead of encrypted and signed structures, including destinations,
leasesets, streaming SYN and SYN ACK. It is important to minimize this
overhead where possible before PQ crypto is adopted in I2P.


Design
============

This proposal uses repliable datagram2, repliable datagram3, and raw datagrams,
as defined in [DATAGRAMS]_.
Datagram2 and Datagram3 are new variants of repliable datagrams,
defined in Proposal 163 [Prop163]_.
Datagram2 adds replay resistance and offline signature support.
Datagram3 is smaller than the old datagram format, but without authentication.


BEP 15
-------

For reference, the message flow defined in [BEP15]_ is as follows:

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
This connection ID expires by default in one minute at the client, and in two minutes at the tracker.

I2P will use the same message flow as BEP 15,
for ease of adoption in existing UDP-capable client code bases:
for efficiency, and for security reasons discussed below:

.. raw:: html

  {% highlight %}
Client                        Tracker
    Connect Req. ------------->       (Repliable Datagram2)
      <-------------- Connect Resp.   (Raw)
    Announce Req. ------------->      (Repliable Datagram3)
      <-------------- Announce Resp.  (Raw)
    Announce Req. ------------->      (Repliable Datagram3)
      <-------------- Announce Resp.  (Raw)
             ...
{% endhighlight %}

This potentially provides a large bandwidth savings over
streaming (TCP) announces.
While the Datagram2 is about the same size as a streaming SYN,
the raw response is much smaller than the streaming SYN ACK.
Subsequent requests use Datagram3, and the subsequent responses are raw.

The announce requests are Datagram3 so that the tracker need not
maintain a large mapping table of connection IDs to announce destination or hash.
Instead, the tracker may generate connection IDs cryptographically
from the sender hash, the current timestamp (based on some interval),
and a secret value.
When an announce request is received, the tracker validates the
connection ID, and then uses the
Datagram3 sender hash as the send target.


Tracker/Client support
----------------------

For an integrated application (router and client in one process, for example i2psnark, and the ZzzOT Java plugin),
or for an I2CP-based application (for example BiglyBT),
it should be straightforward to implement and route the streaming and datagram traffic separately.
ZzzOT and i2psnark are expected to be the first tracker and client to implement this proposal.

Non-integrated trackers and clients are discussed below.


Trackers
````````

There are four known I2P tracker implementations:

- zzzot, an integrated Java router plugin, running at opentracker.dg2.i2p and several others
- tracker2.postman.i2p, running presumably behind a Java router and HTTP Server tunnel
- The old C opentracker, ported by zzz, with UDP support commented out
- The new C opentracker, ported by r4sas, running at opentracker.r4sas.i2p and possibly others,
  running presumably behind a i2pd router and HTTP Server tunnel

For an external tracker application that currently uses an HTTP server tunnel to receive
announce requests, the implementation could be quite difficult.
A specialized tunnel could be developed to translate datagrams to local HTTP requests/responses.
Or, a specialized tunnel that handles both HTTP requests and datagrams could be designed
that would forward the datagrams to the external process.
These design decisions will depend heavily on the specific router and tracker implementations,
and are outside the scope of this proposal.


Clients
```````
External SAM-based torrent clients such as qbittorrent and other libtorrent-based clients
would require SAM v3.3 [SAMv3]_ which is not supported by i2pd.
This is also required for DHT support, and is complex enough that no known
SAM torrent client has implemented it.
No SAM-based implementations of this proposal are expected soon.


Connection Lifetime
-------------------

[BEP15]_ specifies that the connection ID expires in one minute at the client, and in two minutes at the tracker.
It is not configurable.
That limits the potential efficiency gains, unless
clients batched announces to do all of them within a one-minute window.
i2psnark does not currently batch announces; it spreads them out, to avoid bursts of traffic.
Power users are reported to be running thousands of torrents at once,
and bursting that many announces into one minute is not realistic.

Here, we propose to extend the connect response to add an optional connection lifetime field.
The default, if not present, is one minute. Otherwise, the lifetime specified
in seconds, shall be used by the client, and the tracker will maintain the
connection ID for one minute more.


Compatibility with BEP 15
-------------------------

This design maintains compatibility with [BEP15]_ as much as possible
to limit changes required in existing clients and trackers.

The only required change is the format of peer info in the announce response.
The addition of the lifetime field in the connect response is not required
but is strongly recommended for efficiency, as explained above.



Security Analysis
------------------

An important goal of a UDP announce protocol is to prevent address spoofing.
The client must actually exist and bundle a real leaseset.
It must have inbound tunnels to receive the Connect Response.
These tunnels could be zero-hop and built instantly, but that would
expose the creator.
This protocol accomplishes that goal.



Issues
------

- This proposal does not support blinded destinations,
  but may be extended to do so. See below.




Specification
=============

Protocols and Ports
-------------------

Repliable Datagram2 uses I2CP protocol 19;
repliable Datagram3 uses I2CP protocol 20;
raw datagrams use I2CP protocol 18.
Requests may be Datagram2 or Datagram3. Responses are always raw.
The older repliable datagram ("Datagram1") format using I2CP protocol 17
must NOT be used for requests or replies; these must be dropped if received
on the request/reply ports. Note that Datagram1 protocol 17
is still used for the DHT protocol.

Requests use the I2CP "to port" from the announce URL; see below.
The request "from port" is chosen by the client, but should be nonzero,
and a different port from those used by DHT, so that responses
may be easily classified.
Trackers should reject requests received on the wrong port.

Responses use the I2CP "to port" from the request.
The request "from port" is the "to port" from the request.


Announce URL
------------

The announce URL format is not specified in [BEP15]_,
but as in clearnet, UDP announce URLs are of the form "udp://host:port/path".
The path is ignored and may be empty, but is typically "/announce" on clearnet.
The :port part should always be present, however,
if the ":port" part is omitted, use a default I2CP port of 6969,
as that is the common port on clearnet.
There may also be cgi parameters &a=b&c=d appended,
those may be processed and provided in the announce request, see [BEP41]_.
If there are no parameters or path, the trailing / may also be omitted,
as implied in [BEP41]_.


Datagram Formats
----------------

All values are send in network byte order (big endian).
Do not expect packets to be exactly of a certain size.
Future extensions could increase the size of packets.



Connect Request
```````````````

Client to tracker.
16 bytes. Must be repliable Datagram2. Same as in [BEP15]_. No changes.


.. raw:: html

  {% highlight %}
Offset  Size            Name            Value
  0       64-bit integer  protocol_id     0x41727101980 // magic constant
  8       32-bit integer  action          0 // connect
  12      32-bit integer  transaction_id
{% endhighlight %}



Connect Response
````````````````

Tracker to client.
16 or 18 bytes. Must be raw. Same as in [BEP15]_ except as noted below.


.. raw:: html

  {% highlight %}
Offset  Size            Name            Value
  0       32-bit integer  action          0 // connect
  4       32-bit integer  transaction_id
  8       64-bit integer  connection_id
  16      16-bit integer  lifetime        optional  // Change from BEP 15
{% endhighlight %}

The response MUST be sent to the I2CP "to port" that was received as the request "from port".

The lifetime field is optional and indicates the connection_id client lifetime in seconds.
The default is 60, and the minimum if specified is 60.
The maximum is 65535 or about 18 hours.
The tracker should maintain the connection_id for 60 seconds more than the client lifetime.



Announce Request
````````````````

Client to tracker.
98 bytes minimum. Must be repliable Datagram3. Same as in [BEP15]_ except as noted below.

The connection_id is as received in the connect response.



.. raw:: html

  {% highlight %}
Offset  Size            Name            Value
  0       64-bit integer  connection_id
  8       32-bit integer  action          1     // announce
  12      32-bit integer  transaction_id
  16      20-byte string  info_hash
  36      20-byte string  peer_id
  56      64-bit integer  downloaded
  64      64-bit integer  left
  72      64-bit integer  uploaded
  80      32-bit integer  event           0     // 0: none; 1: completed; 2: started; 3: stopped
  84      32-bit integer  IP address      0     // default
  88      32-bit integer  key
  92      32-bit integer  num_want        -1    // default
  96      16-bit integer  port
  98      varies          options     optional  // As specified in BEP 41
{% endhighlight %}

Changes from [BEP15]_:

- key is ignored
- port is probably ignored
- The options section, if present, is as defined in [BEP41]_

The response MUST be sent to the I2CP "to port" that was received as the request "from port".
Do not use the port from the announce request.



Announce Response
`````````````````

Tracker to client.
20 bytes minimum. Must be raw. Same as in [BEP15]_ except as noted below.



.. raw:: html

  {% highlight %}
Offset  Size            Name            Value
  0           32-bit integer  action          1 // announce
  4           32-bit integer  transaction_id
  8           32-bit integer  interval
  12          32-bit integer  leechers
  16          32-bit integer  seeders
  20   32 * n 32-byte hash    binary hashes     // Change from BEP 15
  ...                                           // Change from BEP 15
{% endhighlight %}

Changes from [BEP15]_:

- Instead of 6-byte IPv4+port or 18-byte IPv6+port, we return
  a multiple of 32-byte "compact responses" with the SHA-256 binary peer hashes.
  As with TCP compact responses, we do not include a port.

The response MUST be sent to the I2CP "to port" that was received as the request "from port".
Do not use the port from the announce request.

I2P datagrams have a very large maximum size of about 64 KB;
however, for reliable delivery, datagrams larger than 4 KB should be avoided.
For bandwidth efficiency, trackers should probably limit the maximum peers
to about 50, which corresponds to about a 1600 byte packet before overhead
at various layers, and should be within a two-tunnel-message payload limit
after fragmentation.

As in BEP 15, there is no count included of the number of peer addresses
(IP/port for BEP 15, hashes here) to follow.
While not contemplated in BEP 15, an end-of-peers marker
of all zeros could be defined to indicate that the peer info is complete
and some extension data follows.

So that extension is possible in the future, clients should ignore
a 32-byte all-zeros hash, and any data that follows.
Trackers should reject announces from an all-zeros hash,
although that hash is already banned by Java routers.


Scrape
``````

Scrape request/response from [BEP15]_ is not required by this proposal,
but may be implemented if desired, no changes required.
The client must acquire a connection ID first.
The scrape request is always repliable Datagram3.
The scrape response is always raw.



Error Response
``````````````

Tracker to client.
8 bytes minimum (if the message is empty).
Must be raw. Same as in [BEP15]_. No changes.

.. raw:: html

  {% highlight %}

Offset  Size            Name            Value
  0       32-bit integer  action          3 // error
  4       32-bit integer  transaction_id
  8       string          message

{% endhighlight %}



Extensions
=============

Extension bits or a version field are not included.
Clients and trackers should not assume packets to be of a certain size.
This way, additional fields can be added without breaking compatibility.
The extensions format defined in [BEP41]_ is recommended if required.

The connect response is modified to add an optional connection ID lifetime.

If blinded destination support is required, we can either add the
blinded 35-byte address to the end of the announce request,
or request blinded hashes in the responses,
using the [BEP41]_ format (paramters TBD).
The set of blinded 35-byte peer addresses could be added to the end of the announce reply,
after an all-zeros 32-byte hash.



Implementation guidelines
==========================

See the design section above for a discussion of the challenges for
non-integrated, non-I2CP clients and trackers.


Clients
--------

For a given tracker hostname, a client should prefer UDP over HTTP URLs,
and should not announce to both.

Clients with existing BEP 15 support should require only small modifications.

If a client support DHT or other datagram protocols, it should probably
select a different port as the request "from port" so that the replies
come back to that port and are not mixed up with DHT messages.
The client only receives raw datagrams as replies.
Trackers will never send a repliable datagram2 to the client.

Clients with a default list of opentrackers should update the list to
add UDP URLs after the known opentrackers are known to support UDP.

Clients may or may not implement retransmission of requests.
Retransmissions, if implemented, should use an initial timeout
of at least 15 seconds, and double the timeout for each retransmission
(exponential backoff).

Clients must back off after receiving an error response.


Trackers
---------

Trackers with existing BEP 15 support should require only small modifications.
This proposal differs from the 2014 proposal, in that the tracker
must support reception of repliable datagram2 and datagram3 on the same port.



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

.. [BEP41]
    http://www.bittorrent.org/beps/bep_0041.html

.. [DATAGRAMS]
    {{ spec_url('datagrams') }}

.. [Prop163]
    {{ proposal_url('163') }}

.. [Prop169]
    {{ proposal_url('169') }}

.. [SAMv3]
    {{ site_url('docs/api/samv3') }}

.. [SPEC]
    {{ site_url('docs/applications/bittorrent', True) }}
