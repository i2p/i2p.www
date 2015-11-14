==================
I2CP Specification
==================
.. meta::
    :lastupdated: June 2015
    :accuratefor: 0.9.21


Overview
========

This page specified the I2P Control Protocol (I2CP), which is the interface
between clients and the router.  Java clients will use the I2CP client API,
which implements this protocol.  Non-Java clients will most likely use a
higher-layer protocol such as SAM or BOB.

The protocol is only serialized if the client and router are not in the same
JVM; otherwise, I2CP message objects are passed via an internal JVM interface.

More information is on the I2CP Overview page [I2CP]_.


Sessions
========

The protocol was designed to handle multiple "sessions", each with a 2-byte
session ID, over a single TCP connection, however, Multiple sessions were not
implemented until version 0.9.21.  See the `multisession section below`_.  Do
not attempt to use multiple sessions on a single I2CP connection with routers
older than version 0.9.21.

.. _multisession section below: _multisession

It also appears that there are some provisions for a single client to talk to
multiple routers over separate connections. This is also untested, and probably
not useful.

It does not appear that there is currently a way for a session to be maintained
after a disconnect, or to be recovered on a different I2CP connection.


Example Message Sequences
=========================

Note: The examples below do not show the Protocol Byte (0x2a) that must be sent
from the client to the router when first connecting.  More information about
connection initialization is on the I2CP Overview page [I2CP]_.

Standard Session Establish
--------------------------

.. raw:: html

  {% highlight %}
    Client                                           Router

                             --------------------->  Get Date Message
          Set Date Message  <---------------------
                             --------------------->  Create Session Message
    Session Status Message  <---------------------
  Request LeaseSet Message  <---------------------
                             --------------------->  Create LeaseSet Message
{% endhighlight %}

Get Bandwidth Limits (Simple Session)
-------------------------------------

.. raw:: html

  {% highlight %}
    Client                                           Router

                             --------------------->  Get Bandwidth Limits Message
  Bandwidth Limits Message  <---------------------
{% endhighlight %}

Destination Lookup (Simple Session)
-----------------------------------

.. raw:: html

  {% highlight %}
    Client                                           Router

                             --------------------->  Dest Lookup Message
        Dest Reply Message  <---------------------
{% endhighlight %}

Outgoing Message
----------------

Existing session, with i2cp.messageReliability=none

.. raw:: html

  {% highlight %}
    Client                                           Router

                             --------------------->  Send Message Message
{% endhighlight %}

Existing session, with i2cp.messageReliability=none and nonzero nonce

.. raw:: html

  {% highlight %}
    Client                                           Router

                             --------------------->  Send Message Message
    Message Status Message  <---------------------
    (succeeded)
{% endhighlight %}

Existing session, with i2cp.messageReliability=BestEffort

.. raw:: html

  {% highlight %}
    Client                                           Router

                             --------------------->  Send Message Message
    Message Status Message  <---------------------
    (accepted)
    Message Status Message  <---------------------
    (succeeded)
{% endhighlight %}

Incoming Message
----------------

Existing session, with i2cp.fastReceive=true (as of 0.9.4)

.. raw:: html

  {% highlight %}
    Client                                           Router

   Message Payload Message  <---------------------
{% endhighlight %}

Existing session, with i2cp.fastReceive=false

.. raw:: html

  {% highlight %}
    Client                                           Router

    Message Status Message  <---------------------
    (available)
                             --------------------->  Receive Message Begin Message
   Message Payload Message  <---------------------
                             --------------------->  Receive Message End Message
{% endhighlight %}


.. _multisession:

Multisession Notes
------------------

Multiple sessions on a single I2CP connection are supported as of router
version 0.9.21.  The first session that is created is the "primary session".
Additional sessions are "subsessions".  Subsessions are used to support
multiple destinations sharing a common set of tunnels.  The initial application
is for the primary session to use ECDSA signing keys, while the subsession uses
DSA signing keys for communication with old eepsites.

Subsessions share the same inbound and outbound tunnel pools as the primary
session.  Subsessions must use the same encryption keys as the primary session.
This applies both to the LeaseSet encryption keys and the (unused) Destination
encryption keys.  Subsessions must use different signing keys in the
destination, so the destination hash is different from the primary session.  As
subsessions use the same encryption keys and tunnels as the primary session, it
is apparent to all that the Destinations are running on the same router, so the
usual anti-correlation anonymity guarantees do not apply.

