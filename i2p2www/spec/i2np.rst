==================
I2NP Specification
==================
.. meta::
    :lastupdated: January 2016
    :accuratefor: 0.9.24

.. contents::


Overview
========

The I2P Network Protocol (I2NP), which is sandwiched between I2CP and the
various I2P transport protocols, manages the routing and mixing of messages
between routers, as well as the selection of what transports to use when
communicating with a peer for which there are multiple common transports
supported.


.. _versions:

Protocol Versions
=================

All routers must publish their I2NP protocol version in the "router.version"
field in the RouterInfo properties.  This version field indicates their level
of support for various I2NP protocol features, and is not necessarily the
actual router version.

If alternative (non-Java) routers wish to publish any version information about
the actual router implementation, they must do so in another property.
Versions other than those listed below are allowed. Support will be determined
through a numeric comparison; for example, 0.9.13 implies support for 0.9.12
features.  Note that the "coreVersion" property is not used for determination
of the I2NP protocol version.

A basic summary of the I2NP protocol versions is as follows. For details, see
below.

==============  ================================================================
   Version      Required I2NP Features
==============  ================================================================
   0.9.18       DSM type bits 7-1 ignored

   0.9.16       RI key certs / ECDSA and EdDSA sig types

                Note: RSA sig types also supported as of this version, but
                currently unused

                DLM lookup types (DLM flag bits 3-2)

   0.9.15       Dest/LS key certs w/ EdDSA Ed25519 sig type (if floodfill)

   0.9.12       Dest/LS key certs w/ ECDSA P-256, P-384, and P-521 sig types (if
                floodfill)

                Note: RSA sig types also supported as of this version, but
                currently unused

                Nonzero expiration allowed in RouterAddress

   0.9.7        Encrypted DSM/DSRM replies supported (DLM flag bit 1) (if
                floodfill)

   0.9.6        Nonzero DLM flag bits 7-1 allowed

   0.9.3        Requires zero expiration in RouterAddress

   0.9          Supports up to 16 leases in a DSM LS store (6 previously)

   0.7.12       VTBM and VTBRM message support

   0.7.10       Floodfill supports encrypted DSM stores

0.7.9 or lower  All messages and features not listed above

   0.6.1.10     TBM and TBRM messages introduced

                Minimum version compatible with current network
==============  ================================================================

Note that there are also transport-related features and compatibility issues;
see the NTCP and SSU transport documentation for details.


.. _structures:

Common structures
=================

The following structures are elements of multiple I2NP messages.
They are not complete messages.

.. _struct-I2NPMessageHeader:

I2NP message header
-------------------

Description
```````````
Common header to all I2NP messages, which contains important information like a checksum, expiration date, etc.

Contents
````````
1 byte [Integer]_ specifying the type of this message, followed by a 4 byte
[Integer]_ specifying the message-id.  After that there is an expiration
[Date]_, followed by a 2 byte [Integer]_ specifying the length of the message
payload, followed by a [Hash]_, which is truncated to the first byte. After
that the actual message data follows.

.. raw:: html

  {% highlight lang='dataspec' %}
Standard (16 bytes):

  +----+----+----+----+----+----+----+----+
  |type|      msg_id       |  expiration
  +----+----+----+----+----+----+----+----+
                           |  size   |chks|
  +----+----+----+----+----+----+----+----+

  Short (SSU, 5 bytes):

  +----+----+----+----+----+
  |type| short_expiration  |
  +----+----+----+----+----+

  type :: `Integer`
          length -> 1 byte
          purpose -> identifies the message type (see table below)

  msg_id :: `Integer`
            length -> 4 bytes
            purpose -> uniquely identifies this message (for some time at least)
                       This is usually a locally-generated random number, but
                       for outgoing tunnel build messages it may be derived from
                       the incoming message. See below.

  expiration :: `Date`
                8 bytes
                date this message will expire

  short_expiration :: `Integer`
                      4 bytes
                      date this message will expire (seconds since the epoch)

  size :: `Integer`
          length -> 2 bytes
          purpose -> length of the payload

  chks :: `Integer`
          length -> 1 byte
          purpose -> checksum of the payload
                     SHA256 hash truncated to the first byte

  data ::
          length -> $size bytes
          purpose -> actual message contents
{% endhighlight %}

Notes
`````
* When transmitted over [SSU]_, the 16-byte standard header is not used. Only a
  1-byte type and a 4-byte expiration in seconds is included. The message id
  and size are incorporated into various parts of the SSU data packet format.
  The checksum is not required since errors are caught in decryption.

