==============
I2P Mime Types
==============
.. meta::
    :author: zzz
    :created: 2017-05-16
    :thread: http://zzz.i2p/topics/1957
    :lastupdated: 2017-05-16
    :status: Open

.. contents::


Overview
========

Define mime types for common I2P file formats.
Include the definitions in Debian packages.
Provide a handler for the .su3 type, and possibly others.


Motivation
==========

To make reseeding and plugin installation easier when downloading with a browser,
we need a mime type and handler for .su3 files.

While we are at it, after learning how to write the mime definition file,
following the freedesktop.org standard, we can add definitions for other common
I2P file types.
While less useful for files that aren't usually downloaded, such as the
addressbook blockfile database (hostsdb.blockfile), these definitions will
allow files to be better identified and iconified when using a graphical
directory viewer such as "nautilus" on Ubuntu.

By standardizing the mime types, each router implementation may write handlers
as appropriate, and the mime definition file may be shared by all implementations.



Design
======

Write an XML source file following the freedesktop.org standard and include it
in Debian packages. The file is "debian/(package).sharedmimeinfo".

All I2P mime types will start with "application/x-i2p-", except for the jrobin rrd.

Handlers for these mime types are application-specific and will not
be specified here.

We will also include the definitions with Jetty, and include them with
the reseed software or instructions.



Specification
=============

.blockfile 		application/x-i2p-blockfile

.config 		application/x-i2p-config

.dat	 		application/x-i2p-privkey

.dat	 		application/x-i2p-dht

=.dat	 		application/x-i2p-routerinfo

.ht	 		application/x-i2p-errorpage

.info	 		application/x-i2p-routerinfo

.jrb	 		application/x-jrobin-rrd

.su2			application/x-i2p-update

.su3	(generic)	application/x-i2p-su3

.su3	(router update)	application/x-i2p-su3-update

.su3	(plugin)	application/x-i2p-su3-plugin

.su3	(reseed)	application/x-i2p-su3-reseed

.su3	(news)		application/x-i2p-su3-news

.su3	(blocklist)	application/x-i2p-su3-blocklist

.sud			application/x-i2p-update

.syndie	 		application/x-i2p-syndie

=.txt.gz 		application/x-i2p-peerprofile

.xpi2p	 		application/x-i2p-plugin




Notes
=====

Not all file formats listed above are used by non-Java router implementations;
some may not even be well-specified. However, documenting them here
may enable cross-implementation consistency in the future.

Some file suffixes such as ".config", ".dat" and ".info" may overlap with other
mime types. These may be disambiguated with additional data such as
full file name, a file name pattern, or magic numbers.
See the draft i2p.sharedmimeinfo file in the zzz.i2p thread for examples.

The important ones are the .su3 types, and those type have both
a unique suffix and robust magic number definitions.


Migration
=========

Not applicable.

