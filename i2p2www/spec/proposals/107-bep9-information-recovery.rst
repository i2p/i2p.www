=========================
BEP9 Information Recovery
=========================
.. meta::
    :author: sponge
    :created: 2011-02-23
    :thread: http://zzz.i2p/topics/860
    :lastupdated: 2011-02-23
    :status: Draft

.. contents::


Problem
=======

BEP9 does not send the entire torrent file, thus losing several important
dictionary items, and changes the torrent files total SHA1. This is bad for
maggot links, and bad because important information is lost. Tracker lists,
comments, and any additional data is gone. A way to recover this information is
important, and it needs to add as little as possible to the torrent file. It
also must not be circular dependent. Recovery information should not affect
current clients in any way. torrents that are trackerless (tracker URL is
literally 'trackerless') do not contain the extra field, as they are specific to
using the maggot protocol of discovery and download, which does not ever lose
the information in the first place.


Solution
========

All that needs to be done is to compress the information that would be lost, and
store it in the info dictionary.


Implementation
--------------
1. Generate the normal info dictionary.
2. Generate the main dictionary, and leave out the info entry.
3. Bencode, and compress he main dictionary with gzip.
4. Add the compressed main dictionary to the info dictionary.
5. Add info to the main dictionary.
6. Write the torrent file

Recovery
--------
1. Decompress the recovery entry in the info dict.
2. Bendecode the recovery entry.
3. Add info to the recovered dictionary.
4. For maggot-aware clients, you can now verify that the SHA1 is correct.
5. Write out the recovered torrent file.


Discussion
==========

Using the above outlined method, the size of the torrent increase is very small,
200 to 500 bytes is typical. Robert will be shipping with the new info
dictionary entry creation, and it will not be able to be turned off. Here is the
structure::

    main dict {
        Tracker strings, comments, etc...
        info : {
            gzipped main bencoded dict minus the info dictionary and all other
            usual info
        }
    }
