=============================
Authenticated Address Helpers
=============================
.. meta::
    :author: zzz
    :created: 2017-02-25
    :thread: http://zzz.i2p/topics/2241
    :lastupdated: 2017-02-25
    :status: Open

.. contents::


Overview
========

This proposal adds an authentication mechanism to address helper URLs.


Motivation
==========

Address helper URLs are inherently insecure. Anybody may put an address helper 
parameter in a link, even for an image, and may put any destination in the 
"i2paddresshelper" URL parameter. Depending on the user's HTTP proxy 
implementation, this hostname/destination mapping, if not currently in the 
addressbook, may be accepted, either with or without an interstitial for the 
user to accept.


Design
======

Trusted jump servers and addressbook registration services would provide new 
address helper links that add authentication parameters. The two new parameters 
would be a base 64 signature and a signed-by string.

These services would generate and provide a public key certificate. This 
certificate would be available for download and inclusion in http proxy 
software. Users and software developers would decide whether to trust such 
services by including the certificate.

On encountering an address helper link, the http proxy would check for the 
additional authentication parameters, and attempt to verify the signature. On 
successful verification, the proxy wold proceed as before, either by accepting 
the new entry or showing an interstitial to the user. On verification failure, 
the proxy could reject the address helper or show additional information to the 
user.

If no authentication parameters are present, the http proxy may accept, 
decline, or present information to the user.

Jump services would be trusted as usual, but with the additional authentication 
step. Address helper links on other sites would need to be modified.



Security Implications
=====================

This proposal adds security by adding authentication from trusted registration 
/ jump services. 



Specification
=============

TBD.

The two new parameters could be i2paddresshelpersig and i2paddresshelpersigner?

Accepted signature types TBD. Probably not RSA as the base 64 signatures would 
be very long.

Signature algorithm: TBD. Maybe just hostname=b64dest (same as proposal 112 for 
registration authentication)

Possible third new parameter: The registration authentication string (the part 
after the "#!") to be used for additional verification by the HTTP proxy. Any 
"#" in the string would have to be escaped as "&#35;" or "&num;", or be 
replaced by some other specified (TBD) URL-safe character.


Migration
=========

Old HTTP proxies that don't support the new authentication parameters would 
ignore them, and pass them along to the web server, which should be harmless.

New HTTP proxies that optionally support authentication parameters would work 
fine with old address helper links that don't contain them.

New HTTP proxies that require authentication parameters would not allow old 
address helper links that don't contain them.

A proxy implementation's policies may evolve over the course of a migration 
period.

Issues
======

A site owner could not generate an address helper for his own site, as it needs 
the signature from a trusted jump server. He would have to register it on the 
trusted server and get the authenticated helper  URL from that server. Is there 
a way for a site to generate a self-authenticated address helper URL?

Alternatively, the proxy could check the Referer for  an address helper 
request. If the Referer were present, contained a b32, and the b32 matched the 
helper's destination, then it could be allowed as a self-referral. Otherwise it 
could be assumed to be a 3rd-party request, and rejected.

