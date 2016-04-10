=================
Service Directory
=================
.. meta::
    :author: zzz
    :created: 2009-01-01
    :thread: http://zzz.i2p/topics/180
    :lastupdated: 2009-01-06
    :status: Draft

.. contents::


Introduction
============

This is similar to a proposal Sponge had a while back on IRC. I don't think he
wrote it up, but his idea was to put it in the netDb. I'm not in favor of that,
but the discussion of the best method of accessing the directory (netDb lookups,
DNS-over-i2p, HTTP, hosts.txt, etc.) I will leave for another day.

I could probably hack this up pretty quickly using HTTP and the collection of
perl scripts I use for the add key form.


Directory Interface
===================

Here's how an app would interface with the directory:

REGISTER
  - DestKey
  - List of Protocol/Service pairs:

    - Protocol (optional, default: HTTP)
    - Service (optional, default: website)
    - ID (optional, default: none)

  - Hostname (optional)
  - Expiration (default: 1 day? 0 for delete)
  - Sig (using privkey for dest)

  Returns: success or failure

  Updates allowed

LOOKUP
  - Hash or key (optional). ONE of:

    - 80-bit partial hash
    - 256-bit full hash
    - full destkey

  - Protocol/service pair (optional)

  Returns: success, failure, or (for 80-bit) collision.
  If success, returns signed descriptor above.
