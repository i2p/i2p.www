{% trans -%}
================================
I2P Summer Dev 2017: MOAR Speed!
================================
{%- endtrans %}

.. meta::
    :author: str4d
    :date: 2017-06-01
    :category: summer-dev
    :excerpt: {% trans %}This year's Summer Dev will be focused on metrics collection and performance improvements for the network.{% endtrans %}

{% trans -%}
It's that time of year again! We're embarking on our summer development
programme, where we focus on a particular aspect of I2P to push it forward. For
the next three months, we'll be encouraging both new contributors and existing
community members to pick a task and have fun with it!
{%- endtrans %}

{% trans -%}
`Last year`__, we focused on helping users and developers leverage I2P, by
improving API tooling and giving some love to applications that run over I2P.
This year, we want to improve the user experience by working on an aspect that
affects everyone: performance.
{%- endtrans %}

__ {{ get_url('blog_post', slug='2016/06/01/I2P-Summer-Dev') }}

{% trans -%}
Despite onion-routing networks often being called "low-latency" networks, there
is significant overhead created by routing traffic through additional computers.
I2P's unidirectional tunnel design means that by default, a round trip between
two Destinations will involve twelve participants! Improving the performance of
these participants will help to both reduce the latency of end-to-end
connections [1]_, and increase the quality of tunnels network-wide.
{%- endtrans %}

{% trans -%}
MOAR speed!
===========
{%- endtrans %}

{% trans -%}
Our development programme this year will have four components:
{%- endtrans %}

{% trans -%}
Measure
-------
{%- endtrans %}

{% trans -%}
We can't tell if we improve performance without a baseline! We'll be creating a
metrics system for collecting usage and performance data about I2P in a
privacy-preserving way, as well as porting various benchmarking tools to run
over I2P (e.g. iperf3_).
{%- endtrans %}

.. _iperf3: https://github.com/esnet/iperf

{% trans -%}
Optimise
--------
{%- endtrans %}

{% trans -%}
There's a lot of scope for improving the performance of our existing code, to
e.g. reduce the overhead of participating in tunnels. We will be looking at
potential improvements to:
{%- endtrans %}

* {% trans %}Cryptographic primitives{% endtrans %}
* {% trans %}Network transports, both at the link-layer (NTCP_, SSU_) and end-to-end (Streaming_){% endtrans %}
* {% trans %}Peer profiling{% endtrans %}
* {% trans %}Tunnel path selection{% endtrans %}

.. _NTCP: {{ site_url('docs/transport/ntcp') }}
.. _SSU: {{ site_url('docs/transport/ssu') }}
.. _Streaming: {{ site_url('docs/api/streaming') }}

{% trans -%}
Advance
-------
{%- endtrans %}

{% trans -%}
We have several open proposals for improving the scalability of the I2P network
(e.g. Prop115_, Prop123_, Prop124_, Prop125_, Prop138_, Prop140_). We will be
working on these proposals, and begin implementing the finalised ones in the
various network routers. The more feedback these proposals receive, the sooner
we can roll them out, and the sooner I2P services can start using them!
{%- endtrans %}

.. _Prop115: {{ proposal_url('115') }}
.. _Prop123: {{ proposal_url('123') }}
.. _Prop124: {{ proposal_url('124') }}
.. _Prop125: {{ proposal_url('125') }}
.. _Prop138: {{ proposal_url('138') }}
.. _Prop140: {{ proposal_url('140') }}

{% trans -%}
Research
--------
{%- endtrans %}

{% trans -%}
I2P is a packet-switched network, like the internet it runs on top of. This
gives us significant flexibility in how we route packets, both for performance
and privacy. The majority of this flexibility is unexplored! We want to
encourage research into how various clearnet techniques for improving bandwidth
can be applied to I2P, and how they might affect the privacy of network
participants.
{%- endtrans %}

{% trans -%}
Take part in Summer Dev!
========================
{%- endtrans %}

{% trans -%}
We have many more ideas for things we'd like to get done in these areas. If
you're interested in hacking on privacy and anonymity software, designing
protocols (cryptographic or otherwise), or researching future ideas - come and
chat with us on IRC or Twitter! We are always happy to welcome newcomers into
our community, both inside and outside the I2P network. We'll also be sending
I2P stickers out to all new contributors taking part! If you want to chat about
a specific idea, contact `@GetI2P`_, `@i2p`_ or `@str4d`_ on Twitter. You can
also find us in #i2p-dev on OFTC or Freenode.
{%- endtrans %}

{% trans -%}
We'll be posting here as we go, but you can also follow our progress, and share
your own ideas and work, with the hashtag `#I2PSummer`_ on Twitter. Bring on the
summer!
{%- endtrans %}

.. _`@GetI2P`: https://twitter.com/GetI2P
.. _`@i2p`: https://twitter.com/i2p
.. _`@str4d`: https://twitter.com/str4d
.. _`#I2PSummer`: https://twitter.com/hashtag/I2PSummer

.. [1] {% trans %}Low-latency onion-routing networks are vulnerable to traffic confirmation attacks, so it would be reasonable to ask whether improved performance equates to reduced privacy. Some latency can help privacy if applied correctly via random delays or batching (neither of which are currently employed by any general-purpose onion-routing network). However, if a tunnel has uniform overall latency, then traffic confirmation attacks should be just as viable with or without that latency; thus there should be little statistical difference when the latency is reduced uniformly.{% endtrans %}
