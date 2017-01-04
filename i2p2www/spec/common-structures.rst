===============================
Common structures Specification
===============================
.. meta::
    :category: Design
    :lastupdated: January 2017
    :accuratefor: 0.9.28

.. contents::


This document describes some data types common to all I2P protocols, like
[I2NP]_, [I2CP]_, [SSU]_, etc.


Common type specification
=========================

.. _type-Integer:

Integer
-------

Description
```````````
Represents a non-negative integer.

Contents
````````
1 to 8 bytes in network byte order representing an unsigned integer

.. _type-Date:

Date
----

Description
```````````
The number of milliseconds since midnight on January 1, 1970 in the GMT timezone.
If the number is 0, the date is undefined or null.

Contents
````````
8 byte Integer_

.. _type-String:

String
------

Description
```````````
Represents a UTF-8 encoded string.

Contents
````````
1 or more bytes where the first byte is the number of bytes (not characters!)
in the string and the remaining 0-255 bytes are the non-null terminated UTF-8
encoded character array.  Length limit is 255 bytes (not characters). Length
may be 0.

.. _type-Boolean:

Boolean
-------

Description
```````````
A boolean value, supporting null/unknown representation
0=false, 1=true, 2=unknown/null

Contents
````````
1 byte Integer_

Notes
`````
Deprecated - unused

.. _type-PublicKey:

PublicKey
---------

Description
```````````
This structure is used in ElGamal encryption, representing only the exponent,
not the primes, which are constant and defined in the cryptography
specification [ELGAMAL]_.

Contents
````````
256 bytes

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/PublicKey.html

.. _type-PrivateKey:

PrivateKey
----------

Description
```````````
This structure is used in ElGamal decryption, representing only the exponent,
not the primes which are constant and defined in the cryptography specification
[ELGAMAL]_.

Contents
````````
256 bytes

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/PrivateKey.html

.. _type-SessionKey:

SessionKey
----------

Description
```````````
This structure is used for AES256 encryption and decryption.

Contents
````````
32 bytes

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/SessionKey.html

.. _type-SigningPublicKey:

SigningPublicKey
----------------

Description
```````````
This structure is used for verifying signatures.

Contents
````````
Key type and length are inferred from context or are specified in the Key
Certificate of a Destination.  The default type is DSA_SHA1.  As of release
0.9.12, other types may be supported, depending on context.

======================  ==============  ======  =====
         Type           Length (bytes)  Since   Usage
======================  ==============  ======  =====
DSA_SHA1                     128                Legacy Router Identities and Destinations
ECDSA_SHA256_P256             64        0.9.12  Recent Destinations
ECDSA_SHA384_P384             96        0.9.12  Rarely used for Destinations
ECDSA_SHA512_P521            132        0.9.12  Rarely used for Destinations
RSA_SHA256_2048              256        0.9.12  Offline signing, never used for Router Identities or Destinations
RSA_SHA384_3072              384        0.9.12  Offline signing, never used for Router Identities or Destinations
RSA_SHA512_4096              512        0.9.12  Offline signing, never used for Router Identities or Destinations
EdDSA_SHA512_Ed25519          32        0.9.15  Recent Router Identities and Destinations
EdDSA_SHA512_Ed25519ph        32        0.9.25  Offline signing, never used for Router Identities or Destinations
======================  ==============  ======  =====

Notes
`````
* When a key is composed of two elements (for example points X,Y), it is
  serialized by padding each element to length/2 with leading zeros if
  necessary.

* All types are Big Endian, except for EdDSA, which is stored and transmitted
  in a Little Endian format.

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/SigningPublicKey.html

.. _type-SigningPrivateKey:

SigningPrivateKey
-----------------

