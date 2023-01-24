===================================
Datagram2 Protocol
===================================
.. meta::
    :author: zzz
    :created: 2023-01-24
    :thread: http://zzz.i2p/topics/3540
    :lastupdated: 2023-01-24
    :status: Open
    :target: 0.9.60

.. contents::



Overview
========

Pulled out from [Prop123]_ as a separate proposal. Copied from [Prop123]_:

Offline signatures cannot be verified in the repliable datagram processing.
Needs a flag to indicate offline signed but there's no place to put a flag.

Will require a completely new protocol number and format.
to be added to the [DATAGRAMS]_ specification.
Let's call it "Datagram2".


Motivation
==========

Left over from LS2 work otherwise completed in 2019.



Design
======

Define new protocol 19 - Repliable datagram with options.

New signature specification.



Specification
=============

Add Datagram2 to [DATAGRAMS]_ as follows:


Format
-------

Preliminary, copied from [Prop123]_:

.. raw:: html

  {% highlight %}
From (387+ bytes)

  Flags (2 bytes)
  Bit order: 15 14 ... 3 2 1 0
  Bit 0: If 0, no offline keys; if 1, offline keys
  Bits 1-15: set to 0 for compatibility with future uses
  If flag indicates offline keys, the offline signature section:

  Expires timestamp
  (4 bytes, big endian, seconds since epoch, rolls over in 2106)

  Transient sig type (2 bytes, big endian)

  Transient signing public key (length as implied by sig type)

  Signature of expires timestamp, transient sig type,
  and public key, by the destination public key,
  length as implied by destination public key sig type.
  This section can, and should, be generated offline.

  Payload

  Signature
{% endhighlight %}



Signatures
----------

TBD

Prelude: "DatagramProtocol" ?




SAM
---

Add STYLE=DATAGRAM2



Security Analysis
=================




Notes
=====



Compatibility
===============

None


Migration
=========

Each UDP application must separately detect support and migrate.

Bittorrent DHT: Needs extension flag probably,
e.g. i2p_dg2, coordinate with BiglyBT

Bittorrent UDP Announces [Prop160]_: Design in from the beginning?
Coorindate with BiglyBT, i2psnark, zzzot

Bote: Unlikely

Streamr: Just switch, nobody's using it

SAM UDP apps: None known


References
==========

.. [DATAGRAMS]
    {{ spec_url('datagrams') }}

.. [I2CP]
    {{ spec_url('i2cp') }}

.. [Prop123]
    {{ proposal_url('123') }}

.. [Prop160]
    {{ proposal_url('160') }}

.. [BT-SPEC]
    {{ site_url('docs/applications/bittorrent', True) }}
