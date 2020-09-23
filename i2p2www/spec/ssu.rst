==========================
SSU Protocol Specification
==========================
.. meta::
    :category: Transports
    :lastupdated: 2020-09
    :accuratefor: 0.9.48

.. contents::


Overview
========

See [SSU]_ for an overview of the SSU transport.


.. _dh:

DH Key Exchange
===============

The initial 2048-bit DH key exchange is described on the SSU page [SSU-KEYS]_.
This exchange uses the same shared prime as that used for I2P's ElGamal
encryption [CRYPTO-ELG]_.


.. _header:

Message Header
==============

All UDP datagrams begin with a 16 byte MAC (Message Authentication Code) and a
16 byte IV (Initialization Vector) followed by a variable-size payload
encrypted with the appropriate key.  The MAC used is HMAC-MD5, truncated to 16
bytes, while the key is a full 32 byte AES256 key.  The specific construct of
the MAC is the first 16 bytes from::

  HMAC-MD5(encryptedPayload + IV + (payloadLength ^ protocolVersion ^ ((netid - 2) << 8)), macKey)

where '+' means append and '^' means exclusive-or.

The IV is generated randomly for each packet.  The encryptedPayload is the
encrypted version of the message starting with the flag byte
(encrypt-then-MAC).  The payloadLength used in the MAC is a 2 byte unsigned
integer, big endian.  Note that protocolVersion is 0, so the exclusive-or is a no-op.  The
macKey is either the introduction key or is constructed from the exchanged DH
key (see details below), as specified for each message below.

**WARNING** - the HMAC-MD5-128 used here is non-standard, see [CRYPTO-HMAC]_
for details.

The payload itself (that is, the message starting with the flag byte) is
AES256/CBC encrypted with the IV and the sessionKey, with replay prevention
addressed within its body, explained below.

The protocolVersion is a 2 byte unsigned integer, big endian, and is currently set to 0.
Peers using a different protocol version will not be able to communicate with
this peer, though earlier versions not using this flag are.

The exclusive OR of ((netid - 2) << 8) is used to quickly identify cross-network connections.
The netid is a 2 byte unsigned integer, big endian, and is currently set to 2.
As of 0.9.42. See proposal 147 for more information.
As the current network ID is 2, this is a no-op for the current network and is backward compatible.
Any connections from test networks should have a different ID and will fail the HMAC.




HMAC Specification
------------------

* Inner padding: 0x36...
* Outer padding: 0x5C...
* Key: 32 bytes
* Hash digest function: MD5, 16 bytes
* Block size: 64 bytes
* MAC size: 16 bytes
* Example C implementations:

  * hmac.h in i2pd [I2PD-SRC]_
  * I2PHMAC.cpp in i2pcpp [I2PCPP-SRC]_.

* Example Java implementation:

  * I2PHMac.java in I2P [I2P-SRC]_

Session Key Details
-------------------

The 32-byte session key is created as follows:

