=================
New netDB Entries
=================
.. meta::
    :author: zzz, str4d, orignal
    :created: 2016-01-16
    :thread: http://zzz.i2p/topics/2051
    :lastupdated: 2019-03-13
    :status: Open
    :supercedes: 110, 120, 121, 122

.. contents::


Status
======

Portions of this proposal are complete, and implemented in 0.9.38 and 0.9.39.
The Common Structures, I2CP, I2NP, and other specifications
are now updated to reflect the changes that are supported now.

The completed portions are still subject to minor revision.
Other portions of this proposal are still in development
and subject to substantial revision.

Service Lookup (types 9 and 11) are low-priority and
unscheduled, and may be split off to a separate proposal.


Overview
========

This is an update and aggregation of the following 4 proposals:

- 110 LS2
- 120 Meta LS2 for massive multihoming
- 121 Encrypted LS2
- 122 Unauthenticated service lookup (anycasting)

These proposals are mostly independent, but for sanity we define and use a
common format for several of them.

The following proposals are somewhat related:

- 140 Invisible Multihoming (incompatible with this proposal)
- 142 New Crypto Template (for new symmetric crypto)
- 144 ECIES-X25519-AEAD-Ratchet
- 145 ECIES-P256
- 146 Red25519
- 148 EdDSA-BLAKE2b-Ed25519


Proposal
========

This proposal defines 5 new DatabaseEntry types and the process for
storing them to and retrieving them from the network database,
as well as the method for signing them and verifying those signatures.

Goals
-----

- Backwards compatible
- LS2 Usable with old-style mulithoming
- No new crypto or primitives required for support
- Maintain decoupling of crypto and signing; support all current and future versions
- Enable optional offline signing keys
- Reduce accuracy of timestamps to reduce fingerprinting
- Enable new crypto for destinations
- Enable massive multihoming
- Fix multiple issues with existing encrypted LS
- Optional blinding to reduce visibility by floodfills
- Encrypted supports both single-key and multiple revocable keys
- Service lookup for easier lookup of outproxies, application DHT bootstrap,
  and other uses
