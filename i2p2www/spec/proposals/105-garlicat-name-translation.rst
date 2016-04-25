=============================
Name Translation for GarliCat
=============================
.. meta::
    :author: Bernhard R. Fischer
    :created: 2009-12-04
    :thread: http://zzz.i2p/topics/453
    :lastupdated: 2009-12-04
    :status: Dead

.. contents::


Overview
========

This proposal is about adding support for DNS reverse lookups to I2P.


Current Translation Mechanism
=============================

GarliCat (GC) performs name translation for setting up connections to other GC
nodes. This name translation is just a recoding of the binary representation of
an address into the Base32 encoded form. Thus, translation works back and
forth.

Those addresses are chosen to be 80 bits long. This is because Tor uses 80 bit
long values for addressing its hidden services. Thus, OnionCat (which is GC for
Tor) works with Tor without further intervention.

Unfortunately (in respect to this addressing scheme), I2P uses 256 bit long
values for addressing of its services. As already mentioned, GC transcodes
between binary and Base32 encoded form. Due to the nature of GC being a layer 3
VPN, in its binary representation the addresses are defined to be IPv6
addresses which have a total length of 128 bit. Obviously, 256 bit long I2P
addresses do not fit into.

Thus, a second step of name translation becomes necessary:
IPv6 address (binary) -1a-> Base32 address (80 bits) -2a-> I2P address (256 bits)
-1a- ... GC translation
-2a- ... I2P hosts.txt lookup

The current solution is to let the I2P router do the work. This is accomplished
by insertion of the 80 bit Base32 address and its destination (the I2P address)
as a name/value pair into the hosts.txt or privatehosts.txt file of the I2P
router.

This basically works but it depends on a naming service which (IMHO) itself is
in a state of development and not mature enough (especially in respect to name
distribution).


A Scalable Solution
===================

I suggest to change the stages of addressing in respect to I2P (and maybe also
for Tor) in that way that GC does reverse lookups on the IPv6 addresses using
the regular DNS protocol. The reverse zone shall directly contain the 256 bit
I2P address in its Base32 encoded form. This changes the lookup mechanism to a
single step thereby adding further advantages.
IPv6 address (binary) -1b-> I2P address (256 bits)
-1b- ... DNS reverse lookup

DNS lookups within the Internet are known to be information leaks in respect to
anonymity. Thus, those lookups have to be carried out within I2P. This implies
that several DNS services should be around within I2P. As DNS queries are
usually performed by using the UDP protocol, GC itself is needed for data
transport because it does carry UDP packets which I2P natively does not.

Further advantages are associated with DNS:
1) It is a well-known standard protocol, hence, it is continously improved and
many tools (clients, servers, libraries,...) exist.
2) It is a distributed system. It supports the name space being hosted on
serveral servers in parallel by default.
3) It supports cryptography (DNSSEC) which enables authentication of resource
records. This could directly be tied with the keys of a destination.


Future Opportunities
====================

It may be possible that this naming service can also be used to do forward
lookups. This is translating hostnames into I2P addresses and/or IPv6
addresses. But this kind of lookup needs additional investigation because those
lookups are usually done by the locally installed resolver library which uses
regular Internet name servers (e.g. as specified in /etc/resolv.conf on
Unix-like systems). This is different from the reverse lookups of GC that I
explained above.
A further opportunity could be that the I2P address (destination) gets
registered automatically when creating a GC inbound tunnnel. This would greatly
improve the usability.