1. Take the exchanged DH key, represented as a positive minimal-length
   BigInteger byte array (two's complement big-endian)

2. If the most significant bit is 1 (i.e. array[0] & 0x80 != 0), prepend a 0x00
   byte, as in Java's BigInteger.toByteArray() representation

3. If the byte array is greater than or equal to 32 bytes, use the first (most
   significant) 32 bytes

4. If the byte array is less than 32 bytes, append 0x00 bytes to extend to 32
   bytes. *Very unlikely - See note below.*

MAC Key Details
---------------

The 32-byte MAC key is created as follows:

1. Take the exchanged DH key byte array, prepended with a 0x00 byte if
   necessary, from step 2 in the Session Key Details above.

2. If that byte array is greater than or equal to 64 bytes, the MAC key is
   bytes 33-64 from that byte array.

3. If that byte array is less than 64 bytes, the MAC key is the SHA-256 Hash of
   that byte array. *As of release 0.9.8. See note below.*

Important note
``````````````
Code before release 0.9.8 was broken and did not correctly handle DH key byte
arrays between 32 and 63 bytes (steps 3 and 4 above) and the connection will
fail.  As these cases didn't ever work, they were redefined as described above
for release 0.9.8, and the 0-32 byte case was redefined as well.  Since the
nominal exchanged DH key is 256 bytes, the chances of the mininimal
representation being less than 64 bytes is vanishingly small.

Header Format
-------------

Within the AES encrypted payload, there is a minimal common structure to the
various messages - a one byte flag and a four byte sending timestamp (seconds
since the unix epoch).

The header format is:

.. raw:: html

  {% highlight lang='dataspec' %}
Header: 37+ bytes
  Encryption starts with the flag byte.
  +----+----+----+----+----+----+----+----+
  |                  MAC                  |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                   IV                  |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |flag|        time       |              |
  +----+----+----+----+----+              +
  | keying material (optional)            |
  +                                       +
  |                                       |
  ~                                       ~
  |                                       |
  +                        +----+----+----+
  |                        |#opt|         |
  +----+----+----+----+----+----+         +
  | #opt extended option bytes (optional) |
  ~                                       ~
  ~                                       ~
  +----+----+----+----+----+----+----+----+
{% endhighlight %}

The flag byte contains the following bitfields:

.. raw:: html

  {% highlight %}
  Bit order: 76543210 (bit 7 is MSB)

    bits 7-4: payload type
       bit 3: If 1, rekey data is included. Always 0, unimplemented
       bit 2: If 1, extended options are included. Always 0 before release
              0.9.24.
    bits 1-0: reserved, set to 0 for compatibility with future uses
{% endhighlight %}

Without rekeying and extended options, the header size is 37 bytes.

.. _rekey:

Rekeying
--------

If the rekey flag is set, 64 bytes of keying material follow the timestamp.

When rekeying, the first 32 bytes of the keying material is fed into a SHA256
to produce the new MAC key, and the next 32 bytes are fed into a SHA256 to
produce the new session key, though the keys are not immediately used.  The
other side should also reply with the rekey flag set and that same keying
material.  Once both sides have sent and received those values, the new keys
should be used and the previous keys discarded.  It may be useful to keep the
old keys around briefly, to address packet loss and reordering.

NOTE: Rekeying is currently unimplemented.

.. _extend:

Extended Options
----------------

If the extended options flag is set, a one byte option size value is appended,
followed by that many extended option bytes. Extended options have always been
part of the specification, but were unimplemented until release 0.9.24. When
present, the option format is specific to the message type. See message
documentation below on whether extended options are expected for the given
message, and the specified format. While Java routers have always recognized the
flag and options length, other implementations have not. Therefore, do not send
extended options to routers older than release 0.9.24.


Padding
=======

All messages contain 0 or more bytes of padding.  Each message must be padded
to a 16 byte boundary, as required by the AES256 encryption layer
[CRYPTO-AES]_.

Through release 0.9.7, messages were only padded to the next 16 byte boundary,
and messages not a multiple of 16 bytes could possibly be invalid.

As of release 0.9.7, messages may be padded to any length as long as the
current MTU is honored.  Any extra 1-15 padding bytes beyond the last block of
16 bytes cannot be encrypted or decrypted and will be ignored.  However, the
full length and all padding is included in the MAC calculation.

As of release 0.9.8, transmitted messages are not necessarily a multiple of 16
bytes.  The SessionConfirmed message is an exception, see below.


Keys
====

Signatures in the SessionCreated and SessionConfirmed messages are generated
using the [SigningPublicKey]_ from the [RouterIdentity]_ which is distributed
out-of-band by publishing in the network database, and the associated
[SigningPrivateKey]_.

Through release 0.9.15, the signature algorithm was always DSA, with a 40 byte
signature.

As of release 0.9.16, the signature algorithm may be specified by a a
[KeyCertificate]_ in Bob's [RouterIdentity]_.

Both introduction keys and session keys are 32 bytes, and are defined by the
Common structures specification [SESSIONKEY]_.  The key used for the MAC and
encryption is specified for each message below.

Introduction keys are delivered through an external channel (the network
database), where they have traditionally been identical to the router Hash through release 0.9.47,
but may be random as of release 0.9.48.


Notes
=====

IPv6
----

The protocol specification allows both 4-byte IPv4 and 16-byte IPv6 addresses.
SSU-over-IPv6 is supported as of version 0.9.8.  See the documentation of
individual messages below for details on IPv6 support.

.. _time:

Timestamps
----------

While most of I2P uses 8-byte [Date]_ timestamps with millisecond resolution,
SSU uses 4-byte unsigned integer timestamps with one-second resolution. Because
these values are unsigned, they will not roll over until February 2106.


Messages
========

There are 10 messages (payload types) defined:

====  ================  =====
Type      Message       Notes
====  ================  =====
  0   SessionRequest
  1   SessionCreated
  2   SessionConfirmed
  3   RelayRequest
  4   RelayResponse
  5   RelayIntro
  6   Data
  7   PeerTest
  8   SessionDestroyed  Implemented as of 0.8.9
 n/a  HolePunch
====  ================  =====

.. _sessionRequest:

SessionRequest (type 0)
-----------------------

This is the first message sent to establish a session.

====================  ======================================================
**Peer:**             Alice to Bob
**Data:**             * 256 byte X, to begin the DH agreement
                      * 1 byte IP address size
                      * that many byte representation of Bob's IP address
                      * N bytes, currently uninterpreted
**Crypto Key used:**  Bob's introKey, as retrieved from the network database
**MAC Key used:**     Bob's introKey, as retrieved from the network database
====================  ======================================================

Message format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |         X, as calculated from DH      |
  ~                .  .  .                ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |size| that many byte IP address (4-16) |
  +----+----+----+----+----+----+----+----+
  | arbitrary amount of uninterpreted data|
  ~                .  .  .                ~
{% endhighlight %}

Typical size including header, in current implementation: 304 (IPv4) or 320
(IPv6) bytes (before non-mod-16 padding)

Extended options
````````````````
Note: Implemented in 0.9.24.

* Minimum length: 3 (option length byte + 2 bytes)

* Option length: 2 minimum

* 2 bytes flags:

.. raw:: html

  {% highlight lang='dataspec'%}
  Bit order: 15...76543210 (bit 15 is MSB)

        bit 0: 1 for Alice to request a relay tag from Bob in the
               `SessionCreated` response, 0 if Alice does not need a relay tag.
               Note that "1" is the default if no extended options are present
    bits 15-1: unused, set to 0 for compatibility with future uses
{% endhighlight %}

Notes
`````
* IPv4 and IPv6 addresses are supported.

* The uninterpreted data could possibly be used in the future for challenges.

.. _sessioncreated:

SessionCreated (type 1)
-----------------------

This is the response to a SessionRequest_.

====================  ==========================================================
**Peer:**             Bob to Alice
**Data:**             * 256 byte Y, to complete the DH agreement
	              * 1 byte IP address size
	              * that many byte representation of Alice's IP address
	              * 2 byte Alice's port number
                      * 4 byte relay (introduction) tag which Alice can publish
                        (else 0x00000000)
                      * 4 byte timestamp (seconds from the epoch) for use in the
                        DSA signature
                      * Bob's [Signature]_ of the critical exchanged data (X +
                        Y + Alice's IP + Alice's port + Bob's IP + Bob's port +
                        Alice's new relay tag + Bob's signed on time), encrypted
                        with another layer of encryption using the negotiated
                        sessionKey.  The IV is reused here. See notes for length
                        information.
                      * 0-15 bytes of padding of the signature, using random
                        data, to a multiple of 16 bytes, so that the signature +
                        padding may be encrypted with an additional layer of
                        encryption using the negotiated session key as part of
                        the DSA block.
                      * N bytes, currently uninterpreted
**Crypto Key used:**  Bob's introKey, with an additional layer of encryption
                      over the 40 byte signature and the following 8 bytes
                      padding.
**MAC Key used:**     Bob's introKey
====================  ==========================================================

Message format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |         Y, as calculated from DH      |
  ~                .  .  .                ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |size| that many byte IP address (4-16) |
  +----+----+----+----+----+----+----+----+
  | Port (A)| public relay tag  |  signed
  +----+----+----+----+----+----+----+----+
    on time |                             |
  +----+----+                             +
  |                                       |
  +                                       +
  |             signature                 |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +         +----+----+----+----+----+----+
  |         |   (0-15 bytes of padding) 
  +----+----+----+----+----+----+----+----+
            |                             |
  +----+----+                             +
  |           arbitrary amount            |
  ~        of uninterpreted data          ~
  ~                .  .  .                ~
{% endhighlight %}

Typical size including header, in current implementation: 368 bytes (IPv4 or
IPv6) (before non-mod-16 padding)

Notes
`````
* IPv4 and IPv6 addresses are supported.

* If the relay tag is nonzero, Bob is offering to act as an introducer for
  Alice. Alice may subsequently publish Bob's address and the relay tag in the
  network database.

* For the signature, Bob must use his external port, as that what Alice will
  use to verify. If Bob's NAT/firewall has mapped his internal port to a
  different external port, and Bob is unaware of it, the verification by Alice
  will fail.

* See the Keys_ section above for details on signatures. Alice already has
  Bob's public signing key, from the network database.

* Through release 0.9.15, the signature was always a 40 byte DSA signature and
  the padding was always 8 bytes. As of release 0.9.16, the signature type and
  length are implied by the type of the [SigningPublicKey]_ in Bob's
  [RouterIdentity]_. The padding is as necessary to a multiple of 16 bytes.

* This is the only message that uses the sender's intro key. All others use the
  receiver's intro key or the established session key.

* Signed-on time appears to be unused or unverified in the current
  implementation.

* The uninterpreted data could possibly be used in the future for challenges.

* Extended options in the header: Not expected, undefined.

.. _sessionconfirmed:

SessionConfirmed (type 2)
-------------------------

This is the response to a SessionCreated_ message and the last step in
establishing a session.  There may be multiple SessionConfirmed messages
required if the Router Identity must be fragmented.

====================  ==========================================================
**Peer:**             Alice to Bob
**Data:**             * 1 byte identity fragment info::

                          Bit order: 76543210 (bit 7 is MSB)
                          bits 7-4: current identity fragment # 0-14
                          bits 3-0: total identity fragments (F) 1-15

                      * 2 byte size of the current identity fragment
                      * that many byte fragment of Alice's [RouterIdentity]_
                      * After the last identity fragment only:

                        * 4 byte signed-on time

                      * N bytes padding, currently uninterpreted
                      * After the last identity fragment only:

                        * The remaining bytes contain Alice's [Signature]_ of
                          the critical exchanged data (X + Y + Alice's IP +
                          Alice's port + Bob's IP + Bob's port + Alice's new
                          relay tag + Alice's signed on time). See notes for
                          length information.
**Crypto Key used:**  Alice/Bob sessionKey, as generated from the DH exchange
**MAC Key used:**     Alice/Bob MAC Key, as generated from the DH exchange
====================  ==========================================================

**Fragment 0 through F-2** (only if F > 1; currently unused, see notes below):

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |info| cursize |                        |
  +----+----+----+                        +
  |      fragment of Alice's full         |
  ~            Router Identity            ~
  ~                .  .  .                ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | arbitrary amount of uninterpreted data|
  ~                .  .  .                ~
{% endhighlight %}
 
**Fragment F-1 (last or only fragment):**

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |info| cursize |                        |
  +----+----+----+                        +
  |     last fragment of Alice's full     |
  ~            Router Identity            ~
  ~                .  .  .                ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  signed on time   |                   |
  +----+----+----+----+                   +
  |  arbitrary amount of uninterpreted    |
  ~      data, until the signature at     ~
  ~       end of the current packet       ~
  |  Packet length must be mult. of 16    |
  +----+----+----+----+----+----+----+----+
  +                                       +
  |                                       |
  +                                       +
  |             signature                 |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
{% endhighlight %}
 
Typical size including header, in current implementation: 480 bytes (before
non-mod-16 padding)

Notes
`````
* In the current implementation, the maximum fragment size is 512 bytes. This
  should be extended so that longer signatures will work without fragmentation.
  The current implementation does not correctly process signatures split across
  two fragments.

* The typical [RouterIdentity]_ is 387 bytes, so no fragmentation is ever
  necessary. If new crypto extends the size of the RouterIdentity, the
  fragmentation scheme must be tested carefully.

* There is no mechanism for requesting or redelivering missing fragments.

* The total fragments field F must be set identically in all fragments.

* See the Keys_ section above for details on DSA signatures.

* Signed-on time appears to be unused or unverified in the current
  implementation.

* Since the signature is at the end, the padding in the last or only packet
  must pad the total packet to a multiple of 16 bytes, or the signature will
  not get decrypted correctly. This is different from all the other message
  types, where the padding is at the end.

* Through release 0.9.15, the signature was always a 40 byte DSA signature. As
  of release 0.9.16, the signature type and length are implied by the type of
  the [SigningPublicKey]_ in Alice's [RouterIdentity]_. The padding is as
  necessary to a multiple of 16 bytes.

* Extended options in the header: Not expected, undefined.

.. _sessiondestroyed:

SessionDestroyed (type 8)
-------------------------

The SessionDestroyed message was implemented (reception only) in release 0.8.1,
and is sent as of release 0.8.9.

====================  ============================
**Peer:**             Alice to Bob or Bob to Alice
**Data:**             none
**Crypto Key used:**  Alice/Bob sessionKey
**MAC Key used:**     Alice/Bob MAC Key
====================  ============================

This message does not contain any data.  Typical size including header, in
current implementation: 48 bytes (before non-mod-16 padding)

Notes
`````
* Destroy messages received with the sender's or receiver's intro key will be
  ignored.

* Extended options in the header: Not expected, undefined.


.. _relayrequest:

RelayRequest (type 3)
---------------------

This is the first message sent from Alice to Bob to request an introduction to
Charlie.

====================  ==========================================================
**Peer:**             Alice to Bob
**Data:**             * 4 byte relay (introduction) tag, nonzero, as received by
                        Alice in the SessionCreated_ message from Bob
                      * 1 byte IP address size
                      * that many byte representation of Alice's IP address
                      * 2 byte port number (of Alice)
                      * 1 byte challenge size
                      * that many bytes to be relayed to Charlie in the intro
                      * Alice's 32-byte introduction key (so Bob can reply with
                        Charlie's info)
                      * 4 byte nonce of Alice's relay request
                      * N bytes, currently uninterpreted
**Crypto Key used:**  Bob's introKey, as retrieved from the network database (or
                      Alice/Bob sessionKey, if established)
**MAC Key used:**     Bob's introKey, as retrieved from the network database (or
                      Alice/Bob MAC Key, if established)
