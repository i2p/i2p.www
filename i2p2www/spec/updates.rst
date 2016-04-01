=============================
Software Update Specification
=============================
.. meta::
    :lastupdated: March 2016
    :accuratefor: 0.9.25

.. contents::


Overview
========

I2P uses a simple, yet secure, system for automated software update.  The
router console periodically pulls a news file from a configurable I2P URL.
There is a hardcoded backup URL pointing to the project website, in case the
default project news host goes down.

The contents of the news file are displayed on the home page of the router
console.  In addition, the news file contains the most recent version number of
the software.  If the version is higher than the router's version number, it
will display an indication to the user that an update is available.

The router may optionally download, or download and install, the new version if
configured to do so.

Old News File Specification
---------------------------

This format is replaced by the su3 news format as of release 0.9.17.

The news.xml file may contain the following elements::

    <i2p.news date="$Date: 2010-01-22 00:00:00 $" />
    <i2p.release version="0.7.14" date="2010/01/22" minVersion="0.6" />

Parameters in the i2p.release entry are as follows.  All keys are
case-insensitive. All values must be enclosed in double quotes.

    date
        The release date of the router version.

        Unused. Format not specified.

    minJavaVersion
        The minimum version of Java required to run the current version.

        As of release 0.9.9.

    minVersion
        The minimum version of the router required to update to the current
        version. If a router is older than this, the user must (manually?)
        update to an intermediate version first.

        As of release 0.9.9.

    su3Clearnet
        One or more HTTP URLs where the .su3 update file may be found on the
        clearnet (non-I2P). Multiple URLs must be separated by a space or comma.

        As of release 0.9.9.

    su3SSL
        One or more HTTPS URLs where the .su3 update file may be found on the
        clearnet (non-I2P). Multiple URLs must be separated by a space or comma.

        As of release 0.9.9.

    sudTorrent
        The magnet link for the .sud (non-pack200) torrent of the update.

        As of release 0.9.4.

    su2Torrent
        The magnet link for the .su2 (pack200) torrent of the update.

        As of release 0.9.4.

    su3Torrent
        The magnet link for the .su3 (new format) torrent of the update.

        As of release 0.9.9.

    version
        Required.

        The latest current router version available.

The elements may be included inside XML comments to prevent interpretation by
browsers.  The i2p.release element and version are required. All others are
optional.  NOTE: Due to parser limitations an entire element must be on a
single line.

Update File Specification
-------------------------

As of release 0.9.9, the signed update file, named i2pupdate.su3, will use the
"su3" file format specified below.  Approved release signers will use 4096-bit
RSA keys.  The X.509 public key certificates for these signers are distributed
in the router installation packages.  The updates may contain certificates for
new, approved signers, and/or contain a list of certificates to delete for
revocation.


Old Update File Specification
-----------------------------

This format is obsolete as of release 0.9.9.

The signed update file, traditionally named i2pupdate.sud, is simply a zip file
with a prepended 56 byte header.  The header contains:

* A 40-byte DSA [Signature]_
* A 16-byte I2P version in UTF-8, padded with trailing zeroes if necessary

The signature covers only the zip archive - not the prepended version.  The
signature must match one of the DSA [SigningPublicKey]_ configured into the
router, which has a hardcoded default list of keys of the current project
release managers.

For version comparison purposes, version fields contain [0-9]*, field
separators are '-', '_', and '.', and all other characters are ignored.

As of version 0.8.8, the version must also be specified as a zip file comment
in UTF-8, without the trailing zeroes.  The updating router verifes that the
version in the header (not covered by the signature) matches the version in the
zip file comment, which is covered by the signature.  This prevents spoofing of
the version number in the header.

Download and Installation
-------------------------

The router first downloads the header of the update file from one in a
configurable list of I2P URLs, using the built-in HTTP client and proxy, and
checks that the version is newer.  This prevents the problem of update hosts
that do not have the latest file.  The router then downloads the full update
file.  The router verifies that the update file version is newer before
installation.  It also, of course, verifies the signature, and verifes that the
zip file comment matches the header version, as explained above.

