========================================
Database Lookups from ECIES Destinations
========================================
.. meta::
    :author: zzz
    :created: 2020-03-23
    :thread: http://zzz.i2p/topics/2856
    :lastupdated: 2020-04-21
    :status: Closed
    :target: 0.9.46
    :implementedin: 0.9.46

.. contents::


Note
====
ECIES to ElG is implemented and the proposal phase is closed.
See [I2NP]_ for the official specification.
This proposal may still be referenced for background information.
ECIES to ECIES is not fully specified or implemented at this time.
The ECIES-to-ECIES section may be reopened or incorporated
in a future proposal.


Overview
========

Definitions
-----------

- AEAD: ChaCha20/Poly1305
- DLM: I2NP Database Lookup Message
- DSM: I2NP Database Store Message
- DSRM: I2NP Database Search Reply Message
- ECIES: ECIES-X25519-AEAD-Ratchet (propoosal 144)
- ElG: ElGamal
- ENCRYPT(k, n, payload, ad): As defined in [ECIES]_
- LS: Leaseset
- lookup: I2NP DLM
- reply: I2NP DSM or DSRM


Summary
-------

When sending a DLM for a LS to a floodfill, the DLM generally specifies
that the reply be tagged, AES encrypted, and sent down a tunnel to the destination.
Support for AES-encrypted replies was added in 0.9.7.

AES-encrypted replies were specified in 0.9.7 to minimize the large crypto
overhead of ElG, and because it reused the tags/AES facility
in ElGamal/AES+SessionTags.
However, AES replies may be tampered with at the IBEP as there is no authentication,
and the replies are not forward secret.

With [ECIES]_ destinations, the intent of proposal 144 is that
the destinations no longer support 32-byte tags and AES decryption.
The specifics were intentionally not included in that proposal.

This proposal documents a new option in the DLM to request ECIES-encrypted replies.


Goals
-----

- New flags for DLM when an encrypted reply is requested down a tunnel to a ECIES destination
- For the reply, add forward secrecy and sender authentication resistant to
  the requester's (destination) key compromise impersonation (KCI).
- Maintain anonymity of requester
- Minimize crypto overhead

Non-Goals
---------

- No change to the encryption or security properties of the lookup (DLM).
  The lookup has forward secrecy for requester key compromise only.
  The encryption is to the floodfill's static key.
- No forward secrecy or sender authentication issues resistant to
  the responder's (floodfill's) key compromise impersonation (KCI).
  The floodfill is a public database and will respond to lookups
  from anybody.
- Don't design ECIES routers in this proposal.
  Where a router's X25519 public key goes is TBD.


Alternatives
============

In the absence of a defined way to encrypt replies to ECIES destinations, there
are several alternatives:

1) Do not request encrypted replies. Replies will be unencrypted.
Java I2P currently uses this approach.

2) Add support for 32-byte tags and AES-encrypted replies to ECIES-only destinations,
and request AES-encrypted replies as usual. i2pd currently uses this approach.

3) Request AES-encrypted replies as usual, but route them back through
exploratory tunnels to the router.
Java I2P currently uses this approach in some cases.

4) For dual ElG and ECIES destinations,
request AES-encrypted replies as usual. Java I2P currently uses this approach.
i2pd has not yet implemented dual-crypto destinations.


Design
======

- New DLM format will add a bit to the flags field to specify ECIES-encrypted replies.
  ECIES-encrypted replies will use the [ECIES]_ Existing Session message format,
  with a prepended tag and a ChaCha/Poly payload and MAC.

- Define two variants. One for ElG routers, where a DH operation is not possible,
  and one for future ECIES routers, where a DH operation is possible and may provide
  additional security. For further study.

DH is not possible for replies from ElG routers because they do not publish
a X25519 public key.




Specification
=============

In the [I2NP]_ DLM (DatabaseLookup) specification, make the following changes.


Add flag bit 4 "ECIESFlag" for the new encryption options.

.. raw:: html

  {% highlight lang='dataspec' %}