====================  ==========================================================
 
Message format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |      relay tag    |size| Alice IP addr
  +----+----+----+----+----+----+----+----+
       | Port (A)|size| challenge bytes   |
  +----+----+----+----+                   +
  |      to be delivered to Charlie       |
  +----+----+----+----+----+----+----+----+
  | Alice's intro key                     |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |       nonce       |                   |
  +----+----+----+----+                   +
  | arbitrary amount of uninterpreted data|
  ~                .  .  .                ~
{% endhighlight %}

Typical size including header, in current implementation: 96 bytes (no Alice IP
included) or 112 bytes (4-byte Alice IP included) (before non-mod-16 padding)

Notes
`````
* The IP address is only included if it is be different than the packet's
  source address and port. In the current implementation, the IP length is
  always 0 and the port is always 0, and the receiver should use the packet's
  source address and port.

* This message may be sent via IPv4 or IPv6. If IPv6, Alice must include her
  IPv4 address and port.

* If Alice includes her address/port, Bob may perform additional validation
  before continuing.

  * Prior to release 0.9.24, Java I2P rejected any address or port that was
    different from the connection.

* Challenge is unimplemented, challenge size is always zero

* There are no plans to implement relaying for IPv6.

* Prior to release 0.9.12, Bob's intro key was always used. As of release
  0.9.12, the session key is used if there is an established session between
  Alice and Bob. In practice, there must be an established session, as Alice
  will only get the nonce (introduction tag) from the session created message,
  and Bob will mark the introduction tag invalid once the session is destroyed.

* Extended options in the header: Not expected, undefined.

.. _relayresponse:

RelayResponse (type 4)
----------------------

This is the response to a RelayRequest_ and is sent from Bob to Alice.

====================  ==========================================================
**Peer:**             Bob to Alice
**Data:**             * 1 byte IP address size
                      * that many byte representation of Charlie's IP address
                      * 2 byte Charlie's port number
                      * 1 byte IP address size
                      * that many byte representation of Alice's IP address
                      * 2 byte Alice's port number
                      * 4 byte nonce sent by Alice
                      * N bytes, currently uninterpreted
**Crypto Key used:**  Alice's introKey, as received in the Relay Request (or
                      Alice/Bob sessionKey, if established)
**MAC Key used:**     Alice's introKey, as received in the Relay Request (or
                      Alice/Bob MAC Key, if established)
====================  ==========================================================

Message format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |size|    Charlie IP     | Port (C)|size|
  +----+----+----+----+----+----+----+----+
  |    Alice IP       | Port (A)|  nonce
  +----+----+----+----+----+----+----+----+
            |   arbitrary amount of       |
  +----+----+                             +
  |          uninterpreted data           |
  ~                .  .  .                ~
{% endhighlight %}

Typical size including header, in current implementation: 64 (Alice IPv4) or 80
(Alice IPv6) bytes (before non-mod-16 padding)

Notes
`````
* This message may be sent via IPv4 or IPv6.

