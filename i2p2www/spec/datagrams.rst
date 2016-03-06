======================
Datagram Specification
======================
.. meta::
    :lastupdated: July 2014
    :accuratefor: 0.9.14

.. contents::


Overview
========

See [DATAGRAMS]_ for an overview of the Datagrams API.


.. _raw:

Non-Repliable Datagrams
=======================

Non-repliable datagrams have no 'from' address and are not authenticated.  They
are also called "raw" datagrams.  Strictly speaking, they are not "datagrams"
at all, they are just raw data.  They are not handled by the datagram API.
However, SAM and the I2PTunnel classes support "raw datagrams".

Format
------

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----//
  | payload...
  +----+----+----+----+----//

  length: 0 - unlimited (see notes)
{% endhighlight %}

Notes
-----

The practical length is limited by lower layers of protocols - the tunnel
message spec [TUNMSG]_ limits messages to about 61.2 KB and the transports
[TRANSPORT]_ currently limit messages to about 32 KB, although this may be
raised in the future.


.. _repliable:

Repliable Datagrams
===================

Repliable datagrams contain a 'from' address and a signature. These add at
least 427 bytes of overhead.

Format
------

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  | from                                  |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +                                       +
  |                                       |
  |                                       |
  +----+----+----+----+----+----+----+----+
  | signature                             |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  | payload...
  +----+----+----+----//


  from :: a `Destination`
          length: 387+ bytes
          The originator and signer of the datagram

  signature :: a `Signature`
               Signature type must match the signing public key type of $from
               length: 40+ bytes, as implied by the Signature type.
               For the default DSA_SHA1 key type:
                  The DSA `Signature` of the SHA-256 hash of the payload.
               For other key types:
                  The `Signature` of the payload.
               The signature may be verified by the signing public key of $from

  payload ::  The data
              Length: 0 to ~31.5 KB (see notes)

  Total length: Payload length + 427+
{% endhighlight %}

Notes
-----

* The practical length is limited by lower layers of protocols - the transports
  [TRANSPORT]_ currently limit messages to about 32 KB, so the data length here
  is limited to about 31.5 KB.

* See important notes about the reliability of large datagrams [DATAGRAMS]_. For
  best results, limit the payload to about 10 KB or less.

* Signatures for types other than DSA_SHA1 were redefined in release 0.9.14.


References
==========

.. [DATAGRAMS]
    {{ site_url('docs/api/datagrams', True) }}

.. [TRANSPORT]
    {{ site_url('docs/transport', True) }}

.. [TUNMSG]
    {{ spec_url('tunnel-message') }}#notes
