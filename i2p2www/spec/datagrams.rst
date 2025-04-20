======================
Datagram Specification
======================
.. meta::
    :category: Protocols
    :lastupdated: 2025-04
    :accuratefor: 0.9.66

.. contents::


Overview
========

See [DATAGRAMS]_ for an overview of the Datagrams API.

The following types are defined. The standard protocol numbers
are listed, however any other protocol numbers may be used other than
the streaming protocol number (6), application-specific.


=========  ========  ==========  ==============  ==================  =====
Type       Protocol  Repliable?  Authenticated?  Replay Prevention?  As Of	
=========  ========  ==========  ==============  ==================  =====
Raw          18         no             no               no
Datagram1    17        yes            yes               no
Datagram2    19        yes            yes               yes          0.9.66
Datagram3    20        yes             no               no           0.9.66
=========  ========  ==========  ==============  ==================  =====


Support for Datagram2 and Datagram3 in various router and library implementations
is TBD. Check the documentation for those implementations.



Datagram Type Identification
----------------------------

The four datagram types do not share a common header with the protocol
version in the same place. Packets cannot be identified by type
based on their content. When using multiple types on the same session,
or a single type together with streaming, applications must use
protocol numbers and/or I2CP/SAM ports to route incoming packets to the
right place. Using standard protocol numbers will make this easier.
Leaving the protocol number unset (0 or PROTO_ANY), even for a datagram-only
application, is not recommended as it increases the chance of routing
errors and makes upgrades to a multi-protocol application harder.
Version fields in Datagram 2 and 3 are provided only as
an additional check for routing errors and future changes.



Application Design
------------------

All uses of datagrams are application-specific.

As authenticated datagrams carry substantial overhead,
a typical application uses both authenticated and non-authenticated datagrams.
A typical design is to send single authenticated datagram
containing a token from the client to the server.
The server replies with an unauthenticated datagram containing the same token.
Any subsequent communication, before token timeout, uses raw datagrams.

Applications send and receive datagrams using protocol and port numbers
via the I2CP API [I2CP]_ or SAMv3 [SAMv3]_.

Datagrams are, of course, unreliable. Applications must design for unreliable
delivery. Within I2P, delivery is reliable hop-to-hop
if the next hop is reachable, as the NTCP2 and SSU2
transports provide reliablity. However, end-to-end delivery is
not reliable, as I2NP messages may be dropped within any hop due
to queue limits, expirations, timeouts, bandwidth limits,
or unreachable next-hops.


Datagram Size
-------------

The nominal size limit for I2NP messages, including datagrams, is 64 KB.
Garlic and tunnel message overhead reduce somewhat.

However, all I2NP messages must be fragmented into 1 KB tunnel messages.
The drop probability of a n KB I2NP message is the exponential function of
the drop probability of a single tunnel message, p ** n.
As fragmentation results in a burst of tunnel messages,
actual drop probability is much higher than the exponential
function would imply, due to queue limits and active queue management
(AQM, CoDel or similar) in router implementations.

Recommended typical max size to ensure reliable delivery is a few KB,
or at the most 10 KB.
With careful analysis of overhead sizes at all protocol layers (except transport),
developers should set a max payload size
that will fit precisely in one, two, or three tunnel messages.
This will maximize efficiency and reliability.
Overhead at various layers includes the gzip header,
I2NP header, garlic message header, garlic encryption,
tunnel message header, tunnel message fragmentation headers,
and others.
See streaming MTU calculations in Proposal 144 [Prop144]_
and ConnectionOptions.java in the Java I2P source for examples.



SAM Considerations
------------------

Applications send and receive datagrams using protocol and port numbers
via the I2CP API or SAM. Specifying protocol and port numbers
via SAM requires SAM v3.2 or higher.
Using both datagrams and streaming (UDP and TCP) on the same SAM session (tunnels)
requires SAM v3.3 or higher.
Using multiple datagram types on the same SAM session (tunnels)
requires SAM v3.3 or higher.
SAM v3.3 is only supported by the Java I2P router at this time.

