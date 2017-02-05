=====================
Introducer Expiration
=====================
.. meta::
    :author: zzz
    :created: 2017-02-05
    :thread: http://zzz.i2p/topics/2230
    :lastupdated: 2017-02-05
    :status: Open

.. contents::


Overview
========

Introducers expire after a certain time, but that info isn't published in the Router Info.
Routers must currently use heuristics to estimate when an introducer is no longer valid.


Motivation
==========

Improve success rate for introductions.


Design
======

Include new parameters in a SSU Router Address containing introducers.


Specification
=============

In a SSU Router Address containing introducers, the publisher may optionally include expiration times for each introducer.
The expiration is specified as iexpX=nnnnnnnnnn where X is the introducer number (0-2)
and nnnnnnnnnn is the time in seconds (not ms) since the epoch.

Each expiration must be greater than the publish date of the Router Info,
and less than 6 hours after the publish date of the Router Info.

Publishing routers and introducers should attempt to keep the introducer valid until expiration,
however there is no way for them to guarantee this.

Routers should not use a published introducer after its expiration.

Example: iexp0=1486309470


Migration
=========

No issues. Implementation is optional.
Backwards compatibility is assured, as older routers will ignore unknown parameters.



See Also
========

Trac ticket 1352
