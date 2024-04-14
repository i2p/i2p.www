===================================
Datagram2 Protocol
===================================
.. meta::
    :author: zzz
    :created: 2023-01-24
    :thread: http://zzz.i2p/topics/3540
    :lastupdated: 2024-04-14
    :status: Open
    :target: 0.9.64

.. contents::



Overview
========

Pulled out from [Prop123]_ as a separate proposal.

Offline signatures cannot be verified in the repliable datagram processing.
Needs a flag to indicate offline signed but there's no place to put a flag.

Will require a completely new I2CP protocol number and format,
to be added to the [DATAGRAMS]_ specification.
Let's call it "Datagram2".


Motivation
==========

Left over from LS2 work otherwise completed in 2019.

The first application to use Datagram2 is expected to be
bittorrent UDP announces, as implemented in i2psnark and zzzot,
see [Prop160]_.


Repliable Datagram Spec
========================

For reference,
following is a review of the specification for repliable datagrams,
copied from [Datagrams]_.
The standard I2CP protocol number for repliable datagrams is PROTO_DATAGRAM (17).

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
              Length: 0 to ~63 KB (see notes)

  Total length: Payload length + 427+
{% endhighlight %}



Design
======

- Define new protocol 19 - Repliable datagram with options.
- Add flags field for offline signatures and future expansion
- Move signature after the payload for easier processing
- New signature specification different from repliable datagram or streaming, so that
  signature verification will fail if interpreted as repliable datagram or streaming.
  This is accomplished by moving the signature after the payload,
  and by adding a prelude to the signature function.
- Add replay prevention as in [Prop164]_ for streaming.
- Offline signature section must be before the variable-length
  payload and signature sections, as it specifies the length
  of the signature.


Specification
=============

Protocol
--------

The new I2CP protocol number for Datagram2 is 19.
Add it as PROTO_DATAGRAM2 to [I2CP]_.


Format
-------

Add Datagram2 to [DATAGRAMS]_ as follows:

.. raw:: html

  {% highlight %}
  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  |                                       |
  ~            from                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  flags  |       tohash      |         |
  +----+----+----+----+----+----+         +
  |                                       |
  ~     offline_signature (optional)      ~
  ~   expires, sigtype, pubkey, offsig    ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  ~            payload                    ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                                       |
  ~            signature                  ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  from :: a `Destination`
          length: 387+ bytes
          The originator and (unless offline signed) signer of the datagram

  flags :: (2 bytes)
           Bit order: 15 14 ... 3 2 1 0
           Bits 3-0: Version: 0x02 (0 0 1 0)
           Bit 4: If 0, no offline sig; if 1, offline sig
           Bits 15-5: unused, set to 0 for compatibility with future uses

  tohash :: (4 bytes)
            The first 4 bytes of the target destination, for replay prevention

  offline_signature ::
               If flag indicates offline keys, the offline signature section,
               with the following 4 fields. Length: varies by online and offline
               sig types, typically 102 bytes for Ed25519
               This section can, and should, be generated offline.

  expires :: Expires timestamp
             (4 bytes, big endian, seconds since epoch, rolls over in 2106)

  sigtype :: Transient sig type (2 bytes, big endian)

  pubkey :: Transient signing public key (length as implied by sig type),
            typically 32 bytes for Ed25519 sig type.

  offsig :: a `Signature`
            Signature of expires timestamp, transient sig type,
            and public key, by the destination public key,
            length: 40+ bytes, as implied by the Signature type, typically
            64 bytes for Ed25519 sig type.

  payload ::  The data
              Length: 0 to ~63 KB (see notes)

  signature :: a `Signature`
               Signature type must match the signing public key type of $from
               (if no offline signature) or the transient sigtype
               (if offline signed)
               length: 40+ bytes, as implied by the Signature type, typically
               64 bytes for Ed25519 sig type.
               The `Signature` of the payload and other fields as specified below.
               The signature is verified by the signing public key of $from
               (if no offline signature) or the transient pubkey
               (if offline signed)

{% endhighlight %}



Signatures
----------

The signature is over the following fields.

- Prelude: "DatagramProtocol" ? (not included in the datagram)
- flags
- tohash
- offline_signature (if present)
- payload

In repliable datagram, for the DSA_SHA1 key type, the signature was over the
SHA-256 hash of the payload, not the payload itself; here, the signature is
always over the fields above (NOT the hash), regardless of key type.


SAM
---

Add STYLE=DATAGRAM2 to the SAMv3 specification.
Update the information on offline signatures.


Overhead
--------

This design adds 6 bytes of overhead to repliable datagrams; 2 for flags and 4 for replay prevention.
This is acceptable.



Security Analysis
=================

Four bytes for the hash prefix should be sufficient?



Notes
=====

* The practical length is limited by lower layers of protocols - the transports
  [TRANSPORT]_ currently limit messages to about 64 KB, so the data length here
  is limited to about 63 KB.

* See important notes about the reliability of large datagrams [API]_. For
  best results, limit the payload to about 10 KB or less.




Compatibility
===============

None. Applications must be rewritten to route Datagram2 I2CP messages
based on protocol and/or port.
Datagram2 messages that are misrouted and interpreted as
Repliable datagram or streaming messages will fail based on signature, format, or both.



Migration
=========

Each UDP application must separately detect support and migrate.
The most prominent UDP application is bittorrent.

Bittorrent
----------

Bittorrent DHT: Needs extension flag probably,
e.g. i2p_dg2, coordinate with BiglyBT

Bittorrent UDP Announces [Prop160]_: Design in from the beginning.
Coordindate with BiglyBT, i2psnark, zzzot

Others
------

Bote: Unlikely to migrate, not actively maintained

Streamr: Nobody's using it, no migration planned

SAM UDP apps: None known


References
==========

.. [API]
    {{ site_url('docs/api/datagrams', True) }}

.. [BT-SPEC]
    {{ site_url('docs/applications/bittorrent', True) }}

.. [DATAGRAMS]
    {{ spec_url('datagrams') }}

.. [I2CP]
    {{ site_url('docs/protocol/i2cp', True) }}

.. [Prop123]
    {{ proposal_url('123') }}

.. [Prop160]
    {{ proposal_url('160') }}

.. [Prop164]
    {{ proposal_url('164') }}

.. [TRANSPORT]
    {{ site_url('docs/transport', True) }}

