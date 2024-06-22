===================================
Service Records in LS2
===================================
.. meta::
    :author: zzz
    :created: 2024-06-22
    :thread: http://zzz.i2p/topics/3641
    :lastupdated: 2024-06-22
    :status: Open
    :target: 0.9.65

.. contents::



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


Related Proposals
==================

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


Design
======

Service records are placed in the (currently unused) options section in LS2 [LS2]_.
Not supported for LS1.

To lookup a service address for a specific hostname or b32, the router fetches the
leaseset and looks up the service record in the properties.

The service may be hosted on the same destination as the LS itself, or may reference
a different hostname/b32.

If the target destination for the service is different, the target LS must also
include a service record, pointing to itself, indicating that it supports the service.



Specification
=============

LS2 Option Specification
---------------------------

Defined as follows:

- serviceoption := optionkey optionvalue
- optionkey := _service._proto
- service := The symbolic name of the desired service. Must be lower case. Example: "smtp".
  Allowed chars are [a-z0-9-] and must not start or end with a '-'.
  Standard identifiers from [REGISTRY]_ or Linux /etc/services must be used if defined there.
- proto := The transport protocol of the desired service. Must be lower case, either "tcp" or "udp".
  "tcp" means streaming and "udp" means repliable datagrams.
  Indicators for raw datagrams and datagram2 may be defined later.
  Allowed chars are [a-z0-9-] and must not start or end with a '-'.
- optionvalue := self | srvrecord[,srvrecord]*
- self := "0" ttl port [appoptions]
- srvrecord := "1" ttl priority weight port target [appoptions]
- ttl := time to live, integer seconds. Positive integer. Example: "85400"
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


Service Name Registry
----------------------

Non-standard identifiers that are not listed in [REGISTRY]_ or Linux /etc/services
may be requested and added to the common structures specification [LS2]_.

Service-specific appoptions formats may also be added there.


I2CP Specification
------------------

The [I2CP]_ protocol may need to be extended to support service lookups;
or, maybe, just do a lookup for "_service._proto.xxx.b32.i2p" and the router figures it out.
But no way to pass ttl and port back without changes.
See Recommendations section below.

TODO


SAM Specification
------------------

The [SAMv3]_ protocol may need to be extended to support service lookups;
or, maybe, just do a lookup for "_service._proto.xxx.b32.i2p" and the router figures it out.
But no way to pass ttl and port back without changes.
See Recommendations section below.

TODO


Naming Specification
---------------------

Update [NAMING]_ to specify handling of hostnames starting with '_', as
documented in the implementation section below.




Recommendations
================

It may be difficult and low-priority for us to design and implement the
I2CP and SAM changes necessary to pass through the TTL and port information to the client.
If those are unavailable to the application, it should assume a TTL
of 86400 (one day) and use the standard internet port (e.g. 25 for SMTP)
as the I2CP port.

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

Configuration is implementation-dependent. We may define standard I2CP options
for i2ptunnel and SAM.

Naming service subsystems must check for a leading "_", strip off the first two labels,
look up the leaseset for the remaining part of the hostname, and then lookup the
two labels in the options field of the leaseset.


Security Analysis
=================

As the leaseset is signed, any service records within it are authenticated by the signing key of the destination.

The service records are public and visible to floodfills, unless the leaseset is encrypted.
Any router requesting the leaseset will be able to see the service records.



Compatibility
===============

No issues. All known implementations currently ignore the properties field in LS2.
LS2 was implemented in 0.9.38 in 2016 and is well-supported by all router implementations.

'_' is not a valid character in i2p hostnames.


Migration
=========

Implementations may add support at any time, no coordination is needed.



References
==========

.. [DOTWELLKNOWN]
    http://i2pforum.i2p/viewtopic.php?p=3102

.. [I2CP]
    {{ spec_url('i2cp') }}

.. [LS2]
    {{ spec_url('common-structures') }}

.. [GNS]
    http://zzz.i2p/topcs/1545

.. [NAMING]
    {{ site_url('docs/naming', True) }}

.. [Prop123]
    {{ proposal_url('123') }}

.. [REGISTRY]
    http://www.dns-sd.org/ServiceTypes.html

.. [RFC2782]
    https://datatracker.ietf.org/doc/html/rfc2782

.. [SAMv3]
    {{ site_url('docs/api/samv3') }}

.. [SRV]
    https://en.wikipedia.org/wiki/SRV_record
