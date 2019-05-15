====================
Garlic Farm Protocol
====================
.. meta::
    :author: zzz
    :created: 2019-05-02
    :thread: http://zzz.i2p/topics/2234
    :lastupdated: 2019-05-15
    :status: Open

.. contents::


Overview
========

This is the spec for the Garlic Farm wire protocol,
based on JRaft, its "exts" code for implementation over TCP,
and its "dmprinter" sample application [JRAFT]_.
JRaft is an implementation of the Raft protocol [RAFT]_.

We were unable to find any implementation with a documented wire protocol.
However, the JRaft implementation is simple enough that we could
inspect the code and then document its protocol.
This proposal is the result of that effort.

This will be the backend for coordination of routers publishing
entries in a Meta LeaseSet. See proposal 123.


Goals
=====

- Small code size
- Based on existing implementation
- No serialized Java objects or any Java-specific features or encoding
- Any bootstrapping is out-of-scope. At least one other server is assumed
  to be hardcoded, or configured out-of-band of this protocol.
- Support both out-of-band and in-I2P use cases.


Design
======

The Raft protocol is not a concrete protocol; it defines only a state machine.
Therefore we document the concrete protocol of JRaft and base our protocol on it.
There are no changes to the JRaft protocol other than the addition of
an authentication handshake.

Raft elects a Leader whose job is to publish a log.
The log contains Raft Configuration data and Application data.
Application data contains the status of each Server's Router and the Destination
for the Meta LS2 cluster.
The servers use a common algorithm to determine the publisher and contents
of the Meta LS2.
The publisher of the Meta LS2 is NOT necessarily the Raft Leader.



Specification
=============

The wire protocol is over SSL sockets or non-SSL I2P sockets.
I2P sockets are proxied through the HTTP Proxy.
There is no support for clearnet non-SSL sockets.

Handshake and authentication
----------------------------

Not defined by JRaft.

Goals:

- User/password authentication method
- Version identifier
- Cluster identifier
- Extensible
- Ease of proxying when used for I2P sockets
- Do not unnecessarily expose server as a Garlic Farm server
- Simple protocol so a full web server implementation is not required

We will use an websocket-like handshake [WEBSOCKET]_ and
HTTP Digest authentication [RFC-2617]_.
RFC 2617 Basic authentication is NOT supported.
When proxying through the HTTP proxy, communicate with
the proxy as specified in [RFC-2616]_.

Credentials
~~~~~~~~~~~

Whether usernames and passwords are per-cluster, or
per-server, is implementation-dependent.


HTTP Request 1
~~~~~~~~~~~~~~

The originator will send the following.
All lines are teriminated with \r\n as required by HTTP.

.. raw:: html

  {% highlight %}
GET /GarlicFarm/CLUSTER/VERSION/websocket HTTP/1.1
   Host: (ip):(port)
   Cache-Control: no-cache
   Connection: close
   (any other headers ignored)
   (blank line)

   CLUSTER is the name of the cluster (default "farm")
   VERSION is the Garlic Farm version (currently "1")

{% endhighlight %}


HTTP Response 1
~~~~~~~~~~~~~~~

If the path is not correct, the recipient will send a standard "HTTP/1.1 404 Not Found" response,
as in [RFC-2616]_.
If the path is correct, the recipient will send a standard "HTTP/1.1 401 Unauthorized" response,
including the WWW-Authenticate HTTP digest authentication header,
as in [RFC-2617]_.
Both parties will then close the socket.


HTTP Request 2
~~~~~~~~~~~~~~

The originator will send the following,
as in [RFC-2617]_ and [WEBSOCKET]_.
All lines are teriminated with \r\n as required by HTTP.

.. raw:: html

  {% highlight %}
GET /GarlicFarm/CLUSTER/VERSION/websocket HTTP/1.1
   Host: (ip):(port)
   Cache-Control: no-cache
   Connection: keep-alive, Upgrade
   Upgrade: websocket
   (Sec-Websocket-* headers if proxied)
   Authorization: (HTTP digest authorization header as in RFC 2617)
   (any other headers ignored)
   (blank line)

   CLUSTER is the name of the cluster (default "farm")
   VERSION is the Garlic Farm version (currently "1")

{% endhighlight %}


HTTP Response 2
~~~~~~~~~~~~~~~