* The standard header is also required for I2NP messages contained in other
  messages and structures (Data, TunnelData, TunnelGateway, and GarlicClove).
  As of release 0.8.12, to reduce overhead, checksum verification is disabled
  at some places in the protocol stack. However, for compatibility with older
  versions, checksum generation is still required. It is a topic for future
  research to determine points in the protocol stack where the far-end router's
  version is known and checksum generation can be disabled.

* The short expiration is unsigned and will wrap around on Feb. 7, 2106. As of
  that date, an offset must be added to get the correct time.

.. _struct-BuildRequestRecord:

BuildRequestRecord
------------------

Description
```````````
One Record in a set of multiple records to request the creation of one hop in
the tunnel. For more details see the tunnel overview [TUNNEL-IMPL]_ and the
tunnel creation specification [TUNNEL-CREATION]_.

Contents
````````
[TunnelId]_ to receive messages on, followed by the [Hash]_ of our
[RouterIdentity]_. After that the [TunnelId]_ and the [Hash]_ of the next
router's [RouterIdentity]_ follow.

Definition
``````````
ElGamal and AES encrypted:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | encrypted data...                     |
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  encrypted_data :: ElGamal and AES encrypted data
                    length -> 528

  total length: 528
{% endhighlight %}

ElGamal encrypted:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | toPeer                                |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  | encrypted data...                     |
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  toPeer :: First 16 bytes of the SHA-256 Hash of the peer's `RouterIdentity`
            length -> 16 bytes

  encrypted_data :: ElGamal-2048 encrypted data (see notes)
                    length -> 512

  total length: 528
{% endhighlight %}

Cleartext:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | receive_tunnel    | our_ident         |
  +----+----+----+----+                   +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                   +----+----+----+----+
  |                   | next_tunnel       |
  +----+----+----+----+----+----+----+----+
  | next_ident                            |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  | layer_key                             |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  | iv_key                                |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  | reply_key                             |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  | reply_iv                              |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |flag| request_time      | send_msg_id
  +----+----+----+----+----+----+----+----+
       |                                  |
  +----+                                  +
  |         29 bytes padding              |
  +                                       +
  |                                       |
  +                             +----+----+
  |                             |
  +----+----+----+----+----+----+

  receive_tunnel :: `TunnelId`
                    length -> 4 bytes

  our_ident :: `Hash`
               length -> 32 bytes

  next_tunnel :: `TunnelId`
                 length -> 4 bytes

  next_ident :: `Hash`
                length -> 32 bytes

  layer_key :: `SessionKey`
               length -> 32 bytes

  iv_key :: `SessionKey`
            length -> 32 bytes

  reply_key :: `SessionKey`
               length -> 32 bytes

  reply_iv :: data
              length -> 16 bytes

  flag :: `Integer`
          length -> 1 byte

  request_time :: `Integer`
                  length -> 4 bytes
                  Hours since the epoch, i.e. current time / 3600

  send_message_id :: `Integer`
                     length -> 4 bytes

  padding :: Data
             length -> 29 bytes
             source -> random

  total length: 222
{% endhighlight %}

Notes
`````
* In the 512-byte encrypted record, the ElGamal data contains bytes 1-256 and
  258-513 of the 514-byte ElGamal encrypted block [CRYPTO-ELG]_. The two
  padding bytes from the block (the zero bytes at locations 0 and 257) are
  removed.

* See the tunnel creation specification [TUNNEL-CREATION]_ for details on field
  contents.

.. _struct-BuildResponseRecord:

BuildResponseRecord
-------------------

.. raw:: html

  {% highlight lang='dataspec' %}
Encrypted:

  bytes 0-527 :: AES-encrypted record (note: same size as `BuildRequestRecord`)

  Unencrypted:

  +----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |                                       |
  +   SHA-256 Hash of following bytes     +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  | random data...                        |
  ~                                       ~
  |                                       |
  +                                  +----+
  |                                  | ret|
  +----+----+----+----+----+----+----+----+

  bytes 0-31   :: SHA-256 Hash of bytes 32-527
  bytes 32-526 :: random data
  byte  527    :: reply

  total length: 528
{% endhighlight %}

