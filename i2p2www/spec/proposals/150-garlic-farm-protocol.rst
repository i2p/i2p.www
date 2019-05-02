====================
Garlic Farm Protocol
====================
.. meta::
    :author: zzz
    :created: 2019-05-03
    :thread: http://zzz.i2p/topics/2234
    :lastupdated: 2019-05-03
    :status: Open

.. contents::


Overview
========

This is the spec for the Garlic Farm wire protocol,
based on the jraft "dmprinter" demo app [JRAFT]_.

This will be the backend for coordination of routers publishing
entries in a Meta LeaseSet. See proposal 123.


Goals
=====




Design
======



Specification
=============

The wire protocol is over SSL sockets or non-SSL I2P sockets.
There is no support for clearnet non-SSL sockets.

TODO authentication. Perhaps new messages, or perhaps something before
the request/response phase happens.

There are two types of messages, requests and responses.


Message Types
-------------

========================  ======
Message                   Number
========================  ======
RequestVoteRequest           1
RequestVoteResponse          2
AppendEntriesRequest         3
AppendEntriesResponse        4
ClientRequest                5
AddServerRequest             6
AddServerResponse            7
RemoveServerRequest          8
RemoveServerResponse         9
SyncLogRequest              10
SyncLogResponse             11
JoinClusterRequest          12
JoinClusterResponse         13
LeaveClusterRequest         14
LeaveClusterResponse        15
InstallSnapshotRequest      16
InstallSnapshotResponse     17
========================  ======

Definitions
-----------

- Source: Identifies the originator of the message
- Destination: Identifies the recipient of the message
- Term: See Raft 
- Last Log Term: See Raft 
- Last Log Index: See Raft 
- Commit Index: See Raft 



Requests
--------

Requests contain a header and zero or more log entries.


Request Header
``````````````

The request header is 45 bytes, as follows.
All values are big-endian.

.. raw:: html

  {% highlight lang='dataspec' %}

Message type:   1 byte
  Source:         4 byte integer
  Destination:    4 byte integer
  Term:           8 byte integer
  Last Log Term:  8 byte integer
  Last Log Index: 8 byte integer
  Commit Index:   8 byte integer
  Log size:       4 byte integer

{% endhighlight %}


Log Entries
```````````

The log contains zero or more log entries.
Each log entry is as follows.

.. raw:: html

  {% highlight lang='dataspec' %}

Term:           8 byte integer
  Value type:     1 byte
  Entry size:     4 byte integer
  Entry:          length as specified

{% endhighlight %}


Log Contents
````````````

TBD, probably JSON.




Responses
---------

The response is 26 bytes, as follows.
All values are big-endian.

.. raw:: html

  {% highlight lang='dataspec' %}

Message type:   1 byte
  Source:         4 byte integer
  Destination:    4 byte integer
  Term:           8 byte integer
  Next Index:     8 byte integer
  Is Accepted:    1 byte

{% endhighlight %}


Justification
=============

Atomix is too large and won't allow customization for us to route
the protocol over I2P. Also, its wire format is undocumented, and depends
on Java serialization.


Notes
=====



Issues
======



Migration
=========

No backward compatibility issues.




References
==========

.. [JRAFT]
    https://github.com/datatechnology/jraft