flags ::
       bit 4: ECIESFlag
               before release 0.9.46 ignored
               as of release 0.9.46:
               0  => send unencrypted or ElGamal reply
               1  => send ChaCha/Poly encrypted reply using enclosed key
                     (whether tag is enclosed depends on bit 1)
{% endhighlight %}

Flag bit 4 is used in combination with bit 1 to determine the reply encryption mode.
Flag bit 4 must only be set when sending to routers with version 0.9.46 or higher.


=============  =========  =========  ======  ===  =======
Flag bits 4,1  From Dest  To Router  Reply   DH?  notes
=============  =========  =========  ======  ===  =======
0 0            Any        Any        no enc  no   current
0 1            ElG        ElG        AES     no   current
0 1            ECIES      ElG        AES     no   i2pd workaround
1 0            ECIES      ElG        AEAD    no   new, no DH
1 1            ECIES      ECIES      AEAD    yes  future, with DH
=============  =========  =========  ======  ===  =======


ElG to ElG
----------

ElG destination sends a lookup to a ElG router.

Minor changes to the specification to check for new bit 4.
No changes to the existing binary format.


Requester key generation (clarification):

.. raw:: html

  {% highlight lang='dataspec' %}
reply_key :: CSRNG(32) 32 bytes random data
  reply_tags :: Each is CSRNG(32) 32 bytes random data
{% endhighlight %}

Message format (add check for ECIESFlag):

.. raw:: html

  {% highlight lang='dataspec' %}
reply_key ::
       32 byte `SessionKey` big-endian
       only included if encryptionFlag == 1 AND ECIESFlag == 0, only as of release 0.9.7

  tags ::
       1 byte `Integer`
       valid range: 1-32 (typically 1)
       the number of reply tags that follow
       only included if encryptionFlag == 1 AND ECIESFlag == 0, only as of release 0.9.7

  reply_tags ::
       one or more 32 byte `SessionTag`s (typically one)
       only included if encryptionFlag == 1 AND ECIESFlag == 0, only as of release 0.9.7
{% endhighlight %}




ECIES to ElG
------------

ECIES destination sends a lookup to a ElG router.
Supported as of 0.9.46.

The reply_key and reply_tags fields are redefined for an ECIES-encrypted reply.

Requester key generation:

.. raw:: html

  {% highlight lang='dataspec' %}
reply_key :: CSRNG(32) 32 bytes random data
  reply_tags :: Each is CSRNG(8) 8 bytes random data
{% endhighlight %}

Message format:
Redefine reply_key and reply_tags fields as follows:

.. raw:: html

  {% highlight lang='dataspec' %}
reply_key ::
       32 byte ECIES `SessionKey` big-endian
       only included if encryptionFlag == 0 AND ECIESFlag == 1, only as of release 0.9.46

  tags ::
       1 byte `Integer`
       required value: 1
       the number of reply tags that follow
       only included if encryptionFlag == 0 AND ECIESFlag == 1, only as of release 0.9.46

  reply_tags ::
       an 8 byte ECIES `SessionTag`
       only included if encryptionFlag == 0 AND ECIESFlag == 1, only as of release 0.9.46

{% endhighlight %}


The reply is an ECIES Existing Session message, as defined in [ECIES]_.

.. raw:: html

  {% highlight lang='dataspec' %}
tag :: 8 byte reply_tag

  k :: 32 byte session key
     The reply_key.

  n :: 0

  ad :: The 8 byte reply_tag

  payload :: Plaintext data, the DSM or DSRM.

  ciphertext = ENCRYPT(k, n, payload, ad)

{% endhighlight %}





ECIES to ECIES
--------------

ECIES destination sends a lookup to a ECIES router.
Supported as of 0.9.TBD.

The lookup will use the "one time format" in [ECIES]_
as the requester is anonymous.

Redefine reply_key field as follows. There are no associated tags.
The tags will be generated in the KDF below.

This section is incomplete and requires further study.
ECIES routers do not yet exist and there is no documented proposal
for ECIES routers at this time.


.. raw:: html

  {% highlight lang='dataspec' %}
reply_key ::
       32 byte X25519 ephemeral `PublicKey` of the requester, little-endian
       only included if encryptionFlag == 1 AND ECIESFlag == 1, only as of release 0.9.TBD

