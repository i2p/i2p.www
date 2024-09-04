===================================================
I2P proposal #166: Identity/Host Aware Tunnel Types
===================================================
.. meta::
    :author: eyedeekay
    :created: 2024-05-27
    :thread: http://i2pforum.i2p/viewforum.php?f=13
    :lastupdated: 2024-08-27
    :status: Open
    :target: 0.9.65

.. contents::

Proposal for a Host-Aware HTTP Proxy Tunnel Type
------------------------------------------------

This is a proposal to resolve the “Shared Identity Problem” in
conventional HTTP-over-I2P usage by introducing a new HTTP proxy tunnel
type. This tunnel type has supplemental behavior which is intended to
prevent or limit the utility of tracking conducted by potential hostile
hidden service operators, against targeted user-agents(browsers) and the
I2P Client Application itself.

What is the “Shared Identity” problem?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The “Shared Identity” problem occurs when a user-agent on a
cryptographically addressed overlay network shares a cryptographic
identity with another user-agent. This occurs, for instance, when a
Firefox and GNU Wget are both configured to use the same HTTP Proxy.

In this scenario, it is possible for the server to collect and store the
cryptographic address(Destination) used to reply to the activity. It can
treat this as a “Fingerprint” which is always 100% unique, because it is
cryptographic in origin. This means that the linkability observed by the
Shared Identity problem is perfect.

But is it a problem?
^^^^^^^^^^^^^^^^^^^^

The shared identity problem is a problem when user-agents that speak the
same protocol desire unlinkability. `It was first mentioned in the
context of HTTP in this Reddit
Thread <https://old.reddit.com/r/i2p/comments/579idi/warning_i2p_is_linkablefingerprintable/>`__,
with the deleted comments accessible courtesy of
`pullpush.io <https://api.pullpush.io/reddit/search/comment/?link_id=579idi>`__.
*At the time* I was one of the most active respondents, and *at the
time* I believed the issue was small. In the past 8 years, the situation
and my opinion of it have changed, I now believe the threat posed by
malicious destination correlation grows considerably as more sites are
in a position to “profile” specific users.

This attack has a very low barrier to entry. It only requires that a
hidden service operator operate multiple services. For attacks on
contemporary visits(visiting multiple sites at the same time), this is
the only requirement. For non-contemporary linking, one of those
services must be a service which hosts “accounts” which belong to a
single user who is targeted for tracking.

Currently, any service operator who hosts user accounts will be able to
correlate them with activity across any sites they control by exploiting
the Shared Identity problem. Mastodon, Gitlab, or even simple forums
could be attackers in disguise as long as they operate more than one
service and have an interest in creating a profile for a user. This
surveillance could be conducted for stalking, financial gain, or
intelligence-related reasons. Right now there are dozens of major
operators, who could carry out this attack and gain meaningful data from
it. We mostly trust them not to for now, but players who don’t care
about our opinions could easily emerge.

This is directly related to a fairly basic form of profile-building on
the clear web where organizations can correlate interactions on their
site with interations on networks they control. On I2P, because the
cryptographic destination is unique, this technique can sometimes be
even more reliable, albeit without the additional power of geolocation.

The Shared Identity is not useful against a user who is using I2P solely
to obfuscate geolocation. It also cannot be used to break I2P’s routing.
It is only a problem of contextual identity management.

-  It is impossible to use the Shared Identity problem to geolocate an
   I2P user.
-  It is impossible to use the Shared Identity problem to link I2P
   sessions if they are not contemporary.

However, it is possible to use it to degrade the anonymity of an I2P
user in circumstances which are probably very common. One reason they
are common is becase we encourage the use of Firefox, a web browser
which supports “Tabbed” operation.

-  It is *always* possible to produce a fingerprint from the Shared
   Identity problem in *any* web browser which supports requesting
   third-party resources.
-  Disabling Javascript accomplishes **nothing** against the Shared
   Identity problem.