The zip file is extracted and copied to "i2pupdate.zip" in the I2P
configuration directory (~/.i2p on Linux).

As of release 0.7.12, the router supports Pack200 decompression.  Files inside
the zip archive with a .jar.pack or .war.pack suffix are transparently
decompressed to a .jar or .war file.  Update files containing .pack files are
traditionally named with a '.su2' suffix.  Pack200 shrinks the update files by
about 60%.

As of release 0.8.7, the router will delete the libjbigi.so and libjcpuid.so
files if the zip archive contains a lib/jbigi.jar file, so that the new files
will be extracted from jbigi.jar.

As of release 0.8.12, if the zip archive contains a file deletelist.txt, the
router will delete the files listed there. The format is:

* One file name per line

* All file names are relative to the installation directory; no absolute file
  names allowed, no files starting with ".."

* Comments start with '#'

The router will then delete the deletelist.txt file.

.. _su3:

SU3 File Specification
----------------------

This specification is used for router updates as of release 0.9.9, reseed data
as of release 0.9.14, plugins as of release 0.9.15, and the news file as of
release 0.9.17.

Issues with the previous .sud/.su2 format
`````````````````````````````````````````
* No magic number or flags

* No way to specify compression, pack200 or not, or signing algo

* Version is not covered by signature, so it is enforced by requiring it to be
  in the zip file comment (for router files) or in the plugin.config file (for
  plugins)

* Signer not specified so verifier must try all known keys

* Signature-before-data format requires two passes to generate file

Goals
`````
* Fix above problems

* Migrate to more secure signature algorithm

* Keep version info in same format and offset for compatibility with existing
  version checkers

* One-pass signature verification and file extraction

Specification
`````````````

======  ========================================================================
Bytes   Contents
======  ========================================================================
 0-5    Magic number "I2Psu3"
  6     unused = 0
  7     su3 file format version = 0

 8-9    Signature type

        * 0x0000 = DSA-SHA1
        * 0x0001 = ECDSA-SHA256-P256
        * 0x0002 = ECDSA-SHA384-P384
        * 0x0003 = ECDSA-SHA512-P521
        * 0x0004 = RSA-SHA256-2048
        * 0x0005 = RSA-SHA384-3072
        * 0x0006 = RSA-SHA512-4096

10-11   Signature length, e.g. 40 (0x0028) for DSA-SHA1. Must match that
        specified for the [Signature]_ type.
 12     unused = 0

 13     Version length (in bytes not chars, including padding)

        must be at least 16 (0x10) for compatibility

 14     unused = 0
 15     Signer ID length (in bytes not chars)
16-23   Content length (not including header or sig)
 24     unused = 0

 25     File type

        * 0x00 = zip file
        * 0x01 = xml file (as of 0.9.15)
        * 0x02 = html file (as of 0.9.17)
        * 0x03 = xml.gz file (as of 0.9.17)

 26     unused = 0

 27     Content type

        * 0x00 = unknown
        * 0x01 = router update
        * 0x02 = plugin or plugin update
        * 0x03 = reseed data
        * 0x04 = news feed (as of 0.9.15)

28-39   unused = 0

40-55+  Version, UTF-8 padded with trailing 0x00, 16 bytes minimum, length
        specified at byte 13. Do not append 0x00 bytes if the length is 16 or
        more.

 xx+    ID of signer, (e.g. "zzz@mail.i2p") UTF-8, not padded, length specified
        at byte 15

 xx+    Content:

        * Length specified in header at bytes 16-23
        * Format specified in header at byte 25
        * Content specified in header at byte 27

 xx+    Signature: Length is specified in header at bytes 10-11, covers
        everything starting at byte 0
======  ========================================================================

All unused fields must be set to 0 for compatibility with future versions.

Signature Details
`````````````````
The signature covers the entire header starting at byte 0, through the end of
the content.  We use raw signatures. Take the hash of the data (using the hash
type implied by the signature type at bytes 8-9) and pass that to a "raw" sign
or verify function (e.g. "NONEwithRSA" in Java).

