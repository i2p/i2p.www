===========================================================
{% trans -%}20 Years of Privacy: A Brief History of I2P{%- endtrans %}
===========================================================

.. meta::
    :author: sadie
    :date: 2021-08-28
    :category: general
    :excerpt: {% trans %}A history of I2P As We Know It{% endtrans %}

{% trans -%}
Invisibility is the best defense: building an internet within an internet
{%- endtrans %}
-------------------------------------------------------------------------

    {% trans -%}I believe most people want this technology so they can express
    themselves freely. It’s a comfortable feeling when you know you can
    do that. At the same time we can conquer some of the problems seen
    within the Internet by changing the way security and privacy is
    viewed, as well as the extent to what it is valued.{%- endtrans %}


{% trans -%}In October 2001, 0x90 ( Lance James) had a dream. It started as a
“desire for instant communication with other Freenet users to talk about
Freenet issues, and exchange Freenet keys while still maintaining
anonymity, privacy and security.” It was called IIP — the Invisible IRC
Project.{%- endtrans %}

.. compound::
  .. image:: /_static/images/history/invisibleirc_banner.png
    :width: 100%
  .. image:: /_static/images/history/invisibleirc.png
    :width: 100%

{% trans -%}The Invisible IRC Project was based on an ideal and framework behind The
InvisibleNet:{%- endtrans %}

{% trans -%}In an interview from 2002, 0x90 described the project:{%- endtrans %}

    {% trans -%}“InvisibleNet is a research & development driven organization whose main
    focus is the innovation of intelligent network technology. Our goal is
    to provide the highest standards in security and privacy on the widely
    used, yet notoriously insecure Internet."{%- endtrans %}

    {% trans -%}"The InvisibleNet team is comprised of a talented group of developers and
    architects entirely dedicated to providing its users with both
    convenience and the very best in secure communication."{%- endtrans %}

    {% trans -%}"Our technological ideals are reflected in the implementation of a
    framework that is solid in design, and transparent in its application."{%- endtrans %}

    {% trans -%}"Here at InvisibleNet we strive towards the greatest level of quality
    possible by keeping all areas of our research & development open and
    available to the public for peer review, feedback, suggestions and new
    ideas.”{%- endtrans %}

    {% trans -%}"The Invisible Internet Project: Defined as the “New Internet”.
    Peer 2 Peer Internet. Using your peers to protect you. It is a
    similar concept to the Invisible IRC Project, with its design as our
    test model. We plan to re-design the Internet by taking it a step
    further and having security and privacy be first priority."{%- endtrans %}

    {% trans -%}"The Invisible Internet Project or Protocol will be utilizing the
    tests and research/development concepts of the Invisible IRC Project
    to give us the scalability that we need and leverage this to take it
    to the next level."{%- endtrans %}

    {% trans -%}"This, in essence will be an impenetrable neural-network, that is
    self-driven, self-defensed, and completely seamless to already
    applied protocols, specifically client to server (or agents as I call
    them). It will be THE next transport layer, a layer on top of the
    notoriously insecure Internet, to deliver full anonymity, privacy,
    and security at the highest level possible. Decentralized and peer to
    peer Internet, by the way, means no more worrying about your ISP
    controlling your traffic. This will allow you to do seamless
    activities and change the way we look at security and even the
    Internet, utilizing public key cryptography, IP steganography, and
    message authentication. The Internet that should have been, will be
    soon."{%- endtrans %}

.. compound::
  .. image:: /_static/images/history/invisiblenet.png
     :width: 100%

| {% trans -%}All citations and quotes are from the interviews found here:{%- endtrans %}
| http://invisibleip.sourceforge.net/iip/mediaDCInterview1.php
| http://invisibleip.sourceforge.net/iip/mediaDCInterview2.php
| http://invisibleip.sourceforge.net/index.php

{% trans -%}By 2003, several other similar projects had started, the largest being
Freenet, GNUNet, and Tor. All of these projects had broad goals to
encrypt and anonymize a variety of traffic. For IIP, it became clear
that IRC alone was not a big-enough target. What was needed was an
anonymizing layer for all protocols. IIP by now was also being called
“InvisibleNet”.{%- endtrans %}