-  If a link can be established between non-contemporary sessions such
   as by “traditional” browser fingerprinting, then the Shared Identity
   can be applied transitively, potentially enabling a non-contemporary
   linking strategy.
-  If a link can be established between a clearnet activity and an I2P
   identity, for instance, if the target is logged into a site with both
   an I2P and a clearnet presence on both sides, the Shared Identity can
   be applied transitively, potentially enabling complete
   de-anonymization.

How you view the severity of the Shared Identity problem as it applies
to the I2P HTTP proxy depends on where you(or more to the point, a
“user” with potentially uninformed expectationss) think the “contextual
identity” for the application lies. There are several possibilities:

1. HTTP is both the Application and the Contextual Identity - This is
   how it works now. All HTTP Applications share an identity.
2. The Process is the Application and the Contextual Identity - This is
   how it works when an application uses an API like SAMv3 or I2CP,
   where an application creates it’s identity and controls it’s
   lifetime.
3. HTTP is the Application, but the Host is the Contextual Identity
   -This is the object of this proposal, which treats each Host as a
   potential “Web Application” and treats the threat surface as such.

Is it Solvable?
^^^^^^^^^^^^^^^

It is probably not possible to make a proxy which intelligently responds
to every possible case in which it’s operation could weaken the
anonymity of an application. However, it is possible to build a proxy
which intelligently responds to a specific application which behaves in
a predictable way. For instance, in modern Web Browsers, it is expected
that users will have multiple tabs open, where they will be interacting
with multiple web sites, which will be distinguished by hostname.

This allows us to improve upon the behavior of the HTTP Proxy for this
type of HTTP user-agent by making the behavior of the proxy match the
behavior of the user-agent by giving each host it’s own Destination when
used with the HTTP Proxy. This change makes it impossible to use the
Shared Identity problem to derive a fingerprint which can be used to
correlate client activity with 2 hosts, because the 2 hosts will simply
no longer share a return identity.

Description:
^^^^^^^^^^^^

A new HTTP Proxy will be created and added to Hidden Services
Manager(I2PTunnel). The new HTTP Proxy will operate as a “multiplexer”
of I2PSocketManagers. The multiplexer itself has no destination. Each
individual I2PSocketManager which becomes part of the multiplex has it’s own
local destination, and it’s own tunnel pool. I2PSocketManagerss are created
on-demand by the multiplexer, where the “demand” is the first visit to the
new host. It is possible to optimize the creation of the I2PSocketManagers
before inserting them into the multiplexer by creating one or more in advance
and storing them outside the multiplexer. This may improve performance.

An additional I2PSocketManager, with it’s own destination, is set up as the
carrier of an “Outproxy” for any site which does *not* have an I2P
Destination, for example any Clearnet site. This effectively makes all
Outproxy usage a single Contextual Identity, with the caveat that
configuring multiple Outproxies for the tunnel will cause the normal
“Sticky” outproxy rotation, where each outproxy only gets requests for a
single site. This is *almost* the equivalent behavior as isolating
HTTP-over-I2P proxies by destination, on the clear internet.

Resource Considerations:
''''''''''''''''''''''''

The new HTTP proxy requires additional resources compared to the
existing HTTP proxy. It will:

-  Potentially build more tunnels and I2PSocketManagers
-  Build tunnels more often

Each of these requires:

-  Local computing resources
-  Network resources from peers