While signature verification and content extraction may be implemented in one
pass, an implementation must read and buffer the first 10 bytes to determine
the hash type before starting to verify.

Signature lengths for the various signature types are given in the [Signature]_
specification.  Pad the signature with leading zeros if necessary.  See the
cryptography details page [CRYPTO-SIG]_ for parameters of the various signature
types.

Notes
`````
The content type specifies the trust domain.  For each content type, clients
maintain a set of X.509 public key certificates for parties trusted to sign
that content.  Only certificates for the specified content type may be used.
The certificate is looked up by the ID of the signer.  Clients must verify that
the content type is that expected for the application.

All values are in network byte order (big endian).

SU3 Router Update File Specification
------------------------------------

SU3 Details
```````````
* SU3 Content Type: 1 (ROUTER UPDATE)

* SU3 File Type: 0 (ZIP)

* SU3 Version: The router version

* Jar and war files in the zip are compressed with pack200 as documented above
  for "su2" files. If the client does not support pack200, it must download the
  update in a "sud" format.

Notes
`````
* For releases, the SU3 version is the "base" router version, e.g. "0.9.20".

* For development builds, which are supported as of release 0.9.20, the SU3
  version is the "full" router version, e.g. "0.9.20-5" or "0.9.20-5-rc". See
  RouterVersion.java [I2P-SRC]_.

SU3 Reseed File Specification
-----------------------------

As of 0.9.14, reseed data is delivered in an "su3" file format.

Goals
`````
* Signed files with strong signatures and trusted certificates to prevent
  man-in-the-middle attacks that could boot victims into a separate, untrusted
  network.

* Use su3 file format already used for updates, reseeding, and plugins

* Single compressed file to speed up reseeding, which was slow to fetch 200 files

Specification
`````````````
1. The file must be named "i2pseeds.su3".

2. The file must be in the same directory as the router infos on the web server.

3. A router will first try to fetch (index URL)/i2pseeds.su3; if that fails it
   will fetch the index URL and then fetch the individual router info files
   found in the links.

SU3 Details
```````````
* SU3 Content Type: 3 (RESEED)

* SU3 File Type: 0 (ZIP)

* SU3 Version: Seconds since the epoch, in ASCII (date +%s)

* Router info files in the zip file must be at the "top level". No directories
  are in the zip file.

* Router info files must be named "routerInfo-(44 character base 64 router
  hash).dat", as in the old reseed mechanism. The I2P base 64 alphabet must be
  used.

SU3 Plugin File Specification
-----------------------------

As of 0.9.15, plugins may be packaged in an "su3" file format.

SU3 Details
```````````
* SU3 Content Type: 2 (PLUGIN)

* SU3 File Type: 0 (ZIP)

  * See the plugin specification [PLUGIN]_ for details.

* SU3 Version: The plugin version, must match that in plugin.config.

* Jar and war files in the zip are compressed with pack200 as documented above
  for "su2" files.

SU3 News File Specification
---------------------------

As of 0.9.17, the news is delivered in an "su3" file format.

Goals
`````
* Signed news with strong signatures and trusted certificates

* Use su3 file format already used for updates, reseeding, and plugins

* Standard XML format for use with standard parsers

* Standard Atom format for use with standard feed readers and generators

* Sanitization and verification of HTML before displaying on console

* Suitable for easy implementation on Android and other platforms without an
  HTML console

SU3 Details
```````````
* SU3 Content Type: 4 (NEWS)

* SU3 File Type: 1 (XML) or 3 (XML.GZ)

* SU3 Version: Seconds since the epoch, in ASCII (date +%s)

* File Format: XML or gzipped XML, containing an [RFC-4287]_ (Atom) XML Feed.
  Charset must be UTF-8.

Specification
`````````````
**Atom <feed> Details:**