Description
```````````
This structure is used for creating signatures.

Contents
````````
Key type and length are specified when created.  The default type is DSA_SHA1.
As of release 0.9.12, other types may be supported, depending on context.

======================  ==============  ======  =====
         Type           Length (bytes)  Since   Usage
======================  ==============  ======  =====
DSA_SHA1                      20                Legacy Router Identities and Destinations
ECDSA_SHA256_P256             32        0.9.12  Recent Destinations
ECDSA_SHA384_P384             48        0.9.12  Rarely used for Destinations
ECDSA_SHA512_P521             66        0.9.12  Rarely used for Destinations
RSA_SHA256_2048              512        0.9.12  Offline signing, never used for Router Identities or Destinations
RSA_SHA384_3072              768        0.9.12  Offline signing, never used for Router Identities or Destinations
RSA_SHA512_4096             1024        0.9.12  Offline signing, never used for Router Identities or Destinations
EdDSA_SHA512_Ed25519          32        0.9.15  Recent Router Identities and Destinations
EdDSA_SHA512_Ed25519ph        32        0.9.25  Offline signing, never used for Router Identities or Destinations
======================  ==============  ======  =====

Notes
`````
* When a key is composed of two elements (for example points X,Y), it is
  serialized by padding each element to length/2 with leading zeros if
  necessary.

* All types are Big Endian, except for EdDSA, which is stored and transmitted
  in a Little Endian format.

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/SigningPrivateKey.html

.. _type-Signature:

Signature
---------

Description
```````````
This structure represents the signature of some data.

Contents
````````
Signature type and length are inferred from the type of key used.  The default
type is DSA_SHA1.  As of release 0.9.12, other types may be supported,
depending on context.

======================  ==============  ======  =====
         Type           Length (bytes)  Since   Usage
======================  ==============  ======  =====
DSA_SHA1                      40                Legacy Router Identities and Destinations
ECDSA_SHA256_P256             64        0.9.12  Recent Destinations
ECDSA_SHA384_P384             96        0.9.12  Rarely used for Destinations
ECDSA_SHA512_P521            132        0.9.12  Rarely used for Destinations
RSA_SHA256_2048              256        0.9.12  Offline signing, never used for Router Identities or Destinations
RSA_SHA384_3072              384        0.9.12  Offline signing, never used for Router Identities or Destinations
RSA_SHA512_4096              512        0.9.12  Offline signing, never used for Router Identities or Destinations
EdDSA_SHA512_Ed25519          64        0.9.15  Recent Router Identities and Destinations
EdDSA_SHA512_Ed25519ph        64        0.9.25  Offline signing, never used for Router Identities or Destinations
======================  ==============  ======  =====

Notes
`````
* When a signature is composed of two elements (for example values R,S), it is
  serialized by padding each element to length/2 with leading zeros if
  necessary.

* All types are Big Endian, except for EdDSA, which is stored and transmitted
  in a Little Endian format.

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/Signature.html

.. _type-Hash:

Hash
----

Description
```````````
Represents the SHA256 of some data.

Contents
````````
32 bytes

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/Hash.html

.. _type-SessionTag:

Session Tag
-----------

Description
```````````
A random number

Contents
````````
32 bytes

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/SessionTag.html

.. _type-TunnelId:

TunnelId
--------

Description
```````````
Defines an identifier that is unique to each router in a tunnel.  A Tunnel ID
is generally greater than zero; do not use a value of zero except in special
cases.

Contents
````````
4 byte Integer_

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/TunnelId.html

.. _type-Certificate:

Certificate
-----------

Description
```````````
A certificate is a container for various receipts or proof of works used
throughout the I2P network.

Contents
````````
1 byte Integer_ specifying certificate type, followed by a 2 byte Integer_
specifying the size of the certificate payload, then that many bytes.

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+-//
  |type| length  | payload
  +----+----+----+----+----+-//

  type :: `Integer`
          length -> 1 byte

          case 0 -> NULL
          case 1 -> HASHCASH
          case 2 -> HIDDEN
          case 3 -> SIGNED
          case 4 -> MULTIPLE
          case 5 -> KEY

  length :: `Integer`
            length -> 2 bytes

  payload :: data
             length -> $length bytes
{% endhighlight %}