Subsessions are created by sending a CreateSession message and receiving a
SessionStatus message in reply, as usual. Subsessions must be created after the
primary session is created.  The SessionStatus response will, on success,
contain a unique Session ID, distinct from the ID for the primary session.
While CreateSession messages should be processed in-order, there is no sure way
to correlate a CreateSession message with the response, so a client should not
have multiple CreateSession messages outstanding simultaneously.  SessionConfig
options for the subsession may not be honored where they are different from the
primary session.  In particular, since subsessions use the same tunnel pool as
the primary session, tunnel options may be ignored.

The router will send separate RequestVariableLeaseSet messages for each
Destination to the client, and the client must reply with a CreateLeaseSet
message for each.  The leases for the two Destinations will not necessarily be
identical, even though they are selected from the same tunnel pool.

A subsession may be destroyed with the DestroySession message as usual.  This
will not destroy the primary session or stop the I2CP connection.  Destroying
the primary session will, however, destroy all subsessions and stop the I2CP
connection.  A Disconnect message destroys all sessions.

Note that most, but not all, I2CP messages contain a Session ID.  For the ones
that do not, clients may need additional logic to properly handle router
responses.  DestLookup and DestReply do not contain Session IDs; use the newer
HostLookup and HostReply instead.  GetBandwidthLimts and BandwidthLimits do not
contain session IDs, however the response is not session-specific.

Support for multiple sessions is preliminary and subject to change.  Support
may not be complete in other parts of the API and user interface, particularly
streaming and i2ptunnel.  Current support is primarily for clients (i.e.
Destinations that do not publish their leaseset or accept incoming
connections), and is incomplete and untested for servers.  Future releases may
provide additional features and options.


.. _notes:

Version Notes
-------------

The initial protocol version byte (0x2a) sent by the client is not expected to
change.  Prior to release 0.8.7, the router's version information was not
available to the client, thus preventing new clients from working with old
routers.  As of release 0.8.7, the two parties' protocol version strings are
exchanged in the Get/Set Date Messages.  Going forward, clients may use this
information to communicate correctly with old routers.  Clients and routers
should not send messages that are unsupported by the other side, as they
generally disconnect the session upon reception of an unsupported message.

The exchanged version information is the "core" version or I2CP protocol
version, and is not necessarily the router version.

A basic summary of the I2CP protocol versions is as follows. For details, see
below.

==============  ======================
   Version      Required I2CP Features
==============  ======================
   0.9.21       Multiple sessions on a single I2CP connection supported

   0.9.20       Additional SetDate messages may be sent to the client at any
                time

   0.9.16       Authentication, if enabled, is required via GetDate before all
                other messages

   0.9.15       Dest/LS key certs w/ EdDSA Ed25519 sig type supported

   0.9.14       Per-message override of messageReliability=none with nonzero
                nonce

   0.9.12       Dest/LS key certs w/ ECDSA P-256, P-384, and P-521 sig types
                supported

                Note: RSA sig types also supported as of this version, but
                currently unused

   0.9.11       Host Lookup and Host Reply messages supported

                Authentication mapping in Get Date message supported

   0.9.7        Request Variable Lease Set message supported

   0.9.5        Additional Message Status codes defined

   0.9.4        Send Message nonce=0 allowed

                Fast receive mode is the default

   0.9.2        Send Message Expires flag tag bits supported

   0.9          Supports up to 16 leases in a lease set (6 previously)

   0.8.7        Get Date and Set Date version strings included.

                If not present, the client or router is version 0.8.6 or older.

   0.8.4        Send Message Expires flag bits supported

   0.8.3        Dest Lookup and Get Bandwidth messages supported in standard
                session

                Concurrent Dest Lookup messages supported

   0.8.1        i2cp.messageReliability=none supported

   0.7.2        Get Bandwidth Limits and Bandwidth Limits messages supported

   0.7.1        Send Message Expires message supported<br>
                     Reconfigure Session message supported

   0.7          Dest Lookup and Dest Reply messages supported

0.6.5 or lower  All messages and features not listed above
==============  ======================


.. _structures:

Common structures
=================

.. _struct-i2cpmessageheader:

I2CP message header
-------------------

Description
```````````
Common header to all I2CP messages, containing the message length and message
type.

Contents
````````
1. 4 byte [Integer]_ specifying the length of the message body
2. 1 byte [Integer]_ specifying the message type.
3. The I2CP message body, 0 or more bytes

Notes
`````
Actual message length limit is about 64 KB.

.. _struct-messageid:

Message ID
----------

Description
```````````
Uniquely identifies a message waiting on a particular router at a point in
time.  This is always generated by the router and is NOT the same as the nonce
generated by the client.

Contents
````````
1. 4 byte [Integer]_

Notes
`````
Message IDs are unique within a session only; they are not globally unique.

.. _struct-payload:

Payload
-------

