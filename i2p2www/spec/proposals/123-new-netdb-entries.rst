=================
New netDB Entries
=================
.. meta::
    :author: zzz
    :created: 2016-01-16
    :thread: http://zzz.i2p/topics/2051
    :lastupdated: 2018-08-06
    :status: Open
    :supercedes: 110, 120, 121, 122

.. contents::


Overview
========

This is an update and aggregation of the following 4 proposals:

- 110 LS2
- 120 Meta LS2 for massive multihoming
- 121 Encrypted LS2
- 122 Unauthenticated service lookup (anycasting)

These proposals are mostly independent, but for sanity we define and use a
common format for several of them.


Proposal
========

This proposal defines 5 new DatabaseEntry types and the process for
storing them to and retrieving them from the network database,
as well as the method for signing them and verifying those signatures.


Justification
-------------

LS2 adds fields for changing encryption type and for future protocol changes.

Encrypted LS2 fixes several security issues with the existing encrypted LS by
using asymmetric encryption of the entire set of leases.

Meta LS2 provides flexible, efficient, effective, and large-scale multihoming.

Service Record and Service List provide anycast services such as naming lookup
and DHT bootstrapping.


Existing types:
0: RI
1: LS

New types:
2: LS2
3: Encrypted LS2
4: Meta LS2
5: Service Record
6: Service List

Lookup/Store process
--------------------

Types 2-4 may be returned in response to a standard leaseset lookup (type 1).
Type 5 is never returned in response to a lookup.
Types 6 is returned in response to a new service lookup type (type 2).

Only type 2 may be sent in a client-to-client Garlic message.



Format
------

Types 2, 4, and 5 all have a common format::

  Standard LS2 Header
  - as defined below

  Type-Specific Part
  - as defined below in each part

  Standard LS2 Signature:
  - Length as implied by sig type of signing key

Type 3 (Encrypted) does not start with a Destination and has a
different format. See below.

Type 6 (Service List) is an aggregation of several Service Records and has a
different format. See below.


Standard LS2 Header
===================

Types 2, 4, and 5 use the standard LS2 header, specified below:


Format
------
::

  Standard LS2 Header:
  - Destination (387+ bytes)
  - Published timestamp (8 bytes)
  - Expires (4 bytes) (offset from published in ms)
  - Flags (2 bytes)
    Bit order: 15 14 ... 3 2 1 0
    Bit 0: If 0, no offline keys; if 1, offline keys
    Other bits: set to 0 for compatibility with future uses
  - If flag indicates offline keys:
    Transient sig type (2 bytes)
    Transient signing public key (length as implied by sig type)
    Signature of transient sig type and public key, by the destination public key,
    length as implied by destination public key sig type





New DatabaseEntry types
=======================


LeaseSet 2
----------

Changes from existing LeaseSet:

- Add published timestamp, expires timestamp, flags, and properties
- Add encryption type
- Remove revocation key

Lookup with:
    Standard LS flag (1)
Store with:
    Standard LS2 type (2)
Store at:
    Hash of destination, with daily rotation, as for LS 1
Typical expiration:
    10 minutes, as in a regular LS.
Published by:
    Destination

Format
``````
::

  Standard LS2 Header as specified above

  Standard LS2 Type-Specific Part
  - Encryption type (2 bytes)
  - Encryption key (256 bytes or depending on enc type)
  - Number of leases (1 byte)
  - Leases (44 bytes each)
  - Properties (2 bytes if none)

  Standard LS2 Signature:
  - Signature
    If flag indicates offline keys, this is signed by the transient pubkey, otherwise, by the destination pubkey
    Length as implied by sig type of signing key


Flag definition::

  Bit order: 15 14 ... 2 1 0
  Bit 0: If 0, a standard published leaseset.
         If 1, an unpublished leaseset. Should not be flooded, published, or
         sent in response to a query. If this leaseset expires, do not query the
         netdb for a new one.
  Bits 1-15: Unused, set to 0 for compatibility with future uses.

Properties is for future use, no current plans.


