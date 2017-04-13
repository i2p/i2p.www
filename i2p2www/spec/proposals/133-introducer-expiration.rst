=====================
Introducer Expiration
=====================
.. meta::
    :author: zzz
    :created: 2017-02-05
    :thread: http://zzz.i2p/topics/2230
    :lastupdated: 2017-04-13
    :status: Closed
    :target: 0.9.30
    :implementedin: 0.9.30

.. contents::


Overview
========

This proposal is about improving the success rate for introductions. See
[TRAC-TICKET]_.


Motivation
==========

Introducers expire after a certain time, but that info isn't published in the
[RouterInfo]_. Routers must currently use heuristics to estimate when an
introducer is no longer valid.


Design
======

In an SSU [RouterAddress]_ containing introducers, the publisher may optionally
include expiration times for each introducer.


Specification
=============

.. raw:: html

  {% highlight lang='dataspec' %}
iexp{X}={nnnnnnnnnn}

  X :: The introducer number (0-2)

  nnnnnnnnnn :: The time in seconds (not ms) since the epoch.
{% endhighlight %}

Notes
`````
* Each expiration must be greater than the publish date of the [RouterInfo]_,
  and less than 6 hours after the publish date of the RouterInfo.

* Publishing routers and introducers should attempt to keep the introducer valid
  until expiration, however there is no way for them to guarantee this.

* Routers should not use a published introducer after its expiration.

Example: ``iexp0=1486309470``


Migration
=========

No issues. Implementation is optional.
Backwards compatibility is assured, as older routers will ignore unknown parameters.



References
==========

.. [RouterAddress]
    {{ ctags_url('RouterAddress') }}

.. [RouterInfo]
    {{ ctags_url('RouterInfo') }}

.. [TRAC-TICKET]
    http://{{ i2pconv('trac.i2p2.i2p') }}/ticket/1352