* Alice's IP address/port are the apparent IP/port that Bob received the
  RelayRequest on (not necessarily the IP Alice included in the RelayRequest),
  and may be IPv4 or IPv6. Alice currently ignores these on receive.

* Charlie's IP address must be IPv4, as that is the address that Alice will
  send the SessionRequest to after the Hole Punch.

* There are no plans to implement relaying for IPv6.

* Prior to release 0.9.12, Alice's intro key was always used. As of release
  0.9.12, the session key is used if there is an established session between
  Alice and Bob.

* Extended options in the header: Not expected, undefined.

.. _relayintro:

RelayIntro (type 5)
-------------------

This is the introduction for Alice, which is sent from Bob to Charlie.

====================  =====================================================
**Peer:**             Bob to Charlie
**Data:**             * 1 byte IP address size
                      * that many byte representation of Alice's IP address
                      * 2 byte port number (of Alice)
                      * 1 byte challenge size
                      * that many bytes relayed from Alice
                      * N bytes, currently uninterpreted
**Crypto Key used:**  Bob/Charlie sessionKey
**MAC Key used:**     Bob/Charlie MAC Key
====================  =====================================================

Message format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |size|     Alice IP      | Port (A)|size|
  +----+----+----+----+----+----+----+----+
  |      that many bytes of challenge     |
  +                                       +
  |        data relayed from Alice        |
  +----+----+----+----+----+----+----+----+
  | arbitrary amount of uninterpreted data|
  ~                .  .  .                ~
{% endhighlight %}