- Don't break anything that relies on 32-byte binary destination hashes, e.g. bittorrent
- Add flexibility to leasesets via properties, like we have in routerinfos.
- Put published timestamp and variable expiration in header, so it works even
  if contents are encrypted (don't derive timestamp from earliest lease)
- All new types live in the same DHT space and same locations as existing leasesets,
  so that users may migrate from the old LS to LS2,
  or change among LS2, Meta, and Encrypted,
  without changing the Destination or hash.
- An existing Destination may be converted to use offline keys,
  or back to online keys, without changing the Destination or hash.


Non-Goals / Out-of-scope
------------------------

- New DHT rotation algorithm or shared random generation
- The specific new encryption type and end-to-end encryption scheme
  to use that new type would be in a separate proposal.
  No new crypto is specified or discussed here.
- New encryption for RIs or tunnel building.
  That would be in a separate proposal.
- Methods of encryption, transmission, and reception of I2NP DLM / DSM / DSRM messages.
  Not changing.
- How to generate and support Meta, including backend inter-router communication, management, failover, and coordination.
  Support may be added to I2CP, or i2pcontrol, or a new protocol.
  This may or may not be standardized.
- How to actually implement and manage longer-expiring tunnels, or cancel existing tunnels.
  That's extremely difficult, and without it, you can't have a reasonable graceful shutdown.
- Threat model changes
- Offline storage format, or methods to store/retrieve/share the data.
- Implementation details are not discussed here and are left to each project.



Justification
-------------

LS2 adds fields for changing encryption type and for future protocol changes.

Encrypted LS2 fixes several security issues with the existing encrypted LS by
using asymmetric encryption of the entire set of leases.

Meta LS2 provides flexible, efficient, effective, and large-scale multihoming.

Service Record and Service List provide anycast services such as naming lookup
and DHT bootstrapping.


NetDB Data Types
----------------

The type numbers are used in the I2NP Database Lookup/Store Messages.

The end-to-end column refers to whether queries/responses are sent to a Destination in a Garlic Message.


Existing types:

==================================  ============= ============
            NetDB Data               Lookup Type   Store Type 
==================================  ============= ============
any                                       0           any     
LS                                        1            1      
RI                                        2            0      
exploratory                               3           DSRM    
==================================  ============= ============

New types:

==================================  ============= ============ ================== ==================
            NetDB Data               Lookup Type   Store Type   Std. LS2 Header?   Sent end-to-end?
==================================  ============= ============ ================== ==================
LS2                                       1            3             yes                 yes
Encrypted LS2                             1            5             no                  no
Meta LS2                                  1            7             yes                 no
Service Record                           n/a           9             yes                 no
Service List                              4           11             no                  no
==================================  ============= ============ ================== ==================



Notes
`````
- Lookup types are currently bits 3-2 in the Database Lookup Message.
  Any additional types would require use of bit 4.

- All store types are odd since upper bits in the Database Store Message
  type field are ignored by old routers.
  We would rather have the parse fail as an LS than as a compressed RI.

- Should type be explicit or implicit or neither in the data covered by the signature?



Lookup/Store process
--------------------

Types 3, 5, and 7 may be returned in response to a standard leaseset lookup (type 1).
Type 9 is never returned in response to a lookup.
Types 11 is returned in response to a new service lookup type (type 11).

Only type 3 may be sent in a client-to-client Garlic message.



Format
------

Types 3, 7, and 9 all have a common format::

  Standard LS2 Header
  - as defined below

  Type-Specific Part
  - as defined below in each part

  Standard LS2 Signature:
  - Length as implied by sig type of signing key

Type 5 (Encrypted) does not start with a Destination and has a
different format. See below.

Type 11 (Service List) is an aggregation of several Service Records and has a
different format. See below.


Privacy/Security Considerations
-------------------------------

TBD



Standard LS2 Header
===================

Types 3, 7, and 9 use the standard LS2 header, specified below:


Format
------
::

  Standard LS2 Header:
  - Type (1 byte)
    Not actually in header, but part of data covered by signature.
    Take from field in Database Store Message.
  - Destination (387+ bytes)
  - Published timestamp (4 bytes, big endian, seconds since epoch, rolls over in 2106)
  - Expires (2 bytes, big endian) (offset from published timestamp in seconds, 18.2 hours max)
  - Flags (2 bytes)
    Bit order: 15 14 ... 3 2 1 0
    Bit 0: If 0, no offline keys; if 1, offline keys
    Bit 1: If 0, a standard published leaseset.
           If 1, an unpublished leaseset. Should not be flooded, published, or
           sent in response to a query. If this leaseset expires, do not query the
           netdb for a new one.
    Bits 2-15: set to 0 for compatibility with future uses
  - If flag indicates offline keys, the offline signature section:
    Expires timestamp (4 bytes, big endian, seconds since epoch, rolls over in 2106)
    Transient sig type (2 bytes, big endian)
    Transient signing public key (length as implied by sig type)
    Signature of expires timestamp, transient sig type, and public key, by the destination public key,
    length as implied by destination public key sig type.
    This section can, and should, be generated offline.


Justification
`````````````

- Unpublished/published: For use when sending a database store end-to-end,
  the sending router may wish to indicate that this leaseset should not be
  sent to others. We currently use heuristics to maintain this state.

- Published: Replaces the complex logic required to determine the 'version' of the
  leaseset. Currently, the version is the expiration of the last-expiring lease,
  and a publishing router must increment that expiration by at least 1ms when
  publishing a leaseset that only removes an older lease.

- Expires: Allows for an expiration of a netdb entry to be earlier than that of
  its last-expiring leaseset. May not be useful for LS2, where leasesets
  are expected to remain with a 11-minute maximum expiration, but
  for other new types, it is necessary (see Meta LS and Service Record below).

- Offline keys are optional, to reduce initial/required implementation complexity.


Issues
------

- Could reduce timestamp accuracy even more (10 minutes?) but would have to add
  version number. This could break multihoming, unless we have order preserving encryption?
  Probably can't do without timestamps at all.

- Alternative: 3 byte timestamp (epoch / 10 minutes), 1-byte version, 2-byte expires

- Is type explicit or implicit in data / signature? "Domain" constants for signature?


Notes
`````

- Routers should not publish a LS more than once a second.
  If they do, they must artificially increment the published timestamp by 1
  over the previously published LS.

- Router implementations could cache the transient keys and signature to
  avoid verification every time. In particular, floodfills, and routers at
  both ends of long-lived connections, could benefit from this.

- Offline keys and signature are only appropriate for long-lived destinations,
  i.e. servers, not clients.



New DatabaseEntry types
=======================


LeaseSet 2
----------

Changes from existing LeaseSet:

- Add published timestamp, expires timestamp, flags, and properties
- Add encryption type
- Remove revocation key

Lookup with
    Standard LS flag (1)
Store with
    Standard LS2 type (3)
Store at
    Hash of destination
    This hash is then used to generate the daily "routing key", as in LS1
Typical expiration
    10 minutes, as in a regular LS.
Published by
    Destination

Format
``````
::

  Standard LS2 Header as specified above

  Standard LS2 Type-Specific Part
  - Properties (Mapping as specified in common structures spec, 2 zero bytes if none)
  - Number of key sections to follow (1 byte, max TBD)
  - Key sections:
    - Encryption type (2 bytes, big endian)
    - Encryption key length (2 bytes, big endian)
      This is explicit, so floodfills can parse LS2 with unknown encryption types.
    - Encryption key (number of bytes specified)
  - Number of lease2s (1 byte)
  - Lease2s (40 bytes each)
    These are leases, but with a 4-byte instead of an 8-byte expiration,
    seconds since the epoch (rolls over in 2106)

  Standard LS2 Signature:
  - Signature
    If flag indicates offline keys, this is signed by the transient pubkey, otherwise, by the destination pubkey
    Length as implied by sig type of signing key
    The signature is of everything above.




Justification
`````````````

- Properties: Future expansion and flexibility.
  Placed first in case necessary for parsing of the remaining data.

- Multiple encryption type/public key pairs are
  to ease transition to new encryption types. The other way to do it
  is to publish multiple leasesets, possibly using the same tunnels,
  as we do now for DSA and EdDSA destinations.
  Identification of the incoming encryption type on a tunnel
  may be done with the existing session tag mechanism,
  and/or trial decryption using each key. Lengths of the incoming
  messages may also provide a clue.

Discussion
``````````

This proposal continues to use the public key in the leaseset for the
end-to-end encryption key, and leaves the public key field in the
Destination unused, as it is now. The encryption type is not specified
in the Destination key certificate, it will remain 0.

A rejected alternative is to specify the encryption type in the Destination key certificate,
use the public key in the Destination, and not use the public key
in the leaseset. We do not plan to do this.

Benefits of LS2:

- Location of actual public key doesn't change.
- Encryption type, or public key, may change without changing the Destination.
- Removes unused revocation field
- Basic compatibility with other DatabaseEntry types in this proposal
- Allow multiple encryption types

Drawbacks of LS2:

- Location of public key and encryption type differs from RouterInfo
- Maintains unused public key in leaseset
- Requires implementation across the network; in the alternative, experimental
  encryption types may be used, if allowed by floodfills
  (but see related proposals 136 and 137 about support for experimental sig types).
  The alternative proposal could be easier to implement and test for experimental encryption types.


New Encryption Issues
`````````````````````
Some of this is out-of-scope for this proposal,
but putting notes here for now as we don't have
a separate encryption proposal yet.
See also the ECIES proposals 144 and 145.

- The encryption type represents the combination
  of curve, key length, and end-to-end scheme,
  including KDF and MAC, if any.

- We have included a key length field, so that the LS2 is
  parsable and verifiable by the floodfill even for unknown encryption types.

- The first new encryption type to be proposed will
  probably be ECIES/X25519. How it's used end-to-end
  (either a slightly modified version of ElGamal/AES+SessionTag
  or something completely new, e.g. ChaCha/Poly) will be specified
  in one or more separate proposals.
  See also the ECIES proposals 144 and 145.


Notes
`````
- 8-byte expiration in leases changed to 4 bytes.

- If we ever implement revocation, we can do it with an expires field of zero,
  or zero leases, or both. No need for a separate revocation key.

- Encryption keys are in order of server preference, most-preferred first.
  Default client behavior is to select the first key with
  a supported encryption type. Clients may use other selection algorithms
  based on encryption support, relative performance, and other factors.


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


Changes from existing encrypted LeaseSet:

- Encrypt the whole thing for security
- Securely encrypt, not with AES only.
- Encrypt to each recipient

Lookup with
    Standard LS flag (1)
Store with
    Encrypted LS2 type (5)
Store at
    Hash of blinded sig type and blinded public key
    Two byte sig type (big endian, e.g. 0x000b) || blinded public key
    This hash is then used to generate the daily "routing key", as in LS1
Typical expiration
    10 minutes, as in a regular LS, or hours, as in a meta LS.
Published by
    Destination


Definitions
```````````
We define the following functions corresponding to the cryptographic building blocks used
for encrypted LS2:

CSRNG(n)
    n-byte output from a cryptographically-secure random number generator.

    In addition to the requirement of CSRNG being cryptographically-secure (and thus
    suitable for generating key material), it MUST be safe
    for some n-byte output to be used for key material when the byte sequences immediately
    preceding and following it are exposed on the network (such as in a salt, or encrypted
    padding). Implementations that rely on a potentially-untrustworthy source should hash
    any output that is to be exposed on the network [PRNG-REFS]_.

H(p, d)
    SHA-256 hash function that takes a personalization string p and data d, and
    produces an output of length 32 bytes.

    Use SHA-256 as follows::

        H(p, d) := SHA-256(p || d)

STREAM
    The ChaCha20 stream cipher as specified in [RFC-7539-S2.4]_, with the initial counter
    set to 1. S_KEY_LEN = 32 and S_IV_LEN = 12.

    ENCRYPT(k, iv, plaintext)
        Encrypts plaintext using the cipher key k, and nonce iv which MUST be unique for
        the key k. Returns a ciphertext that is the same size as the plaintext.

        The entire ciphertext must be indistinguishable from random if the key is secret.

    DECRYPT(k, iv, ciphertext)
        Decrypts ciphertext using the cipher key k, and nonce iv. Returns the plaintext.


SIG
    The RedDSA signature scheme (corresponding to SigType 11) with key blinding.
    It has the following functions:

    DERIVE_PUBLIC(privkey)
        Returns the public key corresponding to the given private key.

    SIGN(privkey, m)
        Returns a signature by the private key privkey over the given message m.

    VERIFY(pubkey, m, sig)
        Verifies the signature sig against the public key pubkey and message m. Returns
        true if the signature is valid, false otherwise.

    It must also support the following key blinding operations:

    GENERATE_ALPHA(data, secret)
        Generate alpha for those who know the data and an optional secret.
        The result must be identically distributed as the private keys.

    BLIND_PRIVKEY(privkey, alpha)
        Blinds a private key, using a secret alpha.

    BLIND_PUBKEY(pubkey, alpha)
        Blinds a public key, using a secret alpha.
        For a given keypair (privkey, pubkey) the following relationship holds::

            BLIND_PUBKEY(pubkey, alpha) ==
            DERIVE_PUBLIC(BLIND_PRIVKEY(privkey, alpha))

DH
    X25519 public key agreement system. Private keys of 32 bytes, public keys of 32
    bytes, produces outputs of 32 bytes. It has the following
    functions:

    GENERATE_PRIVATE()
        Generates a new private key.

    DERIVE_PUBLIC(privkey)
        Returns the public key corresponding to the given private key.

    DH(privkey, pubkey)
        Generates a shared secret from the given private and public keys.

HKDF(salt, ikm, info, n)
    A cryptographic key derivation function which takes some input key material ikm (which
    should have good entropy but is not required to be a uniformly random string), a salt
    of length 32 bytes, and a context-specific 'info' value, and produces an output
    of n bytes suitable for use as key material.

    Use HKDF as specified in [RFC-5869]_, using the HMAC hash function SHA-256
    as specified in [RFC-2104]_. This means that SALT_LEN is 32 bytes max.


Format
``````
The encrypted LS2 format consists of three nested layers:

- An outer layer containing the necessary plaintext information for storage and retrieval.
- A middle layer that handles client authentication.
- An inner layer that contains the actual LS2 data.

The overall format looks like::

    Layer 0 data + Enc(layer 1 data + Enc(layer 2 data)) + Signature

Note that encrypted LS2 is blinded. The Destination is not in the header.
DHT storage location is SHA-256(sig type || blinded public key), and rotated daily.

Does NOT use the standard LS2 header specified above.

Layer 0 (outer)
~~~~~~~~~~~~~~~
Type
    1 byte

    Not actually in header, but part of data covered by signature.
    Take from field in Database Store Message.

Blinded Public Key Sig Type
    2 bytes, big endian
    This will always be type 11, identifying a Red25519 blinded key.

Blinded Public Key
    Length as implied by sig type

Published timestamp
    4 bytes, big endian

    Seconds since epoch, rolls over in 2106

Expires
    2 bytes, big endian

    Offset from published timestamp in seconds, 18.2 hours max

Flags
    2 bytes

    Bit order: 15 14 ... 3 2 1 0

    Bit 0: If 0, no offline keys; if 1, offline keys

    Other bits: set to 0 for compatibility with future uses

Transient key data
    Present if flag indicates offline keys

    Expires timestamp
        4 bytes, big endian

        Seconds since epoch, rolls over in 2106

    Transient sig type
        2 bytes, big endian

    Transient signing public key
        Length as implied by sig type

    Signature
        Length as implied by blinded public key sig type

        Over expires timestamp, transient sig type, and transient public key.

        Verified with the blinded public key.

lenOuterCiphertext
    2 bytes, big endian

outerCiphertext
    lenOuterCiphertext bytes

    Encrypted layer 1 data. See below for key derivation and encryption algorithms.

Signature
    Length as implied by sig type of the signing key used

    The signature is of everything above.

    If the flag indicates offline keys, the signature is verified with the transient
    public key. Otherwise, the signature is verified with the blinded public key.


Layer 1 (middle)
~~~~~~~~~~~~~~~~
Flags
    1 byte
    
    Bit order: 76543210

    Bit 0: 0 for everybody, 1 for per-client, auth section to follow

    Bits 3-1: Authentication scheme, only if bit 1 is set to 1 for per-client, otherwise 0
              0: DH client authentication (or no per-client authentication)
              1: PSK client authentication

    Bits 7-4: Unused, set to 0 for future compatibility

DH client auth data
    Present if flag bit 0 is set to 1 and flag bits 3-1 are set to 0.

    ephemeralPublicKey
        32 bytes

    clients
        2 bytes, big endian

        Number of authClient entries to follow, 40 bytes each

    authClient
        Authorization data for a single client.
        See below for the per-client authorization algorithm.

        clientID_i
            8 bytes

        clientCookie_i
            32 bytes

PSK client auth data
    Present if flag bit 0 is set to 1 and flag bits 3-1 are set to 0.

    authSalt
        32 bytes

    clients
        2 bytes, big endian

        Number of authClient entries to follow, 40 bytes each

    authClient
        Authorization data for a single client.
        See below for the per-client authorization algorithm.

        clientID_i
            8 bytes

        clientCookie_i
            32 bytes


innerCiphertext
    Length implied by lenOuterCiphertext (whatever data remains)

    Encrypted layer 2 data. See below for key derivation and encryption algorithms.


Layer 2 (inner)
~~~~~~~~~~~~~~~
Type
    1 byte

    Either 3 (LS2) or 7 (Meta LS2)

Data
    LeaseSet2 data for the given type.

    Includes the header and signature.


Blinding Key Derivation
```````````````````````

We use the following scheme for key blinding,
based on Ed25519 and ZCash RedDSA [ZCASH]_.
The Re25519 signatures are over the Ed25519 curve, using SHA-512 for the hash.

We do not use Tor's rend-spec-v3.txt appendix A.2 [TOR-REND-SPEC-V3]_,
which has similar design goals, because its blinded public keys
may be off the prime-order subgroup, with unknown security implications.


Goals
~~~~~

- Signing public key in unblinded destination must be
  Ed25519 (sig type 7) or Red25519 (sig type 11);
  no other sig types are supported
- If the signing public key is offline, the transient signing public key must also be Ed25519
- Blinding is computationally simple
- Use existing cryptographic primitives
- Blinded public keys cannot be unblinded
- Blinded public keys must be on the Ed25519 curve and prime-order subgroup
- Must know the destination's signing public key
  (full destination not required) to derive the blinded public key
- Optionally provide for an additional secret required to derive the blinded public key


Security
~~~~~~~~

The security of a blinding scheme requires that the
distribution of alpha is the same as the unblinded private keys.
However, when we blind an Ed25519 private key (sig type 7)
to a Red25519 private key (sig type 11), the distribution is different.
To meet the requirements of zcash section 4.1.6.1 [ZCASH]_,
Red25519 (sig type 11) should be used for the unblinded keys as well, so that
"the combination of a re-randomized public key and signature(s)
under that key do not reveal the key from which it was re-randomized."
We allow type 7 for existing destinations, but recommend
type 11 for new destinations that will be encrypted.



Definitions
~~~~~~~~~~~

B
    The Ed25519 base point (generator) 2^255 - 19 as in [ED25519-REFS]_

L
    The Ed25519 order 2^252 + 27742317777372353535851937790883648493
    as in [ED25519-REFS]_

DERIVE_PUBLIC(a)
    Convert a private key to public, as in Ed25519 (mulitply by G)

alpha
    A 32-byte random number known to those who know the destination.

GENERATE_ALPHA(destination, date, secret)
    Generate alpha for the current date, for those who know the destination and the secret.
    The result must be identically distributed as Ed25519 private keys.

a
    The unblinded 32-byte EdDSA or RedDSA signing private key used to sign the destination

A
    The unblinded 32-byte EdDSA or RedDSA signing public key in the destination,
    = DERIVE_PUBLIC(a), as in Ed25519

a'
    The blinded 32-byte EdDSA signing private key used to sign the encrypted leaseset
    This is a valid EdDSA private key.

A'
    The blinded 32-byte EdDSA signing public key in the Destination,
    may be generated with DERIVE_PUBLIC(a'), or from A and alpha.
    This is a valid EdDSA public key, on the curve and on the prime-order subgroup.

LEOS2IP(x)
    Flip the order of the input bytes to little-endian

H*(x)
    32 bytes = (LEOS2IP(SHA512(x))) mod B, same as in Ed25519 hash-and-reduce


Blinding Calculations
~~~~~~~~~~~~~~~~~~~~~

A new secret alpha and blinded keys must be generated each day (UTC).
The secret alpha and the blinded keys are calculated as follows.

GENERATE_ALPHA(destination, date, secret), for all parties:

.. raw:: html

  {% highlight lang='text' %}
// GENERATE_ALPHA(destination, date, secret)

  // secret is optional, else zero-length
  A = destination's signing public key
  stA = signature type of A, 2 bytes big endian (0x0007 or 0x000b)
  stA' = signature type of blinded public key A', 2 bytes big endian (0x000b)
  keydata = A || stA || stA'
  datestring = 8 bytes ASCII YYYYMMDD from the current date UTC
  secret = UTF-8 encoded string
  seed = HKDF(H("I2PGenerateAlpha", keydata), datestring || secret, "i2pblinding1", 64)
  // treat seed as a 64 byte little-endian value
  alpha = seed mod L
{% endhighlight %}

BLIND_PRIVKEY(), for the owner publishing the leaseset:

.. raw:: html

  {% highlight lang='text' %}
// BLIND_PRIVKEY()

  alpha = GENERATE_ALPHA(destination, date, secret)
  a = destination's signing private key
  // Addition using scalar arithmentic
  blinded signing private key = a' = BLIND_PRIVKEY(a, alpha) = (a + alpha) mod L
  blinded signing public key = A' = DERIVE_PUBLIC(a')
{% endhighlight %}

BLIND_PUBKEY(), for the clients retrieving the leaseset:

.. raw:: html

  {% highlight lang='text' %}
// BLIND_PUBKEY()

  alpha = GENERATE_ALPHA(destination, date, secret)
  A = destination's signing public key
  // Addition using group elements (points on the curve)
  blinded public key = A' = BLIND_PUBKEY(A, alpha) = A + DERIVE_PUBLIC(alpha)
{% endhighlight %}

Both methods of calculating A' yield the same result, as required.



Signing
~~~~~~~

The unblinded leaseset is signed by the unblinded Ed25519 or Red25519 signing private key
and verified with the unblinded Ed25519 or Red25519 signing public key (sig types 7 or 11) as usual.

If the signing public key is offline,
the unblinded leaseset is signed by the unblinded transient Ed25519 or Red25519 signing private key
and verified with the unblinded Ed25519 or Red25519 transient signing public key (sig types 7 or 11) as usual.
See below for additional notes on offline keys for encrytped leasesets.

For signing of the encrypted leaseset, we use Red25519, based on RedDSA [ZCASH]_
to sign and verify with blinded keys.
The Red25519 signatures are over the Ed25519 curve, using SHA-512 for the hash.

Red25519 is identical to standard Ed25519 except as specified below.


Sign/Verify Calculations
~~~~~~~~~~~~~~~~~~~~~~~~

The outer portion of the encrypted leaseset uses Red25519 keys and signatures.

Red25519 is almost identical to Ed25519. There are two differences:

Red25519 private keys are generated from random numbers and then must be reduced mod L, where L is defined above.
Ed25519 private keys are generated from random numbers and then "clamped" using
bitwise masking to bytes 0 and 31. This is not done for Red25519.
The functions GENERATE_ALPHA() and BLIND_PRIVKEY() defined above generate proper
Red25519 private keys using mod L.

In Red25519, the calculation of r for signing uses additional random data,
and uses the public key value rather than the hash of the private key.
Because of the random data, every Red25519 signature is different, even
when signing the same data with the same key.

Signing:

.. raw:: html

  {% highlight lang='text' %}
T = 80 random bytes
  r = H*(T || publickey || message)
  // rest is the same as in Ed25519
{% endhighlight %}

Verification:

.. raw:: html

  {% highlight lang='text' %}
// same as in Ed25519
{% endhighlight %}



Encryption and processing
`````````````````````````
Derivation of subcredentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
As part of the blinding process, we need to ensure that an encrypted LS2 can only be
decrypted by someone who knows the corresponding Destination's signing public key.
The full Destination is not required.
To achieve this, we derive a credential from the signing public key:

.. raw:: html

  {% highlight lang='text' %}
A = destination's signing public key
  stA = signature type of A, 2 bytes big endian (0x0007 or 0x000b)
  stA' = signature type of A', 2 bytes big endian (0x000b)
  keydata = A || stA || stA'
  credential = H("credential", keydata)
{% endhighlight %}

The personalization string ensures that the credential does not collide with any hash used
as a DHT lookup key, such as the plain Destination hash.

For a given blinded key, we can then derive a subcredential:

.. raw:: html

  {% highlight lang='text' %}
subcredential = H("subcredential", credential || blindedPublicKey)
{% endhighlight %}

The subcredential is included in the key derivation processes below, which binds those
keys to knowledge of the Destination's signing public key.

Layer 1 encryption
~~~~~~~~~~~~~~~~~~
First, the input to the key derivation process is prepared:

.. raw:: html

  {% highlight lang='text' %}
outerInput = subcredential || publishedTimestamp
{% endhighlight %}

Next, a random salt is generated:

.. raw:: html

  {% highlight lang='text' %}
outerSalt = CSRNG(32)
{% endhighlight %}

Then the key used to encrypt layer 1 is derived:

.. raw:: html

  {% highlight lang='text' %}
keys = HKDF(outerSalt, outerInput, "ELS2_L1K", 44)
  outerKey = keys[0:31]
  outerIV = keys[32:43]
{% endhighlight %}

Finally, the layer 1 plaintext is encrypted and serialized:

.. raw:: html

  {% highlight lang='text' %}
outerCiphertext = outerSalt || ENCRYPT(outerKey, outerIV, outerPlaintext)
{% endhighlight %}

Layer 1 decryption
~~~~~~~~~~~~~~~~~~
The salt is parsed from the layer 1 ciphertext:

.. raw:: html

  {% highlight lang='text' %}
outerSalt = outerCiphertext[0:31]
{% endhighlight %}

Then the key used to encrypt layer 1 is derived:

.. raw:: html

  {% highlight lang='text' %}
outerInput = subcredential || publishedTimestamp
  keys = HKDF(outerSalt, outerInput, "ELS2_L1K", 44)
  outerKey = keys[0:31]
  outerIV = keys[32:43]
{% endhighlight %}

Finally, the layer 1 ciphertext is decrypted:

.. raw:: html

  {% highlight lang='text' %}
outerPlaintext = DECRYPT(outerKey, outerIV, outerCiphertext[32:end])
{% endhighlight %}

Layer 2 encryption
~~~~~~~~~~~~~~~~~~
When client authorization is enabled, ``authCookie`` is calculated as described below.
When client authorization is disabled, ``authCookie`` is the zero-length byte array.

Encryption proceeds in a similar fashion to layer 1:

.. raw:: html

  {% highlight lang='text' %}
innerInput = authCookie || subcredential || publishedTimestamp
  innerSalt = CSRNG(32)
  keys = HKDF(innerSalt, innerInput, "ELS2_L2K", 44)
  innerKey = keys[0:31]
  innerIV = keys[32:43]
  innerCiphertext = innerSalt || ENCRYPT(innerKey, innerIV, innerPlaintext)
{% endhighlight %}

Layer 2 decryption
~~~~~~~~~~~~~~~~~~
When client authorization is enabled, ``authCookie`` is calculated as described below.
When client authorization is disabled, ``authCookie`` is the zero-length byte array.

Decryption proceeds in a similar fashion to layer 1:

.. raw:: html

  {% highlight lang='text' %}
innerInput = authCookie || subcredential || publishedTimestamp
  innerSalt = innerCiphertext[0:31]
  keys = HKDF(innerSalt, innerInput, "ELS2_L2K", 44)
  innerKey = keys[0:31]
  innerIV = keys[32:43]
  innerPlaintext = DECRYPT(innerKey, innerIV, innerCiphertext[32:end])
{% endhighlight %}


Per-client authorization
````````````````````````
When client authorization is enabled for a Destination, the server maintains a list of
clients they are authorizing to decrypt the encrypted LS2 data. The data stored per-client
depends on the authorization mechanism, and includes some form of key material that each
client generates and sends to the server via a secure out-of-band mechanism.

There are two alternatives for implementing per-client authorization:

DH client authorization
~~~~~~~~~~~~~~~~~~~~~~~
Each client generates a DH keypair ``[csk_i, cpk_i]``, and sends the public key ``cpk_i``
to the server.

Server processing
^^^^^^^^^^^^^^^^^
The server generates a new ``authCookie`` and an ephemeral DH keypair:

.. raw:: html

  {% highlight lang='text' %}
authCookie = CSRNG(32)
  esk = GENERATE_PRIVATE()
  epk = DERIVE_PUBLIC(esk)
{% endhighlight %}

Then for each authorized client, the server encrypts ``authCookie`` to its public key:

.. raw:: html

  {% highlight lang='text' %}
sharedSecret = DH(esk, cpk_i)
  authInput = sharedSecret || cpk_i || subcredential || publishedTimestamp
  okm = HKDF(epk, authInput, "ELS2_XCA", 52)
  clientKey_i = okm[0:31]
  clientIV_i = okm[32:43]
  clientID_i = okm[44:51]
  clientCookie_i = ENCRYPT(clientKey_i, clientIV_i, authCookie)
{% endhighlight %}

The server places each ``[clientID_i, clientCookie_i]`` tuple into layer 1 of the
encrypted LS2, along with ``epk``.

Client processing
^^^^^^^^^^^^^^^^^
The client uses its private key to derive its expected client identifier ``clientID_i``,
encryption key ``clientKey_i``, and encryption IV ``clientIV_i``:

.. raw:: html

  {% highlight lang='text' %}
sharedSecret = DH(csk_i, epk)
  authInput = sharedSecret || cpk_i || subcredential || publishedTimestamp
  okm = HKDF(epk, authInput, "ELS2_XCA", 52)
  clientKey_i = okm[0:31]
  clientIV_i = okm[32:43]
  clientID_i = okm[44:51]
{% endhighlight %}

Then the client searches the layer 1 authorization data for an entry that contains
``clientID_i``. If a matching entry exists, the client decrypts it to obtain
``authCookie``:

.. raw:: html

  {% highlight lang='text' %}
authCookie = DECRYPT(clientKey_i, clientIV_i, clientCookie_i)
{% endhighlight %}

Pre-shared key client authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each client generates a secret 32-byte key ``psk_i``, and sends it to the server.

Server processing
^^^^^^^^^^^^^^^^^
The server generates a new ``authCookie`` and salt:

.. raw:: html

  {% highlight lang='text' %}
authCookie = CSRNG(32)
  authSalt = CSRNG(32)
{% endhighlight %}

Then for each authorized client, the server encrypts ``authCookie`` to its pre-shared key:

.. raw:: html

  {% highlight lang='text' %}
authInput = psk_i || subcredential || publishedTimestamp
  okm = HKDF(authSalt, authInput, "ELS2PSKA", 52)
  clientKey_i = okm[0:31]
  clientIV_i = okm[32:43]
  clientID_i = okm[44:51]
  clientCookie_i = ENCRYPT(clientKey_i, clientIV_i, authCookie)
{% endhighlight %}

The server places each ``[clientID_i, clientCookie_i]`` tuple into layer 1 of the
encrypted LS2, along with ``authSalt``.

Client processing
^^^^^^^^^^^^^^^^^
The client uses its pre-shared key to derive its expected client identifier ``clientID_i``,
encryption key ``clientKey_i``, and encryption IV ``clientIV_i``:

.. raw:: html

  {% highlight lang='text' %}
authInput = psk_i || subcredential || publishedTimestamp
  okm = HKDF(authSalt, authInput, "ELS2PSKA", 52)
  clientKey_i = okm[0:31]
  clientIV_i = okm[32:43]
  clientID_i = okm[44:51]
{% endhighlight %}

Then the client searches the layer 1 authorization data for an entry that contains
``clientID_i``. If a matching entry exists, the client decrypts it to obtain
``authCookie``:

.. raw:: html

  {% highlight lang='text' %}
authCookie = DECRYPT(clientKey_i, clientIV_i, clientCookie_i)
{% endhighlight %}

Security considerations
~~~~~~~~~~~~~~~~~~~~~~~
Both of the client authorization mechanisms above provide privacy for client membership.
An entity that only knows the Destination can see how many clients are subscribed at any
time, but cannot track which clients are being added or revoked.

Servers SHOULD randomize the order of clients each time they generate an encrypted LS2, to
prevent clients learning their position in the list and inferring when other clients have
been added or revoked.

A server MAY choose to hide the number of clients that are subscribed by inserting random
entries into the list of authorization data.

Advantages of DH client authorization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Security of the scheme is not solely dependent on the out-of-band exchange of client key
  material. The client's private key never needs to leave their device, and so an
  adversary that is able to intercept the out-of-band exchange, but cannot break the DH
  algorithm, cannot decrypt the encrypted LS2, or determine how long the client is given
  access.

Downsides of DH client authorization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Requires N + 1 DH operations on the server side for N clients.
- Requires one DH operation on the client side.

Advantages of PSK client authorization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Requires no DH operations.

Downsides of PSK client authorization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Security of the scheme is critically dependent on the out-of-band exchange of client key
  material. An adversary that intercepts the exchange for a particular client can decrypt
  any subsequent encrypted LS2 for which that client is authorized, as well as determine
  when the client's access is revoked.


Encrypted LS with Base 32 Addresses
```````````````````````````````````

See proposal 149.

You can't use an encrypted LS2 for bittorrent, because of compact announce replies which are 32 bytes.
The 32 bytes contain only the hash. There is no room for an indication that the
leaseset is encrypted, or the signature types.



Encrypted LS with Offline Keys
``````````````````````````````
For encrypted leasesets with offline keys, the blinded private keys must also be generated offline,
one for each day.

As the optional offline signature block is in the cleartext part of the encryted leaseset,
anybody scraping the floodfills could use this to track the leaseset (but not decrypt it)
over several days.
To prevent this, the owner of the keys should generate new transient keys
for each day as well.
Both the transient and blinded keys can be generated in advance, and delivered to the router
in a batch.

There is no file format defined in this proposal for packaging multiple transient and
blinded keys and providing them to the client or router.
There is no I2CP protocol enhancement defined in this proposal to support
encrypted leasesets with offline keys.


Issues
``````

- If we care about speed, we could use keyed-BLAKE2b instead. It has an output
  size large enough to accommodate the largest n we require (or we can call it once per
  desired key with a counter argument). BLAKE2b is much faster than SHA-256, and
  keyed-BLAKE2b would reduce the total number of hash function calls.
  [UNSCIENTIFIC-KDF-SPEEDS]_


Notes
`````

- A service using encrypted leasesets would publish the encrypted version to the
  floodfills. However, for efficiency, it would send unencrypted leasesets to
  clients in the wrapped garlic message, once authenticated (via whitelist, for
  example).

- Floodfills may limit the max size to a reasonable value to prevent abuse.

- After decryption, several checks should be made, including that
  the inner timestamp and expiration match those at the top level.

- ChaCha20 was selected over AES. While the speeds are similar if AES
  hardware support is available, ChaCha20 is 2.5-3x faster when
  AES hardware support is not available, such as on lower-end ARM devices.


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
The top level may have an expiration several hours after the publication date.
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
"sticky" to a single router, see http://zzz.i2p/topics/2335 .

The back-end protocol, and interaction with router and client internals, would be
quite complex for invisible multihoming.

To avoid overloading the floodfill for the top-level Meta LS, the expiration should
be several hours at least. Clients must cache the top-level Meta LS, and persist
it across restarts if unexpired.

We need to define some algorithm for clients to traverse the tree, including fallbacks,
so that the usage is dispersed. Some function of hash distance, cost, and randomness.
If a node has both LS or LS2 and Meta LS, we need to know when it's allowed
to use those leasesets, and when to keep traversing the tree.




Lookup with
    Standard LS flag (1)
Store with
    Meta LS2 type (7)
Store at
    Hash of destination
    This hash is then used to generate the daily "routing key", as in LS1
Typical expiration
    Hours. Max 18.2 hours (65535 seconds)
Published by
    "master" Destination or coordinator, or intermediate coordinators

Format
``````
::

  Standard LS2 Header as specified above

  Meta LS2 Type-Specific Part
  - Properties (Mapping as specified in common structures spec, 2 zero bytes if none)
  - Number of entries (1 byte) Maximum TBD
  - Entries. Each entry contains: (40 bytes)
    - Hash (32 bytes)
    - Flags (3 bytes)
      TBD. Set all to zero for compatibility with future uses.
      TODO: Use a few bits to (optionally) indicate the type of the LS it is referencing.
      All zeros means don't know.
    - Cost (priority) (1 byte)
    - Expires (4 bytes) (4 bytes, big endian, seconds since epoch, rolls over in 2106)
  - Number of revocations (1 byte) Maximum TBD
  - Revocations: Each revocation contains: (32 bytes)
    - Hash (32 bytes)

  Standard LS2 Signature:
  - Signature (40+ bytes)
    The signature is of everything above.

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

Lookup with
    n/a, see Service List
Store with
    Service Record type (9)
Store at
    Hash of service name
    This hash is then used to generate the daily "routing key", as in LS1
Typical expiration
    Hours. Max 18.2 hours (65535 seconds)
Published by
    Destination

Format
``````
::

  Standard LS2 Header as specified above

  Service Record Type-Specific Part
  - Port (2 bytes, big endian) (0 if unspecified)
  - Hash of service name (32 bytes)

  Standard LS2 Signature:
  - Signature (40+ bytes)
    The signature is of everything above.


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

Lookup with
    Service List lookup type (11)
Store with
    Service List type (11)
Store at
    Hash of service name
    This hash is then used to generate the daily "routing key", as in LS1
Typical expiration
    Hours, not specified in the list itself, up to local policy
Published by
    Nobody, never sent to floodfill, never flooded.

Format
``````
Does NOT use the standard LS2 header specified above.

::

  - Type (1 byte)
    Not actually in header, but part of data covered by signature.
    Take from field in Database Store Message.
  - Hash of the service name (implicit, in the Database Store message)
  - Hash of the Creator (floodfill) (32 bytes)
  - Published timestamp (8 bytes, big endian)

  - Number of Short Service Records (1 byte)
  - List of Short Service Records:
    Each Short Service Record contains (90+ bytes)
    - Dest hash (32 bytes)
    - Published timestamp (8 bytes, big endian)
    - Expires (4 bytes, big endian) (offset from published in ms)
    - Flags (2 bytes)
    - Port (2 bytes, big endian)
    - Sig length (2 bytes, big endian)
    - Signature of dest (40+ bytes)

  - Number of Revocation Records (1 byte)
  - List of Revocation Records:
    Each Revocation Record contains (86+ bytes)
    - Dest hash (32 bytes)
    - Published timestamp (8 bytes, big endian)
    - Flags (2 bytes)
    - Port (2 bytes, big endian)
    - Sig length (2 bytes, big endian)
    - Signature of dest (40+ bytes)

  - Signature of floodfill (40+ bytes)
    The signature is of everything above.

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
- We use signature length instead of sig type so we can support unknown signature
  types.

- There is no expiration of a service list, recipients may make their own
  decision based on policy or the expiration of the individual records.

- Service Lists are not flooded, only individual Service Records are. Each
  floodfill creates, signs, and caches a Service List. The floodfill uses its
  own policy for cache time and the maximum number of service and revocation
  records.



Common Structures Spec Changes Required
=======================================


Key Certificates
----------------

Out of scope for this proposal.
Add to the ECIES proposals 144 and 145.


New Intermediate Structures
---------------------------

Add new structures for Lease2, MetaLease, LeaseSet2Header, and OfflineSignature.
Effective as of release 0.9.38.


New NetDB Types
---------------

Add structures for each new leaseset type, incorporated from above.
For LeaseSet2, EncryptedLeaseSet, and MetaLeaseSet,
effective as of release 0.9.38.
For Service Record and Service List,
preliminary and unscheduled.


New Signature Type
------------------

Add RedDSA_SHA512_Ed25519 Type 11.
Public key is 32 bytes; private key is 32 bytes; hash is 64 bytes; signature is 64 bytes.



Encryption Spec Changes Required
================================

Out of scope for this proposal.
See proposals 144 and 145.



I2NP Changes Required
=====================

Add note: LS2 can only be published to floodfills with a minimum version.


Database Lookup Message
-----------------------

Add the service list lookup type.

Changes
```````
::

  Flags byte: Lookup type field, currently bits 3-2, expands to bits 4-2.
  Lookup type 0x04 is defined as the service list lookup.

  Add note: Service list loookup may only be sent to floodfills with a minimum version.
  Minimum version is 0.9.38.


Database Store Message
----------------------

Add all the new store types.

Changes
```````
::

  Type byte: Type field, currently bit 0, expands to bits 3-0.
  Type 3 is defined as a LS2 store.
  Type 5 is defined as a encrypted LS2 store.
  Type 7 is defined as a meta LS2 store.
  Type 9 is defined as a service record store.
  Type 11 is defined as a service list store.
  Other types are undefined and invalid.

  Add note: All new types may only be published to floodfills with a minimum version.
  Minimum version is 0.9.38.




I2CP Changes Required
=====================


I2CP Options
------------

New options interpreted router-side, sent in SessionConfig Mapping:

::

  i2cp.leaseSetType=nnn       The type of leaseset to be sent in the Create Leaseset Message
                              Value is the same as the netdb store type in the table above.
                              Interpreted client-side, but also passed to the router in the
                              SessionConfig, to declare intent and check support.

  i2cp.leaseSetEncType=nnn[,nnn]  The encryption types to be used.
                                  Interpreted client-side, but also passed to the router in
                                  the SessionConfig, to declare intent and check support.
                                  See proposals 144 and 145.

  i2cp.leaseSetOfflineExpiration=nnn  The expiration of the offline signature, ASCII,
                                      seconds since the epoch.

  i2cp.leaseSetTransientPublicKey=[type:]b64  The base 64 of the transient private key,
                                              prefixed by an optional sig type number
                                              or name, default DSA_SHA1.
                                              Length as inferred from the sig type

  i2cp.leaseSetOfflineSignature=b64   The base 64 of the offline signature.
                                      Length as inferred from the destination
                                      signing public key type

  i2cp.leaseSetSecret=xxxx    A secret used to encrypt/decrypt the leaseset, default ""

  i2cp.leaseSetAuthType=nnn   The type of authentication for encrypted LS2.
                              0 for no per-client authentication (the default)
                              1 for DH per-client authentication
                              2 for PSK per-client authentication

  i2cp.leaseSetPrivKey=b64    A base 64 private key for the router to use to
                              decrypt the encrypted LS2,
                              only if per-client authentication is enabled


New options interpreted client-side:

::

  i2cp.leaseSetType=nnn     The type of leaseset to be sent in the Create Leaseset Message
                            Value is the same as the netdb store type in the table above.
                            Interpreted client-side, but also passed to the router in the
                            SessionConfig, to declare intent and check support.

  i2cp.leaseSetEncType=nnn[,nnn]  The encryption types to be used.
                                  Interpreted client-side, but also passed to the router in
                                  the SessionConfig, to declare intent and check support.
                                  See proposals 144 and 145.

  i2cp.leaseSetSecret=xxxx        A secret used to encrypt/decrypt the leaseset, default ""

  i2cp.leaseSetAuthType=nnn       The type of authentication for encrypted LS2.
                                  0 for no per-client authentication (the default)
                                  1 for DH per-client authentication
                                  2 for PSK per-client authentication

  i2cp.leaseSetBlindedType=nnn   The sig type of the blinded key for encrypted LS2.
                                 Default depends on the destination sig type.
                                 See proposal 123.


Session Config
--------------

Note that for offline signatures, the options
i2cp.leaseSetOfflineExpiration,
i2cp.leaseSetTransientPublicKey, and
i2cp.leaseSetOfflineSignature are required,
and the signature is by the transient signing private key.



Request Leaseset Message
------------------------

Router to client.
No changes.
The leases are sent with 8-byte timestamps, even if the
returned leaseset will be a LS2 with 4-byte timestamps.
Note that the response may be a Create Leaseset or Create Leaseset2 Message.



Request Variable Leaseset Message
---------------------------------

Router to client.
No changes.
The leases are sent with 8-byte timestamps, even if the
returned leaseset will be a LS2 with 4-byte timestamps.
Note that the response may be a Create Leaseset or Create Leaseset2 Message.



Create Leaseset2 Message
------------------------

Client to router.
New message, to use in place of Create Leaseset Message.


Justification
`````````````

- For the router to parse the store type, the type must be in the message,
  unless it is passed to the router before hand in the session config.
  For for common parsing code, it's easier to have it in the message itself.

- For the router to know the type and length of the private key,
  it must be after the lease set, unless the parser knows the type before hand
  in the session config.
  For for common parsing code, it's easier to know it from the message itself.

- The signing private key, previously defined for revocation and unused,
  is not present in LS2.

Message Type
````````````

The message type for the Create Leaseset2 Message is 41.


Format
``````

::

  Session ID
  Type byte: Type of lease set to follow
             Type 1 is a LS
             Type 3 is a LS2
             Type 5 is a encrypted LS2
             Type 7 is a meta LS2
  LeaseSet: type specified above
  Number of private keys to follow (1 byte)
  Encryption Private Keys: For each public key in the lease set,
                           in the same order
                           (Not present for Meta LS2)
                           - Encryption type (2 bytes, big endian)
                           - Encryption key length (2 bytes, big endian)
                           - Encryption key (number of bytes specified)


Notes
`````

- Minimum router version is 0.9.39.
- Preliminary version with message type 40 was in 0.9.38 but the format was changed.
  Type 40 is abandoned and is unsupported.


Issues
``````

- More changes are needed to support encrypted and meta LS.



Host Lookup Message
-------------------

Client to router.

A lookup of a hash will force the router to fetch the Lease Set,
so extended results may be returned in the Host Reply Message.
However, a lookup of a host name will not force the router to fetch the Lease Set
(unless the lookup was for a b32.i2p, which is discouraged, the client side
normally converts this to a hash lookup).

To force a Lease Set lookup for a host name lookup,
we need a new request type.


Changes
```````

::

  Add request type 3: Host name lookup and request Lease Set lookup.
  Same contents as type 1, what follows is a host name string.


Notes
`````

- Minimum router and client version is 0.9.40 for request type 3.



Host Reply Message
------------------

Router to client.

A client doesn't know a priori that a given Hash will resolve
to a Meta LS.

If a Host Lookup Message for a Hash yields a Meta LS,
the router needs to return one or more Destinations and expirations to the client.
Either the client must to the recursive resolution, or the router can do it.
Not clear how it should work.
For either method, we either need a new flavor of the Host Reply Message,
or define a new result code that means what follows is a list of Destinations
and expirations.

If the router simply returns a single Destination whose Hash doesn't match
that of the lookup, it may fail sanity checks on the client side,
and the client has no way to get an alternate if that fails,
and has no way to know the expiration time.

There may be similar issues in BOB and SAM.

Changes
```````

::

  If the client version is 0.9.40 or higher, and the result code is 0,
  the following extended results are included after the Destination.
  These are included no matter what the request type.

  5.  LeaseSet type (1 byte)
      0: Unknown
      1: LS 1
      3: LS 2
      7: Meta LS
  6.  LeaseSet expiration (4 bytes, big endian, seconds since the epoch)
      0 if unknown
  7.  Number of encryption types supported (1 byte)
      0 if unknown
  8.  That number of encryption types, 2 bytes each
  9.  Lease set options, a Mapping, or 2 bytes of zeros if unknown.
  10. Flags (2 bytes)
      Bit order: 15 14 13...3210
      Bit 0: 1 for offline keys, 0 if not
      Bits 15-1: Unused, set to 0 for compatibility with future uses
  11. If offline keys, the transient key sig type (2 bytes, big endian)
  12. If offline keys, the transient public key
      (length as implied by sig type)
  13. If LeaseSet type is Meta (7), the number of
      meta entries to follow (1 byte)
  14. If LeaseSet type is Meta (7), the Meta Entries.
      Each entry contains: (40 bytes)
      - Hash (32 bytes)
      - Flags (3 bytes)
        TBD. Set all to zero for compatibility with future uses.
        TODO: Use a few bits to (optionally) indicate
        the type of the LS it is referencing.
        All zeros means don't know.
      - Cost (priority) (1 byte)
      - Expires (4 bytes, big endian, seconds since epoch, rolls over in 2106)

Notes
`````

- Minimum router and client version is 0.9.40 for the extended results.



Changes to support Meta
-----------------------

How to generate and support Meta, including inter-router communication and coordination,
is out of scope for this proposal.
Support may be added to I2CP, or i2pcontrol, or a new protocol.


Changes to support Offline Keys
-------------------------------

Offline signatures cannot be verified in streaming or repliable datagrams.
See sections below.


Private Key File Changes Required
=================================

The private key file (eepPriv.dat) format is not an official part of our specifications
but it is documented in the Java I2P javadocs
http://echelon.i2p/javadoc/net/i2p/data/PrivateKeyFile.html
and other implementations do support it.
This enables portability of private keys to different implementations.

Changes are necessary to store the transient public key and
offline signing information.

Changes
-------

::

  If the signing private key is all zeros, the offline information section follows:

  - Expires timestamp (4 bytes, big endian, seconds since epoch, rolls over in 2106)
  - Sig type of transient Signing Public Key (2 bytes, big endian)
  - Transient Signing Public key (length as specified by transient sig type)
  - Signature of above three fields by offline key (length as specified by destination sig type)
  - Transient Signing Private key (length as specified by transient sig type)


Private Key File CLI Changes Required
-------------------------------------

Add support for the following options:

::

      -d days              (specify expiration in days of offline sig, default 365)
      -o offlinedestfile   (generate the online key file using the offline key file specified)
      -r sigtype           (specify sig type of transient key, default Ed25519)




Streaming Changes Required
==========================

Offline signatures cannot currently be verified in streaming.
The change below adds the offline signing block to the options.
This avoids having to retrieve this information via I2CP.

Changes
-------

::

  Add new option:
  Bit:          11
  Flag:         OFFLINE_SIGNATURE
  Option order: 4
  Option data:  Variable bytes
  Function:     Contains the offline signature section from LS2.
                FROM_INCLUDED must also be set.
                Expires timestamp (4 bytes, big endian, seconds since epoch, rolls over in 2106)
                Transient sig type (2 bytes, big endian)
                Transient signing public key (length as implied by sig type)
                Signature of expires timestamp, transient sig type, and public key, by the destination public key,
                length as implied by destination public key sig type.

  Change option:
  Bit:          3
  Flag:         SIGNATURE_INCLUDED
  Option order: Change from 4 to 5

  Add information about transient keys to the Variable Length Signature Notes section:
  The offline signature option does not needed to be added for a CLOSE packet if
  a SYN packet containing the option was previously acked.
  More info TODO


Notes
-----

- Alternative is to just add a flag, and retrieve the transient public key via I2CP
  (See Host Lookup / Host Reply Message sections above)



Repliable Datagram Changes Required
===================================

Offline signatures cannot be verified in the repliable datagram processing.
Needs a flag to indicate offline signed but there's no place to put a flag.
Will require a completely new protocol number and format.


Changes
-------

::

  Define new protocol 19 - Repliable datagram with options?
  - Destination (387+ bytes)
  - Flags (2 bytes)
    Bit order: 15 14 ... 3 2 1 0
    Bit 0: If 0, no offline keys; if 1, offline keys
    Bits 1-15: set to 0 for compatibility with future uses
  - If flag indicates offline keys, the offline signature section:
    Expires timestamp (4 bytes, big endian, seconds since epoch, rolls over in 2106)
    Transient sig type (2 bytes, big endian)
    Transient signing public key (length as implied by sig type)
    Signature of expires timestamp, transient sig type, and public key, by the destination public key,
    length as implied by destination public key sig type.
    This section can, and should, be generated offline.
  - Data

Notes
-----

- Alternative is to just add a flag, and retrieve the transient public key via I2CP
  (See Host Lookup / Host Reply Message sections above)
- Any other options we should add now that we have flag bytes?


SAM V3 Changes Required
=======================

SAM must be enhanced to support offline signatures in the DESTINATION base 64.


Changes
-------

::

  Note that in the SESSION CREATE DESTINATION=$privkey,
  the $privkey raw data (before base64 conversion)
  may be optionally followed by the Offline Signature as specified in the
  Common Structures Specification.

  If the signing private key is all zeros, the offline information section follows:

  - Expires timestamp (4 bytes, big endian, seconds since epoch, rolls over in 2106)
  - Sig type of transient Signing Public Key (2 bytes, big endian)
  - Transient Signing Public key (length as specified by transient sig type)
  - Signature of above three fields by offline key (length as specified by destination sig type)
  - Transient Signing Private key (length as specified by transient sig type)

  Note that offline signatures are only supported for STREAM and RAW, not for DATAGRAM.
  (until we define a new DATAGRAM protocol)

  Note that the SESSION STATUS will return a Signing Private Key of all zeros and
  the Offline Signature data exactly as supplied in the SESSION CREATE.

  Note that DEST GENERATE and SESSION CREATE DESTINATION=TRANSIENT
  may not be used to create an offline signed destination.



Issues
------
- Bump version to 3.4, or leave it at 3.1/3.2/3.3 so it can be added
  without requiring all the 3.2/3.3 stuff?
- Other changes TBD. See I2CP Host Reply Message section above.



BOB Changes Required
====================

BOB would have to be enhanced to support offline signatures and/or Meta LS.
This is low priority and probably won't ever be specified or implemented.
SAM V3 is the preferred interface.




Publishing, Migration, Compatibility
====================================

LS2 (other than encrypted LS2) is published at the same DHT location as LS1.
There is no way to publish both a LS1 and LS2, unless LS2 were at a different location.

Encrypted LS2 is published at the hash of the blinded key type and key data.
This hash is then used to generate the daily "routing key", as in LS1.

LS2 would only be used when new features are required
(new crypto, encrypted LS, meta, etc.).
LS2 can only be published to floodfills of a specified version or higher.

Servers publishing LS2 would know that any connecting clients support LS2.
They could send LS2 in the garlic.

Clients would send LS2 in garlics only if using new crypto.
Shared clients would use LS1 indefinitely?
TODO: How to have a shared clients that supports both old and new crypto?


Rollout
=======

0.9.38 contains floodfill support for standard LS2, including offline keys.

0.9.39 contains I2CP support for LS2 and Encrypted LS2,
sig type 11 signing/verification,
floodfill support for Encrypted LS2 (sig types 7 and 11, without offline keys),
and encrypting/decrypting LS2 (without per-client authorization).

0.9.40 is scheduled to contain support for
encrypting/decrypting LS2 with per-client authorization,
floodfill and I2CP support for Meta LS2,
support for encrypted LS2 with offline keys,
and b32 support for encrypted LS2.


Acknowledgements
================

The encrypted LS2 design is heavily influenced by Tor's v3 hidden service descriptors,
which had similar design goals [TOR-REND-SPEC-V3]_.



References
==========

.. [ED25519-REFS]
    "High-speed high-security signatures" by Daniel
    J. Bernstein, Niels Duif, Tanja Lange, Peter Schwabe, and
    Bo-Yin Yang. http://cr.yp.to/papers.html#ed25519

.. [KEYBLIND-PROOF]
    https://lists.torproject.org/pipermail/tor-dev/2013-December/005943.html

.. [KEYBLIND-REFS]
    https://trac.torproject.org/projects/tor/ticket/8106
    https://lists.torproject.org/pipermail/tor-dev/2012-September/004026.html

.. [PRNG-REFS]
    http://projectbullrun.org/dual-ec/ext-rand.html
    https://lists.torproject.org/pipermail/tor-dev/2015-November/009954.html

.. [RFC-2104]
    https://tools.ietf.org/html/rfc2104

.. [RFC-4880-S5.1]
    https://tools.ietf.org/html/rfc4880#section-5.1

.. [RFC-5869]
    https://tools.ietf.org/html/rfc5869

.. [RFC-7539-S2.4]
    https://tools.ietf.org/html/rfc7539#section-2.4

.. [TOR-REND-SPEC-V3]
    https://spec.torproject.org/rend-spec-v3

.. [UNSCIENTIFIC-KDF-SPEEDS]
    https://www.lvh.io/posts/secure-key-derivation-performance.html

.. [ZCASH]
   https://github.com/zcash/zips/tree/master/protocol/protocol.pdf