Justification
`````````````

- Published: Replaces the complex logic required to determine the 'version' of the
  leaseset. Currently, the version is the expiration of the last-expiring lease,
  and a publishing router must increment that expiration by at least 1ms when
  publishing a leaseset that only removes an older lease.
- Expires: Allows for an expiration of a netdb entry to be earlier than that of
  its last-expiring leaseset. May not be useful for LS2, where leasesets
  are expected to remain with a 11-minute maximum expiration, but
  for other new types, it is necessary (see Meta LS and Service Record below).
  Max is about 49.7 days.
- Flags: For future expansion, and the unpublished/published bit.
- Unpublished/published: For use when sending a database store end-to-end,
  the sending router may wish to indicate that this leaseset should not be
  sent to others. We currently use heuristics to maintain this state.
- Properties: Future expansion


Discussion
``````````

This proposal continues to use the public key in the leaseset for the
end-to-end encryption key, and leaves the public key field in the
Destination unused, as it is now. The encryption type is not specified
in the Destination key certificate, it will remain 0.

Possible extension: Optionally include multiple encryption type/public key pairs,
to ease transition to new encryption types.

An alternative is to specify the encryption type in the Destination key certificate,
use the public key in the Destination, and not use the public key
in the leaseset. A formal proposal for this is in progress.

Benefits of LS2:

- Location of actual public key doesn't change.
- Encryption type, or public key, may change without changing the Destination.
- Removes unused revocation field
- Basic compatibility with other DatabaseEntry types in this proposal
- Could allow multiple encryption types

Drawbacks of LS2:

- Location of public key and encryption type differs from RouterInfo
- Maintains unused public key in leaseset
- Requires implementation across the network; in the alternative, experimental
  encryption types may be used, if allowed by floodfills
  (but see related proposals 136 and 137 about support for experimental sig types).
  The alternative proposal could be easier to implement and test for experimental encryption types.


Notes
`````
- Should we reduce the 8-byte expiration in leases to a 2-byte offset from the
  published timestamp in seconds? Or 4-byte offset in milliseconds?

- If we ever implement revocation, we can do it with an expires field of zero,
  or zero leases, or both. No need for a separate revocation key.


Encrypted LS2
-------------

Goals:

- Add blinding
- Allow multiple sig types
- Don't require any new crypto primitives
- Optionally encrypt to each recipient, revokable
- Support encryption of Standard LS2 and Meta LS2 only

Encrypted LS2 is never sent in an end-to-end garlic message.
Use the standard LS2 as above.

You can't use a b32 for an encrypted LS2, as you don't have the non-blinded public key.
We need a new "b33" format, or use one of the four unused bits at the end of b32 to indicate it's blinded.
You can't use an encrypted LS2 for bittorrent, because of compact announce replies.


Changes from existing encrypted LeaseSet:

- Encrypt the whole thing for security
- Securely encrypt, not with AES only.
- Encrypt to each recipient

Lookup with:
    Standard LS flag (1)
Store with:
    Encrypted LS2 type (3)
Store at:
    Hash of blinded sig type and public key, with daily rotation
Typical expiration:
    10 minutes, as in a regular LS.
Published by:
    Destination


Format
``````
Note that encrypted LS2 is blinded. The Destination is not in the header.
DHT storage location is SHA-256(sig type || blinded public key), and rotated daily.

Blinding is only defined for Ed25519 signing keys (sig type 7).
Blinding is rougly as specified in Tor's rend-spec-v3 appendices A.1 and A.2.
Exact specification including KDF is TBD.


::

  - Blinded Public Key Sig Type (2 bytes)
  - Blinded Public Key (length as implied by sig type)
  - Signature of destination by blinded public key?
  - Published timestamp (8 bytes)
  - Expires (4 bytes) (offset from published in ms)
  - Flags (2 bytes)
    Bit order: 15 14 ... 3 2 1 0
    Bit 0: If 0, no offline keys; if 1, offline keys
    Other bits: set to 0 for compatibility with future uses
  - If flag indicates offline keys:
    Transient sig type (2 bytes)
    Transient signing public key (length as implied by sig type)
    Signature of transient sig type and public key, by the destination public key,
    length as implied by destination public key sig type
  - Length of IV + encrypted data (2 bytes)
  - IV (8 bytes)
  - Outer Encrypted data (AEAD ChaCha/Poly1305)
    Published timestamp is the nonce
    Do we need HMAC or ChaCha only? Probably don't need HMAC, everything is signed.
    KDF TBD, uses Destination
    When decrypted, contains:
    1) Flag - per-client or for everybody? (1 byte)
    If per-client, 2) and 3) are present.
    2) number of recipients to follow (2 bytes)
    3) that many entries of [id_i, iv_i, Encrypted cookie]
    where the recipient looks for his ID, then decrypts the inner.
    The same cookie is encrypted once for each recipient.
    Length of each field TBD.
    KDF and encryption for cookie TBD.
  - Inner Encrypted data (AEAD ChaCha/Poly1305)
    Published timestamp is the nonce
    Do we need HMAC or ChaCha only? Probably don't need HMAC, everything is signed.
    KDF TBD. Used blinded public key. Uses cookie also if per-client.
    When decrypted, the data for type 2 or 4, including the header,
    but without the timestamp and expires fields?
  - Signature (by blinded public key, length as implied by blinded sig type)

