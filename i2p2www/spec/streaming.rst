===============================
Streaming Library Specification
===============================
.. meta::
    :lastupdated: June 2015
    :accuratefor: 0.9.20


Overview
========

See [STREAMING]_ for an overview of the Streaming Library.


Protocol Specification
======================

Packet Format
-------------

The format of a single packet in the streaming protocol is:

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  | send Stream ID    | rcv Stream ID     |
  +----+----+----+----+----+----+----+----+
  | sequence  Num     | ack Through       |
  +----+----+----+----+----+----+----+----+
  | nc |   NACKs ...
  +----+----+----+----+----+----+----+----+
       | rd |  flags  | opt size| opt data
  +----+----+----+----+----+----+----+----+
     ...                                  |
  +----+----+----+----+----+----+----+----+
  |   payload ...
  +----+----+----+-//

  sendStreamId :: 4 byte `Integer`
                  Random number selected by the packet recipient before sending
                  the first SYN reply packet and constant for the life of the
                  connection. 0 in the SYN message sent by the connection
                  originator, and in subsequent messages, until a SYN reply is
                  received, containing the peer's stream ID.

  receiveStreamId :: 4 byte `Integer`
                     Random number selected by the packet originator before
                     sending the first SYN packet and constant for the life of
                     the connection. May be 0 if unknown, for example in a RESET
                     packet.

  sequenceNum :: 4 byte `Integer`
                 The sequence for this message, starting at 0 in the SYN
                 message, and incremented by 1 in each message except for plain
                 ACKs and retransmissions. If the sequenceNum is 0 and the SYN
                 flag is not set, this is a plain ACK packet that should not be
                 ACKed.

  ackThrough :: 4 byte `Integer`
                The highest packet sequence number that was received on the
                $receiveStreamId. This field is ignored on the initial
                connection packet (where $receiveStreamId is the unknown id) or
                if the NO_ACK flag set. All packets up to and including this
                sequence number are ACKed, EXCEPT for those listed in NACKs
                below.

  NACK count :: 1 byte `Integer`
                The number of 4-byte NACKs in the next field

  NACKs :: $nc * 4 byte `Integer`s
           Sequence numbers less than ackThrough that are not yet received. Two
           NACKs of a packet is a request for a 'fast retransmit' of that packet.

  resendDelay :: 1 byte `Integer`
                 How long is the creator of this packet going to wait before
                 resending this packet (if it hasn't yet been ACKed).  The value
                 is seconds since the packet was created. Currently ignored on
                 receive.

  flags :: 2 byte value
           See below.

  option size :: 2 byte `Integer`
                 The number of bytes in the next field

  option data :: 0 or more bytes
                 As specified by the flags. See below.

  payload :: remaining packet size
{% endhighlight %}

Flags and Option Data Fields
----------------------------

The flags field above specifies some metadata about the packet, and in turn may
require certain additional data to be included.  The flags are as follows. Any
data structures specified must be added to the options area in the given order.

Bit order: 15....0 (15 is MSB)

=====  ========================  ============  ===============  ===============================================================
 Bit             Flag            Option Order    Option Data    Function
=====  ========================  ============  ===============  ===============================================================
  0    SYNCHRONIZE                    --             --         Similar to TCP SYN. Set in the initial packet and in the first
                                                                response. FROM_INCLUDED and SIGNATURE_INCLUDED must also be
                                                                set.

  1    CLOSE                          --             --         Similar to TCP FIN. If the response to a SYNCHRONIZE fits in a
                                                                single message, the response will contain both SYNCHRONIZE and
                                                                CLOSE. SIGNATURE_INCLUDED must also be set.

  2    RESET                          --             --         Abnormal close. SIGNATURE_INCLUDED must also be set. Prior to
                                                                release 0.9.20, due to a bug, FROM_INCLUDED must also be set.

  3    SIGNATURE_INCLUDED              4       variable length  Currently sent only with SYNCHRONIZE, CLOSE, and RESET, where
                                               [Signature]_     it is required, and with ECHO, where it is required for a
                                                                ping. The signature uses the Destination's [SigningPrivateKey]_
                                                                to sign the entire header and payload with the space in the
                                                                option data field for the signature being set to all zeroes.

                                                                Prior to release 0.9.11, the signature was always 40 bytes. As
                                                                of release 0.9.11, the signature may be variable-length, see
                                                                below for details.

  4    SIGNATURE_REQUESTED            --             --         Unused. Requests every packet in the other direction to have
                                                                SIGNATURE_INCLUDED

  5    FROM_INCLUDED                   2       387+ byte        Currently sent only with SYNCHRONIZE, where it is required, and
                                               [Destination]_   with ECHO, where it is required for a ping. Prior to release
                                                                0.9.20, due to a bug, must also be sent with RESET.

  6    DELAY_REQUESTED                 1       2 byte           Optional delay. How many milliseconds the sender of this packet
                                               [Integer]_       wants the recipient to wait before sending any more data. A
                                                                value greater than 60000 indicates choking.

  7    MAX_PACKET_SIZE_INCLUDED        3       2 byte           Currently sent with SYNCHRONIZE only. Was also sent in
                                               [Integer]_       retransmitted packets until release 0.9.1.

  8    PROFILE_INTERACTIVE            --             --         Unused or ignored; the interactive profile is unimplemented.

  9    ECHO                           --             --         Unused except by ping programs. If set, most other options are
                                                                ignored. See the streaming docs [STREAMING]_.

 10    NO_ACK                         --             --         This flag simply tells the recipient to ignore the ackThrough
                                                                field in the header. Currently set in the inital SYN packet,
                                                                otherwise the ackThrough field is always valid. Note that this
                                                                does not save any space, the ackThrough field is before the
                                                                flags and is always present.

11-15  unused                                                   Set to zero for compatibility with future uses.
=====  ========================  ============  ===============  ===============================================================

Variable Length Signature Notes
```````````````````````````````
Prior to release 0.9.11, the signature in the option field was always 40 bytes.
As of release 0.9.11, the signature is variable length.  The Signature type and
length are inferred from the type of key used in the FROM_INCLUDED option and
the [Signature]_ documentation.

* When a packet contains both FROM_INCLUDED and SIGNATURE_INCLUDED (as in
  SYNCHRONIZE), the inference may be made directly.

* When a packet does not contain FROM_INCLUDED, the inference must be made from
  a previous SYNCHRONIZE packet.

* When a packet does not contain FROM_INCLUDED, and there was no previous
  SYNCHRONIZE packet (for example a stray CLOSE or RESET packet), the inference
  can be made from the length of the remaining options (since
  SIGNATURE_INCLUDED is the last option), but the packet will probably be
  discarded anyway, since there is no FROM available to validate the signature.
  If more option fields are defined in the future, they must be accounted for.


References
==========

.. [Destination]
    {{ spec_url('common-structures') }}#struct-destination

.. [Integer]
    {{ spec_url('common-structures') }}#type-integer

.. [Signature]
    {{ spec_url('common-structures') }}#type-signature

.. [SigningPrivateKey]
    {{ spec_url('common-structures') }}#type-signingprivatekey

.. [STREAMING]
    {{ site_url('docs/api/streaming', True) }}
