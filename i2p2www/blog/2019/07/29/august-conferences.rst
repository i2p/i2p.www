.. meta::
    :title: {% trans %}August 2019 Conference Schedule{% endtrans %}
    :author: sadie
    :date: 2019-07-29
    :excerpt: {% trans %}I2P developers are attending multiple conferences this month{% endtrans %}

{% trans %}Conference Schedule August 2019{% endtrans %}
========================================================

{% trans %}Hi Everyone{% endtrans %},

{% trans %}Next month will be busy! Meet up with I2P developers at two workshops at
Defcon 27, and connect with researchers who have been observing I2P censorship
at FOCI '19.{% endtrans %}

{% trans %}I2P for Cryptocurrency Developers{% endtrans %}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|zzz|

-  {% trans %}Monero Village{% endtrans %}
-  {% trans %}August 9, 3:15pm{% endtrans %}
-  {% trans %}Monero Village will be on the 26th floor of Bally's{% endtrans %} `map <https://defcon.org/html/defcon-27/dc-27-venue.html>`__

{% trans %}This workshop will assist developers in designing applications to communicate
over I2P for anonymity and security. We will discuss common requirements for
cryptocurrency applications, and review each application's architecture and
specific needs.Then, we will cover tunnel communications, router and library
selection, and packaging choices, and answer all questions related to
integrating I2P.{% endtrans %}

{% trans %}The goal is to create secure, scalable, extensible, and efficient designs that
meets the needs of each particular project.{% endtrans %}

{% trans %}I2P For Application Developers{% endtrans %}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|idk|

-  {% trans %}Crypto & Privacy Village{% endtrans %}
-  {% trans %}Saturday August 10, 2pm - 3:30pm{% endtrans %}
-  {% trans %}Planet Hollywood{% endtrans %} `map <https://defcon.org/images/defcon-27/maps/ph-final-public.pdf>`__
-  {% trans %}This workshop is not recorded. So don't miss it!{% endtrans %}

{% trans %}The workshop provides an introduction to the ways an application can be made to
work with the I2P Anonymous Peer-to-Peer network. Developers should learn that
the use of anonymous P2P in their applications need not be that different than
what they are already doing in non-anonymous Peer-to-Peer applications. It
begins with an introduction to the I2P plugins system, showing how the existing
plugins set themselves up to do communication over I2P and what's good and bad
about each approach. Afterwards, we'll continue on to the programatically
controlling I2P via it's SAM and I2PControl API's. Finally, we'll take a dive
into the SAMv3 API by starting a new library utilizing it in Lua and writing a
simple application.{% endtrans %}

{% trans %}Measuring I2P Censorship at a Global Scale{% endtrans %}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|sadie|

-  {% trans %}FOCI '19{% endtrans %}
-  {% trans %}Tuesday August 13th 10:30am{% endtrans %}
-  {% trans %}Hyatt Regency Santa Clara{% endtrans %}
-  {% trans %}Co-located with USENIX Security '19{% endtrans %}
-  `{% trans %}Workshop Program{% endtrans %} <https://www.usenix.org/conference/foci19/workshop-program>`__

{% trans %}The prevalence of Internet censorship has prompted the creation of several
measurement platforms for monitoring filtering activities. An important
challenge faced by these platforms revolves around the trade-off between depth
of measurement and breadth of coverage. In this paper, we present an
opportunistic censorship measurement infrastructure built on top of a network of
distributed VPN servers run by volunteers, which we used to measure the extent
to which the I2P anonymity network is blocked around the world. This
infrastructure provides us with not only numerous and geographically diverse
vantage points, but also the ability to conduct in-depth measurements across all
levels of the network stack. Using this infrastructure, we measured at a global
scale the availability of four different I2P services: the official homepage,
its mirror site, reseed servers, and active relays in the network. Within a
period of one month, we conducted a total of 54K measurements from 1.7K network
locations in 164 countries. With different techniques for detecting domain name
blocking, network packet injection, and block pages, we discovered I2P
censorship in five countries: China, Iran, Oman, Qatar, and Kuwait. Finally, we
conclude by discussing potential approaches to circumvent censorship on I2P.{% endtrans %}

.. |zzz| image:: /_static/images/monerovillageblog.png
.. |idk| image:: /_static/images/cryptovillageblog.png
.. |sadie| image:: /_static/images/censorship.jpg