Description
```````````
This structure is the content of a message being delivered from one Destination
to another.

Contents
````````
1. 4 byte [Integer]_ length
2. That many bytes

Notes
`````
The payload is in a gzip format as specified on the I2CP Overview page
[I2CP-FORMAT]_.

.. _struct-sessionconfig:

Session Config
--------------

Description
```````````
Defines the configuration options for a particular client session.

Contents
````````
1. [Destination]_
2. [Mapping]_ of options
3. Creation [Date]_
4. [Signature]_ of the previous 3 fields, signed by the [SigningPrivateKey]_

Notes
`````
* The options are specified on the
<a href="{{ site_url('docs/protocol/i2cp') }}#options">I2CP Overview page</a>.

* The [Mapping]_ must be sorted by key so that the signature will be validated
  correctly in the router.

* The creation date must be within +/- 30 seconds of the current time when
  processed by the router, or the config will be rejected.

.. _struct-sessionid:

Session ID
----------

Description
```````````
Uniquely identifies a session on a particular router at a point in
time.

Contents
````````
1. 2 byte [Integer]_

Notes
`````


Messages
========

See also the I2CP Javadocs [I2CP-JAVADOCS]_.

.. _types:

Message Types
-------------

===============================  =========  ====  =====
            Message              Direction  Type  Since
===============================  =========  ====  =====
BandwidthLimitsMessage_           R -> C     23   0.7.2
CreateLeaseSetMessage_            C -> R      4
CreateSessionMessage_             C -> R      1
DestLookupMessage_                C -> R     34   0.7
DestReplyMessage_                 R -> C     35   0.7
DestroySessionMessage_            C -> R      3
DisconnectMessage_                bidir.     30
GetBandwidthLimitsMessage_        C -> R      8   0.7.2
GetDateMessage_                   C -> R     32
HostLookupMessage_                C -> R     38   0.9.11
HostReplyMessage_                 R -> C     39   0.9.11
MessagePayloadMessage_            R -> C     31
MessageStatusMessage_             R -> C     22
ReceiveMessageBeginMessage_       C -> R      6
ReceiveMessageEndMessage_         C -> R      7
ReconfigureSessionMessage_        C -> R      2   0.7.1
ReportAbuseMessage_               bidir.     29
RequestLeaseSetMessage_           R -> C     21
RequestVariableLeaseSetMessage_   R -> C     37   0.9.7
SendMessageMessage_               C -> R      5
SendMessageExpiresMessage_        C -> R     36   0.7.1
SessionStatusMessage_             R -> C     20
SetDateMessage_                   R -> C     33
===============================  =========  ====  =====

.. _msg_bandwidthlimits:

BandwidthLimitsMessage
----------------------

Description
```````````
Tell the client what the bandwidth limits are.

Sent from Router to Client in response to a GetBandwidthLimitsMessage_.

Contents
````````
1. 4 byte [Integer]_ Client inbound limit (KBps)
2. 4 byte [Integer]_ Client outbound limit (KBps)
3. 4 byte [Integer]_ Router inbound limit (KBps)
4. 4 byte [Integer]_ Router inbound burst limit (KBps)
5. 4 byte [Integer]_ Router outbound limit (KBps)
6. 4 byte [Integer]_ Router outbound burst limit (KBps)
7. 4 byte [Integer]_ Router burst time (seconds)
8. Nine 4-byte [Integer]_ (undefined)

Notes
`````
Currently, the client limits are the only values set, and are actually the
router limits. All the values labeled as router limits are always 0.  As of
release 0.7.2.

.. _msg-createleaseset:

CreateLeaseSetMessage
---------------------

Description
```````````
This message is sent in response to a RequestLeaseSetMessage_ or
RequestVariableLeaseSetMessage_ and contains all of the [Lease]_ structures that
should be published to the I2NP Network Database.

Sent from Client to Router.

Contents
````````
1. `Session ID`_
2. [SigningPrivateKey]_
3. [PrivateKey]_
4. [LeaseSet]_

Notes
`````
The SigningPrivateKey matches the [SigningPublicKey]_ from within the LeaseSet,
as does the PrivateKey with the [PublicKey]_. The signing key is necessary to
allow the router to revoke the LeaseSet if the client goes offline, and the
encryption key is necessary for decrypting garlic routed messages. The LeaseSet
granted may include Lease structures for tunnels pointing at another router if
the client is actively connected to multiple routers with Leases granted to
each.

**XXX** Really?
Revocation is unimplemented.
Connection to multiple routers is untested.

.. _msg-CreateSession:

CreateSessionMessage
--------------------

Description
```````````
This message is sent from a client to initiate a session, where a session is
defined as a single Destination's connection to the network, to which all
messages for that Destination will be delivered and from which all messages
that Destination sends to any other Destination will be sent through.

Sent from Client to Router.  The router responds with a SessionStatusMessage_.

Contents
````````
1. `Session Config`_

Notes
`````
* This is the second message sent by the client. Previously the client sent a
  GetDateMessage_ and received a SetDateMessage_ response.