Typical size including header, in current implementation: 48 bytes (before
non-mod-16 padding)

Notes
`````
* Alice's IP address is always 4 bytes in the current implementation, because
  Alice is trying to connect to Charlie via IPv4.

* This message must be sent via an established IPv4 connection, as that's the
  only way that Bob knows Charlie's IPv4 address to return to Alice in the
  RelayResponse_.

* Challenge is unimplemented, challenge size is always zero

* Extended options in the header: Not expected, undefined.

.. _data:

Data (type 6)
-------------

This message is used for data transport and acknowledgment.

====================  ==========================================================
**Peer:**             Any
**Data:**             * 1 byte flags::

                          Bit order: 76543210 (bit 7 is MSB)
                          bit 7: explicit ACKs included
                          bit 6: ACK bitfields included
                          bit 5: reserved
                          bit 4: explicit congestion notification (ECN)
                          bit 3: request previous ACKs
                          bit 2: want reply
                          bit 1: extended data included (unused, never set)
                          bit 0: reserved

                      * if explicit ACKs are included:

	                * a 1 byte number of ACKs
                        * that many 4 byte MessageIds being fully ACKed

                      * if ACK bitfields are included:

                        * a 1 byte number of ACK bitfields
                        * that many 4 byte MessageIds + a 1 or more byte ACK
                          bitfield. The bitfield uses the 7 low bits of each
                          byte, with the high bit specifying whether an
                          additional bitfield byte follows it (1 = true, 0 = the
                          current bitfield byte is the last).  These sequence of
                          7 bit arrays represent whether a fragment has been
                          received - if a bit is 1, the fragment has been
                          received.  To clarify, assuming fragments 0, 2, 5, and
                          9 have been received, the bitfield bytes would be as
                          follows::

                              byte 0:
                                 Bit order: 76543210 (bit 7 is MSB)
                                 bit 7: 1 (further bitfield bytes follow)
                                 bit 6: 0 (fragment 6 not received)
                                 bit 5: 1 (fragment 5 received)
                                 bit 4: 0 (fragment 4 not received)
                                 bit 3: 0 (fragment 3 not received)
                                 bit 2: 1 (fragment 2 received)
                                 bit 1: 0 (fragment 1 not received)
                                 bit 0: 1 (fragment 0 received)
                              byte 1:
                                 Bit order: 76543210 (bit 7 is MSB)
                                 bit 7: 0 (no further bitfield bytes)
                                 bit 6: 0 (fragment 13 not received)
                                 bit 5: 0 (fragment 12 not received)
                                 bit 4: 0 (fragment 11 not received)
                                 bit 3: 0 (fragment 10 not received)
                                 bit 2: 1 (fragment 9 received)
                                 bit 1: 0 (fragment 8 not received)
                                 bit 0: 0 (fragment 7 not received)

                      * If extended data included:

                        * 1 byte data size
                        * that many bytes of extended data (currently
                          uninterpreted)

                      * 1 byte number of fragments (can be zero)
                      * If nonzero, that many message fragments. Each fragment
                        contains:

                        * 4 byte messageId
                        * 3 byte fragment info::

                            Bit order: 76543210 (bit 7 is MSB)
                            bits 23-17: fragment # 0 - 127
                            bit 16: isLast (1 = true)
                            bits 15-14: unused, set to 0 for compatibility with
                                        future uses
                            bits 13-0: fragment size 0 - 16383

                        * that many bytes

                      * N bytes padding, uninterpreted
**Crypto Key used:**  Alice/Bob sessionKey
**MAC Key used:**     Alice/Bob MAC Key
====================  ==========================================================

Message format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |flag| (additional headers, determined  |
  +----+                                  +
  ~ by the flags, such as ACKs or         ~
  | bitfields                             |
  +----+----+----+----+----+----+----+----+
  |#frg|     messageId     |   frag info  |
  +----+----+----+----+----+----+----+----+
  | that many bytes of fragment data      |
  ~                .  .  .                ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |     messageId     |   frag info  |    |
  +----+----+----+----+----+----+----+    +
  | that many bytes of fragment data      |
  ~                .  .  .                ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  |     messageId     |   frag info  |    |
  +----+----+----+----+----+----+----+    +
  | that many bytes of fragment data      |
  ~                .  .  .                ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | arbitrary amount of uninterpreted data|
  ~                .  .  .                ~
{% endhighlight %}

Notes
`````
* The current implementation adds a limited number of duplicate acks for
  messages previously acked, if space is available.