Notes
`````
* The random data field could, in the future, be used to return congestion or
  peer connectivity information back to the requestor.

* See the tunnel creation specification [TUNNEL-CREATION]_ for details on the
  reply field.

.. _struct-GarlicClove:
.. _Garlic Cloves:

GarlicClove
-----------

.. raw:: html

  {% highlight lang='dataspec' %}
Unencrypted:

  +----+----+----+----+----+----+----+----+
  | Delivery Instructions                 |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | I2NP Message                          |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |    Clove ID       |     Expiration
  +----+----+----+----+----+----+----+----+
                      | Certificate  |
  +----+----+----+----+----+----+----+

  Delivery Instructions :: as defined below
         Length varies but is typically 1, 33, or 37 bytes

  I2NP Message :: Any I2NP Message

  Clove ID :: 4 byte `Integer`

  Expiration :: `Date` (8 bytes)

  Certificate :: Always NULL in the current implementation (3 bytes total, all zeroes)
{% endhighlight %}

Notes
`````
* Cloves are never fragmented. When used in a Garlic Clove, the first bit of
  the Delivery Instructions flag byte specifies encryption. If this bit is 0,
  the clove is not encrypted. If 1, the clove is encrypted, and a 32 byte
  Session Key immediately follows the flag byte. Clove encryption is not fully
  implemented.

* See also the garlic routing specification [GARLIC]_.

* Maximum length is a function of the total length of all the cloves and the
  maximum length of the GarlicMessage.

* In the future, the certificate could possibly be used for a HashCash to "pay"
  for the routing.

* The message can be any I2NP message (including a GarlicMessage, although that
  is not used in practice). The messages used in practice are DataMessage,
  DeliveryStatusMessage, and DatabaseStoreMessage.

* The Clove ID is generally set to a random number on transmit and is checked
  for duplicates on receive (same message ID space as top-level Message IDs)

.. _struct-GarlicCloveDeliveryInstructions:

Garlic Clove Delivery Instructions
----------------------------------

This specification is for Delivery Instructions inside Garlic Cloves only.
Note that "Delivery Instructions" are also used inside Tunnel Messages, where
the format is significantly different.  See the Tunnel Message documentation
[TMDI]_ for details.  Do NOT use the following specification for Tunnel Message
Delivery Instructions!

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |flag|                                  |
  +----+                                  +
  |                                       |
  +       Session Key (optional)          +
  |                                       |
  +                                       +
  |                                       |
  +    +----+----+----+----+--------------+
  |    |                                  |
  +----+                                  +
  |                                       |
  +         To Hash (optional)            +
  |                                       |
  +                                       +
  |                                       |
  +    +----+----+----+----+--------------+
  |    |  Tunnel ID (opt)  |  Delay (opt)  
  +----+----+----+----+----+----+----+----+
       |
  +----+

  flag ::
         1 byte
         Bit order: 76543210
         bit 7: encrypted? Unimplemented, always 0
                  If 1, a 32-byte encryption session key is included
         bits 6-5: delivery type
                  0x0 = LOCAL, 0x01 = DESTINATION, 0x02 = ROUTER, 0x03 = TUNNEL
         bit 4: delay included?  Not fully implemented, always 0
                  If 1, four delay bytes are included
         bits 3-0: reserved, set to 0 for compatibility with future uses

  Session Key ::
         32 bytes
         Optional, present if encrypt flag bit is set.
         Unimplemented, never set, never present.

  To Hash ::
         32 bytes
         Optional, present if delivery type is DESTINATION, ROUTER, or TUNNEL
            If DESTINATION, the SHA256 Hash of the destination
            If ROUTER, the SHA256 Hash of the router
            If TUNNEL, the SHA256 Hash of the gateway router

  Tunnel ID :: `TunnelId`
         4 bytes
         Optional, present if delivery type is TUNNEL
         The destination tunnel ID

  Delay :: `Integer`
         4 bytes
         Optional, present if delay included flag is set
         Not fully implemented. Specifies the delay in seconds.

  Total length: Typical length is:
         1 byte for LOCAL delivery;
         33 bytes for ROUTER / DESTINATION delivery;
         37 bytes for TUNNEL delivery
{% endhighlight %}


Messages
========

==================================  =======
             Message                 Type