* If the Date in the Session Config is too far (more than +/- 30 seconds) from
  the router's current time, the session will be rejected.

* If there is already a session on the router for this Destination, the session
  will be rejected.

* The [Mapping]_ in the Session Config must be sorted by key so that the
  signature will be validated correctly in the router.

.. _msg-destlookup:

DestLookupMessage
-----------------

Description
```````````
Sent from Client to Router.  The router responds with a DestReplyMessage_.

Contents
````````
1. SHA-256 [Hash]_

Notes
`````
As of release 0.7.

As of release 0.8.3, multiple outstanding lookups are supported, and lookups
are supported in both I2PSimpleSession and in standard sessions.

HostLookupMessage_ is preferred as of release 0.9.11.

.. _msg-DestReply:

DestReplyMessage
----------------

Description
```````````
Sent from Router to Client in response to a DestLookupMessage_.

Contents
````````
1. [Destination]_ on success, or [Hash]_ on failure

Notes
`````
As of release 0.7.

As of release 0.8.3, the requested Hash is returned if the lookup failed, so
that the client may have multiple lookups outstanding and correlate the replies
to the lookups.  To correlate a Destination response with a request, take the
Hash of the Destination.  Prior to release 0.8.3, the response was empty on
failure.

.. _msg-destroysession:

DestroySessionMessage
---------------------

Description
```````````
This message is sent from a client to destroy a session.

Sent from Client to Router. The router responds with a SessionStatusMessage_.

Contents
````````
1. `Session ID`_

Notes
`````
The router at this point should release all resources related to the session.

.. _msg-disconnect:

DisconnectMessage
-----------------

Description
```````````
Tell the other party that there are problems and the current connection is about to
be destroyed. This does not necessarily end a session.
Sent either from router to client or from client to router.

Contents
````````
1. Reason [String]_

Notes
`````
Only implemented in the router-to-client direction.  Disconnecting probably
does end a session, in practice.

.. _msg-GetBandwidthLimits:

GetBandwidthLimitsMessage
-------------------------

Description
```````````
Request that the router state what its current bandwidth limits are.

Sent from Client to Router.  The router responds with a
BandwidthLimitsMessage_.

Contents
````````
*None*

Notes
`````
As of release 0.7.2.

As of release 0.8.3, supported in both I2PSimpleSession and in standard
sessions.

.. _msg-GetDate:

GetDateMessage
--------------

Description
```````````
Sent from Client to Router.  The router responds with a SetDateMessage_.

Contents
````````
1. I2CP Version [String]_
2. Authentication [Mapping]_ (optional, as of release 0.9.11)

Notes
`````
* Generally the first message sent by the client after sending the protocol
  version byte.

* The version string is included as of release 0.8.7. This is only useful if
  the client and router are not in the same JVM. If it is not present, the
  client is version 0.8.6 or earlier.

* As of release 0.9.11, the authentication [Mapping]_ may be included, with the
  keys i2cp.username and i2cp.password. The Mapping need not be sorted as this
  message is not signed. Prior to and including 0.9.10, authentication is
  included in the `Session Config`_ Mapping, and no authentication is enforced
  for GetDateMessage_, GetBandwidthLimitsMessage_, or DestLookupMessage_. When
  enabled, authentication via GetDateMessage_ is required before any other
  messages as of release 0.9.16. This is only useful outside router context.
  This is an incompatible change, but will only affect sessions outside router
  context with authentication, which should be rare.

.. _msg-HostLookup:

HostLookupMessage
-----------------

Description
```````````
Sent from Client to Router.  The router responds with a HostReplyMessage_.

This replaces the DestLookupMessage_ and adds a request ID, a timeout, and host
name lookup support.  As it also supports Hash lookups, it may be used for all
lookups if the router supports it.  For host name lookups, the router will
query its context's naming service.  This is only useful if the client is
outside the router's context.  Inside router context, the client should query
the naming service itself, which is much more efficient.

Contents
````````
1. `Session ID`_
2. 4 byte [Integer]_ request ID
3. 4 byte [Integer]_ timeout (ms)
4. 1 byte [Integer]_ request type
5. SHA-256 [Hash]_ or host name [String]_

Notes
`````
* As of release 0.9.11. Use DestLookupMessage_ for older routers.

* The session ID and request ID will be returned in the HostReplyMessage_. Use
  0xFFFF for the session ID if there is no session.

* Timeout is useful for Hash lookups. Recommended minimum 10,000 (10 sec.). In
  the future it may also be useful for remote naming service lookups. The value
  may be not be honored for local host name lookups, which should be fast.