Notes
`````
* For `Router Identities`_, the Certificate is always NULL through version
  0.9.15. As of 0.9.16, a Key Certificate may be used to specify the signing
  public key type. See below.

* For `Garlic Cloves`_, the Certificate is always NULL, no others are currently
  implemented.

* For `Garlic Messages`_, the Certificate is always NULL, no others are
  currently implemented.

* For `Destinations`_, the Certificate may be non-NULL. As of 0.9.12, a Key
  Certificate may be used to specify the signing public key type. See below.

.. _Router Identities: #struct_RouterIdentity
.. _Garlic Cloves: {{ site_url('docs/spec/i2np') }}#struct_GarlicClove
.. _Garlic Messages: {{ site_url('docs/spec/i2np') }}#msg_Garlic
.. _Destinations: #struct_Destination

Certificate Types
`````````````````
The following certificate types are defined:

========  =========  ==============  ============  =====
Type      Type Code  Payload Length  Total Length  Notes
========  =========  ==============  ============  =====
Null          0             0              3
HashCash      1          varies         varies     Experimental, unused. Payload contains an ASCII colon-separated hashcash string.
Hidden        2             0              3       Experimental, unused. Hidden routers generally do not announce that they are hidden.
Signed        3         40 or 72       43 or 75    Experimental, unused. Payload contains a 40-byte DSA signature,
                                                   optionally followed by the 32-byte Hash of the signing Destination.
Multiple      4          varies         varies     Experimental, unused. Payload contains multiple certificates.
Key           5             4+             7+      Since 0.9.12. See below for details.
========  =========  ==============  ============  =====


Key Certificates
````````````````
Key certificates were introduced in release 0.9.12.  Prior to that release, all
PublicKeys were 256-byte ElGamal keys, and all SigningPublicKeys were 128-byte
DSA-SHA1 keys.  A key certificate provides a mechanism to indicate the type of
the PublicKey and SigningPublicKey in the Destination or RouterIdentity, and to
package any key data in excess of the standard lengths.

By maintaining exactly 384 bytes before the certificate, and putting any excess
key data inside the certificate, we maintain compatibility for any software
that parses Destinations and Router Identities.

The key certificate payload contains:

==================================  ======
              Data                  Length
==================================  ======
Signing Public Key Type (Integer_)    2
Crypto Public Key Type (Integer_)     2
Excess Signing Public Key Data        0+
Excess Crypto Public Key Data         0+
==================================  ======

The defined Signing Public Key types are:

======================  ===========  =======================  ======  =====
        Type             Type Code   Total Public Key Length  Since   Usage
======================  ===========  =======================  ======  =====
DSA_SHA1                     0                  128           0.9.12  Legacy Router Identities and Destinations, never explicitly set
ECDSA_SHA256_P256            1                   64           0.9.12  Recent Destinations
ECDSA_SHA384_P384            2                   96           0.9.12  Sometimes used for Destinations
ECDSA_SHA512_P521            3                  132           0.9.12  Sometimes used for Destinations
RSA_SHA256_2048              4                  256           0.9.12  Offline only; never used in Key Certificates for Router Identities or Destinations
RSA_SHA384_3072              5                  384           0.9.12  Offline only; never used in Key Certificates for Router Identities or Destinations
RSA_SHA512_4096              6                  512           0.9.12  Offline only; never used in Key Certificates for Router Identities or Destinations
EdDSA_SHA512_Ed25519         7                   32           0.9.15  Recent Router Identities and Destinations
EdDSA_SHA512_Ed25519ph       8                   32           0.9.25  Offline only; never used in Key Certificates for Router Identities or Destinations
reserved                65280-65534                                   Reserved for experimental use
reserved                   65535                                      Reserved for future expansion
======================  ===========  =======================  ======  =====

The defined Crypto Public Key types are:

========  ===========  =======================  =====
  Type     Type Code   Total Public Key Length  Usage
