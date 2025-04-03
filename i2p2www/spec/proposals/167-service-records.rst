===================================
Service Records in LS2
===================================
.. meta::
    :author: zzz, orignal, eyedeekay
    :created: 2024-06-22
    :thread: http://zzz.i2p/topics/3641
    :lastupdated: 2025-04-03
    :status: Closed
    :target: 0.9.66

.. contents::


Status
======
Approved on 2nd review 2025-04-01; specs are updated; not yet implemented.


Overview
========

I2P lacks a centralized DNS system.
However, the address book, together with the b32 hostname system, allows
the router to look up full destinations and fetch lease sets, which contain
a list of gateways and keys so that clients may connect to that destination.

So, leasesets are somewhat like a DNS record. But there is currently no facility to
find out if that host supports any services, either on that destination or a different one,
in a manner similar to DNS SRV records [SRV]_ [RFC2782]_.

The first application for this may be peer-to-peer email.
Other possible applications: DNS, GNS, key servers, certificate authorities, time servers,
bittorrent, cryptocurrencies, other peer-to-peer applications.


Related Proposals and Alternatives
==================================

Service Lists
--------------

The LS2 proposal 123 [Prop123]_ defined 'service records' that indicated a destination
was participating in a global service. The floodfills would aggregate these records
into global 'service lists'.
This was never implemented due to complexity, lack of authentication,
security, and spamming concerns.

This proposal is different in that it provides lookup for a service for a specific destination,
not a global pool of destinations for some global service.

GNS
-----

GNS [GNS]_ proposes that everybody runs their own DNS server.
This proposal is complementary, in that we could use service records to specify
that GNS (or DNS) is supported, with a standard service name of "domain" on port 53.

Dot well-known
---------------

In [DOTWELLKNOWN]_ it is proposed that services be looked up via an HTTP request to
/.well-known/i2pmail.key. This requires that every service must have a related
website to host the key. Most users do not run websites.

One workaround is that we could presume that a service for a b32 address is actually
running on that b32 address. So that looking for the service for example.i2p requires
the HTTP fetch from http://example.i2p/.well-known/i2pmail.key, but
a service for aaa...aaa.b32.i2p does not require that lookup, it can just connect directly.

But there's an ambiguity there, because example.i2p can also be addressed by its b32.

MX Records
----------

SRV records are simply a generic version of MX records for any service.
"_smtp._tcp" is the "MX" record.
There is no need for MX records if we have SRV records, and MX records
alone do not provide a generic record for any service.


Design
======

Service records are placed in the options section in LS2 [LS2]_.
The LS2 options section is currently unused.
Not supported for LS1.
This is similar to the tunnel bandwidth proposal [Prop168]_,
which defines options for tunnel build records.

To lookup a service address for a specific hostname or b32, the router fetches the
leaseset and looks up the service record in the properties.

The service may be hosted on the same destination as the LS itself, or may reference
a different hostname/b32.

If the target destination for the service is different, the target LS must also
include a service record, pointing to itself, indicating that it supports the service.

The design does not require special support or caching or any changes in the floodfills.
Only the leaseset publisher, and the client looking up a service record,
must support these changes.

Minor I2CP and SAM extensions are proposed to facilitate retrieval of
service records by clients.



Specification
=============

LS2 Option Specification
---------------------------

LS2 options MUST be sorted by key, so the signature is invariant.

Defined as follows:

- serviceoption := optionkey optionvalue
- optionkey := _service._proto
- service := The symbolic name of the desired service. Must be lower case. Example: "smtp".
  Allowed chars are [a-z0-9-] and must not start or end with a '-'.
  Standard identifiers from [REGISTRY]_ or Linux /etc/services must be used if defined there.
- proto := The transport protocol of the desired service. Must be lower case, either "tcp" or "udp".
  "tcp" means streaming and "udp" means repliable datagrams.
  Protocol indicators for raw datagrams and datagram2 may be defined later.
  Allowed chars are [a-z0-9-] and must not start or end with a '-'.
- optionvalue := self | srvrecord[,srvrecord]*
- self := "0" ttl port [appoptions]
- srvrecord := "1" ttl priority weight port target [appoptions]
- ttl := time to live, integer seconds. Positive integer. Example: "86400".
  A minimum of 86400 (one day) is recommended, see Recommendations section below for details.
- priority := The priority of the target host, lower value means more preferred. Non-negative integer. Example: "0"
  Only useful if more than one record, but required even if just one record.
- weight := A relative weight for records with the same priority. Higher value means more chance of getting picked. Non-negative integer. Example: "0"
  Only useful if more than one record, but required even if just one record.
- port := The I2CP port on which the service is to be found. Non-negative integer. Example: "25"
  Port 0 is supported but not recommended.