{% endhighlight %}

The reply is an ECIES Existing Session message, as defined in [ECIES]_.
See [ECIES]_ for all definitions.


.. raw:: html

  {% highlight lang='dataspec' %}
// Alice's X25519 ephemeral keys
  // aesk = Alice ephemeral private key
  aesk = GENERATE_PRIVATE()
  // aepk = Alice ephemeral public key
  aepk = DERIVE_PUBLIC(aesk)
  // Bob's X25519 static keys
  // bsk = Bob private static key
  bsk = GENERATE_PRIVATE()
  // bpk = Bob public static key
  // bpk is either part of RouterIdentity, or published in RouterInfo (TBD)
  bpk = DERIVE_PUBLIC(bsk)

  // (DH()
  //[chainKey, k] = MixKey(sharedSecret)
  // chainKey from ???
  sharedSecret = DH(aesk, bpk) = DH(bsk, aepk)
  keydata = HKDF(chainKey, sharedSecret, "ECIES-DSM-Reply1", 32)
  chainKey = keydata[0:31]

  1) rootKey = chainKey from Payload Section
  2) k from the New Session KDF or split()

  // KDF_RK(rk, dh_out)
  keydata = HKDF(rootKey, k, "KDFDHRatchetStep", 64)

  // Output 1: unused
  unused = keydata[0:31]
  // Output 2: The chain key to initialize the new
  // session tag and symmetric key ratchets
  // for Alice to Bob transmissions
  ck = keydata[32:63]

  // session tag and symmetric key chain keys
  keydata = HKDF(ck, ZEROLEN, "TagAndKeyGenKeys", 64)
  sessTag_ck = keydata[0:31]
  symmKey_ck = keydata[32:63]

  tag :: 8 byte tag as generated from RATCHET_TAG() in [ECIES]_

  k :: 32 byte key as generated from RATCHET_KEY() in [ECIES]_

  n :: The index of the tag. Typically 0.

  ad :: Associated data. ZEROLEN.

  payload :: Plaintext data, the DSM or DSRM.

  ciphertext = ENCRYPT(k, n, payload, ad)
{% endhighlight %}



Reply format
------------

This is the existing session message,
same as in [ECIES]_, copied below for reference.

.. raw:: html

  {% highlight lang='dataspec' %}
+----+----+----+----+----+----+----+----+
  |       Session Tag                     |
  +----+----+----+----+----+----+----+----+
  |                                       |
  +            Payload Section            +
  |       ChaCha20 encrypted data         |
  ~                                       ~
  |                                       |
  +                                       +
  |                                       |
  +----+----+----+----+----+----+----+----+
  |  Poly1305 Message Authentication Code |
  +              (MAC)                    +
  |             16 bytes                  |
  +----+----+----+----+----+----+----+----+

  Session Tag :: 8 bytes, cleartext

  Payload Section encrypted data :: remaining data minus 16 bytes

  MAC :: Poly1305 message authentication code, 16 bytes

{% endhighlight %}


Justification
=============

The reply encryption parameters in the lookup, first introduced in 0.9.7, 
are somewhat of a layering violation. It's done this way for efficiency.
But also because the lookup is anonymous.

We could make the lookup format generic, like with an encryption type field,
but that's probably more trouble than it's worth.

The above proposal is the easiest and minimizes the change to the lookup format.



Notes
=====

Database lookups and stores to ElG routers must be ElGamal/AESSessionTag encrypted
as usual.


Issues
======

Further analysis is required on the security of the two ECIES reply options.



Migration
=========

No backward compatibility issues. Routers advertising a router.version of 0.9.46 or higher
in their RouterInfo must support this feature.
Routers must not send a DatabaseLookup with the new flags to routers with a version less than 0.9.46.
If a database lookup message with bit 4 set and bit 1 unset is mistakenly sent to
a router without support, it will probably ignore the supplied key and tag, and
sent the reply unencrypted.

References
==========

.. [ECIES]
   {{ proposal_url('144') }}

.. [I2NP]
    {{ spec_url('i2np') }}

