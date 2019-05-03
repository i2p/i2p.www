====================
Garlic Farm Protocol
====================
.. meta::
    :author: zzz
    :created: 2019-05-02
    :thread: http://zzz.i2p/topics/2234
    :lastupdated: 2019-05-03
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


Design
======

The Raft protocol is not a concrete protocol; it defines only a state machine.
Therefore we document the concrete protocol of JRaft and base our protocol on it.
There are no changes to the JRaft protocol other than the addition of
an authentication handshake.


Specification
=============

The wire protocol is over SSL sockets or non-SSL I2P sockets.
There is no support for clearnet non-SSL sockets.


Handshake and authentication
----------------------------

Not defined by JRaft.

TODO authentication. Perhaps new messages, or perhaps something before
the request/response phase happens.

Requirements:

- user/password
- version
- cluster identifier
- extensible


Message Types
-------------

There are two types of messages, requests and responses.
Requests may contain Log Entries, and are variable-sized;
responses do not contain Log Entries, and are fixed-size.




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
InstallSnapshotRequest      16    Leader       Follower            Must contain a single SnapshotSyncRequest log entry only
InstallSnapshotResponse     17    Follower     Leader              Raft Section 7
========================  ======  ===========  =================   =====================================


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
  Term:              Current term (or candidate term for RequestVoteRequest), 8 byte integer
  Last Log Term:     8 byte integer
  Last Log Index:    8 byte integer
  Commit Index:      8 byte integer
  Log entries size:  Total size in bytes, 4 byte integer
  Log entries:       see below, total length as specified

{% endhighlight %}


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
  Is Accepted:    1 if accepted, 0 if not accepted (1 byte)

{% endhighlight %}


Notes
`````

The Destination ID is usually the actual destination for this message.
However, for AppendEntriesResponse, AddServerResponse, and RemoveServerResponse,
it is the ID of the current leader.


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