- target := The hostname or b32 of the destination providing the service. A valid hostname as in [NAMING]_. Must be lower case.
  Example: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.b32.i2p" or "example.i2p".
  b32 is recommended unless the hostname is "well known", i.e. in official or default address books.
- appoptions := arbitrary text specific to the application, must not contain " " or ",". Encoding is UTF-8.

Examples
``````````

In LS2 for aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.b32.i2p, pointing to one SMTP server:

"_smtp._tcp" "1 86400 0 0 25 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.b32.i2p"

In LS2 for aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.b32.i2p, pointing to two SMTP servers:

"_smtp._tcp" "1 86400 0 0 25 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.b32.i2p,86400 1 0 25 cccccccccccccccccccccccccccccccccccccccccccc.b32.i2p"

In LS2 for bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.b32.i2p, pointing to itself as a SMTP server:

"_smtp._tcp" "0 999999 25"

Possible format for redirecting email (see below):

"_smtp._tcp" "1 86400 0 0 25 smtp.postman.i2p example@mail.i2p"


Limits
```````

The Mapping data structure format used for LS2 options limits keys and values to 255 bytes (not chars) max.
With a b32 target, the optionvalue is about 67 bytes, so only 3 records would fit.
Maybe only one or two with a long appoptions field, or up to four or five with a short hostname.
This should be sufficient; multiple records should be rare.


Differences from [RFC2782]_
````````````````````````````

- No trailing dots
- No name after the proto
- Lower case required
- In text format with comma-separated records, not binary DNS format
- Different record type indicators
- Additional appoptions field


Notes
`````

No wildcarding such as (asterisk), (asterisk)._tcp, or _tcp is allowed.
Each supported service must have its own record.



Service Name Registry
----------------------

Non-standard identifiers that are not listed in [REGISTRY]_ or Linux /etc/services
may be requested and added to the common structures specification [LS2]_.

Service-specific appoptions formats may also be added there.


I2CP Specification
------------------

The [I2CP]_ protocol must be extended to support service lookups.
Additional MessageStatusMessage and/or HostReplyMessage error codes related to service lookup
are required.
To make the lookup facility general, not just service record-specific,
the design is to support retrieval of all LS2 options.

Implementation: Extend HostLookupMessage to add request for
LS2 options for hash, hostname, and destination (request types 2-4).
Extend HostReplyMessage to add the options mapping if requested.
Extend HostReplyMessage with additional error codes.

Options mappings may be cached or negative cached for a short time on either the client or router side,
implementation-dependent. Recommended maximum time is one hour, unless the service record TTL is shorter.
Service records may be cached up to the TTL specified by the application, client, or router.

Extend the specification as follows:

