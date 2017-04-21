=======================
Blocklist in SU3 Format
=======================
.. meta::
    :author: psi, zzz
    :created: 2016-11-23
    :thread: http://zzz.i2p/topics/2192
    :lastupdated: 2016-11-23
    :status: Open

.. contents::


Overview
========

This proposal is to distribute blocklist updates in a separate su3 file.


Motivation
==========

Without this, the blocklist is only updated in the release.
This format could be used in various router implementations.


Design
======

Define the format to be wrapped in an su3 file.
Allow blocking by IP or router hash.
Routers may subscribe to a URL, or import a file obtained by other means.
The su3 file contains a signature which must be verifed on import.


Specification
=============

To be added to the router update specification page.

Define new content type BLOCKLIST (5).
Define new file type TXT_GZ (4) (.txt.gz format).
Entries are one per line, either a literal IPv4 or IPv6 address,
or a 44-character base64-encoded router hash.
Support for blocking with a net mask, e.g. x.y.0.0/16, is optional.
To unblock an entry, precede it with a '!'.
Comments start with a '#'.


Migration
=========

n/a



See Also
========

Proposal 129