If the authentication is not correct, the recipient will send another standard "HTTP/1.1 401 Unauthorized" response,
as in [RFC-2617]_.
If the authentication is correct, the recipient will send the following response,
as in [WEBSOCKET]_.
All lines are teriminated with \r\n as required by HTTP.

.. raw:: html

  {% highlight %}
HTTP/1.1 101 Switching Protocols
   Connection: Upgrade
   Upgrade: websocket
   (Sec-Websocket-* headers)
   (any other headers ignored)
   (blank line)

{% endhighlight %}

After this is received, the socket remains open.
The Raft protocol as defined below commences, on the same socket.


Caching
~~~~~~~

Credentials shall be cached for at least one hour, so that
subsequent connections may jump directly to
"HTTP Request 2" above.



Message Types
-------------

There are two types of messages, requests and responses.
Requests may contain Log Entries, and are variable-sized;
responses do not contain Log Entries, and are fixed-size.

Message types 1-4 are the standard RPC messages defined by Raft.
This is the core Raft protocol.

Message types 5-15 are the extended RPC messages defined by
JRaft, to support clients, dynamic server changes, and
efficient log synchronization.

Message types 16-17 are the Log Compaction RPC messages defined
in Raft section 7.


========================  ======  ===========  =================   =====================================
Message                   Number  Sent By      Sent To             Notes
========================  ======  ===========  =================   =====================================
RequestVoteRequest           1    Candidate    Follower            Standard Raft RPC; must not contain log entries
RequestVoteResponse          2    Follower     Candidate           Standard Raft RPC
AppendEntriesRequest         3    Leader       Follower            Standard Raft RPC
AppendEntriesResponse        4    Follower     Leader / Client     Standard Raft RPC
ClientRequest                5    Client       Leader / Follower   Response is AppendEntriesResponse; must contain Application log entries only
AddServerRequest             6    Client       Leader              Must contain a single ClusterServer log entry only
AddServerResponse            7    Leader       Client              Leader will also send a JoinClusterRequest
RemoveServerRequest          8    Follower     Leader              Must contain a single ClusterServer log entry only
RemoveServerResponse         9    Leader       Follower
SyncLogRequest              10    Leader       Follower            Must contain a single LogPack log entry only
SyncLogResponse             11    Follower     Leader
JoinClusterRequest          12    Leader       New Server          Invitation to join; must contain a single Configuration log entry only
JoinClusterResponse         13    New Server   Leader
LeaveClusterRequest         14    Leader       Follower            Command to leave
LeaveClusterResponse        15    Follower     Leader
InstallSnapshotRequest      16    Leader       Follower            Raft Section 7; Must contain a single SnapshotSyncRequest log entry only
InstallSnapshotResponse     17    Follower     Leader              Raft Section 7
========================  ======  ===========  =================   =====================================


Establishment
-------------

After the HTTP handshake, the establishment sequence is as follows:

.. raw:: html

  {% highlight %}
New Server Alice              Random Follower Bob

  ClientRequest   ------->
          <---------   AppendEntriesResponse

  If Bob says he is the leader, continue as below.
  Else, Alice must disconnect from Bob and connect to the leader.


  New Server Alice              Leader Charlie

  ClientRequest   ------->
          <---------   AppendEntriesResponse
  AddServerRequest   ------->
          <---------   AddServerResponse
          <---------   JoinClusterRequest
  JoinClusterResponse  ------->
          <---------   SyncLogRequest
                       OR InstallSnapshotRequest
  SyncLogResponse  ------->
  OR InstallSnapshotResponse

{% endhighlight %}

Disconnect Sequence:

.. raw:: html

  {% highlight %}

Follower Alice              Leader Charlie

  RemoveServerRequest   ------->
          <---------   RemoveServerResponse
          <---------   LeaveClusterRequest
  LeaveClusterResponse  ------->

{% endhighlight %}

Election Sequence:

.. raw:: html

  {% highlight %}

Candidate Alice             Candidate/Follower Bob

  RequestVoteRequest   ------->
          <---------   RequestVoteResponse

  if Alice wins election:

  Leader Alice                Follower Bob

  AppendEntriesRequest   ------->
  (heartbeat)
          <---------   AppendEntriesResponse

{% endhighlight %}


Definitions
-----------

