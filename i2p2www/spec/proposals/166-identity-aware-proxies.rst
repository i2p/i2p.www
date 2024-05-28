===================================================
I2P proposal #166: Identity/Host Aware Tunnel Types
===================================================
.. meta::
    :author: eyedeekay
    :created: 2024-05-27
    :thread: http://i2pforum.i2p/viewforum.php?f=13
    :lastupdated: 2024-05-27
    :status: Open
    :target: 0.9.62

.. contents::

Proposal for a Host-Aware HTTP Proxy Tunnel Type
================================================

This is a proposal to resolve the “Shared Identity Problem” in
conventional HTTP-over-I2P usage by introducing a new HTTP proxy tunnel
type. This tunnel type has supplemental behavior which is intended to
prevent or limit the utility of tracking conducted by server operators,
against user-agents(browsers) and the I2P Client Application itself.

What is the “Shared Identity” problem?
--------------------------------------

The “Shared Identity” problem occurs when a user-agent on a
cryptographically addressed overlay network shares a cryptographic
identity with another user-agent. This occurs, for instance, when a
Firefox and GNU Wget are both configured to use the same HTTP Proxy. In
this scenario, it is possible for the server to collect and store the
cryptographic address(Destination) used to reply to the activity. It can
treat this as a “Fingerprint” which is always 100% unique, because it is
cryptographic in origin. This means that the linkability observed by the
Shared Identity problem is perfect.

But is it a problem?
~~~~~~~~~~~~~~~~~~~~

The shared identity problem is a problem when user-agents that speak the
same protocol desire unlinkability. `It was first mentioned in the
context of HTTP in this Reddit
Thread <https://old.reddit.com/r/i2p/comments/579idi/warning_i2p_is_linkablefingerprintable/>`__,
with the deleted comments accessible courtesy of
`pullpush.io <https://api.pullpush.io/reddit/search/comment/?link_id=579idi>`__.
*At the time* I was one of the most active respondents, and *at the
time* I believed the issue was small. In the past 8 years, the situation
and my opinion of it have changed, with the emergence of Mastodon and
Matrix servers inside of I2P, the threat posed by malicious destination
correlation grows considerably as these sites are in a position to
“profile” specific users. `An example implementation of the Shared
Identity attack on HTTP
User-Agents <https://github.com/eyedeekay/colluding_sites_attack/>`__

The Shared Identity is not useful against a user who is using I2P to
obfuscate geolocation. It also cannot be used to break I2P’s routing.

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
3. HTTP is the Application, but the Contextual Identity is controlled
   with the “Authentication Hack” - Interesting possibility detailed at
   the end of this proposal, not the object of this proposal
4. HTTP is the Application, but the Host is the Contextual Identity -
   This is the object of this proposal, which treats each Host as a
   potential “Web Application” and treats the threat surface as such.

It also depends on who you think your attackers are and what you would
like to prevent. Someone in a position to carry out this attack would be
a person in a position to have multiple sites “collude” in order to
collect the destinations of I2P Clients, in order to correlate activity
on one site with activity on another. This is a fairly basic form of
profile-building on the clear web where organizations can correlate
interactions on their site with interations on networks they control. On
I2P, because the cryptographic destination is unique, this technique can
sometimes be even more reliable, albeit without the additional power of
geolocation. Any service which hosts user accounts would be able to
correlate them with activity across any sites they control using the
Shared Identity problem. Mastodon, Gitlab, or even simple Forums could
be attackers in disguise as long as they operate more than one service
and have an interest in creating a profile for a user. This surveillance
could be conducted for stalking, financial gain, or intelligence-related
reasons.

Is it Solvable?
~~~~~~~~~~~~~~~

It is probably not possible to make a proxy which intelligently responds
to every possible case in which it’s operation could weaken the
anonymity of an application. However, it is possible to build a proxy
which intelligently responds to a specific application which behaves
in a predictable way. For instance, in modern Web Browsers, it is
expected that users will have multiple tabs open, where they will be
interacting with multiple web sites, which will be distinguished by
hostname. This allows us to improve upon the behavior of the HTTP Proxy
for this type of HTTP user-agent by making the behavior of the proxy
match the behavior of the user-agent by giving each host it’s own
Destination when used with the HTTP Proxy. This change makes it
impossible to use the Shared Identity problem to derive a fingerprint
which can be used to correlate client activity with 2 hosts, because the
2 hosts will simply no longer share a return identity.

Description:
~~~~~~~~~~~~

A new HTTP Proxy will be created and added to Hidden Services
Manager(I2PTunnel). The new HTTP Proxy will operate as a “multiplexer”
of HTTP Proxies. The multiplexer itself has no destination. Each
individual HTTP Proxy which becomes part of the multiplex has it’s own
local destination, random local port, and it’s own tunnel pool. HTTP
proxies are created on-demand by the multiplexer, where the “demand” is
the first visit to the new host. It is possible to optimize the creation
of the HTTP proxies before inserting them into the multiplexer by
creating one or more in advance and storing them outside the multiplexer

An additional HTTP proxy, with it’s own destination, is set up as the
carrier of an “Outproxy” for any site which does *not* have an I2P
Destination, for example any Clearnet site.

Resource Considerations:
^^^^^^^^^^^^^^^^^^^^^^^^

The new HTTP proxy requires additional resources compared to the
existing HTTP proxy. It will:

-  Potentially build more tunnels
-  Build tunnels more often
-  Occupy more ports

Each of these requires:

-  Local computing resources
-  Network resources from peers

Settings:
^^^^^^^^^

