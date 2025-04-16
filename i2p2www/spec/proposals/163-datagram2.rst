===================================
Datagram2 Protocol
===================================
.. meta::
    :author: zzz, orignal, drzed, eyedeekay
    :created: 2023-01-24
    :thread: http://zzz.i2p/topics/3540
    :lastupdated: 2025-04-16
    :status: Closed
    :target: 0.9.67

.. contents::


Status
======

Approved at review 2025-04-15.
Changes incorporated into specs.
Not yet supported in any known implenentations.
Target implementation for Java I2P is API 0.9.67.
Check implementation documentation for status.



Overview
========

Pulled out from [Prop123]_ as a separate proposal.

Offline signatures cannot be verified in the repliable datagram processing.
Needs a flag to indicate offline signed but there's no place to put a flag.

Will require a completely new I2CP protocol number and format,
to be added to the [DATAGRAMS]_ specification.
Let's call it "Datagram2".


Goals
=====

- Add support for offline signatures
- Add replay resistance
- Add flavor without signatures
- Add flags and options fields for extensibility


Non-Goals
=========

Full end-to-end protocol support for congestion control, etc.
That would be build on top of, or an alternative to, Datagram2, which is a low-level protocol.
It would not make sense to design a high-performance protocol solely atop
Datagram2, because of the from field and signature overhead.
Any such protocol should do an initial handshake with Datagram2 and then
switch to RAW datagrams.


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
              Length: 0 to about 31.5 KB (see notes)

  Total length: Payload length + 423+
{% endhighlight %}



Design
======

- Define new protocol 19 - Repliable datagram with options.
- Define new protocol 20 - Repliable datagram without signature.
- Add flags field for offline signatures and future expansion
- Move signature after the payload for easier processing
- New signature specification different from repliable datagram or streaming, so that
  signature verification will fail if interpreted as repliable datagram or streaming.
  This is accomplished by moving the signature after the payload,
  and by including the destination hash in the signature function.
- Add replay prevention for datagrams, as was done in [Prop164]_ for streaming.
- Add section for arbitrary options
- Reuse offline signature format from [Common]_ and [Streaming]_.
- Offline signature section must be before the variable-length
  payload and signature sections, as it specifies the length
  of the signature.


Specification
=============

Protocol
--------

The new I2CP protocol number for Datagram2 is 19.
Add it as PROTO_DATAGRAM2 to [I2CP]_.

The new I2CP protocol number for Datagram3 is 20.
Add it as PROTO_DATAGRAM2 to [I2CP]_.


Datagram2 Format
----------------

Add Datagram2 to [DATAGRAMS]_ as follows:

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  |                                       |
  ~            from                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  flags  |     options (optional)      |
  +----+----+                             +
  ~                                       ~
  ~                                       ~
  +----+----+----+----+----+----+----+----+
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
           Bit 4: If 0, no options; if 1, options mapping is included
           Bit 5: If 0, no offline sig; if 1, offline signed
           Bits 15-6: unused, set to 0 for compatibility with future uses

  options :: (2+ bytes if present)
           If flag indicates options are present, a `Mapping`
           containing arbitrary text options

  offline_signature ::
               If flag indicates offline keys, the offline signature section,
               as specified in the Common Structures Specification,
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
              Length: 0 to about 61 KB (see notes)

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

Total length: minimum 433 + payload length;
typical length for X25519 senders and without offline signatures:
457 + payload length.
Note that the message will typically be compressed with gzip at the I2CP layer,
which will result in significant savings if the from destination is compressible.

Note: The offline signature format is the same as in the Common Structures spec [Common]_ and [Streaming]_.

Signatures
----------

The signature is over the following fields.

- Prelude: The 32-byte hash of the target destination (not included in the datagram)
- flags
- options (if present)
- offline_signature (if present)
- payload

In repliable datagram, for the DSA_SHA1 key type, the signature was over the
SHA-256 hash of the payload, not the payload itself; here, the signature is
always over the fields above (NOT the hash), regardless of key type.


ToHash Verification
-------------------

Receivers must verify the signature (using their destination hash)
and discard the datagram on failure, for replay prevention.


Datagram3 Format
----------------

Add Datagram3 to [DATAGRAMS]_ as follows:

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  |                                       |
  ~            fromhash                   ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  flags  |     options (optional)      |
  +----+----+                             +
  ~                                       ~
  ~                                       ~
  +----+----+----+----+----+----+----+----+
  |                                       |
  ~            payload                    ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  fromhash :: a `Hash`
              length: 32 bytes
              The originator of the datagram

  flags :: (2 bytes)
           Bit order: 15 14 ... 3 2 1 0
           Bits 3-0: Version: 0x03 (0 0 1 1)
           Bit 4: If 0, no options; if 1, options mapping is included
           Bits 15-5: unused, set to 0 for compatibility with future uses

  options :: (2+ bytes if present)
           If flag indicates options are present, a `Mapping`
           containing arbitrary text options

  payload ::  The data
              Length: 0 to about 61 KB (see notes)

{% endhighlight %}

Total length: minimum 34 + payload length.



SAM
---

Add STYLE=DATAGRAM2 and STYLE=DATAGRAM3 to the SAMv3 specification.
Update the information on offline signatures.


Overhead
--------

This design adds 2 bytes of overhead to repliable datagrams for flags.
This is acceptable.



Security Analysis
=================

Including the target hash in the signature should be effective at preventing replay attacks.

The Datagram3 format lacks signatures, so the sender cannot be verified,
and replay attacks are possible. Any required validation must be done at the application layer,
or by the router at the ratchet layer.



Notes
=====

- The practical length is limited by lower layers of protocols - the tunnel
  message spec [TUNMSG]_ limits messages to about 61.2 KB and the transports
  [TRANSPORT]_ currently limit messages to about 64 KB, so the data length here
  is limited to about 61 KB.
- See important notes about the reliability of large datagrams [API]_. For
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

.. [Common]
    {{ spec_url('common-structures') }}

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

.. [Streaming]
    {{ spec_url('streaming') }}

.. [TRANSPORT]
    {{ site_url('docs/transport', True) }}

.. [TUNMSG]
    {{ spec_url('tunnel-message') }}#notes