Settings:
'''''''''

In order to minimize the impact of the increased resource usage, the
proxy should be configured to use as little as possible. Proxies which
are part of the multiplexer(not the parent proxy) should be configured
to:

-  Multiplexed I2PSocketManagers build 1 tunnel in, 1 tunnel out in their
   tunnel pools
-  Multiplexed I2PSocketManagers take 3 hops by default.
-  Close sockets after 10 minutes of inactivity
-  I2PSocketManagers started by the Multiplexer share the lifespan of the
   Multiplexer. Multiplexed tunnels are not “Destructed” until the
   parent Multiplexer is.

Diagrams:
^^^^^^^^^

The diagram below represents the current operation of the HTTP proxy,
which corresponds to “Possibility 1.” under the “Is it a problem”
section. As you can see, the HTTP proxy interacts with I2P sites
directly using only one destination. In this scenario, HTTP is both the
application and the contextual identity.

.. code:: md

   **Current Situation: HTTP is the Application, HTTP is the Contextual Identity**
                                                          __-> Outproxy <-> i2pgit.org
                                                         /
   Browser <-> HTTP Proxy(one Destination)<->I2PSocketManager <---> idk.i2p
                                                         \__-> translate.idk.i2p
                                                          \__-> git.idk.i2p

The diagram below represents the operation of a host-aware HTTP proxy,
which corresponds to “Possibility 3.” under the “Is it a problem”
section. In this secenario, HTTP is the application, but the Host
defines the contextual identity, wherein each I2P site interacts with a
different HTTP proxy with a unique destination per-host. This prevents
operators of multiple sites from being able to distinguish when the same
person is visiting multiple sites which they operate.

.. code:: md

   **After the Change: HTTP is the Application, Host is the Contextual Identity**
                                                        __-> I2PSocketManager(Destination A - Outproxies Only) <--> i2pgit.org
                                                       /
   Browser <-> HTTP Proxy Multiplexer(No Destination) <---> I2PSocketManager(Destination B) <--> idk.i2p
                                                       \__-> I2PSocketManager(Destination C) <--> translate.idk.i2p
                                                        \__-> I2PSocketManager(Destination C) <--> git.idk.i2p

Status:
^^^^^^^

A working Java implementation of the host-aware proxy which conforms to
an older version of this proposal is available at idk's fork under the
branch: i2p.i2p.2.6.0-browser-proxy-post-keepalive Link in citations. It
is under heavy revision, in order to break down the changes into smaller
sections.

Implementations with varying capabilities have been written in Go using
the SAMv3 library, they may be useful for embedding in other Go
applications or for go-i2p but are unsuitable for Java I2P.
Additionally, they lack good support for working interactively with
encrypted leaseSets.

Addendum: ``i2psocks``
                      

A simple application-oriented approach to isolating other types of
clients is possible without implementing a new tunnel type or changing
the existing I2P code by combining I2PTunnel existing tools which are
already widely available and tested in the privacy community. However,
this approach makes a difficult assumption which is not true for HTTP
and also not true for many other kinds of potentsial I2P clients.

Roughly, the following script will produce an application-aware SOCKS5
proxy and socksify the underlying command:

.. code:: sh

   #! /bin/sh
   command_to_proxy="$@"
   java -jar ~/i2p/lib/i2ptunnel.jar -wait -e 'sockstunnel 7695'
   torsocks --port 7695 $command_to_proxy

Addendum: ``example implementation of the attack``
                                                  

`An example implementation of the Shared Identity attack on HTTP
User-Agents <https://github.com/eyedeekay/colluding_sites_attack/>`__
has existed for several years. An additional example is available in the
``simple-colluder`` subdirectory of `idk’s prop166
repository <https://git.idk.i2p/idk/i2p.host-aware-proxy>`__ These
examples are deliberately designed to demonstrate that the attack works
and would require modification(albeit minor) to be turned into a real
attack.

Citations:
''''''''''

https://old.reddit.com/r/i2p/comments/579idi/warning_i2p_is_linkablefingerprintable/
https://api.pullpush.io/reddit/search/comment/?link_id=579idi
https://github.com/eyedeekay/colluding_sites_attack/
https://en.wikipedia.org/wiki/Shadow_profile
https://github.com/eyedeekay/si-i2p-plugin/
https://github.com/eyedeekay/eeproxy/
https://geti2p.net/en/docs/api/socks
https://i2pgit.org/idk/i2p.www/-/compare/master...166-identity-aware-proxies?from_project_id=17
https://i2pgit.org/idk/i2p.i2p/-/tree/i2p.i2p.2.6.0-browser-proxy-post-keepalive?ref_type=heads