========  ===========  =======================  =====
ElGamal        0                 256            All Router Identities and Destinations
reserved  65280-65534                           Reserved for experimental use
reserved     65535                              Reserved for future expansion
========  ===========  =======================  =====

When a Key Certificate is not present, the preceeding 384 bytes in the
Destination or RouterIdentity are defined as the 256-byte ElGamal PublicKey
followed by the 128-byte DSA-SHA1 SigningPublicKey.  When a Key Certificate is
present, the preceeding 384 bytes are redefined as follows:

* Complete or first portion of Crypto Public Key

* Random padding if the total lengths of the two keys are less than 384 bytes

* Complete or first portion of Signing Public Key

The Crypto Public Key is aligned at the start and the Signing Public Key is
aligned at the end.  The padding (if any) is in the middle.  The lengths and
boundaries of the initial key data, the padding, and the excess key data
portions in the certificates are not explicitly specified, but are derived from
the lengths of the specified key types.  If the total lengths of the Crypto and
Signing Public Keys exceed 384 bytes, the remainder will be contained in the
Key Certificate.  If the Crypto Public Key length is not 256 bytes, the method
for determining the boundary between the two keys is to be specified in a
future revision of this document.

Example layouts using an ElGamal Crypto Public Key and the Signing Public Key
type indicated:

======================  ==============  ===============================
   Signing Key Type     Padding Length  Excess Signing Key Data in Cert
======================  ==============  ===============================
DSA_SHA1                       0                        0
ECDSA_SHA256_P256             64                        0
ECDSA_SHA384_P384             32                        0
ECDSA_SHA512_P521              0                        4
RSA_SHA256_2048                0                      128
RSA_SHA384_3072                0                      256
RSA_SHA512_4096                0                      384
EdDSA_SHA512_Ed25519          96                        0
EdDSA_SHA512_Ed25519ph        96                        0
======================  ==============  ===============================

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/Certificate.html

.. _type-Mapping:

Mapping
-------

Description
```````````
A set of key/value mappings or properties

Contents
````````
A 2-byte size Integer followed by a series of String=String; pairs

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  |  size   | key_string (len + data)| =  |
  +----+----+----+----+----+----+----+----+
  | val_string (len + data)     | ;  | ...
  +----+----+----+----+----+----+----+
  size :: `Integer`
          length -> 2 bytes
          Total number of bytes that follow

  key_string :: `String`
                A string (one byte length followed by UTF-8 encoded characters)

  = :: A single byte containing '='

  val_string :: `String`
                A string (one byte length followed by UTF-8 encoded characters)

  ; :: A single byte containing ';'
{% endhighlight %}

Notes
`````
* The encoding isn't optimal - we either need the '=' and ';' characters, or
  the string lengths, but not both

* Some documentation says that the strings may not include '=' or ';' but this
  encoding supports them

* Strings are defined to be UTF-8 but in the current implementation, I2CP uses
  UTF-8 but I2NP does not. For example, UTF-8 strings in a RouterInfo options
  mapping in a I2NP Database Store Message will be corrupted.

* The encoding allows duplicate keys, however in any usage where the mapping is
  signed, duplicates may cause a signature failure.

* Mappings contained in I2NP messages (i.e. in a RouterAddress or RouterInfo)
  must be sorted by key so that the signature will be invariant. Duplicate keys
  are not allowed.

* Mappings contained in an `I2CP SessionConfig`_ must be sorted by key so that
  the signature will be invariant. Duplicate keys are not allowed.

* The sort method is defined as in Java String.compareTo(), using the Unicode
  value of the characters.

* While it is application-dependent, keys and values are generally
  case-sensitive.

* Key and value string length limits are 255 bytes (not characters) each, plus
  the length byte. Length byte may be 0.

* Total length limit is 65535 bytes, plus the 2 byte size field, or 65537
  total.

.. _I2CP SessionConfig: {{ site_url('docs/spec/i2cp') }}#struct_SessionConfig

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/DataHelper.html