The following <feed> elements are used:

    <entry>
        A news item. See below.

    <i2p:release>
        I2P update metadata. See below.

    <i2p:revocations>
        Certificate revocations. See below.

    <updated>
        Required

        Timestamp for the feed (conforming to [RFC-4287]_ (Atom) section 3.3 and
        [RFC-3339]_.

**Atom <entry> Details:**

Each Atom <entry> in the news feed may be parsed and displayed in the router console.
The following elements are used:

    <author>
        Optional

        Containing:

        <name>
            The name of the entry author

    <content>
        Required

        Content, must be type="xhtml".

        The XHTML will be sanitized with a whitelist of allowed elements and a
        blacklist of disallowed attributes. Clients may ignore an element, or
        the enclosing entry, or the entire feed when a non-whitelisted element
        is encountered.

    <link>
        Optional

        Link for further information

    <summary>
        Optional

        Short summary, suitable for a tooltip

    <title>
        Required

        Title of the news entry

    <updated>
        Required

        Timestamp for this entry (conforming to [RFC-4287]_ (Atom) section 3.3
        and [RFC-3339]_).

**Atom <i2p:release> Details:**

There must be at least one <i2p:release> entity in the feed. Each contains the
following attributes and entities:

    date (attribute)
        Required

        Timestamp for this entry (conforming to [RFC-4287]_ (Atom) section 3.3
        and [RFC-3339]_.

        The date also may be in truncated format yyyy-mm-dd (without the 'T');
        this is the "full-date" format in [RFC-3339]_. In this format the time
        is assumed to be 00:00:00 UTC for any processing.

    minJavaVersion (attribute)
        If present, the minimum version of Java required to run the current
        version.

    minVersion (attribute)
        If present, the minimum version of the router required to update to the
        current version. If a router is older than this, the user must
        (manually?) update to an intermediate version first.

    <i2p:version>
        Required

        The latest current router version available.

    <i2p:update>
        An update file (one or more). It must contain at least one child.

        type (attribute)
            "sud", "su2", or "su3".

            Must be unique across all <i2p:update> elements.

        <i2p:clearnet>
            Out-of-network direct download links (zero or more)

            href (attribute)
                A standard clearnet http link

        <i2p:clearnetssl>
            Out-of-network direct download links (zero or more)

            href (attribute)
                A standard clearnet https link

        <i2p:torrent>
            In-network magnet link

            href (attribute)
                A magnet link

        <i2p:url>
            In-network direct download links (zero or more)

            href (attribute)
                An in-network http .i2p link

**Atom <i2p:revocations> Details:**

This entity is optional and there is at most one <i2p:revocations> entity in the
feed. This feature is scheduled for implementation in release 0.9.26. The
specification below is preliminary and subject to change.

The <i2p:revocations> entity contains one or more <i2p:crl> entities. The
<i2p:crl> entity contains the following attributes:

    date (attribute)
        Required

        Timestamp for this entry (conforming to [RFC-4287]_ (Atom) section 3.3
        and [RFC-3339]_.

        The date also may be in truncated format yyyy-mm-dd (without the 'T');
        this is the "full-date" format in [RFC-3339]_. In this format the time
        is assumed to be 00:00:00 UTC for any processing.

    id (attribute)
        A unique id for the creator of this CRL.

    content
        A standard base 64 encoded Certificate Revocation List (CRL) with
        newlines, starting with the line '<tt>-----BEGIN X509 CRL-----</tt>' and
        ending with the line '<tt>-----END X509 CRL-----</tt>'. See [RFC-5280]_
        for more information on CRLs.


Future Work
===========

* The router update mechanism is part of the web router console. There is
  currently no provision for updates of an embedded router lacking the router
  console.


References
==========

.. [CRYPTO-SIG]
    {{ site_url('docs/how/cryptography', True) }}#sig

.. [I2P-SRC]
    https://github.com/i2p/i2p.i2p

.. [PLUGIN]
    {{ spec_url('plugin') }}

.. [RFC-3339]
    https://tools.ietf.org/html/rfc3339

.. [RFC-4287]
    https://tools.ietf.org/html/rfc4287

.. [RFC-5280]
    https://tools.ietf.org/html/rfc5280

.. [Signature]
    {{ ctags_url('Signature') }}

.. [SigningPublicKey]
    {{ ctags_url('SigningPublicKey') }}