{% trans -%}In early 2003, a new anonymous developer, “jrandom” joined the project.
His explicit goal was to broaden the charter of IIP.{%- endtrans %}

{% trans -%}jrandom wished to rewrite the IIP code base in Java, a language he was
familiar with, and the same language Freenet was using. He also wished
to redesign the IIP protocols based on recent papers and the early
design decisions that Tor and Freenet were making. Some of these
concepts and naming conventions, such as “onion routing”, were modified
to become “garlic routing”. For several of the design decisions, jrandom
made different choices than Tor did, including selecting different
cryptographic primitives in a number of places. Many (but not all) of
these choices turned out quite well. For some others, such as using
unidirectional tunnels rather than Tor’s bidirectional tunnels, the
benefits and trade-offs are still not well-studied.{%- endtrans %}

{% trans -%}jrandom also set out a clear vision for the architecture of the code. It
would be a client/server model, with the server (i.e. the router)
isolated from any “client” protocols. Clients such as web browsers, web
servers, IRC clients and servers, and others, would communicate through
the router using I2CP, the I2P Client Protocol.{%- endtrans %}

{% trans -%}jrandom also had strong opinions on the direction of the project and its
philosophy. He was strongly committed to open source and free software.
He explicitly set a goal of protection from organizations with
“unlimited financial and political resources.”{%- endtrans %}

{% trans -%}By late summer 2003, jrandom had taken control of the project, and
renamed it the Invisible Internet Project or “I2P”. He published a
document outlining the philosophy of the project, and placed its
technical goals and design in the context of mixnets and anonymizing
layers. He also published the specification of two protocols (I2CP and
I2NP) and their underlying data structures, that formed the basis of the
network I2P uses today. Lance (“nop”) was last seen in a project meeting
on November 11, 2003.{%- endtrans %}

.. image:: /_static/images/history/bw1.png

https://www.bloomberg.com/news/articles/2003-09-14/the-underground-internet

.. image:: /_static/images/history/bw2.png

{% trans -%}By fall 2003, I2P, Freenet, and Tor were rapidly developing. Business
Week published an article on “The Underground Internet” which referenced
InvisibleNet and discussed “darknets” extensively. jrandom released I2P
version 0.2 on November 1, 2003, and continued rapid releases for the
next 3 years. He maintained regular weekly meetings and status notes
during this time. Several popular services and “respites” emerged during
this time. Auto updates via clearnet HTTP became available in 2004.{%- endtrans %}

{% trans -%}Through 2004 and 2005, router development continued, and several
“clients” or applications were added to the I2P package. “Mihi” wrote
the first streaming protocol implementation and the i2ptunnel interface
for configuring and starting client tunnels. “Susi” wrote the web mail
and address book applications SusiMail and SusiDNS. Many people worked
on the router console web interface. A bridge to make it easier for
non-I2P clients to communicate over I2P, called “SAM” (Simple Anonymous
Messaging) was added.{%- endtrans %}

| {% trans -%}In February 2005, zzz installed I2P for the first time.{%- endtrans %}
| {% trans -%}Anonymity projects were in the news. After surveying the field, he
  installed Freenet, and found it ambiguous, and difficult to explore.
  Not only that, it was very resource heavy and it was difficult to get
  anything to load. Tor and I2P were the other options, and he tried
  I2P.{% endtrans %}

{% trans -%}zzz had no preconceived plans to contribute to the project, and had
never written a line of Java. He had maybe used IRC once. At this time,
I2P was at version 0.5, with maybe a thousand users and three hard-coded
floodfills. Forum.i2p and postman’s tracker were up and running at the
time, and weekly meetings and status notes, and releases every couple of
week were happening.{%- endtrans %}

{% trans -%}By summer 2005, zzz had set up two websites. The first was zzz.i2p,
which over the years became a central resource for I2P development, and
still is. The second was stats.i2p, the first site to gather statistics
on I2P network performance and present graphs on both the network and
individual routers. While the individual router statistics eventually
had to be shut down due to the tremendous growth of the network, the
overall performance graphs remain. We are not sure that he ever planned
to become the release manger for almost 2 decades, but we are happy he
did. The project has not only stayed active, it has thrived and scaled
to the demands of its growth.{%- endtrans %}