* If the number of fragments is zero, this is an ack-only or keepalive message.

* The ECN feature is unimplemented, and the bit is never set.

* In the current implementation, the want reply bit is set when the number of
  fragments is greater then zero, and not set when there are no fragments.

* Extended data is unimplemented and never present.

* Reception of multiple fragments is supported in all releases. Transmission of
  multiple fragments is implemented in release 0.9.16.

* As currently implemented, maximum fragments is 64 (maximum fragment number =
  63).

* As currently implemented, maximum fragment size is of course less than the
  MTU.

* Take care not to exceed the maximum MTU even if there is a large number of
  ACKs to send.

* The protocol allows zero-length fragments but there's no reason to send them.

* In SSU, the data uses a short 5-byte I2NP header followed by the payload of
  the I2NP message instead of the standard 16-byte I2NP header. The short I2NP
  header consists only of the one-byte I2NP type and 4-byte expiration in
  seconds. The I2NP message ID is used as the message ID for the fragment. The
  I2NP size is assembled from the fragment sizes. The I2NP checksum is not
  required as UDP message integrity is ensured by decryption.

* Message IDs are not sequence numbers and are not consecutive. SSU does not
  guarantee in-order delivery. While we use the I2NP message ID as the SSU
  message ID, from the SSU protocol view, they are random numbers. In fact,
  since the router uses a single Bloom filter for all peers, the message ID
  must be an actual random number.

