================================
Encrypted LeaseSet Specification
================================
.. meta::
    :category: Protocols
    :lastupdated: March 2019
    :accuratefor: 0.9.39

.. contents::


Overview
========

This document specifies the blinding, encryption, and decryption of
encrypted leasesets. For the structure of the encrypted leaseset,
see the common structures specification.
For backround on encrypted leasesets, see proposal 123.
For usage in the netdb, see netdb documentation.


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
    This will always be type 11, identifying a RedDSA blinded key.

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

We use the following scheme for key blinding, based on Ed25519
and ZCash RedDSA [ZCASH]_.
The RedDSA signatures are over the Ed25519 curve, using SHA-512 for the hash.

We do not use Tor's rend-spec-v3.txt appendix A.2 [TOR-REND-SPEC-V3]_,
which has similar design goals, because its blinded public keys
may be off the prime-order subgroup, with unknown security implications.


Goals
~~~~~

- Signing public key in unblinded destination must be
  Ed25519 (sig type 7) or RedDSA (sig type 11);
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
to a RedDSA private key (sig type 11), the distribution is different.
To meet the requirements of zcash section 4.1.6.1 [ZCASH]_,
RedDSA (sig type 11) should be used for the unblinded keys as well, so that
"the combination of a re-randomized public key and signature(s)
under that key do not reveal the key from which it was re-randomized."
We allow type 7 for existing destinations, but recommend
type 11 for new destinations that will be encrypted.



Definitions
~~~~~~~~~~~

B
    The Ed25519 base point (generator) 2^255 - 19 as in [ED25519-REFS]_

l
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

The secret alpha and the blinded keys are calculated as follows:

.. raw:: html

  {% highlight lang='text' %}
GENERATE_ALPHA(destination, date, secret), for all parties:
  // secret is optional, else zero-length
  A = destination's signing public key
  stA = signature type of A, 2 bytes big endian (0x0007 or 0x000b)
  stA' = signature type of blinded public key A', 2 bytes big endian (0x000b)
  keydata = A || stA || stA'
  datestring = 8 bytes ASCII YYYYMMDD from the current date UTC
  seed = HKDF(H("I2PGenerateAlpha", keydata), datestring || secret, "i2pblinding1", 64)
  // treat seed as a 64 byte little-endian value
  alpha = seed mod l

  // BLIND_PRIVKEY(), for the owner publishing the leaseset:
  alpha = GENERATE_ALPHA(destination, date, secret)
  a = destination's signing private key
  // Addition using scalar arithmentic
  blinded signing private key = a' = BLIND_PRIVKEY(a, alpha) = (a + alpha) mod l
  blinded signing public key = A' = DERIVE_PUBLIC(a')

  // BLIND_PUBKEY(), for the clients retrieving the leaseset:
  alpha = GENERATE_ALPHA(destination, date, secret)
  A = destination's signing public key
  // Addition using group elements (points on the curve)
  blinded public key = A' = BLIND_PUBKEY(A, alpha) = A + DERIVE_PUBLIC(alpha)

  //Both methods of calculating A' yield the same result, as required.
{% endhighlight %}



Signing
~~~~~~~

The unblinded leaseset is signed by the unblinded Ed25519 or RedDSA signing private key
and verified with the unblinded Ed25519 or RedDSA signing public key (sig types 7 or 11) as usual.

If the signing public key is offline,
the unblinded leaseset is signed by the unblinded transient Ed25519 or RedDSA signing private key
and verified with the unblinded Ed25519 or RedDSA transient signing public key (sig types 7 or 11) as usual.
See below for additional notes on offline keys for encrytped leasesets.

For signing of the encrypted leaseset, we use RedDSA [ZCASH]_
to sign and verify with blinded keys.
The RedDSA signatures are over the Ed25519 curve, using SHA-512 for the hash.

RedDSA is similar to standard Ed25519 except as specified below.


Sign/Verify Calculations
~~~~~~~~~~~~~~~~~~~~~~~~

The outer portion of the encrypted leaseset uses RedDSA keys and signatures.

RedDSA is similar to Ed25519. There are two differences:

RedDSA private keys are generated from random numbers and then must be reduced mod l, where l is defined above.
Ed25519 private keys are generated from random numbers and then "clamped" using
bitwise masking to bytes 0 and 31. This is not done for RedDSA.
The functions GENERATE_ALPHA() and BLIND_PRIVKEY() defined above generate proper
RedDSA private keys using mod l.

In RedDSA, the calculation of r for signing uses additional random data,
and uses the public key value rather than the hash of the private key.
Because of the random data, every RedDSA signature is different, even
when signing the same data with the same key.


.. raw:: html

  {% highlight lang='text' %}
Signing:
  T = 80 random bytes
  r = H*(T || publickey || message)
  (rest is the same as in Ed25519)

  Verification:
  Same as for Ed25519
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

You can't use a traditional base 32 address for an encrypted LS2,
as it contains only the hash of the destination. It does not provide the non-blinded public key.
Therefore, a base 32 address alone is insufficient.
The client needs either the full destination (which contains the public key),
or the public key by itself.
If the client has the full destination in an address book, and the address book
supports reverse lookup by hash, then the public key may be retrieved.

So we need a new format that puts the public key instead of the hash into
a base32 address. This format must also contain the signature type of the
public key, and the signature type of the blinding scheme.
The total requirements are 32 + 2 + 2 = 36 bytes, requiring 58 characters in base 32.

  {% highlight lang='text' %}
data = 32 byte pubkey || 2 byte unblinded sigtype || 2 byte blinded sigtype
  address = Base32Encode(data) || ".b32.i2p"
{% endhighlight %}

We use the same ".b32.i2p" suffix as for traditional base 32 addresses.
Addresses for encrypted leasesets are identified by the 58 encoded characters
(36 decoded bytes), compared to 52 characters (32 bytes) for traditional base 32 addresses.
The five unused bits at the end of b32 must be 0.

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

There is no file format defined for packaging multiple transient and
blinded keys and providing them to the client or router.
There is no I2CP protocol enhancement defined to support
encrypted leasesets with offline keys.



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

.. [ZCASH]
   https://github.com/zcash/zips/tree/master/protocol/protocol.pdf
