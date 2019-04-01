==================================
Access Filter Format Specification
==================================
.. meta::
    :lastupdated: April 2019
    :accuratefor: 0.9.40

.. contents::

Overview
========

The definition of a filter is a list of Strings.  Blank lines and lines beginning with # are ignored.  

Each line can represent one of these items:

* definition of a default threshold to apply to any remote destinations not listed in this file or any of the referenced files
* definition of a threshold to apply to a specific remote destination
* definition of a threshold to apply to remote destinations listed in a file
* definition of a threshold that if breached will cause the offending remote destination to be recorded in a specified file


The order of the definitions matters.  The first threshold for a given destination
(whether explicit or listed in a file) overrides any future thresholds for the
same destination, whether explicit or listed in a file.


Thresholds
==========


A threshold is defined by the number of connection attempts a remote destination is
permitted to perform over a specified number of minutes before a "breach" occurs.
For example the following threshold definition "15/5" means that the same remote
destination is allowed to make 14 connection attempts over a 5 minute period,  If
it makes one more attempt within the same period, the threshold will be breached.


The threshold format can be one of the following:


* Numeric definition of number of connections over number minutes - "15/5", "30/60", and so on.  Note that if the number of connections is 1 (as for example in "1/1") the first connection attempt will result in a breach.
* The word "allow".  This threshold is never breached, i.e. infinite number of connection attempts is permitted.
* The word "deny".  This threshold is always breached, i.e. no connection attempts will be allowed.


Default Threshold
-----------------

The default threshold applies to any remote destinations that are not explicitly
listed in the definition or in any of the referenced files.  To set a default 
threshold use the keyword "default".  The following are examples of default thresholds::
 

  15/5 default
  allow default
  deny default
  

Explicit Thresholds
-------------------

Explicit thresholds are applied to a remote destination listed in the definition itself.
Examples::
 

 15/5 explicit asdfasdfasdf.b32.i2p
 allow explicit fdsafdsafdsa.b32.i2p
 deny explicit qwerqwerqwer.b32.i2p


Bulk Thresholds
---------------

For convenience it is possible to maintain a list of destinations in a file and define
a threshold for all of them in bulk.  Examples::


 15/5 file /path/throttled_destinations.txt
 deny file /path/forbidden_destinations.txt
 allow file /path/unlimited_destinations.txt


Recorders
=========

Recorders keep track of connection attempts made by a remote destination, and if that
breaches a certain threshold, that destination gets recorded in a given file.  Examples::


 30/5 recorder /path/aggressive.txt
 60/5 recorder /path/very_aggressive.txt


It is possible to use a recorder to record aggressive destinations to a given file,
and then use that same file to throttle them.  For example, the following snippet will
define a filter that initially allows all connection attempts, but if any single
destination exceeds 30 attempts per 5 minutes it gets throttled down to 15 attempts per 
5 minutes::


 # by default there are no limits
 allow default
 # but record overly aggressive destinations
 30/5 recorder /path/throttled.txt
 # and any that end up in that file will get throttled in the future
 15/5 file /path/throttled.txt


It is possible to use a recorder in one tunnel that writes to a file that throttles 
another tunnel.  It is possible to reuse the same file with destinations in multiple
tunnels.  And of course, it is possible to edit these files by hand.

Here is an example filter definition that applies some throttling by default, no throttling
for destinations in the file "friends.txt", forbids any connections from destinations
in the file "enemies.txt" and records any aggressive behavior in a file called
"suspicious.txt"::


 15/5 default
 allow file /path/friends.txt
 deny file /path/enemies.txt
 60/5 recorder /path/suspicious.txt



