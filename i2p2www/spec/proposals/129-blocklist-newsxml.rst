======================
Blocklist in News Feed
======================
.. meta::
    :author: zzz
    :created: 2016-11-23
    :thread: http://zzz.i2p/topics/2191
    :lastupdated: 2016-11-23
    :status: Open

.. contents::


Overview
========

This proposal is to distribute blocklist updates in the news file.


Motivation
==========

Without this, the blocklist is only updated in the release.
Uses existing news subscription.
This format could be used in various router implementations, but only the Java router
uses the news subscription now.


Design
======

Add a new section to the news.xml.
Allow blocking by IP or router hash.
Include a signature of the section, to be specified.
The signature must be verifed on import.


Specification
=============

To be added to the router update specification page.

Entries are either a literal IPv4 or IPv6 address,
or a 44-character base64-encoded router hash.
Support for blocking with a net mask, e.g. x.y.0.0/16, is optional.


Migration
=========

Routers that don't support this will ignore the new XML section.


See Also
========

Proposal 130