Common structure specification
==============================

.. _struct-KeysAndCert:

KeysAndCert
-----------

Description
```````````
An encryption public key, a signing public key, and a certificate, used as
either a RouterIdentity or a Destination.

Contents
````````
A PublicKey_ followed by a SigningPublicKey_ and then a Certificate_.

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  | public_key                            |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | padding (optional)                    |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | signing_key                           |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | certificate                           |
  +----+----+----+-//

  public_key :: `PublicKey` (partial or full)
                length -> 256 bytes or as specified in key certificate

  padding :: random data
             length -> 0 bytes or as specified in key certificate
             padding length + signing_key length == 128 bytes

  signing__key :: `SigningPublicKey` (partial or full)
                  length -> 128 bytes or as specified in key certificate
                  padding length + signing_key length == 128 bytes

  certificate :: `Certificate`
                 length -> >= 3 bytes

  total length: 387+ bytes
{% endhighlight %}

Notes
`````
* Do not assume that these are always 387 bytes! They are 387 bytes plus the
  certificate length specified at bytes 385-386, which may be non-zero.

* As of release 0.9.12, if the certificate is a Key Certificate, the boundaries
  of the key fields may vary. See the Key Certificate section above for
  details.

* The Crypto Public Key is aligned at the start and the Signing Public Key is
  aligned at the end. The padding (if any) is in the middle.

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/KeysAndCert.html

.. _struct-RouterIdentity:

RouterIdentity
--------------

Description
```````````
Defines the way to uniquely identify a particular router

Contents
````````
Identical to KeysAndCert.

Notes
`````
* The certificate for a RouterIdentity was always NULL until release 0.9.12.

* Do not assume that these are always 387 bytes! They are 387 bytes plus the
  certificate length specified at bytes 385-386, which may be non-zero.

* As of release 0.9.12, if the certificate is a Key Certificate, the boundaries
  of the key fields may vary. See the Key Certificate section above for
  details.

* The Crypto Public Key is aligned at the start and the Signing Public Key is
  aligned at the end. The padding (if any) is in the middle.

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/router/RouterIdentity.html

.. _struct-Destination:

Destination
-----------

Description
```````````
A Destination defines a particular endpoint to which messages can be directed
for secure delivery.

Contents
````````
Identical to KeysAndCert_.

Notes
`````
* The public key of the destination was used for the old i2cp-to-i2cp
  encryption which was disabled in version 0.6, it is currently unused except
  for the IV for LeaseSet encryption, which is deprecated. The public key in
  the LeaseSet is used instead.

* Do not assume that these are always 387 bytes! They are 387 bytes plus the
  certificate length specified at bytes 385-386, which may be non-zero.

* As of release 0.9.12, if the certificate is a Key Certificate, the boundaries
  of the key fields may vary. See the Key Certificate section above for
  details.

* The Crypto Public Key is aligned at the start and the Signing Public Key is
  aligned at the end. The padding (if any) is in the middle.

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/Destination.html

.. _struct-Lease:

Lease
-----

Description
```````````
Defines the authorization for a particular tunnel to receive messages targeting
a Destination_.

Contents
````````
SHA256 Hash_ of the RouterIdentity_ of the gateway router, then the TunnelId_,
and finally an end Date_.

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  | tunnel_gw                             |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |     tunnel_id     |      end_date
  +----+----+----+----+----+----+----+----+
                      |
  +----+----+----+----+

  tunnel_gw :: Hash of the `RouterIdentity` of the tunnel gateway
               length -> 32 bytes

  tunnel_id :: `TunnelId`
               length -> 4 bytes

  end_date :: `Date`
              length -> 8 bytes
{% endhighlight %}

Notes
`````
* Total size: 44 bytes

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/Lease.html

.. _struct-LeaseSet:

LeaseSet
--------