SAM support for Datagram2 and Datagram3 in various router and library implementations
is TBD. Check the documentation for those implementations.

Note that sizes over a typical 1500 byte network MTU will prohibit
SAM applications from transporting unfragmented packets to/from
the SAM server, if the application and server are on separate computers.
Typically, this is not the case, they are both on localhost,
where the MTU is 65536 or higher.
If a SAM application is expected to be separated on a different
computer from the server, max payload for a repliable datagram is
slightly under 1 KB.



PQ Considerations
-----------------

If the MLDSA portion of the Post-Quantum proposal [Prop169]_ is implemented,
overhead will increase substantially.
The size of a destination + signature will increase from 391 + 64 = 455 bytes
to a minimum of 3739 for MLDSA44 and a maximum of 7226 for MLDSA87.
The practical effects of this are to be determined.
Datagram3, with authentication provided by the router, may be a solution.




.. _raw:

Raw (Non-Repliable) Datagrams
=============================

Non-repliable datagrams have no 'from' address and are not authenticated.  They
are also called "raw" datagrams.  Strictly speaking, they are not "datagrams"
at all, they are just raw data.  They are not handled by the datagram API.
However, SAM and the I2PTunnel classes support "raw datagrams".

The standard I2CP protocol number for raw datagrams is PROTO_DATAGRAM_RAW (18).

The format is not specified here, it is defined by the application.
For completeness, we include a picture of the format below.


Format
------

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----//
  | payload...
  +----+----+----+----+----//

  length: 0 - about 64 KB (see notes)
{% endhighlight %}

Notes
-----

The practical length is limited by both overhead at various layers and reliability.





.. _repliable:

Datagram1 (Repliable)
=====================

Repliable datagrams contain a 'from' address and a signature. These add at
least 427 bytes of overhead.

The standard I2CP protocol number for repliable datagrams is PROTO_DATAGRAM (17).

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
              Length: 0 to about 63 KB (see notes)

  Total length: Payload length + 427+
{% endhighlight %}

Notes
-----

* The practical length is limited by both overhead at various layers and reliability.

* See important notes about the reliability of large datagrams [DATAGRAMS]_. For
  best results, limit the payload to about 10 KB or less.

* Signatures for types other than DSA_SHA1 were redefined in release 0.9.14.

* The format does not support inclusion of an offline signature block
  for LS2 (proposal 123). A new protocol with flags must be defined for that.



.. _datagram2:

Datagram2
=========

The Datagram2 format is as specified in Proposal 163 [Prop163]_.
The I2CP protocol number for Datagram2 is 19.

Datagram2 is intended as a replacement for Datagram1.
It adds the following features to Datagram1:

- Replay prevention
- Offline signature support
- Flags and options fields for extensibility

Note that the signature calculation algorithm for Datagram2
is substantially different than for Datagram1.


Format
------


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




.. _datagram3:

Datagram3
=========

The Datagram3 format is as specified in Proposal 163 [Prop163]_.
The I2CP protocol number for Datagram3 is 20.

Datagram3 is intended as an enhanced version of raw datagrams.
It adds the following features to raw datagrams:

- Repliability
- Flags and options fields for extensibility

Datagram3 is NOT authenticated.
In a future proposal, authentication may be provided by
the router's ratchet layer, and authentication status
would be passed to the client.



Format
------

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





References
==========

.. [Common]
    {{ spec_url('common-structures') }}

.. [DATAGRAMS]
    {{ site_url('docs/api/datagrams', True) }}

.. [I2CP]
    {{ site_url('docs/protocol/i2cp', True) }}

.. [Prop144]
    {{ proposal_url('144') }}

.. [Prop163]
    {{ proposal_url('163') }}

.. [Prop169]
    {{ proposal_url('163') }}

.. [SAMv3]
    {{ site_url('docs/api/samv3') }}

.. [Streaming]
    {{ spec_url('streaming') }}

.. [TRANSPORT]
    {{ site_url('docs/transport', True) }}

.. [TUNMSG]
    {{ spec_url('tunnel-message') }}#notes