* The request type is 0 for Hash and 1 for host name.

* Base 32 host name lookup is supported but it is preferred to convert it to a
  Hash first.

.. _msg-hostreply:

HostReplyMessage
----------------

Description
```````````
Sent from Router to Client in response to a HostLookupMessage_.

Contents
````````
1. `Session ID`_
2. 4 byte [Integer]_ request ID
3. 1 byte [Integer]_ result code
4. [Destination]_, only present if result code is zero.

Notes
`````
* As of release 0.9.11. See HostLookupMessage_ notes.

* The session ID and request ID are those from the HostLookupMessage_.

* The result code is 0 for success, 1-255 for failure. Only 1 is used for
  failure now, more specific failure codes may be defined in the future.

.. _msg-messagepayload:

MessagePayloadMessage
---------------------

Description
```````````
Deliver the payload of a message to the client.

Sent from Router to Client.  The client responds with a
ReceiveMessageEndMessage_.

Contents
````````
1. `Session ID`_
2. `Message ID`_
3. Payload_

Notes
`````

.. _msg-messagestatus:

MessageStatusMessage
--------------------

Description
```````````
Notify the client of the delivery status of an incoming or outgoing message.
Sent from Router to Client.  If this message indicates that an incoming message
is available, the client responds with a ReceiveMessageBeginMessage_.  For an
outgoing message, this is a response to a SendMessageMessage_ or
SendMessageExpiresMessage_.

Contents
````````
1. `Session ID`_
2. `Message ID`_ generated by the router
3. 1 byte [Integer]_ status
4. 4 byte [Integer]_ size
5. 4 byte [Integer]_ nonce previously generated by the client

Notes
`````
Through version 0.9.4, the known status values are 0 for message is available,
1 for accepted, 2 for best effort succeeded, 3 for best effort failed, 4 for
guaranteed succeeded, 5 for guaranteed failed. The size Integer specifies the
size of the available message and is only relevant for status = 0.  Even though
guaranteed is unimplemented, (best effort is the only service), the current
router implementation uses the guaranteed status codes, not the best effort
codes.

As of router version 0.9.5, additional status codes are defined, however they
are not necessarily implemented.  See [MSM-JAVADOCS]_ for details.  All status
codes:

===========  =============  ======================  ==========================================================
Status Code  As Of Release           Name           Description
===========  =============  ======================  ==========================================================
     0                      Available               For incoming messages only. All other status codes below
                                                    are for outgoing messages.

                                                    The included size is the size in bytes of the available
                                                    message.

                                                    This is unused in "fast receive" mode, which is the
                                                    default as of release 0.9.4.

     1                      Accepted                Outgoing message accepted by the local router for
                                                    delivery. The included nonce matches the nonce in the
                                                    SendMessageMessage_, and the included Message ID will be
                                                    used for subsequent success or failure notification.

     2                      Best Effort Success     Probable success (unused)

     3                      Best Effort Failure     Probable failure

     4                      Guaranteed Success      Probable success

     5                      Guaranteed Failure      Generic failure, specific cause unknown.
                                                    May not really be a guaranteed failure.

     6           0.9.5      Local Success           Local delivery successful.
                                                    The destination was another client on the same router.

     7           0.9.5      Local Failure           Local delivery failure.
                                                    The destination was another client on the same router.

     8           0.9.5      Router Failure          The local router is not ready, has shut down, or has
                                                    major problems.

                                                    This is a guaranteed failure.

     9           0.9.5      Network Failure         The local computer apparently has no network connectivity
                                                    at all.

                                                    This is a guaranteed failure.

    10           0.9.5      Bad Session             The I2CP session is invalid or closed.

                                                    This is a guaranteed failure.

    11           0.9.5      Bad Message             The message payload is invalid or zero-length or too big.

                                                    This is a guaranteed failure.

    12           0.9.5      Bad Options             Something is invalid in the message options, or the
                                                    expiration is in the past or too far in the future.

                                                    This is a guaranteed failure.

    13           0.9.5      Overflow Failure        Some queue or buffer in the router is full and the message
                                                    was dropped.

                                                    This is a guaranteed failure.

    14           0.9.5      Message Expired         The message expired before it could be sent.

                                                    This is a guaranteed failure.

    15           0.9.5      Bad Local Leaseset      The client has not yet signed a [LeaseSet]_, or the local
                                                    keys are invalid, or it has expired, or it does not have
                                                    any tunnels in it.

                                                    This is a guaranteed failure.

    16           0.9.5      No Local Tunnels        Local problems. No outbound tunnel to send through, or no
                                                    inbound tunnel if a reply is required.

                                                    This is a guaranteed failure.

    17           0.9.5      Unsupported Encryption  The certs or options in the [Destination]_ or its
                                                    [LeaseSet]_ indicate that it uses an encryption format
                                                    that we don't support, so we can't talk to it.

                                                    This is a guaranteed failure.

    18           0.9.5      Bad Destination         Something is wrong with the far-end [Destination]_. Bad
                                                    format, unsupported options, certificates, etc.

                                                    This is a guaranteed failure.

    19           0.9.5      Bad Leaseset            We got the far-end [LeaseSet]_ but something strange is
                                                    wrong with it. Unsupported options or certificates, no
                                                    tunnels, etc.

                                                    This is a guaranteed failure.

    20           0.9.5      Expired Leaseset        We got the far-end [LeaseSet]_ but it's expired and we
                                                    can't get a new one.

                                                    This is a guaranteed failure.

    21           0.9.5      No Leaseset             Could not find the far-end [LeaseSet]_. This is a common
                                                    failure, equivalent to a DNS lookup failure.

                                                    This is a guaranteed failure.
