=======================================
Deprecate hostnames in router addresses
=======================================
.. meta::
    :author: zzz
    :created: 2017-08-03
    :thread: http://zzz.i2p/topics/2363
    :lastupdated: 2017-08-03
    :status: Open

.. contents::


Overview
========

As of release 0.9.32, update the netdb specification
to deprecate hostnames in router infos,
or more precisely, in the individual router addresses.
In all I2P implementations,
publishing routers configured with hostnames should replace hostnames with IPs before publishing,
and other routers should ignore addresses with hostnames.
Routers should not do DNS lookups of published hostnames.


Motivation
==========

Hostnames have been allowed in router addresses since the beginning of I2P.
However, very few routers publish hostnames, because it requires
both a public hostname (which few users have), and manual configuration
(which few users bother to do).
In a recent sample, 0.7% of routers were publishing a hostname.

The original purpose of hostnames was to help users with frequently
changing IPs and a dynamic DNS service (such as http://dyn.com/dns/)
to not lose connectivity when their IP changed. However, back then
the network was small and router info expiration was longer.
Also, the Java code did not have working logic to restart the router or
republish the router info when the local IP changed.

Also, in the beginning, I2P did not support IPv6, so the complication
of resolving a hostname to either an IPv4 or IPv6 address did not exist.

In Java I2P, it's always been a challenge to propagate a configured
hostname to both published transports, and the situation got more complex
with IPv6. Open ticket 1050 http://trac.i2p2.i2p/ticket/1050 details some of the problems.
It isn't clear if a dual-stack host should publish both a hostname and a literal
IPv6 address or not. The hostname is published for the SSU address but not the NTCP address.

Recently, DNS issues were brought up (both indirectly and directly) by
research at Georgia Tech. The researchers ran a large number of floodfills
with published hostnames. The immediate issue was that for a small number of
users with possibly broken local DNS, it hung I2P completely.

The larger issue was DNS in general, and how
DNS (either active or passive) could be used to very quickly enumerate the network,
especially if the publishing routers were floodfill.
Invalid hostnames or unresponsive, slow, or malicious DNS responders could
be used for additional attacks.
EDNS0 may provide further enumeration or attack scenarios.
DNS may also provide attack avenues based on time-of lookup,
revealing router-to-router connection times, help to build connection graphs,
estimate traffic, and other inferences.

Also, the Georgia Tech group, led by David Dagon, has listed several concerns
with DNS in privacy-focused applications. DNS lookups are generally done by
a low-level library, not controlled by the application.
These libraries were not specifically designed for anonymity;
may not provide fine-grained control by the application;
and their output may be fingerprinted.
Java libraries in particular may be problematic, but this is not just a Java issue.
Some libraries use DNS ANY queries which may be rejected.
All this is made more worrisome by the widespread presence
of passive DNS monitoring and queries available to multiple organizations.
All DNS monitoring and attacks are out-of-band from the perspective of
I2P routers and require little to no in-network I2P resources,
and no modification of existing implementations.

While we haven't completely thought through the possible issues,
the attack surface seems to be large. There are other ways to
enumerate the network and gather related data, but DNS attacks
could be much easier, faster, and less detectable.

Router implementations could, in theory, switch to using a sophisticated
3rd-party DNS library, but that would be quite complex, be a maintenance burden,
and is well outside the core expertise of I2P developers.

The immediate solutions implemented for Java 0.9.31 included fixing the hang problem,
increasing DNS cache times, and implementing a DNS negative cache. Of course,
increasing cache times reduces the benefit of having hostnames in routerinfos to begin with.

However, these changes are only short-term mitigations and do not fix the underlying
issues above. Therefore, the simplest and most complete fix is to prohibit
hostnames in router infos, thus eliminating DNS lookups for them.


Design
======

For the router info publishing code, implementers have two choices, either
to disable/remove the configuration option for hostnames, or to
convert configured hostnames to IPs at publishing time.
In either case, routers should republish immediately when their IP changes.

For the router info validation and transport connection code,
implementers should ignore router addresses containing hostnames,
and use the other published addresses containing IPs, if any.
If no addresses in the router info contain IPs, the router
should not connect to the published router.
In no case should a router do a DNS lookup of a published hostname,
either directly or via an underlying library.



Specification
=============

Change the NTCP and SSU transport specs to indicate that the "host" parameter must be
an IP, not a hostname, and that routers should ignore individual
router addresses that contain hostnames.
The relevant section is "Router Address Specification" in the transport specifications:
http://i2p-projekt.i2p/en/docs/transport/ntcp
and
http://i2p-projekt.i2p/en/docs/transport/ssu


Notes
=====

This proposal does not address hostnames for reseed hosts.
While DNS lookups for reseed hosts are much less frequent,
they could still be an issue. If necessary, this can be fixed simply
by replacing the hostnames with IPs in the hardcoded list of URLs;
no specification or code changes would be required.


Migration
=========

This proposal may be implemented immediately, without a gradual migration,
because very few routers publish hostnames, and those that do generally
don't publish the hostname in all addresses.

Routers need not check the published router's version
before deciding to ignore hostnames, and there is no need
for a coordinated release or common strategy across
the various router implementations.

For those routers still publishing hostnames, they will get less
inbound connections, and may eventually have difficulty building
inbound tunnels.

To minimize the impact further, implementers could start by ignoring
router addresses with hostnames only for floodfill routers,
or for routers with a published version less than 0.9.32,
and ignore hostnames for all routers in a later release.
