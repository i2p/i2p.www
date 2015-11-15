==========================================
Blockfile and Hosts Database Specification
==========================================
.. meta::
    :lastupdated: November 2014
    :accuratefor: 0.9.17


Overview
========

This document specifies the I2P blockfile file format and the tables in the
hostsdb.blockfile used by the Blockfile Naming Service [NAMING]_.

The blockfile provides fast Destination lookup in a compact format. While the
blockfile page overhead is substantial, the destinations are stored in binary
rather than in Base 64 as in the hosts.txt format.  In addition, the blockfile
provides the capability of arbitrary metadata storage (such as added date,
source, and comments) for each entry.  The metadata may be used in the future
to provide advanced addressbook features.  The blockfile storage requirement is
a modest increase over the hosts.txt format, and the blockfile provides
approximately 10x reduction in lookup times.

A blockfile is simply on-disk storage of multiple sorted maps (key-value
pairs), implemented as skiplists.  The blockfile format is adopted from the
Metanotion Blockfile Database [METANOTION]_.  First we will define the file
format, then the use of that format by the BlockfileNamingService.


Blockfile Format
================

The original blockfile spec was modified to add magic numbers to each page.
The file is structured in 1024-byte pages. Pages are numbered starting from 1.
The "superblock" is always at page 1, i.e. starting at byte 0 in the file.  The
metaindex skiplist is always at page 2, i.e. starting at byte 1024 in the file.

All 2-byte integer values are unsigned.  All 4-byte integer values (page
numbers) are signed and negative values are illegal.  All integer values are
stored in network byte order (big endian).

The database is designed to be opened and accessed by a single thread.  The
BlockfileNamingService provides synchronization.

Superblock format:

.. raw:: html

  {% highlight %}Byte	Contents
  0-5	Magic number	0x3141de493250 ("1A" 0xde "I2P")
  6	Major version	0x01
  7	Minor version	0x02
  8-15	File length	Total length in bytes
  16-19	First free list page
  20-21	Mounted flag	0x01 = yes
  22-23	Span size	Max number of key/value pairs per span (16 for hostsdb)
  			Used for new skip lists.
  24-27	Page size	As of version 1.2. Prior to 1.2, 1024 is assumed.
  28-1023	unused
{% endhighlight %}

Skip list block page format:

.. raw:: html

  {% highlight %}Byte	Contents
  0-7	Magic number	0x536b69704c697374 "SkipList"
  8-11	First span page
  12-15	First level page
  16-19	Size (total number of keys - may only be valid at startup)
  20-23	Spans (total number of spans - may only be valid at startup)
  24-27	Levels (total number of levels - may only be valid at startup)
  28-29	Span size - As of version 1.2. Max number of key/value pairs per span.
                      Prior to that, specified for all skiplists in the superblock.
                      Used for new spans in this skip list.
  30-1023	unused
{% endhighlight %}

Skip level block page format is as follows.
All levels have a span. Not all spans have levels.

.. raw:: html

  {% highlight %}Byte	Contents
  0-7	Magic number	0x42534c6576656c73 "BSLevels"
  8-9	Max height
  10-11	Current height
  12-15	Span page
  16-	Next level pages ('current height' entries, 4 bytes each, lowest first)
  remaining bytes unused
{% endhighlight %}

Skip span block page format is as follows.
Key/value structures are sorted by key within each span and across all spans.
Key/value structures are sorted by key within each span.
Spans other than the first span may not be empty.

.. raw:: html

  {% highlight %}Byte	Contents
  0-3	Magic number	0x5370616e "Span"
  4-7	First continuation page or 0
  8-11	Previous span page or 0
  12-15	Next span page or 0
  16-17	Max keys (16 for hostsdb)
  18-19	Size (current number of keys)
  20-1023	key/value structures
{% endhighlight %}

Span Continuation block page format:

.. raw:: html

  {% highlight %}Byte	Contents
  0-3	Magic number	0x434f4e54 "CONT"
  4-7	Next continuation page or 0
  8-1023	key/value structures
{% endhighlight %}

Key/value structure format is as follows.
Key and value lengths must not be split across pages, i.e. all 4 bytes must be on the same page.
If there is not enough room the last 1-3 bytes of a page are unused and the lengths will
be at offset 8 in the continuation page.
Key and value data may be split across pages.
Max key and value lengths are 65535 bytes.

.. raw:: html

  {% highlight %}Byte	Contents
  0-1	key length in bytes
  2-3	value length in bytes
  4-	key data
  	value data
{% endhighlight %}

Free list block page format:

.. raw:: html

  {% highlight %}Byte	Contents
  0-7	Magic number	0x2366724c69737423 "#frList#"
  8-11	Next free list block or 0 if none
  12-15	Number of valid free pages in this block (0 - 252)
  16-1023	Free pages (4 bytes each), only the first (valid number) are valid
{% endhighlight %}

Free page block format:

.. raw:: html

  {% highlight %}Byte	Contents
  0-7	Magic number	0x7e2146524545217e "~!FREE!~"
  8-1023	unused
{% endhighlight %}

The metaindex (located at page 2) is a mapping of US-ASCII strings to 4-byte integers.
The key is the name of the skiplist and the value is the page index of the skiplist.


Blockfile Naming Service Tables
===============================

The tables created and used by the BlockfileNamingService are as follows.
The maximum number of entries per span is 16.

Properties Skiplist
-------------------

"%%__INFO__%%" is the master database skiplist with String/Properties key/value
entries containing only one entry:

    info
        a Properties (UTF-9 String/String Map), serialized as a [Mapping]_:

        version
            "3"

        created
            Java long time (ms)

        upgraded
            Java long time (ms) (as of database version 2)

        lists
            Comma-separated list of host databases, to be searched in-order for
            lookups. Almost always "privatehosts.txt,userhosts.txt,hosts.txt".

Reverse Lookup Skiplist
-----------------------

"%%__REVERSE__%%" is the reverse lookup skiplist with Integer/Properties
key/value entries (as of database version 2):

* The skiplist keys are 4-byte Integers, the first 4 bytes of the hash of the
  [Destination]_.

* The skiplist values are each a Properties (a UTF-8 String/String Map)
  serialized as a [Mapping]_

  * There may be multiple entries in the properties, each one is a reverse
    mapping, as there may be more than one hostname for a given destination, or
    there could be collisions with the same first 4 bytes of the hash.

  * Each property key is a hostname.

  * Each property value is the empty string.

hosts.txt, userhosts.txt, and privatehosts.txt Skiplists
--------------------------------------------------------

For each host database, there is a skiplist containing the hosts for that
database.  The keys/values in these skiplists are as follows:

    key
        a UTF-8 String (the hostname)

    value
        a DestEntry, which is a Properties (a UTF-8 String/String Map)
        serialized as a [Mapping]_ followed by a binary [Destination]_
        (serialized as usual).

The DestEntry Properties typically contains:

    "a"
        The time added (Java long time in ms)

    "s"
        The original source of the entry (typically a file name or subscription
        URL)

Hostname keys are stored in lower-case and always end in ".i2p".


References
==========

.. [Destination]
    {{ ctags_url('Destination') }}

.. [Mapping]
    {{ ctags_url('Mapping') }}

.. [METANOTION]
    http://www.metanotion.net/software/sandbox/block.html

.. [NAMING]
    {{ site_url('docs/naming', True) }}