===========  =============  ======================  ==========================================================

When status = 1 (accepted), the nonce matches the nonce in the
SendMessageMessage_, and the included Message ID will be used for subsequent
success or failure notification.  Otherwise, the nonce may be ignored.

.. _msg-receivemessagebegin:

ReceiveMessageBeginMessage
--------------------------

Description
```````````
Request the router to deliver a message that it was previously notified of.
Sent from Client to Router.  The router responds with a MessagePayloadMessage_.

Contents
````````
1. `Session ID`_
2. `Message ID`

Notes
`````
The ReceiveMessageBeginMessage_ is sent as a response to a
MessageStatusMessage_ stating that a new message is available for pickup. If
the message id specified in the ReceiveMessageBeginMessage_ is invalid or
incorrect, the router may simply not reply, or it may send back a
DisconnectMessage_.

This is unused in "fast receive" mode, which is the default as of release
0.9.4.

.. _msg-receivemessageend:

ReceiveMessageEndMessage
------------------------

Description
```````````
Tell the router that delivery of a message was completed successfully and that
the router can discard the message.

Sent from Client to Router.

Contents
````````
1. `Session ID`_
2. `Message ID`

Notes
`````
The ReceiveMessageEndMessage_ is sent after a MessagePayloadMessage_ fully
delivers a message's payload.

This is unused in "fast receive" mode, which is the default as of release
0.9.4.

.. _msg-reconfiguresession:

ReconfigureSessionMessage
-------------------------

Description
```````````

Sent from Client to Router to update the session configuration.  The router
responds with a SessionStatusMessage_.

Contents
````````
1. `Session ID`_
2. `Session Config`_

Notes
`````
* As of release 0.7.1.

* If the Date in the Session Config is too far (more than +/- 30 seconds) from
  the router's current time, the session will be rejected.

* The [Mapping]_ in the Session Config must be sorted by key so that the
  signature will be validated correctly in the router.

* Some configuration options may only be set in the CreateSessionMessage_, and
  changes here will not be recognized by the router. Changes to tunnel options
  inbound.* and outbound.* are always recognized.

.. _msg-reportabuse:

ReportAbuseMessage
------------------

Description
```````````
Tell the other party (client or router) that they are under attack, potentially
with reference to a particular MessageId. If the router is under attack, the
client may decide to migrate to another router, and if a client is under
attack, the router may rebuild its routers or banlist some of the peers that
sent it messages delivering the attack.

Sent either from router to client or from client to router.

Contents
````````
1. `Session ID`_
2. 1 byte [Integer]_ abuse severity (0 is minimally abusive, 255 being
   extremely abusive)
3. Reason [String]_
4. `Message ID`_

Notes
`````
Unused.  Not fully implemented. Both router and client can generate a
ReportAbuseMessage_, but neither has a handler for the message when received.

.. _msg-requestleaseset:

RequestLeaseSetMessage
----------------------

Description
```````````
Request that a client authorize the inclusion of a particular set of inbound
tunnels.  Sent from Router to Client.  The client responds with a
CreateLeaseSetMessage_.

Contents
````````
1. `Session ID`_
2. 1 byte [Integer]_ number of tunnels
3. That many pairs of:

   1. [RouterIdentity]_
   2. [TunnelId]_

4. End [Date]_

Notes
`````
This requests a [LeaseSet]_ with all [Leases]_ set to expire at the same time.
For client versions 0.9.7 or higher, RequestVariableLeaseSetMessage_ is
preferred.

.. _msg-requestvariableleaseset:

RequestVariableLeaseSetMessage
------------------------------

