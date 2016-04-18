==============
Service Lookup
==============
.. meta::
    :author: zzz
    :created: 2016-01-13
    :thread: http://zzz.i2p/topics/2048
    :lastupdated: 2016-01-13
    :status: Draft

.. contents::


Introduction
============

This is the full-monty bombastic anything-goes-in-the-netdb proposal. AKA
anycast. This would be the 4th proposed LS2 subtype.

Say you wanted to advertise your destination as an outproxy, or a GNS node, or a
Tor gateway, or a Bittorrent DHT or imule or i2phex or Seedless bootstrap, etc.
You could store this information in the netDB instead of using a separate
bootstrapping or information layer.

There's nobody in charge so unlike with massive multihoming, you can't have a
signed authoritative list. So you would just publish your record to a floodfill.
The floodfill would aggregate these and send them as a response to queries.


Example
=======

Say your service was "GNS". You would send a database store to the floodfill:

- Hash of "GNS"
- destination
- publish timestamp
- expiration (0 for revocation)
- port
- signature

When somebody did a lookup, they would get back a list of those records:

- Hash of "GNS"
- Floodfill's hash
- Timestamp
- number of records
- List of records
- signature of floodfill

Expirations would be relatively long, hours at least.


Considerations
==============

The downside is that this could turn into the Bittorrent DHT or worse. At a
minimum, the floodfills would have to severely rate- and capacity-limit the
stores and queries. We could whitelist approved service names for higher limits.
We could also ban non-whitelisted services completely.

Of course, even today's netDB is open to abuse. You can store arbitrary data in
the netDB, as long as it looks like a RI or LS and the signature verifies. But
this would make it a lot easier.