==================================  =======
DatabaseStore_                         1
DatabaseLookup_                        2
DatabaseSearchReply_                   3
DeliveryStatus_                        10
Garlic_                                11
TunnelData_                            18
TunnelGateway_                         19
Data_                                  20
TunnelBuild_                           21
TunnelBuildReply_                      22
VariableTunnelBuild_                   23
VariableTunnelBuildReply_              24
Reserved for experimental messages  224-254
Reserved for future expansion         255
==================================  =======

.. _msg-DatabaseStore:

DatabaseStore
-------------

Description
```````````
An unsolicited database store, or the response to a successful DatabaseLookup_ Message

Contents
````````
An uncompressed LeaseSet or a compressed RouterInfo

.. raw:: html

  {% highlight lang='dataspec' %}
with reply token:
  +----+----+----+----+----+----+----+----+
  | SHA256 Hash as key                    |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |type| reply token       | reply_tunnelId
  +----+----+----+----+----+----+----+----+
       | SHA256 of the gateway RouterInfo |
  +----+                                  +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +    +----+----+----+----+----+----+----+
  |    | data ...
  +----+-//

  with reply token == 0:
  +----+----+----+----+----+----+----+----+
  | SHA256 Hash as key                    |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |type|         0         | data ...
  +----+----+----+----+----+-//

  key ::
      32 bytes
      SHA256 hash

  type ::
       1 byte
       type identifier
       bit 0:
               0    `RouterInfo`
               1    `LeaseSet`
       bits 7-1:
              Through release 0.9.17, must be 0
              As of release 0.9.18, ignored, reserved for future options, set to 0 for compatibility

  reply token ::
              4 bytes
              If greater than zero, a `DeliveryStatusMessage`
              is requested with the Message ID set to the value of the Reply Token.
              A floodfill router is also expected to flood the data to the closest floodfill peers
              if the token is greater than zero.

  reply_tunnelId ::
                 4 byte `TunnelId`
                 Only included if reply token &gt; 0
                 This is the `TunnelId` of the inbound gateway of the tunnel the response should be sent to
                 If $reply_tunnelId is zero, the reply is sent directy to the reply gateway router.

  reply gateway ::
                32 bytes
                Hash of the `RouterInfo` entry to reach the gateway
                Only included if reply token &gt; 0
                If $reply_tunnelId is nonzero, this is the router hash of the inbound gateway
                of the tunnel the response should be sent to.
                If $reply_tunnelId is zero, this is the router hash the response should be sent to.

  data ::
       If type == 0, data is a 2-byte `Integer` specifying the number of bytes that follow,
                     followed by a gzip-compressed `RouterInfo`.
       If type == 1, data is an uncompressed `LeaseSet`.
{% endhighlight %}

Notes
`````
* For security, the reply fields are ignored if the message is received down a
  tunnel.

* The key is the "real" hash of the RouterIdentity or Destination, NOT the
  routing key.

.. _msg-DatabaseLookup:

DatabaseLookup
--------------