Description
```````````
Request that a client authorize the inclusion of a particular set of inbound
tunnels.

Sent from Router to Client.  The client responds with a CreateLeaseSetMessage_.

Contents
````````
1. `Session ID`_
2. 1 byte [Integer]_ number of tunnels
3. That many [Leases]_

Notes
`````
This requests a [LeaseSet]_ with an individual expiration time for each
[Lease]_.

As of release 0.9.7.  For clients before that release, use
RequestLeaseSetMessage_.

.. _msg-sendmessage:

SendMessageMessage
------------------

Description
```````````
This is how a client sends a message (the payload) to the [Destination]_.  The
router will use a default expiration.

Sent from Client to Router.  The router responds with a MessageStatusMessage_.

Contents
````````
1. `Session ID`_
2. [Destination]_
3. Payload_
4. 4 byte [Integer]_ nonce

Notes
`````
As soon as the SendMessageMessage_ arrives fully intact, the router should
return a MessageStatusMessage_ stating that it has been accepted for delivery.
That message will contain the same nonce sent here.  Later on, based on the
delivery guarantees of the session configuration, the router may additionally
send back another MessageStatusMessage_ updating the status.

As of release 0.8.1, the router does not send either MessageStatusMessage_ if
i2cp.messageReliability=none.

Prior to release 0.9.4, a nonce value of 0 was not allowed.  As of release
0.9.4, a nonce value of 0 is allowed, and tells to the router that it should
not send either MessageStatusMessage_, i.e. it acts as if
i2cp.messageReliability=none for this message only.

Prior to release 0.9.14, a session with i2cp.messageReliability=none could not
be overridden on a per-message basis.  As of release 0.9.14, in a session with
i2cp.messageReliability=none, the client may request delivery of a
MessageStatusMessage_ with the delivery success or failure by setting the nonce
to a nonzero value.  The router will not send the "accepted"
MessageStatusMessage_ but it will later send the client a MessageStatusMessage_
with the same nonce, and a success or failure value.

.. _msg-sendmessageexpires:

SendMessageExpiresMessage
-------------------------

Description
```````````
Sent from Client to Router. Same as SendMessageMessage_, except includes an
expiration and options.

Contents
````````
1. `Session ID`_
2. [Destination]_
3. Payload_
4. 4 byte [Integer]_ nonce
5. 2 bytes of flags (options)
6. Expiration [Date]_ truncated from 8 bytes to 6 bytes

Notes
`````
As of release 0.7.1.

In "best effort" mode, as soon as the SendMessageExpiresMessage arrives fully
intact, the router should return a MessageStatusMessage stating that it has
been accepted for delivery.  That message will contain the same nonce sent
here.  Later on, based on the delivery guarantees of the session configuration,
the router may additionally send back another MessageStatusMessage updating the
status.

As of release 0.8.1, the router does not send either Message Status Message if
i2cp.messageReliability=none.

Prior to release 0.9.4, a nonce value of 0 was not allowed.  As of release
0.9.4, a nonce value of 0 is allowed, and tells the router that it should not
send either Message Status Message, i.e. it acts as if
i2cp.messageReliability=none for this message only.

Prior to release 0.9.14, a session with i2cp.messageReliability=none could not
be overridden on a per-message basis.  As of release 0.9.14, in a session with
i2cp.messageReliability=none, the client may request delivery of a Message
Status Message with the delivery success or failure by setting the nonce to a
nonzero value.  The router will not send the "accepted" Message Status Message
but it will later send the client a Message Status Message with the same nonce,
and a success or failure value.