Description
```````````
Contains all of the currently authorized Leases_ for a particular Destination_,
the PublicKey_ to which garlic messages can be encrypted, and then the
SigningPublicKey_ that can be used to revoke this particular version of the
structure. The LeaseSet is one of the two structures stored in the network
database (the other being RouterInfo_), and is keyed under the SHA256 of the
contained Destination_.

.. _Leases: _Lease

Contents
````````
Destination_, followed by a PublicKey_ for encryption, then a SigningPublicKey_
which can be used to revoke this version of the LeaseSet, then a 1 byte
Integer_ specifying how many Lease_ structures are in the set, followed by the
actual Lease_ structures and finally a Signature_ of the previous bytes signed
by the Destination_'s SigningPrivateKey_.

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  | destination                           |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | encryption_key                        |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | signing_key                           |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | num| Lease 0                          |
  +----+                                  +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | Lease 1                               |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | Lease ($num-1)                        |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
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

  destination :: `Destination`
                 length -> >= 387 bytes

  encryption_key :: `PublicKey`
                    length -> 256 bytes

  signing_key :: `SigningPublicKey`
                 length -> 128 bytes or as specified in destination's key
                           certificate

  num :: `Integer`
         length -> 1 byte
         Number of leases to follow
         value: 0 <= num <= 16

  leases :: [`Lease`]
            length -> $num*44 bytes

  signature :: `Signature`
               length -> 40 bytes or as specified in destination's key
                         certificate
{% endhighlight %}

Notes
`````
* The public key of the destination was used for the old I2CP-to-I2CP
  encryption which was disabled in version 0.6, it is currently unused.

* The encryption key is used for end-to-end ElGamal/AES+SessionTag encryption
  [ELGAMAL-AES]_. It is currently generated anew at every router startup, it is
  not persistent.

* The signature may be verified using the signing public key of the
  destination.

* The signing_key is currently unused. It was intended for LeaseSet revocation,
  which is unimplemented. It is currently generated anew at every router
  startup, it is not persistent. The signing key type is always the same as the
  destination's signing key type.

* The earliest expiration of all the Leases is treated as the timestamp or
  version of the LeaseSet. Routers will generally not accept a store of a
  LeaseSet unless it is "newer" than the current one. Take care when publishing
  a new LeaseSet where the oldest Lease is the same as the oldest Lease in the
  previous LeaseSet. The publishing router should generally increment the
  expiration of the oldest Lease by at least 1 ms in that case.

* Prior to release 0.9.7, when included in a DatabaseStore Message sent by the
  originating router, the router set all the published leases' expirations to
  the same value, that of the earliest lease. As of release 0.9.7, the router
  publishes the actual lease expiration for each lease. This is an
  implementation detail and not part of the structures specification.

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/LeaseSet.html

.. _struct-RouterAddress:

RouterAddress
-------------

Description
```````````
This structure defines the means to contact a router through a transport
protocol.

Contents
````````
1 byte Integer_ defining the relative cost of using the address, where 0 is
free and 255 is expensive, followed by the expiration Date_ after which the
address should not be used, or if null, the address never expires. After that
comes a String_ defining the transport protocol this router address uses.
Finally there is a Mapping_ containing all of the transport specific options
necessary to establish the connection, such as IP address, port number, email
address, URL, etc.

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  |cost|           expiration
  +----+----+----+----+----+----+----+----+
       |        transport_style           |
  +----+----+----+----+-//-+----+----+----+
  |                                       |
  +                                       +
  |               options                 |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+

  cost :: `Integer`
          length -> 1 byte

          case 0 -> free
          case 255 -> expensive

  expiration :: `Date` (must be all zeros, see notes below)
                length -> 8 bytes

                case null -> never expires

  transport_style :: `String`
                     length -> 1-256 bytes

  options :: `Mapping`
{% endhighlight %}

Notes
`````
* Cost is typically 5 or 6 for SSU, and 10 or 11 for NTCP.