Description
```````````
A request to look up an item in the network database.  The response is either a
DatabaseStore_ or a DatabaseSearchReply_.

Contents
````````
.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | SHA256 hash as the key to look up     |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  | SHA256 hash of the routerInfo         |
  + who is asking, or the gateway to      +
  | send the reply to                     |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |flag| reply_tunnelId    | size    |    |
  +----+----+----+----+----+----+----+    +
  | SHA256 of $key1 to exclude            |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                  +----+
  |                                  |    |
  +----+----+----+----+----+----+----+    +
  | SHA256 of $key2 to exclude            |
  +                                       +
  ~                                       ~
  +                                  +----+
  |                                  |    |
  +----+----+----+----+----+----+----+    +
  |                                       |
  +                                       +
  |   Session key if reply encryption     |
  +   was requested                       +
  |                                       |
  +                                  +----+
  |                                  |tags|
  +----+----+----+----+----+----+----+----+
  |                                       |
  +                                       +
  |   Session tags if reply encryption    |
  +   was requested                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+

  key ::
      32 bytes
      SHA256 hash of the object to lookup

  from ::
       32 bytes
       if deliveryFlag == 0, the SHA256 hash of the routerInfo entry this
                             request came from (to which the reply should be
                             sent)
       if deliveryFlag == 1, the SHA256 hash of the reply tunnel gateway (to
                             which the reply should be sent)

  flags ::
       1 byte
       bit order: 76543210
       bit 0: deliveryFlag
               0  => send reply directly
               1  => send reply to some tunnel
       bit 1: encryptionFlag
               through release 0.9.5, must be set to 0
               as of release 0.9.6, ignored
               as of release 0.9.7:
               0  => send unencrypted reply
               1  => send AES encrypted reply using enclosed key and tag
       bits 3-2: lookup type flags
               through release 0.9.5, must be set to 00
               as of release 0.9.6, ignored
               as of release 0.9.16:
               00  => normal lookup, return `RouterInfo` or `LeaseSet` or
                      `DatabaseSearchReplyMessage`
               01  => LS lookup, return `LeaseSet` or
                      `DatabaseSearchReplyMessage`
               10  => RI lookup, return `RouterInfo` or
                      `DatabaseSearchReplyMessage`
               11  => exploration lookup, return `DatabaseSearchReplyMessage`
                      containing non-floodfill routers only (replaces an
                      excludedPeer of all zeroes)
       bits 7-4:
               through release 0.9.5, must be set to 0
               as of release 0.9.6, ignored, set to 0 for compatibility with
               future uses and with older routers

  reply_tunnelId ::
                 4 byte `TunnelID`
                 only included if deliveryFlag == 1
                 tunnelId of the tunnel to send the reply to

  size ::
       2 byte `Integer`
       valid range: 0-512
       number of peers to exclude from the `DatabaseSearchReplyMessage`

  excludedPeers ::
                $size SHA256 hashes of 32 bytes each (total $size*32 bytes)
                if the lookup fails, these peers are requested to be excluded
                from the list in the `DatabaseSearchReplyMessage`.
                if excludedPeers includes a hash of all zeroes, the request is
                exploratory, and the `DatabaseSearchReplyMessage` is requested
                to list non-floodfill routers only.

  reply_key ::
       32 byte `SessionKey`
       only included if encryptionFlag == 1, only as of release 0.9.7

  tags ::
       1 byte `Integer`
       valid range: 1-32 (typically 1)
       the number of reply tags that follow
       only included if encryptionFlag == 1, only as of release 0.9.7

  reply_tags ::
       one or more 32 byte `SessionTag`s (typically one)
       only included if encryptionFlag == 1, only as of release 0.9.7
{% endhighlight %}

Notes
`````
* Prior to 0.9.16, the key may be for a RouterInfo or LeaseSet, as they are in
  the same key space, and there was no flag to request only a particular type
  of data.

* Encryption flag, reply key, and reply tags as of release 0.9.7.

* Encrypted replies are only useful when the response is through a tunnel.

* The number of included tags could be greater than one if alternative DHT
  lookup strategies (for example, recursive lookups) are implemented.

* The lookup key and exclude keys are the "real" hashes, NOT routing keys.

.. _msg-DatabaseSearchReply:

DatabaseSearchReply
-------------------

Description
```````````
The response to a failed DatabaseLookup_ Message

Contents
````````
A list of router hashes closest to the requested key

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | SHA256 hash as query key              |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  | num| peer_hashes                      |
  +----+                                  +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +    +----+----+----+----+----+----+----+
  |    | from                             |
  +----+                                  +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +    +----+----+----+----+----+----+----+
  |    |
  +----+

  key ::
      32 bytes
      SHA256 of the object being searched

  num ::
      1 byte `Integer`
      number of peer hashes that follow, 0-255

  peer_hashes ::
            $num SHA256 hashes of 32 bytes each (total $num*32 bytes)
            SHA256 of the `RouterIdentity` that the other router thinks is close
            to the key

  from ::
       32 bytes
       SHA256 of the `RouterInfo` of the router this reply was sent from
{% endhighlight %}

Notes
`````
* The 'from' hash is unauthenticated and cannot be trusted.

* The returned peer hashes are not necessarily closer to the key than the
  router being queried.

* Typical number of hashes returned: 3

* The lookup key, peer hashes, and from hash are "real" hashes, NOT routing
  keys.

.. _msg-DeliveryStatus:

DeliveryStatus
--------------