.. compound::
  .. image:: /_static/images/history/statsi2p.png
     :width: 100%

{% trans -%}On July 27, 2005, jrandom released I2P version 0.6, including an
innovative new UDP transport protocol he designed called “SSU”, for
Secure Semi-reliable UDP. It contained features for IP discovery and
firewall traversal.{%- endtrans %}

{% trans -%}In September 2005, jrandom bundled “Syndie”, his new high-latency
anonymous messaging system. In October 2005, jrandom ported Snark, a
Java BitTorrent client, to become an I2P application and bundled it with
the I2P package. This completed the collection of client applications
that are still bundled with I2P today.{%- endtrans %}

{% trans -%}In late 2005 and early 2006, jrandom redesigned the way that I2P built
tunnels. This was a major effort that was done to increase the security
of the tunnel building, which is crucial to maintain anonymity and
resist attacks. He worked closely with the Freenet developers, including
“Toad”, on this design. The new build protocol required new I2NP
messages and a hard cut-over or “flag day”. These changes were released
in version 0.6.1.10 on February 16, 2006. This is significant as it is
the last flag day I2P has had. While, in practice, an 0.6.1.10 router
would not work well, if at all, in today’s network, we are, technically
speaking, backwards-compatible with this ten-year-old version today.{%- endtrans %}

{% trans -%}By early 2006, the I2P software was at least feature-complete, but it
was still not widely-known. jrandom’s view was that it shouldn’t be
marketed publicly until it was near-perfect, and labeled as version 1.0.
The network had perhaps a thousand users at the time. Project members
were discouraged from talking about it online, and the website
(`i2p.net <http://i2p.net>`__) was unpolished and incomplete.{%- endtrans %}

{% trans -%}On July 27, 2006, jrandom released I2P version 0.6.1.23, including an
innovative new TCP transport protocol he designed called “NTCP”, for
new-IO-based TCP. It used Java’s new IO library for efficient handling
of large numbers of TCP connections.{%- endtrans %}

{% trans -%}In late 2006, jrandom turned his focus to Syndie. He came to see it as
his top priority, and the “killer application” for I2P. Highly secure
and almost unusable, it delayed messages for up to two days before
delivery to resist traffic analysis. Later in 2006, he stopped work on
the bundled Syndie application and started a new, incompatible,
standalone messaging application. This application was, confusingly,
also called “Syndie”. The new Syndie was a large and complex
development, and it was essentially a one-man project.{%- endtrans %}

{% trans -%}From late 2006 into 2007, core I2P development and releases slowed
dramatically. From almost 30 releases in 2005 and 13 in the first half
of 2006, there were only 5 in the second half of 2006 and only 4 in all
of 2007. During this time, zzz and a developer named Complication had
source code commit privileges and were making changes, but their
understanding of the code base was limited. zzz worked, for example, on
improving i2psnark, fixing bugs, and redesigning the strategy for
anticipatory tunnel building. But there was a lot more that needed to be
done. Complication and zzz did what they could, and they wrote the code
for almost all the changes in the four 2007 releases
(0.6.1.27–0.6.1.30). By this time, jrandom was providing very little
guidance, code review, or direction for the project.{%- endtrans %}

{% trans -%}It wasn’t apparent at the time, but the project was in trouble.{%- endtrans %}

{% trans -%}jrandom had almost stopped working on the core I2P router and
applications. Even the new Syndie, which he had declared as far more
important than I2P itself, languished. After regular releases through
March 2007, his next Syndie release, 1.100a, was August 25, 2007. All
I2P releases were required to be signed by jrandom’s key, and he built
and signed his last release, 0.6.1.30, on October 7, 2007.{%- endtrans %}

{% trans -%}In November 2007, disaster struck. Complication and zzz received a
cryptic message from jrandom, that he would have to take time off from
both Syndie and I2P development for a year or more. He expected that he
would still be available to sign releases, but was willing to pass the
release signing key to somebody else. Complication and zzz immediately
replied with a request for the release key and other credentials, such
as access to the website, mailing list, CVS administration, and others.
Unfortunately, they never heard from jrandom again.{%- endtrans %}