Flags Field
```````````
As of release 0.8.4, the upper two bytes of the Date are redefined to contain
flags. The flags must default to all zeros for backward compatibility.  The
Date will not encroach on the flags field until the year 10889.  The flags may
be used by the application to provide hints to the router as to whether a
LeaseSet and/or ElGamal/AES Session Tags should be delivered with the message.
The settings will significantly affect the amount of protocol overhead and the
reliability of message delivery.  The individual flag bits are defined as
follows, as of release 0.9.2.  Definitions are subject to change. Use the
SendMessageOptions class to construct the flags.

Bit order: 15...0

Bits 15-11
    Unused, must be zero

Bits 10-9
    Message Reliability Override (Unimplemented, to be removed).

===========  ===========
Field value  Description
===========  ===========
    00       Use session setting i2cp.messageReliability (default)

    01       Use "best effort" message reliability for this message, overriding
             the session setting. The router will send one or more
             MessageStatusMessages in response.

             Unused. Use a nonzero nonce value to override a session setting of
             "none".

    10       Use "guaranteed" message reliability for this message, overriding
             the session setting. The router will send one or more
             MessageStatusMessages in response.

             Unused. Use a nonzero nonce value to override a session setting of
             "none".

    11       Unused. Use a nonce value of 0 to force "none" and override a
             session setting of "best effort" or "guaranteed".
===========  ===========

Bit 8
    If 1, don't bundle a lease set in the garlic with this message.  If 0, the
    router may bundle a lease set at its discretion.

Bits 7-4
    Low tag threshold. If there are less than this many tags available, send
    more.  This is advisory and does not force tags to be delivered.

===========  =============
Field value  Tag threshold
===========  =============
   0000      Use session key manager settings
   0001             2
   0010             3
   0011             6
   0100             9
   0101            14
   0110            20
   0111            27
   1000            35
   1001            45
   1010            57
   1011            72
   1100            92
   1101           117
   1110           147
   1111           192
===========  =============

Bits 3-0
    Number of tags to send if required.  This is advisory and does not force
    tags to be delivered.

===========  ============
Field value  Tags to send
===========  ============
   0000      Use session key manager settings
   0001            2
   0010            4
   0011            6
   0100            8
   0101           12
   0110           16
   0111           24
   1000           32
   1001           40
   1010           51
   1011           64
   1100           80
   1101          100
   1110          125
   1111          160
===========  ============

.. _msg-sessionstatus:

SessionStatusMessage
--------------------

Description
```````````
Instruct the client as to the status of its session.

Sent from Router to Client, possibly in response to a CreateSessionMessage_ or
ReconfigureSessionMessage_.

Contents
````````
1. `Session ID`_
2. 1 byte [Integer]_ status

======  ======  =========  =============================================================
Status  Since     Name     Definition
======  ======  =========  =============================================================
   0            Destroyed  The session with the given ID is terminated.

   1            Created    In response to a CreateSessionMessage_, a new session with
                           the given ID is now active.

   2            Updated    In response to a ReconfigureSessionMessage_, an existing
                           session with the given ID has been reconfigured.

   3            Invalid    In response to a CreateSessionMessage_, the configuration is
                           invalid. The included session ID should be ignored.

                           In response to a ReconfigureSessionMessage_, the new
                           configuration is invalid for the session with the given ID.

   4    0.9.12  Refused    In response to a CreateSessionMessage_, the router was unable
                           to create the session, perhaps due to limits being exceeded.
                           The included session ID should be ignored.
======  ======  =========  =============================================================

Notes
`````
Status values include 0 for destroyed, 1 for created, 2 for updated, and 3 for
invalid session.  If created, the Session ID is the identifier to be used for
the rest of the session.

.. _msg-setdate:
.. _SetDateMessage:

Set Date
--------

Description
```````````
The current date and time.  Sent from Router to Client as a part of the initial
handshake.  As of release 0.9.20, may also be sent at any time after the
handshake to notify the client of a clock shift.

Contents
````````
1. [Date]_
2. I2CP Version [String]_

Notes
`````
This is generally the first message sent by the router.  The version string is
included as of release 0.8.7.  This is only useful if the client and router are
not in the same JVM.  If it is not present, the router is version 0.8.6 or
earlier.

Additional SetDate messages will not be sent to clients in the same JVM.


References
==========

.. [Date]
    {{ spec_url('common-structures') }}#type-date

.. [Destination]
    {{ spec_url('common-structures') }}#struct-destination

.. [Hash]
    {{ spec_url('common-structures') }}#struct-hash

.. [I2CP]
    {{ site_url('docs/protocol/i2cp', True) }}

.. [I2CP-FORMAT]
    {{ site_url('docs/protocol/i2cp', True) }}#format

.. [I2CP-JAVADOCS]
    http://docs.i2p-projekt.de/javadoc/net/i2p/data/i2cp/package-summary.html

.. [Integer]
    {{ spec_url('common-structures') }}#type-integer

.. [Leases]
.. [Lease]
    {{ spec_url('common-structures') }}#struct-lease

.. [LeaseSet]
    {{ spec_url('common-structures') }}#struct-leaseset

.. [Mapping]
    {{ spec_url('common-structures') }}#type-mapping

.. [MSM-JAVADOCS]
    http://docs.i2p-projekt.de/javadoc/net/i2p/data/i2cp/MessageStatusMessage.html

.. [PrivateKey]
    {{ spec_url('common-structures') }}#type-privatekey

.. [RouterIdentity]
    {{ spec_url('common-structures') }}#struct-routeridentity

.. [Signature]
    {{ spec_url('common-structures') }}#type-signature

.. [SigningPrivateKey]
    {{ spec_url('common-structures') }}#type-signingprivatekey

.. [String]
    {{ spec_url('common-structures') }}#struct-string

.. [TunnelId]
    {{ spec_url('common-structures') }}#tunnelid
