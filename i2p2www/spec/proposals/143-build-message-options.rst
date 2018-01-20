============================
Tunnel Build Message Options
============================
.. meta::
    :author: zzz
    :created: 2018-01-14
    :thread: http://zzz.i2p/topics/2500
    :lastupdated: 2017-01-20
    :status: Open

.. contents::


Overview
========

ref: http://i2p-projekt.i2p/spec/tunnel-creation

Add a flexible, extensible mechanism for options in the I2NP Tunnel Build Records
which are contained in the Tunnel Build and Tunnel Build Reply messages.


Motivation
==========


There are a few tentative, undocumented proposals coming to set options or configuration in the Tunnel Build Message,
so the creator of the tunnel may pass some parameters to each tunnel hop.

There are 29 spare bytes in the TBM. We want to keep flexibility for future enhancements, but also use the space wisely.
Using the 'mapping' construction would use at least 6 bytes per option ("1a=1b;").
Defining more option fields rigidly could cause problems later.

This document proposes a new, flexible options mapping scheme.



Design
======

We need an option representation that is compact and yet flexible, so that we may fit multiple
options, of varying length, into 29 bytes.
These options are not yet defined, and are not required to be at this time.
Don't use the "mapping" structure (which encodes a Java Properties object), it is too wasteful.
Use a number to indicate each option and length, which results in a compact yet flexible encoding.
Options must be registered by number in our specifications, but we will also reserve a range for experimental options.


Specification
=============

Preliminary - several alternatives are described below.

This would be present only if bit 5 in the flags (byte 184) is set to 1.

Each option is a two byte option number and length, followed by length bytes of option value.

Options start at byte 193 and continue through at most the last byte 221.

Option number/length:

Two bytes. Bits 15-4 are the 12-bit option number, 1 - 4095.
Bits 3-0 are the number of option value bytes to follow, 0 - 15.
A boolean option could have zero value bytes.
We will maintain a registry of option numbers in our specs, and also define a range for experimental options.

The option value is 0 to 15 bytes, to be interpreted by whatever needs that option. Unknown option numbers should be ignored.

The options are concluded with an option number/length of 0/0, that is two 0 bytes.
 The remainder of the 29 bytes, if any, should be filled with random padding, as usual.

This encoding gives us space for 14 0-byte options, or 9 1-byte options, or 7 2-byte options.
An alternative would be to use only one byte for the option number/length,
perhaps with 5 bits for option number (32 max and 3 bits for length (7 max).
This would increase capacity to 28 0-byte options, 14 1-byte options, or 9 two-byte options.
We could also make it variable, where a 5-bit option number of 31 means read 8 more bits for the option number.

If the tunnel hop needs to return options to the creator, we may use the same format in the tunnel build reply message,
prefixed by some magic number of several bytes (since we don't have a defined flag byte to indicate that options are present).
There are 495 spare bytes in the TBRM.


Notes
=====

These changes are to the Tunnel Build Records, and so may be used in all Build Message flavors -
Tunnel Build Request, Variable Tunnel Build Request, Tunnel Build Reply, and Variable Tunnel Build Reply.



Migration
=========

The unused space in the Tunnel Build Records are filled with random data and currently ignored.
The space can be converted to contain options without migration issues.
In the build message, the presence of options is indicated in the flags byte.
In the build reply message, the presence of options is indicated by a multi-byte magic number.