* Expiration is currently unused, always null (all zeroes). As of release
  0.9.3, the expiration is assumed zero and not stored, so any non-zero
  expiration will fail in the RouterInfo signature verification. Implementing
  expiration (or another use for these bytes) will be a backwards-incompatible
  change. Routers MUST set this field to all zeros. As of release 0.9.12, a
  non-zero expiration field is again recognized, however we must wait several
  releases to use this field, until the vast majority of the network recognizes
  it.

* The following options, while not required, are standard and expected to be
  present in most router addresses: "host" (an IPv4 or IPv6 address or host
  name) and "port".

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/router/RouterAddress.html

.. _struct-RouterInfo:

RouterInfo
----------

Description
```````````
Defines all of the data that a router wants to publish for the network to see.
The RouterInfo_ is one of two structures stored in the network database (the
other being LeaseSet_), and is keyed under the SHA256 of the contained
RouterIdentity_.

Contents
````````
RouterIdentity_ followed by the Date_, when the entry was published

.. raw:: html

  {% highlight lang='dataspec' -%}
+----+----+----+----+----+----+----+----+
  | router_ident                          |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | published                             |
  +----+----+----+----+----+----+----+----+
  |size| RouterAddress 0                  |
  +----+                                  +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | RouterAddress 1                       |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+----+----+----+----+
  | RouterAddress ($size-1)               |
  +                                       +
  |                                       |
  ~                                       ~
  ~                                       ~
  |                                       |
  +----+----+----+----+-//-+----+----+----+
  |psiz| options                          |
  +----+----+----+----+-//-+----+----+----+
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

  router_ident :: `RouterIdentity`
                  length -> >= 387 bytes

  published :: `Date`
               length -> 8 bytes

  size :: `Integer`
          length -> 1 byte
          The number of `RouterAddress`es to follow, 0-255

  addresses :: [`RouterAddress`]
               length -> varies

  peer_size :: `Integer`
               length -> 1 byte
               The number of peer `Hash`es to follow, 0-255, unused, always zero
               value -> 0

  options :: `Mapping`

  signature :: `Signature`
               length -> 40 bytes or as specified in router_ident's key
                         certificate
{% endhighlight %}

Notes
`````
* The peer_size Integer_ may be followed by a list of that many router hashes.
  This is currently unused. It was intended for a form of restricted routes,
  which is unimplemented.
  Certain implementations may require the list to be sorted so the signature is invariant.
  To be researched before enabling this feature.

* The signature may be verified using the signing public key of the
  router_ident.

* See the network database page [NETDB-ROUTERINFO]_ for standard options that
  are expected to be present in all router infos.

* Very old routers required the addresses to be sorted by the SHA256 of their data
  so the signature is invariant.
  This is no longer required, and not worth implementing for backward compatibility.

JavaDoc: http://{{ i2pconv('i2p-javadocs.i2p') }}/net/i2p/data/router/RouterInfo.html

.. _struct-DeliveryInstructions:

Delivery Instructions
---------------------

Tunnel Message Delivery Instructions are defined in the Tunnel Message
Specification [TUNNEL-DELIVERY]_.

Garlic Message Delivery Instructions are defined in the I2NP Message
Specification [GARLIC-DELIVERY]_.


References
==========

.. [ELGAMAL]
    {{ site_url('docs/how/cryptography', True) }}#elgamal

.. [ELGAMAL-AES]
    {{ site_url('docs/how/elgamal-aes', True) }}

.. [GARLIC-DELIVERY]
    {{ ctags_url('GarlicCloveDeliveryInstructions') }}

.. [I2CP]
    {{ site_url('docs/protocol/i2cp', True) }}

.. [I2NP]
    {{ site_url('docs/protocol/i2np', True) }}

.. [NETDB-ROUTERINFO]
    {{ site_url('docs/how/network-database', True) }}#routerInfo

.. [SSU]
    {{ site_url('docs/transport/ssu', True) }}

.. [TUNNEL-DELIVERY]
    {{ ctags_url('TunnelMessageDeliveryInstructions') }}