Configuration options
`````````````````````
Add the following to [I2CP-OPTIONS]

i2cp.leaseSetOption.nnn

Options to be put in the leaseset. Only available for LS2.
nnn starts with 0. Option value contains "key=value".
(do not include quotes)

Example:
i2cp.leaseSetOption.0=_smtp._tcp=1 86400 0 0 25 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.b32.i2p


HostLookup Message
``````````````````

- Lookup type 2: Hash lookup, request options mapping
- Lookup type 3: Hostname lookup, request options mapping
- Lookup type 4: Destination lookup, request options mapping

For lookup type 4, item 5 is a Destination.



HostReply Message
``````````````````

For lookup types 2-4, the router must fetch the leaseset,
even if the lookup key is in the address book.

If successful, the HostReply will contain the options Mapping
from the leaseset, and includes it as item 5 after the destination.
If there are no options in the Mapping, or the leaseset was version 1,
it will still be included as an empty Mapping (two bytes: 0 0).
All options from the leaseset will be included, not just service record options.
For example, options for parameters defined in the future may be present.

On leaseset lookup failure, the reply will contain a new error code 6 (Leaseset lookup failure)
and will not include a mapping.
When error code 6 is returned, the Destination field may or may not be present.
It will be present if a hostname lookup in the address book was successful,
or if a previous lookup was successful and the result was cached,
or if the Destination was present in the lookup message (lookup type 4).

If a lookup type is not supported,
the reply will contain a new error code 7 (lookup type unsupported).



SAM Specification
------------------

The [SAMv3]_ protocol must be extended to support service lookups.

Extend NAMING LOOKUP as follows:

NAMING LOOKUP NAME=example.i2p OPTIONS=true requests the options mapping in the reply.

NAME may be a full base64 destination when OPTIONS=true.

If the destination lookup was successful and options were present in the leaseset,
then in the reply, following the destination,
will be one or more options in the form of OPTION:key=value.
Each option will have a separate OPTION: prefix.
All options from the leaseset will be included, not just service record options.
For example, options for parameters defined in the future may be present.
Example:

NAMING REPLY RESULT=OK NAME=example.i2p VALUE=base64dest OPTION:_smtp._tcp="1 86400 0 0 25 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.b32.i2p"

Keys containing '=', and keys or values containing a newline,
are considered invalid and the key/value pair will be removed from the reply.

If there are no options found in the leaseset, or if the leaseset was version 1,
then the response will not include any options.

If OPTIONS=true was in the lookup, and the leaseset is not found, a new result value LEASESET_NOT_FOUND will be returned.


Naming Lookup Alternative
==========================

An alternative design was considered, to support lookups of services
as a full hostname, for example _smtp._tcp.example.i2p,
by updating [NAMING]_ to specify handling of hostnames starting with '_'.
This was rejected for two reasons:

- I2CP and SAM changes would still be necessary to pass through the TTL and port information to the client.
- It would not be a general facility that could be used to retrieve other LS2
  options that could be defined in the future.


Recommendations
================

Servers should specify a TTL of at least 86400, and the standard port for the application.



Advanced Features
==================

Recursive Lookups
----------------------

It may be desirable to support recursive lookups, where each successive leaseset
is checked for a service record pointing to another leaseset, DNS-style.
This is probably not necessary, at least in an initial implementation.

TODO



Application-specific fields
-----------------------------

It may be desirable to have application-specific data in the service record.
For example, the operator of example.i2p may wish to indicate that email should
be forwarded to example@mail.i2p. The "example@" part would need to be in a separate field
of the service record, or stripped from the target.

Even if the operator runs his own email service, he may wish to indicate that
email should be sent to example@example.i2p. Most I2P services are run by a single person.
So a separate field may be helpful here as well.

TODO how to do this in a generic way


Changes required for Email
------------------------------

Out of the scope of this proposal. See [DOTWELLKNOWN]_ for a discussion.


Implementation Notes
=====================

Caching of service records up to the TTL may be done by the router or the application,
implementation-dependent. Whether to cache persistently is also implementation-dependent.

Lookups must also lookup the target leaseset and verify it contains a "self" record
before returning the target destination to the client.


Security Analysis
=================

As the leaseset is signed, any service records within it are authenticated by the signing key of the destination.

The service records are public and visible to floodfills, unless the leaseset is encrypted.
Any router requesting the leaseset will be able to see the service records.

A SRV record other than "self" (i.e., one that points to a different hostname/b32 target)
does not require the consent of the targeted hostname/b32.
It's not clear if a redirection of a service to an arbitrary destination could facilitate some
sort of attack, or what the purpose of such an attack would be.
However, this proposal mitigates such an attack by requiring that the target
also publish a "self" SRV record. Implementers must check for a "self" record
in the leaseset of the target.


Compatibility
===============

LS2: No issues. All known implementations currently ignore the options field in LS2,
and correctly skip over a non-empty options field.
This was verified in testing by both Java I2P and i2pd during the development of LS2.
LS2 was implemented in 0.9.38 in 2016 and is well-supported by all router implementations.
The design does not require special support or caching or any changes in the floodfills.

Naming: '_' is not a valid character in i2p hostnames.

I2CP: Lookup types 2-4 should not be sent to routers below the minimum API version
at which it is supported (TBD).

SAM: Java SAM server ignores additional keys/values such as OPTIONS=true.
i2pd should as well, to be verified.
SAM clients will not get the additional values in the reply unless requested with OPTIONS=true.
No version bump should be necessary.


Migration
=========

Implementations may add support at any time, no coordination is needed,
except for an agreement on the effective API version for the I2CP changes.
SAM compatibility versions for each implementation will be documented in the SAM spec.


References
==========

.. [DOTWELLKNOWN]
    http://i2pforum.i2p/viewtopic.php?p=3102

.. [I2CP]
    {{ spec_url('i2cp') }}

.. [I2CP-OPTIONS]
    {{ site_url('docs/protocol/i2cp', True) }}

.. [LS2]
    {{ spec_url('common-structures') }}

.. [GNS]
    http://zzz.i2p/topcs/1545

.. [NAMING]
    {{ site_url('docs/naming', True) }}

.. [Prop123]
    {{ proposal_url('123') }}

.. [Prop168]
    {{ proposal_url('168') }}

.. [REGISTRY]
    http://www.dns-sd.org/ServiceTypes.html

.. [RFC2782]
    https://datatracker.ietf.org/doc/html/rfc2782

.. [SAMv3]
    {{ site_url('docs/api/samv3') }}

.. [SRV]
    https://en.wikipedia.org/wiki/SRV_record
