============================================
Floodfill Support for Experimental Sig Types
============================================
.. meta::
    :author: zzz
    :created: 2017-03-31
    :thread: http://zzz.i2p/topics/2279
    :lastupdated: 2017-03-31
    :status: Open

.. contents::


Overview
========

For sig types in the experimental range (65280-65534),
floodfills should accept netdb stores without checking the signature.

This will support testing of new sig types.


Motivation
==========

The GOST proposal 134 has revealed two issues with the previously-unused experimental sig type range.

First, since sig types in the experimental range cannot be reserved, they may be used for
multiple sig types at once.

Second, unless a lease set with an experimental sig type can be stored at a floodfill,
the new sig type is difficult to fully test or use on a trial basis.



Design
======

Floodfills should accept, and flood, LS stores with sig types in the experimental range,
without checking the signature. Support for RI stores is TBD, and may have more security implications.



Specification
=============

Ref: http://i2p-projekt.i2p/en/docs/spec/common-structures
http://i2p-projekt.i2p/en/docs/spec/i2np

For sig types in the experimental range, a floodfill should accept and flood netdb
stores without checking the signature.

To prevent spoofing of non-experimental routers and destinations, a floodfill
should never accept a store of an experimental sig type that has a hash
collision with an existing netdb entry of a different sig type.
This prevents hijacking of a previous netdb entry.

Additionally, a floodfill should overwrite an experimental netdb entry
with a store of a non-experimental sig type that is a hash collision,
to prevent hijacking of a previously-absent hash.

Floodfills should assume the public key length is 256, or derive it from
the key certificate length, if longer. Some implementations may
not support longer lengths unless the sig type is informally reserved.


Migration
=========

Once this feature is supported, in a known router version,
experimental sig type netdb entries may be stored to floodfills of that version or higher.

If some router implementations do not support this feature, the netdb store
will fail, but that's the same as it is now.


Issues
======

There may be additional security implications, to be researched.

Some implementations may not support key lengths greater than 256,
as described above.


See Also
========

Proposal 134
Proposal 137