Flags: for future use

The signature is of everything above.

Notes
`````
- For multiple clients, encrypted format is probably like GPG/OpenPGP does.
  Asymmetrically encrypt a symmetric key for each recipient. Data is decrypted
  with that asymmetric key. See e.g. [RFC-4880-S5.1]_ IF we can find an
  algorithm that's small and fast.

  - Can we use a shortened version of our current ElGamal, which is 222 bytes
    in and 514 bytes out? That's a little long for each record.

- For a single client, we could just ElG encrypt the whole leaseset, 514 bytes
  isn't so bad.

- If we want to specify the encryption format in the clear, we could have an
  identifier just before the encrypted data, or in the flags.

- A service using encrypted leasesets would publish the encrypted version to the
  floodfills. However, for efficiency, it would send unencrypted leasesets to
  clients in the wrapped garlic message, once authenticated (via whitelist, for
  example).

- Floodfills may limit the max size to a reasonable value to prevent abuse.





Meta LS2
--------

This is used to replace multihoming. Like any leaseset, this is signed by the
creator. This is an authenticated list of destination hashes.

The Meta LS2 is the top of, and possibly intermediate nodes of,
a tree structure.
It contains a number of entries, each pointing to a LS, LS2, or another Meta LS2
to support massive multihoming.
A Meta LS2 may contain a mix of LS, LS2, and Meta LS2 entries.
The leaves of the tree are always a LS or LS2.
The tree is a DAG; loops are prohibited; clients doing lookups must detect and
refuse to follow loops.

A Meta LS2 may have a much longer expiration than a standard LS or LS2.
The top level may have an expiration hours or days after the publication date.
Maximum expiration time will be enforced by floodfills and clients, and is TBD.

The use case for Meta LS2 is massive multihoming, but with no more
protection for correlation of routers to leasesets (at router restart time) than
is provided now with LS or LS2.
This is equivalent to the "facebook" use case, which probably doesn't need
correlation protection. This use case probably needs offline keys,
which are provided in the standard header at each node of the tree.

The back-end protocol for coordination between the leaf routers, intermediate and master Meta LS signers
is not specified here. The requirements are extremely simple - just verify that the peer is up,
and publish a new LS every few hours. The only complexity is for picking new
publishers for the top-level or intermediate-level Meta LSes on failure.

Mix-and-match leasesets where leases from multiple routers are combined, signed, and published
in a single leaseset is documented in proposal 140, "invisible multihoming".
This proposal is untenable as written, because streaming connections would not be
"sticky" to a single router, see http://zzz.ip2/topics/2335 .

The back-end protocol, and interaction with router and client internals, would be
quite complex for invisible multihoming.

To avoid overloading the floodfill for the top-level Meta LS, the expiration should
be several hours at least. Clients must cache the top-level Meta LS, and persist
it across restarts if unexpired.

We need to define some algorithm for clients to traverse the tree, including fallbacks,
so that the usage is dispersed. Some function of hash distance and cost.
If a node has both LS or LS2 and Meta LS, we need to know when it's allowed
to use those leasesets, and when to keep traversing the tree.




Lookup with:
    Standard LS flag (1)
Store with:
    Meta LS2 type (4)
Store at:
    Hash of destination, with daily rotation, as for LS 1
Typical expiration:
    Hours to days. Max TBD.
Published by:
    "master" Destination or coordinator, or intermediate coordinators

Format
``````
::

  Standard LS2 Header as specified above

  Meta LS2 Type-Specific Part
  - Number of entries (1 byte) Maximum TBD
  - Entries. Each entry contains: (39 bytes)
    - Hash (32 bytes)
    - Flags (2 bytes)
      TBD. Set all to zero for compatibility with future uses.
    - Expires (4 bytes) (offset from published in ms)
    - Cost (priority) (1 byte)

  - Number of revocations (1 byte) Maximum TBD
  - Revocations: Each revocation contains: (32 bytes)
    - Hash (32 bytes)

  - Properties (2 bytes if empty)

  Standard LS2 Signature:
  - Signature (40+ bytes)

Flags and properties: for future use


Notes
`````
- A distributed service using this would have one or more "masters" with the
  private key of the service destination. They would (out of band) determine the
  current list of active destinations and would publish the Meta LS2. For
  redundancy, multiple masters could multihome (i.e. concurrently publish) the
  Meta LS2.