Description
```````````
A simple message acknowledgment. Generally created by the message originator,
and wrapped in a Garlic Message with the message itself, to be returned by the
destination.

Contents
````````
The ID of the delivered message, and the creation or arrival time.

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+----+----+----+----+
  | msg_id            |           time_stamp                  |
  +----+----+----+----+----+----+----+----+----+----+----+----+

  msg_id :: `Integer`
         4 bytes
         unique ID of the message we deliver the DeliveryStatus for (see
         `I2NPMessageHeader` for details)

  time_stamp :: `Date`
               8 bytes
               time the message was successfully created or delivered
{% endhighlight %}

Notes
`````
* It appears that the time stamp is always set by the creator to the current
  time. However there are several uses of this in the code, and more may be
  added in the future.

* This message is also used as a session established confirmation in SSU
  [SSU-ED]_. In this case, the message ID is set to a random number, and the
  "arrival time" is set to the current network-wide ID, which is 2 (i.e.
  0x0000000000000002).

.. _msg-Garlic:

Garlic
------

Description
```````````
Used to wrap multiple encrypted I2NP Messages

Contents
````````
When decrypted, a series of `Garlic Cloves`_.

Encrypted:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |      length       | data              |
  +----+----+----+----+                   +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  length ::
         4 byte `Integer`
         number of bytes that follow 0 - 64 KB

  data ::
       $length bytes
       ElGamal encrypted data
{% endhighlight %}
Unencrypted data:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | num|  clove 1                         |
  +----+                                  +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |         clove 2 ...                   |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | Certificate  |   Message_ID      |     
  +----+----+----+----+----+----+----+----+
            Expiration               |
  +----+----+----+----+----+----+----+

  num ::
       1 byte `Integer` number of `GarlicClove`s to follow

  clove ::  a `GarlicClove`

  Certificate :: always NULL in the current implementation (3 bytes total, all zeroes)

  Message_ID :: 4 byte `Integer`

  Expiration :: `Date` (8 bytes)
{% endhighlight %}

Notes
`````
* When unencrypted, data contains one or more `Garlic Cloves`_.

* The AES encrypted block is padded to a minimum of 128 bytes; with the 32-byte
  Session Tag the minimum size of the encrypted message is 160 bytes; with the
  4 length bytes the minimum size of the Garlic Message is 164 bytes.

* Actual max length is less than 64 KB; see [I2NP]_.

* See also the ElGamal/AES specification [ELG-AES]_.

* See also the garlic routing specification [GARLIC]_.

* The 128 byte minimum size of the AES encrypted block is not currently
  configurable, however the minimum size of a DataMessage in a GarlicClove in a
  GarlicMessage, with overhead, is 128 bytes anyway. A configurable option to
  increase the minimum size may be added in the future.

* The message ID is generally set to a random number on transmit and appears to
  be ignored on receive.

* In the future, the certificate could possibly be used for a HashCash to "pay"
  for the routing.

.. _msg-TunnelData:

TunnelData
----------

Description
```````````
A message sent from a tunnel's gateway or participant to the next participant
or endpoint.  The data is of fixed length, containing I2NP messages that are
fragmented, batched, padded, and encrypted.

Contents
````````
.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |     tunnnelID     | data              |
  +----+----+----+----+                   |
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +                   +----+----+----+----+
  |                   |
  +----+----+----+----+

  tunnelId ::
           4 byte `TunnelId`
           identifies the tunnel this message is directed at

  data ::
       1024 bytes
       payload data.. fixed to 1024 bytes
{% endhighlight %}

Notes
`````
* The I2NP message ID for this message is set to a new random number at each
  hop.

* See also the Tunnel Message Specification [TUNNEL-MSG]_

.. _msg-TunnelGateway:

TunnelGateway
-------------

Description
```````````
Wraps another I2NP message to be sent into a tunnel at the tunnel's inbound gateway.

Contents
````````
.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+-//
  | tunnelId          | length  | data...
  +----+----+----+----+----+----+----+-//

  tunnelId ::
           4 byte `TunnelId`
           identifies the tunnel this message is directed at

  length ::
         2 byte `Integer`
         length of the payload

  data ::
       $length bytes
       actual payload of this message
{% endhighlight %}

Notes
`````
* The payload is an I2NP message with a standard 16-byte header.

.. _msg-Data:

Data
----

