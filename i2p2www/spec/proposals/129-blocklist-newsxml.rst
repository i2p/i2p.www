======================
Blocklist in News Feed
======================
.. meta::
    :author: zzz
    :created: 2016-11-23
    :thread: http://zzz.i2p/topics/2191
    :lastupdated: 2016-12-02
    :status: Closed

.. contents::


Overview
========

This proposal is to distribute blocklist updates in the news file,
which is distributed in signed su3 format.
Implemented in 0.9.28.


Motivation
==========

Without this, the blocklist is only updated in the release.
Uses existing news subscription.
This format could be used in various router implementations, but only the Java router
uses the news subscription now.


Design
======

Add a new section to the news.xml file.
Allow blocking by IP or router hash.
The section will have its own time stamp.
Allow for unblocking of previously-blocked entries.

Include a signature of the section, to be specified.
The signature will cover the time stamp.
The signature must be verifed on import.
The signer will be specified and may be different from the su3 signer.
Routers may use a different trust list for the blocklist.


Specification
=============

Now on the router update specification page.

Entries are either a literal IPv4 or IPv6 address,
or a 44-character base64-encoded router hash.
IPv6 addresses may be in abbreviated format (containing "::").
Support for blocking with a net mask, e.g. x.y.0.0/16, is optional.
Support for host names is optional.


Migration
=========

Routers that don't support this will ignore the new XML section.


See Also
========

Proposal 130