- A distributed service could start with a single destination or use old-style
  multihoming, then transition to a Meta LS2. A standard LS lookup could return
  any one of a LS, LS2, or Meta LS2.

- When a service uses a Meta LS2, it has no tunnels (leases).


Service Record
--------------

This is an individual record saying that a destination is participating in a
service. It is sent from the participant to the floodfill. It is not ever sent
individually by a floodfill, but only as a part of a Service List. The Service
Record is also used to revoke participation in a service, by setting the
expiration to zero.

This is not a LS2 but it uses the standard LS2 header and signature format.

Lookup with:
    n/a, see Service List
Store with:
    Service Record type (5)
Store at:
    Hash of service name, with daily rotation
Typical expiration:
    Hours
Published by:
    Destination

Format
``````
::

  Standard LS2 Header as specified above

  Service Record Type-Specific Part
  - Port (2 bytes) (0 if unspecified)
  - Hash of service name (32 bytes)

  Standard LS2 Signature:
  - Signature (40+ bytes)

Flags: for future use

Notes
`````
- If expires is all zeros, the floodfill should revoke the record and no longer
  include it in the service list.

- Storage: The floodfill may strictly throttle storage of these records and
  limit the number of records stored per hash and their expiration. A whilelist
  of hashes may also be used.

- Any other netdb type at the same hash has priority, so a service record can never
  overwrite a LS/RI, but a LS/RI will overwrite all service records at that hash.



Service List
------------

This is nothing like a LS2 and uses a different format.

The service list is created and signed by the floodfill. It is unauthenticated
in that anybody can join a service by publishing a Service Record to a
floodfill.

A Service List contains Short Service Records, not full Service Records. These
contain signatures but only hashes, not full destinations, so they cannot be
verified without the full destination.

The security, if any, and desirability of service lists is TBD.
Floodfills could limit publication, and lookups, to a whitelist of services,
but that whitelist may vary based on implementation, or operator preference.
It may not be possible to achieve consensus on a common, base whitelist
across implementations.

If the service name is included in the service record above,
then floodfill operators may object; if only the hash is included,
there's no verification, and a service record could "get in" ahead of
any other netdb type and get stored in the floodfill.

Lookup with:
    Service List lookup type (2)
Store with:
    Service List type (6)
Store at:
    Hash of service name, with daily rotation
Typical expiration:
    Hours, not specified in the list itself, up to local policy
Published by:
    Nobody, never sent to floodfill, never flooded.

Format
``````
::

  - Hash of the service name (implicit, in the Database Store message)
  - Hash of the Creator (floodfill) (32 bytes)
  - Published timestamp (8 bytes)

  - Number of Short Service Records (1 byte)
  - List of Short Service Records:
    Each Short Service Record contains (90+ bytes)
    - Dest hash (32 bytes)
    - Published timestamp (8 bytes)
    - Expires (4 bytes) (offset from published in ms)
    - Flags (2 bytes)
    - Port (2 bytes)
    - Sig length (2 bytes)
    - Signature of dest (40+ bytes)

  - Number of Revocation Records (1 byte)
  - List of Revocation Records:
    Each Revocation Record contains (86+ bytes)
    - Dest hash (32 bytes)
    - Published timestamp (8 bytes)
    - Flags (2 bytes)
    - Port (2 bytes)
    - Sig length (2 bytes)
    - Signature of dest (40+ bytes)

  - Signature of floodfill (40+ bytes)

To verify signature of the Service List:

- prepend the hash of the service name
- remove the hash of the creator
- Check signature of the modified contents

To verify signature of each Short Service Record:

- Fetch destination
- Check signature of (published timestamp + expires + flags + port + Hash of
  service name)

To verify signature of each Revocation Record:

- Fetch destination
- Check signature of (published timestamp + 4 zero bytes + flags + port + Hash
  of service name)

Notes
`````
- We use signature length instead of sigtype so we can support unknown signature
  types.

- There is no expiration of a service list, recipients may make their own
  decision based on policy or the expiration of the individual records.

- Service Lists are not flooded, only individual Service Records are. Each
  floodfill creates, signs, and caches a Service List. The floodfill uses its
  own policy for cache time and the maximum number of service and revocation
  records.


References
==========

.. [RFC-4880-S5.1]
    https://tools.ietf.org/html/rfc4880#section-5.1
