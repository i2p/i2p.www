========================================
Floodfill Support for Optional Sig Types
========================================
.. meta::
    :author: zzz
    :created: 2017-03-31
    :thread: http://zzz.i2p/topics/2280
    :lastupdated: 2017-11-12
    :status: Open

.. contents::


Overview
========

Add a way for floodfills to advertise support for optional sig types.
This will provide a way to support new sig types over the long-term,
even if not all implementations support them.



Motivation
==========

The GOST proposal 134 has revealed several issues with the previously-unused experimental sig type range.

First, since sig types in the experimental range cannot be reserved, they may be used for
multiple sig types at once.

Second, unless a router info or lease set with an experimental sig type can be stored at a floodfill,
the new sig type is difficult to fully test or use on a trial basis.

Third, if proposal 136 is implemented, this is not secure, as anybody can overwrite an entry.

Fourth, implementing a new sig type can be a large development effort.
It may be difficult to convince developers for all router implementations to add support for a new
sig type in time for any particular release. Developer's time and motivations may vary.

Fifth, if GOST uses a sig type in the standard range, there's still no way to know if a particular
floodfill supports GOST.



Design
======

All floodfills must support sig types DSA (0), ECDSA (1-3), and EdDSA (7).

For any other sig type in the standard (non-experimental) range, a floodfill may
advertise support in its router info properties.



Specification
=============

Ref: http://i2p-projekt.i2p/en/docs/spec/common-structures
http://i2p-projekt.i2p/en/docs/spec/i2np

A router that supports an optional sig type shall add "sigTypes" property
to its published router info, with comma-separated sig type numbers.
The sig types will be in sorted numerical order.
Mandatory sig types (0-4,7) shall not be included.

For example: sigTypes=9,10

Routers that support optional sig types must only store, lookup, or flood,
to floodfills that advertise support for that sig type.



Migration
=========

Not applicable.
Only routers that support an optional sig type must implement.



Issues
======

If there are not a lot of floodfills supporting the sig type, they may be difficult to find.

It may not be necessary to require ECDSA 384 and 521 (sig types 2 and 3) for all floodfills.
These types are not widely used.

Similar issues will need to be addressed with non-zero encryption types,
which has not yet been formally proposed.


Notes
=====

NetDB stores of unknown sig types that are not in the experimental range will continue
to be rejected by floodfills, as the signature cannot be verified.


See Also
========

Proposal 134
Proposal 136