- Source: Identifies the originator of the message
- Destination: Identifies the recipient of the message
- Terms: See Raft. Initialized to 0, increases monotonically
- Indexes: See Raft. Initialized to 0, increases monotonically



Requests
--------

Requests contain a header and zero or more log entries.
Requests contain a fixed-size header and optional Log Entries of variable size.


Request Header
``````````````

The request header is 45 bytes, as follows.
All values are unsigned big-endian.

.. raw:: html

  {% highlight lang='dataspec' %}

Message type:      1 byte
  Source:            ID, 4 byte integer
  Destination:       ID, 4 byte integer
  Term:              Current term (see notes), 8 byte integer
  Last Log Term:     8 byte integer
  Last Log Index:    8 byte integer
  Commit Index:      8 byte integer
  Log entries size:  Total size in bytes, 4 byte integer
  Log entries:       see below, total length as specified

{% endhighlight %}


Notes
~~~~~

In the RequestVoteRequest, Term is the candidate's term.
Otherwise, it is the leader's current term.

In the AppendEntriesRequest, when the log entries size is zero,
this message is a heartbeat (keepalive) message.



Log Entries
```````````

The log contains zero or more log entries.
Each log entry is as follows.
All values are unsigned big-endian.

.. raw:: html

  {% highlight lang='dataspec' %}

Term:           8 byte integer
  Value type:     1 byte
  Entry size:     In bytes, 4 byte integer
  Entry:          length as specified

{% endhighlight %}


Log Contents
````````````

All values are unsigned big-endian.

========================  ======
Log Value Type            Number
========================  ======
Application                  1
Configuration                2
ClusterServer                3
LogPack                      4
SnapshotSyncRequest          5
========================  ======


Application
~~~~~~~~~~~

TBD, probably JSON.


Configuration
~~~~~~~~~~~~~

This is used for the leader to serialize a new cluster configuration and replicate to peers.
It contains zero or more ClusterServer configurations.


.. raw:: html

  {% highlight lang='dataspec' %}

Log Index:  8 byte integer
  Last Log Index:  8 byte integer
  ClusterServer Data for each server:
    ID:                4 byte integer
    Endpoint data len: In bytes, 4 byte integer
    Endpoint data:     ASCII string of the form "tcp://localhost:9001", length as specified

{% endhighlight %}


ClusterServer
~~~~~~~~~~~~~

The configuration information for a server in a cluster.
This is included only in a AddServerRequest or RemoveServerRequest message.

When used in a AddServerRequest Message:

.. raw:: html

  {% highlight lang='dataspec' %}

ID:                4 byte integer
  Endpoint data len: In bytes, 4 byte integer
  Endpoint data:     ASCII string of the form "tcp://localhost:9001", length as specified

{% endhighlight %}


When used in a RemoveServerRequest Message:

.. raw:: html

  {% highlight lang='dataspec' %}

ID:                4 byte integer

{% endhighlight %}


LogPack
~~~~~~~

This is included only in a SyncLogRequest message.

The following is gzipped before transmission:


.. raw:: html

  {% highlight lang='dataspec' %}

Index data len: In bytes, 4 byte integer
  Log data len:   In bytes, 4 byte integer
  Index data:     8 bytes for each index, length as specified
  Log data:       length as specified

{% endhighlight %}



SnapshotSyncRequest
~~~~~~~~~~~~~~~~~~~

This is included only in a InstallSnapshotRequest message.

.. raw:: html

  {% highlight lang='dataspec' %}

Last Log Index:  8 byte integer
  Last Log Term:   8 byte integer
  Config data len: In bytes, 4 byte integer
  Config data:     length as specified
  Offset:          The offset of the data in the database, in bytes, 8 byte integer
  Data len:        In bytes, 4 byte integer
  Data:            length as specified
  Is Done:         1 if done, 0 if not done (1 byte)

{% endhighlight %}




Responses
---------

All responses are 26 bytes, as follows.
All values are unsigned big-endian.

.. raw:: html

  {% highlight lang='dataspec' %}

Message type:   1 byte
  Source:         ID, 4 byte integer
  Destination:    Usually the actual destination ID (see notes), 4 byte integer
  Term:           Current term, 8 byte integer
  Next Index:     Initialized to leader last log index + 1, 8 byte integer
  Is Accepted:    1 if accepted, 0 if not accepted (see notes), 1 byte

{% endhighlight %}


Notes
`````