{% trans -%}Late 2007 and early 2008, they awaited jrandom’s response, and wondered
what to do next. However, all of the project infrastructure remained
active, so it didn’t seem to be an immediate crisis. They knew, however,
that without the release key or website access, they would have to sign
with new keys, host the files on a new website, and require everybody to
manually update since their keys wouldn’t be recognized.{%- endtrans %}

{% trans -%}The second stage of the disaster happened on January 13, 2008. The
hosting company for almost all `i2p.net <http://i2p.net>`__ servers
suffered a power outage, and they did not fully return to service. Only
jrandom had the credentials required to restore service. In addition,
the centralized CVS source control appeared to be down, so five years of
source control history appeared to be lost. Luckily, the CVS server was
up, only the name server for it was down. The full contents of the CVS
archive was quickly downloaded.{%- endtrans %}

| {% trans -%}Complication, welterde, and zzz quickly made a number of decisions to
  get the project back up and running. Welterde started a new website at
  `i2p2.de <http://i2p2.de>`__. I2P needed to move to a decentralized
  source code control system. They tested bazaar and that did not work
  well over I2P. Git was just getting started. jrandom had used monotone
  for Syndie and liked its security properties, and it worked well over
  I2P, so it was selected.{%- endtrans %}
| {% trans -%}Several people set up new services. The next release, 0.6.1.31, was
  signed by Complication and required a manual upgrade. It was released
  on February 10, 2008.{%- endtrans %}

{% trans -%}The project realized that even though it claimed to be totally
decentralized, it actually depended on a number of centralized
resources, above all, on jrandom. Work was done throughout 2008 to
decentralize the project, and distribute roles to a number of people.
Additionally, it was realized that development had essentially stalled
in 2007, because jrandom had stopped working on it, but had not
delegated to other developers. Nobody had an overall understanding of
the code base.{%- endtrans %}

{% trans -%}Complication continued to sign the releases through mid-2009, but his
contributions declined as he focused on activism and other projects.
Starting with release 0.7.6 on July 31, 2009, zzz would sign the next 49
releases.{%- endtrans %}

{% trans -%}In December 2008, zzz attended his first CCC, 25C3 in Berlin, and met
other I2P project team members for the first time, including hottuna and
welterde. The experience was overwhelming, and also humbling, as he
struggled to explain I2P to others or answer even basic questions about
its design and use of cryptography.{%- endtrans %}

{% trans -%}By mid-2009, zzz had come to understand the code base much better. Far
from being complete or perfect, it was filled with problems and
scalability issues. In 2009 the project experienced more network growth
due to its anonymizing properties as well as its circumvention
abilities. Participants appeared who were beginning to adopt the network
for reasons like censorship and clearnet issues like blocking of popular
services. For development gains, in-net auto updates became available
for the software.{%- endtrans %}

.. image:: /_static/images/history/propaganda.jpeg

{% trans -%}July 2010 zzz briefly presented I2P at the end of Adrian Hong’s
presentation at HOPE XXXX. Adrian talked about how tech has helped
expose human rights violations, and the need for defensive tools for
activists. He urged that we all be ambassadors for all tech, stay on top
of new tech, and keep the barrier low and educate people about how to
use the tool we create.{%- endtrans %}

{% trans -%}He also talked about how we need many options for people to use, and
asked how do we make it easier to support human rights, freedom of
expression?{%- endtrans %}

{% trans -%}At the end of the talk, zzz was invited on stage to introduce I2P and
give an overview of what the project was about. The same weekend, it was
pointed out that the I2P documentation was not in great shape.{%- endtrans %}

{% trans -%}In Fall 2010, zzz declared a moratorium on I2P development until the
website documentation was complete and accurate. It took 3 months to get
it done.{%- endtrans %}

{% trans -%}Beginning in 2010, until COVID restrictions were put in place, zzz, ech,
hottuna, and other I2P contributors have attended CCC ( Chaos
Communications Congress) every year. Over the years, meeh, Zab, Sadie,
LazyGravy, KYTV, IDK and others have made the trip to Germany to share
tables with other projects and celebrate the end of a year of releases.
The project looks forward to one day being able to meet up again and
have an in-person yearly roadmap meeting.{%- endtrans %}

