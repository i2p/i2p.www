================================
New Encryption Proposal Template
================================
.. meta::
    :author: zzz
    :created: 2018-01-11
    :thread: http://zzz.i2p/topics/2499
    :lastupdated: 2018-01-20
    :status: Meta

.. contents::


Overview
========

This document describes important issues to consider when proposing
a replacement or addition to our ElGamal asymmetric encryption.

This is an informational document.


Motivation
==========

ElGamal is old and slow, and there are better alternatives.
However, there are several issues that must be addressed before we can add or change to any new algorithm.
This document highlights these unresolved issues.



Background Research
===================

Anybody proposing new crypto must first be familiar with the following documents:

- Proposal 111 NTCP2 https://geti2p.net/spec/proposals/111-ntcp-2
- Proposal 123 LS2 https://geti2p.net/spec/proposals/123-new-netdb-entries
- Proposal 136 experimental sig types https://geti2p.net/spec/proposals/136-experimental-sigtypes
- Proposal 137 optional sig types https://geti2p.net/spec/proposals/137-optional-sigtypes
- Discussion threads here for each of the above proposals, linked within
- http://zzz.i2p/topics/2494 2018 proposal priorities
- http://zzz.i2p/topics/2418 ECIES proposal
- http://zzz.i2p/topics/1768 new asymmetric crypto overview
- Low-level crypto overview https://geti2p.net/spec/cryptography


Asymmetric Crypto Uses
======================

As a review, we use ElGamal for:

1) Tunnel Build messages (key is in RouterIdentity)

2) Router-to-router encryption of netdb and other I2NP msgs (Key is in RouterIdentity)

3) Client End-to-end ElGamal+AES/SessionTag (key is in LeaseSet, the Destination key is unused)

4) Ephemeral DH for NTCP and SSU


Design
======

Any proposal to replace ElGamal with something else must provide the following details.



Specification
=============

Any proposal for new asymmetric crypto must fully specify the following things.



1. General
----------

Answer the following questions in your proposal. Note that this may need to be a separate proposal from the specifics in 2) below, as it may conflict with existing proposals 111, 123, 136, 137, or others.

- Which of the above cases 1-4 do you propose to use the new crypto for?
- If for 1) or 2) (router), Where does the public key go, in the RouterIdentity or the RouterInfo props? Do you intend to use the crypto type in the key cert? Completely specify. Justify your decision either way.
- If for 3) (client), do you intend to store the public key in the destination and use the crypto type in the key cert (as in the ECIES proposal), or store it in LS2 (as in proposal 123), or something else? Completely specify, and justify your decision.
- For all uses, how will support be advertised? If for 3), does it go in the LS2, or somewhere else? If for 1) and 2), is it similar to proposals 136 and/or 137? Completely specify, and justify your decisions. Will probably need a separate proposal for this.
- Completely specify how and why this is backward compatible, and fully specify a migration plan.
- Which unimplemented proposals are prerequisites for your proposal?


2. Specific crypto type
-----------------------

Answer the following questions in your proposal:

- General crypto info, specific curves/parameters, completely justify your choice. Provide links to specs and other info.
- Speed test results compared to ElG and other alternatives if applicable. Include encrypt, decrypt, and keygen.
- Library availability in C++ and Java (both OpenJDK, BouncyCastle, and 3rd party)
  For 3rd party or non-Java, provide links and licenses
- Proposed crypto type number(s) (experimental range or not)




Notes
=====



