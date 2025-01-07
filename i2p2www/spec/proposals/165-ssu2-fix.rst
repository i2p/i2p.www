===========================
I2P proposal #165: SSU2 fix
===========================
.. meta::
    :author: weko, orignal, the Anonymous, zzz
    :created: 2024-01-19
    :thread: http://i2pforum.i2p/viewforum.php?f=13
    :lastupdated: 2024-11-17
    :status: Open
    :target: 0.9.62

.. contents::



Proposal by weko, orignal, the Anonymous and zzz.


Overview
--------

This document suggests changes to SSU2 following an attack on I2P that exploited vulnerabilities in SSU2. The primary goal is to enhance security and prevent Distributed Denial of Service (DDoS) attacks and de-anonymization attempts.

Threat model
------------

An attacker creates new fake RIs (router doesn’t exist): is regular RI,
but he puts address, port, s and i keys from real Bob’s router, then he
floods the network. When we are trying to connect to this (as we think
real) router, we, as Alice can connect to this address, but we can’t be
sure what done it with real Bob’s RI. This is possible and was used for
a Distributed Denial of Service attack (make big amount of such RIs and
flood the network), also this can make de-anon attacks easier by framing
good routers and do not framing attacker’s routers, if we ban IP with
many RIs (instead better distrubute tunnel building to this RIs as to
one router).


Potential fixes
---------------

1. Fix with support for old (before the change) routers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _overview-1:

Overview
^^^^^^^^

A workaround to support SSU2 connections with old routers.

Behavivor
^^^^^^^^^

Bob’s router profile should have ‘verified’ flag, it’s false by default
for all new routers (with no profile yet). When ‘verified’ flag is
false, we never do connections with SSU2 as Alice to Bob - we can’t be
sure in RI. If Bob connected to us (Alice) with NTCP2 or SSU2 or we
(Alice) connected to Bob with NTCP2 once (we can verify Bob’s
RouterIdent in these cases) - flag is set to true.

Problems
^^^^^^^^

So, there is a problem with fake SSU2-only RI flood: we can’t verify it
by ourselves and are forced to wait when the real router will make
connections with us.

2. Verify RouterIdent during connection creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _overview-2:

Overview
^^^^^^^^

Add “RouterIdent” block for SessionRequest and SessionCreated.

Possible format of RouterIdent block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1 byte flags, 32 bytes RouterIdent. Flag_0: 0 if receiver’s RouterIdent;
1 if sender’s RouterIdent

Behavior
^^^^^^^^

Alice (should(1), can(2)) send in payload RouterIdent block Flag_0 = 0
and Bob’s RouterIdent. Bob (should(3), can(4)) check if is it his
RouterIdent, and if not: terminate the session with “Wrong RouterIdent”
reason, if it is his RouterIdent: send RI block with 1 in Flag_0 and
Bob’s RouterIdent.

With (1) Bob does not support old routers. With (2) Bob supports old
routers, but can be a victim of DDoS from routers that are trying to
make connection with fake RIs. With (3) Alice does not support old
routers. With (4) Alice supports old routers and is using a hybrid
scheme: Fix 1 for old routers and Fix 2 for new routers. If RI says new
version, but while in the connection we didnt’s recieve the RouterIdent
block - terminate and remove RI.

.. _problems-1:

Problems
^^^^^^^^

An attacker can mask his fake routers as old, and with (4) we are
waiting for ‘verified’ as in fix 1 anyways.

Notes
^^^^^

Instead of 32 byte RouterIdent, we can probably use 4 byte
siphash-of-the-hash, some HKDF or something else, which must be
sufficient.

3. Bob sets i = RouterIdent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _overview-3:

Overview
^^^^^^^^

Bob uses his RouterIdent as i key.

.. _behavior-1:

Behavior
^^^^^^^^

Bob (should(1), can(2)) uses his own RouterIdent as i key for SSU2.

Alice with (1) connects only if i = Bob’s RouterIdent. Alice with (2)
uses the hybrid scheme (fix 3 and 1): if i = Bob’s RouterIdent, we can
make the connection, otherwise we should verify it first (see fix 1).

With (1) Alice does not support old routers. With (2) Alice supports old
routers.

.. _problems-2:

Problems
^^^^^^^^

An attacker can mask his fake routers as old, and with (2) we are
waiting for ‘verified’ as in fix 1 anyways.

.. _notes-1:

Notes
^^^^^

To save on RI size, better add handling if i key isn’t specified. If it
is, then i = RouterIdent. In that case, Bob does not support old
routers.

4. Add one more MixHash to KDF of SessionRequest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _overview-4:

Overview
^^^^^^^^

Add MixHash(Bob's ident hash) to NOISE state of "SessionRequest" message, e.g.
h = SHA256 (h || Bob's ident hash).
It must be last MixHash used as ad for ENCYPT or DECRYPT.
Additional SSU2 header flag "Verify Bob's ident" = 0x02 must be introduced.

.. _behavior-4:

Behavior
^^^^^^^^

- Alice adds MixHash with Bob's ident hash from Bob's RouterInfo and use it as ad for ENCRYPT and sets "Verify Bob's ident" flag
- Bob checks "Verify Bob's ident" flag and adds MixHash with own ident hash and use it ad as for DECRYPT. Is AEAD/Chacha20/Poly1305 fails, Bob closes the session.

Compatibity with older routers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Alice must check Bob's router version and if it satisfies miminal version supporting this proposal add this MixHash and set "Verify Bob's ident" flag. If router is older, Alice doesn't add MixHash and doesn't set "Verify Bob's ident" flag.
- Bob checks "Verify Bob's ident" flag and adds this MixHash if it's set. Older router don't set this flag and this MixHash shouldn't be added.

.. _problems-4:

Problems
^^^^^^^^

- An attacker can claim fake routers with older version. At some point olders router should be used with precaution and  after they got verified by other ways.


Backward compability
--------------------

Described in fixes.


Current status
--------------

i2pd: Fix 1.