{% trans -%}Anoncoin, a digital cryptocurrency that focuses on privacy and anonymity
for its users was created in 2013. It was the first coin that provided
built-in support for I2P, as well as Tor that makes it impossible to
determine the IP address of the user. The developers, including meeh,
also ran organizations like Privacy Solutions, and provided infrastructure
support to the I2P network by running services like outproxies and
reseed servers.{%- endtrans %}

{% trans -%}I2PBote development started to take off again in 2014 when str4d began
contributing to the project. Bote is a server-less email client — it
stores email in a `distributed hash
table <http://en.wikipedia.org/wiki/Distributed_hash_table>`__. Email is
“automatically encrypted and digitally signed, which ensures no one but
the intended recipient can read the email, and third parties cannot
forge them.” ( https://i2pbote.xyz/). The project has existed since
2009.{%- endtrans %}

.. compound::
  .. image:: /_static/images/history/bote.png
     :width: 100%

> I2PBote screenshot Credit: AceBarry

{% trans -%}At Real World Crypto that year, zzz, psi and str4d began to talk about
and review the plan to update I2P’s cryptography. The same year, the
project was awarded a $5k donation from Duck Duck Go. Lavabit,
SecureDrop, RiseUp and Mailpile also received donations for supporting
better trust and privacy online.{%- endtrans %}

{% trans -%}By late 2014 most new signing crypto was complete, including ECDSA and
EdDSA. New destination crypto was available; but new router info crypto
needed to wait a year for the network to upgrade sufficiently.{%- endtrans %}

{% trans -%}During the early part of 2015, zzz posted to Twitter that it would be
great to have a mini conference for I2P. In Spring, it was decided that
I2PCon would take place that August over the course of a weekend.{%- endtrans %}

{% trans -%}Hottuna and Sadie organized most of the details, getting graphic assets
created, posters printed and a banner made for the podium. Nick at
Hacklab, where the event would take place, helped with making sure the
space was ready for the event. Sadie reached out to the local infosec
community and helped secure guest speakers as well. The event happened
on one of the hottest weekends of the Summer, with attendees arriving
from America and Europe. The I2P community did an amazing job of
supporting the event by postering, giving talks, and spreading the word
in forums and on social media. The talks can be viewed on KYTV’s YouTube
Channel https://www.youtube.com/channel/UCZfD2Dk6POE-VU8DOqW7VVw{%- endtrans %}

.. compound::
  .. image:: /_static/images/history/i2pcon1.png
     :width: 100%

{% trans -%}In January 2016 at Real World Crypto Stanford — str4d gave a talk on the
crypto migration progress and future plans for the project. zzz and
others would continue weekly meetings to plan the migration over the
next few years.{%- endtrans %}

{% trans -%}NTCP2 was implemented in 2018, in release 0.9.36. It was disabled by
default so that it could be tested. It was enabled in 0.9.37. NTCP1 was
disabled in 0.9.40.{%- endtrans %}

    {% trans -%}The new I2P transport protocol provides effective resistance against
    DPI censorship. It also results in reduced CPU load because of the
    faster, modern cryptography used. It makes I2P more likely to run on
    low-end devices, such as smartphones and home routers. Both major I2P
    implementations have full support for NTCP2 and it make NTCP2
    available for use starting with version 0.9.36 (Java) and 2.20 (i2pd,
    C++).{%- endtrans %}

{% trans -%}The complete implementation details can be read here
https://geti2p.net/en/blog/post/2018/08/20/NTCP2{%- endtrans %}

{% trans -%}0.9.39 included extensive changes for new network database types
(proposal 123). The i2pcontrol plugin was bundled as a web-app to support
development of RPC applications.{%- endtrans %}

{% trans -%}In 2019, the team decided to attend more conferences. That year IDK and
zzz attended DefCon, and IDK gave a workshop on I2P application
development. At Monero Village, zzz gave a talk called I2P for
Cryptocurrency Developers.{%- endtrans %}

{% trans -%}Late that year, Sadie and IDK attended Our Networks in Toronto, where
IDK gave a lightning talk about I2P.{%- endtrans %}

{% trans -%}Sadie attended RightsCon in Tunis and the Internet Freedom Festival in
Valencia to meet with NGO’s and Human Right Defenders. Thanks to the the
connections we made, the project received grants for usability and
accessibility support from Open Tech Fund, and most recently Internews.
This will ensure more user friendly onboarding, UX, and information
architecture improvements to support the growing interest in the
network. It will also support specific tooling to help in-need users
with specific risk surfaces through user research.{%- endtrans %}

.. image:: /_static/images/history/phong.png

{% trans -%}That Summer, Hoàng Nguyên Phong had his research into I2P censorship
accepted too FOCI at USENIX in Santa Clara. Sadie had supported the
research and they attended together. I2P Metrics was created during this
time https://i2p-metrics.np-tokumei.net/, and well as research into more
resistant reseed servers for the I2P network
https://homepage.np-tokumei.net/post/notes-i2p-reseed-over-cloudflare/.
You can read the research report here
https://homepage.np-tokumei.net/post/notes-otf-wrapup-blogpost/.{%- endtrans %}

{% trans -%}At CCC that year, the decision was made to migrate from Monotone too
GitLab. The project was one of the last to use Monotone, and it was time
to prepare to move on. IDK would spend 2020 ensuring the process was as
smooth as it could be. The pandemic would result in the team not being
able to see each other that year to celebrate the ( mostly) smooth move
to Gitlab. On December 10. 2020, the project switched off the old mtn
i2p.i2p branch, and moved the development of the core Java I2P libraries
from Monotone to Git officially.{%- endtrans %}

    {% trans -%}Congratulations and thanks to everyone who helped in the git
    migration, especially zzz, eche|on, nextloop, and our site mirror
    operators! While some of us will miss Monotone, it has become a
    barrier for new and existing participants in I2P development and
    we’re excited to join the world of developers using Git to manage
    their distributed projects.{%- endtrans %}

https://geti2p.net/en/blog/post/2020/12/10/Hello-git-goodbye-mtn

{% trans -%}0.9.47 enabled the new end-to-end encryption protocol (proposal 144) by
default for some services. A Sybil analysis and blocking tool was also
now enabled by default. 0.9.48 enabled the new end-to-end encryption
protocol (proposal 144) for most services. Preliminary support was added
for new tunnel build message encryption (proposal 152). There were
significant performance improvements throughout the router.{%- endtrans %}

{% trans -%}0.9.49 was the release that brought faster crypto. The I2P network
became faster and more secure. Improvements and fixes for the SSU (UDP)
transport resulted in faster speeds. The release also started the
migration to new, faster ECIES-X25519 encryption for routers. The
project had been working on the specifications and protocols for new
encryption for several years, and was getting close to the end of it.
The migration would take several releases to complete.{%- endtrans %}

{% trans -%}To minimize disruption, only new installs and a very small percentage of
existing installs (randomly selected at restart) would be using the new
encryption.{%- endtrans %}

{% trans -%}The project had “rekeyed” the network twice before, when changing the
default signature type, but this was the first time it had changed the
default encryption type. 0.9.50 enabled DNS over HTTPS for reseeding to
protect users from passive DNS snooping. There were numerous fixes and
improvements for IPv6 addresses, including new UPnP support.{%- endtrans %}

.. _31b4:

{% trans -%}1.5.0 — The early anniversary release because it is so good!{%- endtrans %}
------------------------------------------------------------

    {% trans -%}Yes, that’s right, after 9 years of 0.9.x releases, we are going
    straight from 0.9.50 to 1.5.0. This does not signify a major API
    change, or a claim that development is now complete. It is simply a
    recognition of almost 20 years of work to provide anonymity and
    security for our users.{%- endtrans %}

    {% trans -%}This release finishes implementation of smaller tunnel build messages
    to reduce bandwidth. We continue the transition of the network’s
    routers to X25519 encryption. Of course there are also numerous bug
    fixes and performance improvements.{%- endtrans %}

    {% trans -%}As usual, we recommend that you update to this release. The best way
    to maintain security and help the network is to run the latest
    release.{%- endtrans %}

{% trans -%}Congratulations team. Let’s do another 20.{%- endtrans %}