In order to minimize the impact of the increased resource usage, the
proxy should be configured to use as little as possible. Proxies which
are part of the multiplexer(not the parent proxy) should be configured
to:

-  Multiplexed I2PTunnels build 1 tunnel in, 1 tunnel out in their
   tunnel pools
-  Multiplexed I2PTunnels take 3 hops by default.
-  Close tunnels after 10 minutes of inactivity
-  I2PTunnels started by the Multiplexer share the lifespan of the
   Multiplexer. Multiplexed tunnels are not “Destructed” until the
   parent Multiplexer is.

Diagrams:
~~~~~~~~~

The diagram below represents the current operation of the HTTP proxy,
which corresponds to “Possibility 1.” under the “Is it a problem”
section. As you can see, the HTTP proxy interacts with I2P sites
directly using only one destination. In this scenario, HTTP is both the
application and the contextual identity.

.. code:: md

   **Current Situation: HTTP is the Application, HTTP is the Contextual Identity**
                                             __-> i2pgit.org
                                            /
   Browser <-> HTTP Proxy(one Destination) <---> idk.i2p
                                            \__-> translate.idk.i2p
                                             \__-> git.idk.i2p

The diagram below represents the operation of a host-aware HTTP proxy,
which corresponds to “Possibility 4.” under the “Is it a problem”
section. In this secenario, HTTP is the application, but the Host
defines the contextual identity, wherein each I2P site interacts with a
different HTTP proxy with a unique destination per-host. This prevents
operators of multiple sites from being able to distinguish when the same
person is visiting multiple sites which they operate.

.. code:: md

   **After the Change: HTTP is the Application, Host is the Contextual Identity**
                                                        __-> HTTP Proxy(Destination A) <--> i2pgit.org
                                                       /
   Browser <-> HTTP Proxy Multiplexer(No Destination) <---> HTTP Proxy(Destination B) <--> idk.i2p
                                                       \__-> HTTP Proxy(Destination C) <--> translate.idk.i2p
                                                        \__-> HTTP Proxy(Destination C) <--> git.idk.i2p

Status:
~~~~~~~

A working Java implementation of the host-aware proxy which conforms to this proposal is available at idk's fork under the branch: i2p.i2p.2.6.0-browser-proxy-post-keepalive
Link in citations.
Implementations with varying capabilities have been written in Go using the SAM library, they may be useful for embedding in other Go Applications of for go-i2p but are unsuitable for Java I2P.
Additionally, they lack good support for working interactively with encrypted leaseSets.

Addendum: SOCKS
'''''''''''''''

A similar shared identity problem exists in the SOCKS proxy as well.
However, there, it is harder to solve in part due to the reasons
described on the “SOCKS Tips” page on the I2P site. In particular, it
requires much more effort to determine internal destinations and
outgoing hostnames. However, there is a way which works well, and which
has the additional value of being possible to implement as an HTTP proxy
as well. This could allow an HTTP Proxy and a SOCKS proxy to work in
unison, providing clients with the same identity on a per-host basis.
This in turn could allow for efficient, unlinkable WebRTC inside of I2P.

The drawback, however, is that it requires some basic cooperation on the
part of the client. In lieu of isolating by-host, the client should send
an “Isolation String” as if it were a part of the username and password
sent to the SOCKS proxy server. For instance, if the SOCKS proxy
required username and password, then the isolation string would be
appended after the password as a third component. The username and
password would be authenticated first, and upon success, the isolation
string would be used to add a SOCKS proxy to the multiplex. If the SOCKS
proxy server required no username and password, *any* string would be a
valid “Isolation String.”

This could allow for better and more sophisticated isolation in some
circumstances, because the isolation string need not consist of only a
hostname or destination. A wrapper could be created for ``torsocks``,
``i2psocks`` which would pass this isolation string to the SOCKS proxy
it would use. It would be aware of it’s own arguments, giving it the
ability to generate the isolation string on the fly based on the input.
``i2psocks curl http://idk.i2p"`` could produce an authentication string
like ``curlhttpidk`` giving it a destination which exists only for the
time it takes to run the application. ``curl`` is merely an example,
this approach would work for applications with longer lifetimes too.

.. code:: md

   **Hypothetical Future: SOCKS is the Application, Contextual Identity is decided by the app or perhaps a wrapper**
                                                                              __-> SOCKS Proxy(Isolation String firefoxi2pgitorg) <--> i2pgit.org
                                                                             /
   Browser <-> SOCKS Proxy Multiplexer(No Destination, No Isolation String) <---> SOCKS Proxy(Isolation String curlidk) <--> idk.i2p
                                                                             \__-> SOCKS Proxy(Isolation String firefoxtranslateidk) <--> translate.idk.i2p
                                                                              \__-> SOCKS Proxy(Isolation String firefoxgitidk) <--> git.idk.i2p

Citations:
^^^^^^^^^^

https://old.reddit.com/r/i2p/comments/579idi/warning_i2p_is_linkablefingerprintable/
https://api.pullpush.io/reddit/search/comment/?link_id=579idi
https://github.com/eyedeekay/colluding_sites_attack/
https://en.wikipedia.org/wiki/Shadow_profile
https://github.com/eyedeekay/si-i2p-plugin/
https://github.com/eyedeekay/eeproxy/
https://geti2p.net/en/docs/api/socks
https://i2pgit.org/idk/i2p.www/-/compare/master...166-identity-aware-proxies?from_project_id=17
https://i2pgit.org/idk/i2p.i2p/-/tree/i2p.i2p.2.6.0-browser-proxy-post-keepalive?ref_type=heads