The Destination ID is usually the actual destination for this message.
However, for AppendEntriesResponse, AddServerResponse, and RemoveServerResponse,
it is the ID of the current leader.

In the RequestVoteResponse, Is Accepted is 1 for a vote for the candidate (requestor),
and 0 for no vote.


Application Layer
=================

Each Server periodically posts Application data to the log in a ClientRequest.
Application data contains the status of each Server's Router and the Destination
for the Meta LS2 cluster.
The servers use a common algorithm to determine the publisher and contents
of the Meta LS2.
The server with the "best" recent status in the log is the Meta LS2 publisher.
The publisher of the Meta LS2 is NOT necessarily the Raft Leader.


Application Data Contents
-------------------------

The Application data will be in a JSON format for simplicity and extensibility.
The full specification is TBD.
The goal is to provide enough data to write an algorithm to determine the "best"
router to publish the Meta LS2, and for the publisher to have sufficient information
to weight the Destinations in the Meta LS2.
The data will contain both router and Destination statistics.

The data may optionally contain remote sensing data on the health of the
other servers, and the ability to fetch the Meta LS.
These data would not be supported in the first release.

The data may optionally contain configuration information posted
by an administrator client.
These data would not be supported in the first release.


Config data:

- Raft ID
- Cluster name
- Publisher status off/on
- Publisher request never/yes/force-on

Router data:

- Current router info
- Uptime
- Job lag
- Exploratory tunnels
- Participating tunnels
- Configured bandwidth
- Current bandwidth

Destination data:

- Full destination
- Uptime
- Configured tunnels
- Current tunnels
- Configured bandwidth
- Current bandwidth
- Configured connections
- Current connections
- Blacklist data

Remote router sensing data:

- Last RI version seen
- LS Fetch time
- Connection test data
- Closest floodfills profile data
  for time periods yesterday, today, and tomorrow

Remote destination sensing data:

- Last LS version seen
- LS Fetch time
- Connection test data
- Closest floodfills profile data
  for time periods yesterday, today, and tomorrow

Meta LS sensing data:

- Last version seen
- Fetch time
- Closest floodfills profile data
  for time periods yesterday, today, and tomorrow

Admin data:

- Raft ID
- Cluster name
- Raft parameters?
- TBD


Administration Interface
========================

TBD, possibly a separate proposal.
Not required for the first release.

Requirements of an admin interface:

- Support for multiple master destinations, i.e. multiple virtual clusters (farms)
- Provide comprehensive view of shared cluster state - all stats published by members, who is the current leader, etc.
- Ability to force removal of a participant or leader from the cluster
- Ability to force publish metaLS (if current node is publisher)
- Ability to exclude hashes from metaLS (if current node is publisher)
- Configuration import/export functionality for bulk deployments



Router Interface
================

TBD, possibly a separate proposal.
i2pcontrol is not required for the first release and detailed changes will be included in a separate proposal.

Requirements for Garlic Farm to router API (in-JVM java or i2pcontrol)

- getLocalRouterStatus()
- getLocalLeafHash(Hash masterHash)
- getLocalLeafStatus(Hash leaf)
- getRemoteMeasuredStatus(Hash masterOrLeaf) // probably not in MVP
- publishMetaLS(Hash masterHash, List<MetaLease> contents) // or signed MetaLeaseSet? Who signs?
- stopPublishingMetaLS(Hash masterHash)
- authentication TBD?


Justification
=============

Atomix is too large and won't allow customization for us to route
the protocol over I2P. Also, its wire format is undocumented, and depends
on Java serialization.


Notes
=====



Issues
======

- There's no way for a client to find out about and connect to an unknown leader.
  It would be a minor change for a Follower to send the Configuration as a Log Entry in the AppendEntriesResponse.



Migration
=========

No backward compatibility issues.




References
==========

.. [JRAFT]
    https://github.com/datatechnology/jraft

.. [RAFT]
    https://ramcloud.stanford.edu/wiki/download/attachments/11370504/raft.pdf

.. [RFC-2616]
    https://tools.ietf.org/html/rfc2616

.. [RFC-2617]
    https://tools.ietf.org/html/rfc2617

.. [WEBSOCKET]
    https://en.wikipedia.org/wiki/WebSocket