* Because there are no sequence numbers, there is no way to be sure an ACK was
  received. The current implementation routinely sends a large amount of
  duplicate ACKs. Duplicate ACKs should not be taken as an indication of
  congestion.

* ACK Bitfield notes: The receiver of a data packet does not know how many
  fragments are in the message unless it has received the last fragment.
  Therefore, the number of bitfield bytes sent in response may be less or more
  than the number of fragments divided by 7. For example, if the highest
  fragment the receiver has seen is number 4, only one byte is required to be
  sent, even if there may be 13 fragments total. Up to 10 bytes (i.e. (64 / 7)
  + 1) may be included for each message ID acked.

* Extended options in the header: Not expected, undefined.

.. _peertest:

PeerTest (type 7)
-----------------

See [SSU-PEERTEST]_ for details.

====================  ==========================================================
**Peer:**             Any
**Data:**             * 4 byte nonce
                      * 1 byte IP address size (may be zero)
                      * that many byte representation of Alice's IP address, if
                        size > 0
                      * 2 byte Alice's port number
                      * Alice's or Charlie's 32-byte introduction key
                      * N bytes, currently uninterpreted

**Crypto Key used:**  Listed in order of occurrence:

                      1. When sent from Alice to Bob: Alice/Bob sessionKey

                         (The protocol also permits Bob's introKey if Alice and
                         Bob do not have an established session, but in the
                         current implementation Alice always selects a Bob that
                         is established.  As of release 0.9.15, Bob will reject
                         PeerTests from peers without an established session.)

                      2. When sent from Bob to Charlie: Bob/Charlie sessionKey

                      3. When sent from Charlie to Bob: Bob/Charlie sessionKey

                      4. When sent from Bob to Alice: Alice's introKey, as
                         received in the PeerTest message from Alice

                      5. When sent from Charlie to Alice: Alice's introKey, as
                         received in the PeerTest message from Bob

                      6. When sent from Alice to Charlie: Charlie's introKey, as
                         received in the PeerTest message from Charlie

**MAC Key used:**     Listed in order of occurrence:

                      1. When sent from Alice to Bob: Alice/Bob MAC Key

                         (The protocol also permits Bob's introKey if Alice and
                         Bob do not have an established session, but in the
                         current implementation Alice always selects a Bob that
                         is established. As of release 0.9.15, Bob will reject
                         PeerTests from peers without an established session.)

                      2. When sent from Bob to Charlie: Bob/Charlie MAC Key

                      3. When sent from Charlie to Bob: Bob/Charlie MAC Key

                      4. When sent from Bob to Alice: Alice's introKey, as
                         received in the PeerTest message from Alice

                      5. When sent from Charlie to Alice: Alice's introKey, as
                         received in the PeerTest message from Bob

                      6. When sent from Alice to Charlie: Charlie's introKey, as
                         received in the PeerTest message from Charlie
====================  ==========================================================

Message format:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |    test nonce     |size| Alice IP addr
  +----+----+----+----+----+----+----+----+
       | Port (A)|                        |
  +----+----+----+                        +
  | Alice or Charlie's                    |
  + introduction key (Alice's is sent to  +
  | Bob and Charlie, while Charlie's is   |
  + sent to Alice)                        +
  |                                       |
  +              +----+----+----+----+----+
  |              | arbitrary amount of    |
  +----+----+----+                        |
  | uninterpreted data                    |
  ~                .  .  .                ~
{% endhighlight %}

