==============================================
{% trans -%}Def Con Trip Report- zzz{%- endtrans %}
==============================================

.. meta::
   :author: zzz
   :date: 2019-08-30
   :category: release
   :excerpt: {% trans %}Def Con Trip Report- zzz{% endtrans %}

{% trans -%}Def Con Trip Report{%- endtrans %}
==============================================

{% trans -%}
idk and I attended DEFCON 27 and presented two workshops on I2P for application
developers, with support from mhatta and Alex. I gave the workshop at Monero
Village and idk gave the one at Crypto/Privacy Village. Here, I will summarize
the Monero Village workshop, and a Tor talk by Roger Dingledine. idk will post a
trip report covering his workshop.
{%- endtrans %}

{% trans -%}
We had about 8 attendees for the Monero Village workshop, entitled "I2P for
Cryptocurrency Developers". We planned to discuss the particular networking
needs for each application and work through the various i2ptunnel and SAM
options available. However, all attendees were relatively unfamiliar with I2P,
so we pivoted and gave an overview of I2P. As none of the attendees had a laptop
with them, we helped several of them install I2P on their Android phone and
walked through some of the features of the app. For all users, the app appeared
to reseed and build tunnels fairly quickly.
{%- endtrans %}

{% trans -%}
One common question after installing the app was "what do I do now?". The app
doesn't have a 'hidden services of interest' section or first-run wizard like
our desktop application does, and most of the default addressbook entries are
long-dead. There's improvements we could make to the first-run experience.
Also, some of the more interesting parts of the app are hidden behind an
advanced setting; we should review those items and consider un-hiding some of
them.
{%- endtrans %}

{% trans -%}
It's always useful to go to Tor talks, not so much to find out what they're
doing, but to hear how they explain things to people, and what terminology they
are using. Roger's talk "The Tor Censorship Arms Race" was in a large room
attended by about two thousand people. He gave a very brief overview of Tor
with only three or four slides. He says they now have "two to eight million
users a day". Most of the talk was a review of national blocking attempts over
the years, starting with Thailand and Iran in '06-'07 through Tunisia, china,
and Ethiopia in 2011. He called Tor bridges a "crappy arms race". He showed a
new form to be showed to new users, with a checkbox "Tor is censored in my
country".
{%- endtrans %}

{% trans -%}
Their new pluggable transport "snowflake" uses a combination of domain
fronting, webrtc, javascript, brokers and proxies to reach a Tor bridge. Roger
only had one slide on it, and I wasn't familiar with it, so we should do more
research on what it's all about. He briefly mentioned some things they may be
working on next, including "salmon" distribution of bridges, FTE/Marionette,
decoy routing, and "cupcake" which is an extension of snowflake. While I don't
have any further information about them, they may be good buzzwords to keep an
eye out for on their mailing lists.
{%- endtrans %}

{% trans -%}
Much of Tor's censorship woes is due to Tor's popularity, but their TLS
handshake is a particular issue and it's been the focus of much of the "arms
race" over the years. In some ways we're in better shape, as we've taken
several features of their current-best obfs4 pluggable transport and build them
into NTCP2. However, we do have issues with our website and reseeds being
blocked, as Sadie and Phong will be presenting at USENIX FOCI this week.
{%- endtrans %}

{% trans -%}
Notes for next time: I do recommend DEFCON, as long as we find a village to
call our home. It's an enormous conference and the limited general hangout
spaces are massively overcrowded. Both Monero Village and Crypto/Privacy
Village were fantastic hosts and we had several hours at each spot to meet with
people. We should find more opportunities to work with both organizations.
There were also ZCash people at the Monero Village and we should work with them
also. Any future workshop should be targeted at a more general audience. We do
need a standard "Intro to I2P" slide deck; it would have been helpful at the
workshops. Don't expect attendees to have laptops with them, focus on Android
for any hands-on exercises. There's several improvements to be made in our
Android app. Drink lots of water in Vegas... and stay away from the slot
machines.
{%- endtrans %}