Description
```````````
Used by Garlic Messages and Garlic Cloves to wrap arbitrary data.

Contents
````````
A length Integer, followed by opaque data.

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+-//-+
  | length            | data... |
  +----+----+----+----+----+-//-+

  length ::
         4 bytes
         length of the payload

  data ::
       $length bytes
       actual payload of this message
{% endhighlight %}

Notes
`````
* This message contains no routing information and will never be sent
  "unwrapped". It is only used inside `Garlic` messages.

.. _msg-TunnelBuild:

TunnelBuild
-----------

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | Record 0 ...                          |

  |                                       |
  +----+----+----+----+----+----+----+----+
  | Record 1 ...                          |

  ~ .....                                 ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | Record 7 ...                          |

  |                                       |
  +----+----+----+----+----+----+----+----+

  Just 8 `BuildRequestRecord`s attached together
  record size: 528 bytes
  total size: 8*528 = 4224 bytes
{% endhighlight %}

Notes
`````
* See also the tunnel creation specification [TUNNEL-CREATION]_.

* The I2NP message ID for this message must be set according to the tunnel
  creation specification.

* While this message is rarely seen in today's network, having been replaced by
  the `VariableTunnelBuild` message, it may still be used for very long tunnels,
  and has not been deprecated. Routers must implement.

.. _msg-TunnelBuildReply:

TunnelBuildReply
----------------

.. raw:: html

  {% highlight lang='dataspec' %}
Same format as `TunnelBuildMessage`, with `BuildResponseRecord`s
{% endhighlight %}

Notes
`````
* See also the tunnel creation specification [TUNNEL-CREATION]_.

* The I2NP message ID for this message must be set according to the tunnel
  creation specification.

* While this message is rarely seen in today's network, having been replaced by
  the `VariableTunnelBuildReply` message, it may still be used for very long
  tunnels, and has not been deprecated. Routers must implement.

.. _msg-VariableTunnelBuild:

VariableTunnelBuild
-------------------

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | num| BuildRequestRecords...
  +----+----+----+----+----+----+----+----+

  Same format as `TunnelBuildMessage`, except for the addition of a $num field
  in front and $num number of `BuildRequestRecord`s instead of 8

  num ::
         1 byte `Integer`
         Valid values: 1-8

  record size: 528 bytes
  total size: 1+$num*528
{% endhighlight %}

Notes
`````
* This message was introduced in router version 0.7.12, and may not be sent to
  tunnel participants earlier than that version.

* See also the tunnel creation specification [TUNNEL-CREATION]_.

* The I2NP message ID for this message must be set according to the tunnel
  creation specification.

* Typical number of records in today's network is 5.

.. _msg-VariableTunnelBuildReply:

VariableTunnelBuildReply
------------------------

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | num| BuildResponseRecords...
  +----+----+----+----+----+----+----+----+

  Same format as `VariableTunnelBuildMessage`, with `BuildResponseRecord`s.
{% endhighlight %}

Notes
`````
* This message was introduced in router version 0.7.12, and may not be sent to
  tunnel participants earlier than that version.

* See also the tunnel creation specification [TUNNEL-CREATION]_.

* The I2NP message ID for this message must be set according to the tunnel
  creation specification.

* Typical number of records in today's network is 5.


References
==========

.. [CRYPTO-ELG]
    {{ site_url('docs/how/cryptography', True) }}#elgamal

.. [Date]
    {{ ctags_url('Date') }}

.. [ElG-AES]
    {{ site_url('docs/how/elgamal-aes', True) }}

.. [GARLIC]
    {{ site_url('docs/how/garlic-routing', True) }}

.. [Hash]
    {{ ctags_url('Hash') }}

.. [I2NP]
    {{ site_url('docs/protocol/i2np', True) }}

.. [Integer]
    {{ ctags_url('Integer') }}

.. [RouterIdentity]
    {{ ctags_url('RouterIdentity') }}

.. [SSU]
    {{ site_url('docs/transport/ssu', True) }}

.. [SSU-ED]
    {{ site_url('docs/transport/ssu', True) }}#establishDirect

.. [TMDI]
    {{ ctags_url('TunnelMessageDeliveryInstructions') }}

.. [TUNNEL-CREATION]
    {{ spec_url('tunnel-creation') }}

.. [TUNNEL-MSG]
    {{ spec_url('tunnel-message') }}

.. [TUNNEL-IMPL]
    {{ site_url('docs/tunnels/implementation', True) }}

.. [TunnelId]
    {{ ctags_url('TunnelId') }}