Typical size including header, in current implementation: 80 bytes (before
non-mod-16 padding)

Notes
`````
* When sent by Alice, IP address size is 0, IP address is not present, and port
  is 0, as Bob and Charlie do not use the data; the point is to determine
  Alice's true IP address/port and tell Alice; Bob and Charlie don't care what
  Alice thinks her address is.

* When sent by Bob or Charlie, IP and port are present, and IP address is
  always 4 bytes in the current implementation. IPv6 testing is not currently
  supported.

* IPv6 Notes: Through release 0.9.26, only testing of IPv4 addresses is supported. Therefore, all
  Alice-Bob and Alice-Charlie communication must be via IPv4. Bob-Charlie
  communication, however, may be via IPv4 or IPv6. Alice's address, when
  specified in the PeerTest message, must be 4 bytes.
  As of release 0.9.27, testing of IPv6 addresses is supported,
  and Alice-Bob and Alice-Charlie communication may be via IPv6,
  if Bob and Charlie indicate support with a 'B' capability in their published IPv6 address.
  See Proposal 126 for details.

  Alice sends the request to Bob using an existing session over the transport (IPv4 or IPv6) that she wishes to test.
  When Bob receives a request from Alice via IPv4, Bob must select a Charlie that advertises an IPv4 address.
  When Bob receives a request from Alice via IPv6, Bob must select a Charlie that advertises an IPv6 address.
  The actual Bob-Charlie communication may be via IPv4 or IPv6 (i.e., independent of Alice's address type).

* A peer must maintain a table of active test states (nonces). On reception of
  a PeerTest message, look up the nonce in the table. If found, it's an
  existing test and you know your role (Alice, Bob, or Charlie). Otherwise, if
  the IP is not present and the port is 0, this is a new test and you are Bob.
  Otherwise, this is a new test and you are Charlie.

* As of release 0.9.15, Alice must have an established session with Bob and use
  the session key.

* Extended options in the header: Not expected, undefined.

HolePunch
---------

A HolePunch is simply a UDP packet with no data.  It is unauthenticated and
unencrypted.  It does not contain a SSU header, so it does not have a message
type number.  It is sent from Charlie to Alice as a part of the Introduction
sequence.


.. _sampledatagrams:

Sample datagrams
================

Minimal data message
--------------------

* no fragments, no ACKs, no NACKs, etc
* Size: 39 bytes

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                  MAC                  |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                   IV                  |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |flag|        time       |flag|#frg|    |
  +----+----+----+----+----+----+----+    +
  |  padding to fit a full AES256 block   |
  +----+----+----+----+----+----+----+----+
{% endhighlight %}

Minimal data message with payload
---------------------------------

* Size: 46+fragmentSize bytes

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |                  MAC                  |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |                   IV                  |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |flag|        time       |flag|#frg|
  +----+----+----+----+----+----+----+----+
    messageId    |   frag info  |         |
  ----+----+----+----+----+----+         +
  | that many bytes of fragment data      |
  ~                .  .  .                ~
  |                                       |
  +----+----+----+----+----+----+----+----+
{% endhighlight %}


References
==========

.. [CRYPTO-AES]
    {{ site_url('docs/how/cryptography', True) }}#AES

.. [CRYPTO-ELG]
    {{ site_url('docs/how/cryptography', True) }}#elgamal

.. [CRYPTO-HMAC]
    {{ site_url('docs/how/cryptography', True) }}#udp

.. [Date]
    {{ ctags_url('Date') }}

.. [I2P-SRC]
    https://github.com/i2p/i2p.i2p

.. [I2PCPP-SRC]
    http://{{ i2pconv('git.repo.i2p') }}/w/i2pcpp.git

.. [I2PD-SRC]
    https://github.com/PurpleI2P/i2pd

.. [KeyCertificate]
    {{ spec_url('common-structures') }}#key-certificates

.. [RouterIdentity]
    {{ ctags_url('RouterIdentity') }}

.. [SESSIONKEY]
    {{ ctags_url('SessionKey') }}

.. [Signature]
    {{ ctags_url('Signature') }}

.. [SigningPrivateKey]
    {{ ctags_url('SigningPrivateKey') }}

.. [SigningPublicKey]
    {{ ctags_url('SigningPublicKey') }}

.. [SSU]
    {{ site_url('docs/transport/ssu', True) }}

.. [SSU-KEYS]
    {{ site_url('docs/transport/ssu', True) }}#keys

.. [SSU-PEERTEST]
    {{ site_url('docs/transport/ssu', True) }}#peerTesting
