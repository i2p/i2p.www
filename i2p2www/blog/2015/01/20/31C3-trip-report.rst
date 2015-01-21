{% trans -%}
================
31C3 trip report
================
{%- endtrans %}
.. meta::
   :author: zzz
   :date: 2015-01-20
   :excerpt: {% trans %}CCC has always been a productive time for us, and 31C3 was no exception. Here is a summary of our various meetings and discussions.{% endtrans %}

*Attending:* `Apekatten`_, `Echelon`_, `Hottuna`_, `Marielle`_, `Meeh`_, Sindu, `zzz`_

.. _`Apekatten`: https://twitter.com/apekattenandre
.. _`Echelon`: https://twitter.com/echeloni2p
.. _`Hottuna`: https://twitter.com/hottuna_i2p
.. _`Marielle`: https://twitter.com/k4k3fyll
.. _`Meeh`: https://twitter.com/mikalv
.. _`zzz`: https://twitter.com/i2p

{% trans -%}
We were, for the second year in a row, at a great location in the Congress, in
`Noisy Square`_, right next to the EFF table. Being part of Noisy Square has
really increased our visibility and helped many people find us. Thanks to Noisy
Square and the 31C3 organizers for a great Congress.
{%- endtrans %}

.. _`Noisy Square`: https://noisysquare.com/

{% trans -%}
We also thank Gabriel Weinberg and his fabulous search engine `DuckDuckGo`_ for
their support of open source anonymity tools and their `generous contribution`_
to I2P in 2014. Funding from DuckDuckGo and others helped support our attendance
at CCC. This is the primary annual meetup for I2P developers and it is critical
to our success.
{%- endtrans %}

.. _`DuckDuckGo`: https://duckduckgo.com/
.. _{{ _('`generous contribution`') }}: https://geti2p.net/en/blog/post/2014/03/12/press-release-ddg-donation

{% trans -%}
Discussions with others
=======================
{%- endtrans %}

GNUnet
------

{% trans -%}
We spoke at length with Christian Grothoff of `GNUnet`_. He has moved himself
and the project from TU Munich to `Inria`_ in France. He has a large number of
`open positions`_. This is a great opportunity to get paid to work on open
source anonymity tools, we encourage everybody to contact him about it.
{%- endtrans %}

.. _`GNUnet`: https://gnunet.org/
.. _`Inria`: https://www.inria.fr/en/
.. _{{ _('`open positions`') }}: https://gnunet.org/hiring

{% trans -%}
The prospect of an invigorated GNUnet with a large amount of new funding is
quite interesting. We discussed more ways to work together. In early 2014, we
worked hard to understand the GnuNet DNS replacement, but we were unable to
figure out a good fit for it in I2P. One of his new ideas is a distributed,
anonymous statistics gathering subsystem, for detecting problems or attacks on
the network. We'd definitely be interested in that.
{%- endtrans %}

{% trans -%}
We also discussed the `Special-Use Domain Names of Peer-to-Peer Systems draft`_.
A new, greatly simplified version 3 was posted in December. The prospects for
approval remain unclear. The best way to monitor or participate in the
discussion is via the `IETF DNSOP WG mailing list`_. We will attempt to do so
on our side, and also give Hellekin a new point-of-contact for this topic.
{%- endtrans %}

.. _{{ _('`Special-Use Domain Names of Peer-to-Peer Systems draft`') }}: https://datatracker.ietf.org/doc/draft-grothoff-iesg-special-use-p2p-names/
.. _{{ _('`IETF DNSOP WG mailing list`') }}: https://www.ietf.org/mail-archive/web/dnsop/current/maillist.html

{% trans -%}
We apologized to Christian for not being organized enough to have a talk at his
`We Fix The Net assembly`_. One of our biggest failures is a project is our
seeming inability to submit talks at conferences. We'll have to do better in the
new year.
{%- endtrans %}

.. _{{ _('`We Fix The Net assembly`') }}: https://events.ccc.de/congress/2014/wiki/Session:WeFixTheNet

Debian
------

{% trans -%}
Iain Learmonth, a Debian participant, stopped by. He wants to put I2P in with
other anonymity tools into this new Debian "superpackage" of some sort, and
would love to get I2P into Debian in 2015. He claims the process is now easy,
just `follow the instructions`_. We said that's funny, we've been
`stuck in the process for over 7 years`_.
{%- endtrans %}

.. _{{ _('`follow the instructions`') }}: https://mentors.debian.net/
.. _{{ _('`stuck in the process for over 7 years`') }}: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=448638

{% trans -%}
He said, well, try the new process, it works great, should be no problem at all
if your package is in good shape. The people in Debian that run this process are
eager volunteers who want nothing more than to get more packages in. We said our
package is indeed in fantastic shape, and we would try out the new process as
soon as possible. As best as we can tell, we are orphaned in the old process and
have to restart in the new process? If all this is true, we will be in the next
Debian release in late 2015. This would be very very cool.
{%- endtrans %}

Tails
-----

{% trans -%}
We had a nice discussion with BitingBird of Tails. They are very happy with our
rapid response to the `vulnerability disclosure`_ last summer, resulting in our
`0.9.14 release`_. Our vulnerability was initially blamed on Tails, and they
took `great offense`_ to that and the lack of private notification. We thanked
them for taking the heat and fighting back.
{%- endtrans %}

.. _{{ _('`vulnerability disclosure`') }}: https://twitter.com/ExodusIntel/status/491247299054428160
.. _{{ _('`0.9.14 release`') }}: {{ get_url('blog_post', slug='2014/07/26/0.9.14-Release') }}
.. _{{ _('`great offense`') }}: https://tails.boum.org/news/On_0days_exploits_and_disclosure/index.en.html

{% trans -%}
Biting Bird also handles support, and she tells us the number one issue is how
long I2P takes to start up and be useful for browsing I2P sites. Her standard
answer is "wait ten more minutes" and that seems to be effective. I2P is
particularly slow to startup on Tails since it does not persist peer data by
default. It would be nice to change that, but there's also things we can do on
the I2P side to make things start faster. Expect some improvement in our 0.9.18
release.
{%- endtrans %}

Onioncat
--------

{% trans -%}
Longtime friend of I2P Bernhard Fischer of `OnionCat`_ stopped by. The upcoming
Tor Hidden Services changes mean that their keys will no longer fit into a
portion of an IPv6 address, and he was working on a solution. We reminded him
that this has always been the case for I2P (with "GarliCat"), that it's not a
new problem. He pointed us to `a presentation`_ of his proposal. It involves
storing an extra record in the hidden service directory (equivalent of a
leaseset I2P's network database). It wasn't completely clear how this would
work, or if we would consider it abuse of the netDb. We'll follow up with him
as he gets further.
{%- endtrans %}

.. _`OnionCat`: https://www.onioncat.org/
.. _{{ _('`a presentation`') }}: https://www.youtube.com/watch?v=Zj4hSx6cW80

{% trans -%}
New users
---------
{%- endtrans %}

{% trans -%}
We spent hours and hours explaining I2P to people stopping by our table. Some
had heard of I2P before, some had not; everybody had heard of Tor and had at
least a vague idea of what hidden services are. As usual, introducing people to
I2P was a struggle. By the end of the Congress, we became convinced that a part
of the problem was a difference in terminology. Back 12 years ago, when I2P and
Tor were both getting started, we each came up with terms for the various parts
of our systems. Today, the Tor terminology such as "hidden service" is
well-understood and commonplace. The I2P terminology such as "eepsite" is
neither. We agreed to review our documentation, router console, and other places
for opportunities to simplify it and use common terms.
{%- endtrans %}

{% trans -%}
I2P project topics
------------------
{%- endtrans %}

{% trans -%}
* *Spending money:* We discussed several ways to effectively use our resources
  in 2015, including more hardware for testing and development. Also, we plan to
  increase reimbursement levels for conference attendees.
{%- endtrans %}

{% trans -%}
* *Toronto meetup:* CCC is such a productive time for us, and it seems that a
  second meetup in the year would be quite helpful. We have proposed it for
  August 2015 in Toronto, Canada, in conjunction with `Toronto Crypto`_. It
  would include developer meetings together with presentations and tutorials,
  all open to the public. We are attempting to gauge interest and research
  possible venues. If you are considering attending, please let us know by
  `tweeting @i2p`_ or posting `on the dev forum thread`_. 
{%- endtrans %}

{% trans -%}
* We discussed Meeh's workload and the state of the various services he is
  running. We made some plans to reduce his load and have some other people help
  out.
{%- endtrans %}

{% trans -%}
* We reviewed our critieria for placing links to `i2pd`_ on our download page.
  We agreed that the only remaining item is to have a nice page on the
  `Privacy Solutions web site`_ or elsewhere with binary packages for Windows,
  Linux, and Mac, and source packages. It's not clear who is responsible for
  building the packages and where the "official" version is. Once there's an
  established process for building and signing packages and an official place to
  put them, we're ready to link to it. If it is not feasible to host it on the
  Privacy Solutions website, we will discuss alternatives with orignal,
  including possible migration to our download servers.
{%- endtrans %}

{% trans -%}
* Lots of people coming by the table asked if we had a non-Java version. It was
  great to finally answer "yes" and we're eager to get the word out and get more
  users, testers, and developers on it.
{%- endtrans %}

{% trans -%}
* `Vuze`_ continues to make good progress on their I2P integration. We look
  forward to working with them in the new year on a managed rollout to more
  users.
{%- endtrans %}

{% trans -%}
* We discussed the state of Meeh's and Sindu's reseed servers. They made several
  improvements while at the congress and are investigating migration to
  `Matt Drollette's Go implementation`_. The security and reliability of our
  reseed servers is vital to new users and network operation. `User 'backup'`_
  is doing a great job monitoring and managing the pool of reseed servers.
{%- endtrans %}

{% trans -%}
* We agreed to purchase a second root server for development, testing, and
  services. Echelon will be adminstering it. Contact him is you would like a VM.
{%- endtrans %}

{% trans -%}
* We reiterated that we have funds available to purchase test hardware,
  especially for Windows and Mac. Talk to echelon for details.
{%- endtrans %}

{% trans -%}
* We met with Welterde about the state of his services including his
  `open tracker`_. These services are not being adequately maintained and will
  soon become inaccessible due to crypto changes if they are not upgraded. He
  committed to upgrading them soon.
{%- endtrans %}

{% trans -%}
* We met lots of people interested in our `Android app`_. We passed several
  ideas and bug reports back to str4d. We plan to make a big push to give the
  app some development love early in the year.
{%- endtrans %}

{% trans -%}
* Regrettably, we didn't get to see too many talks at the Congress, as we were
  so busy meeting with people. We plan to catch up and `watch them online`_. As
  usual, Tor's "State of the Onion" talk was excellent, and Jacob's talk was
  great. We hear that the cryptography talks were good as well.
{%- endtrans %}

.. _{{ _('`Toronto Crypto`') }}: https://torontocrypto.org/
.. _{{ _('`tweeting @i2p`') }}: https://twitter.com/i2p
.. _{{ _('`on the dev forum thread`') }}: http://{{ i2pconv('zzz.i2p') }}/topics/1778

.. _`i2pd`: https://github.com/PrivacySolutions/i2pd
.. _{{ _('`Privacy Solutions web site`') }}: https://privacysolutions.no/

.. _`Vuze`: https://www.vuze.com/

.. _{{ _("`Matt Drollette's Go implementation`") }}: https://github.com/MDrollette/i2p-tools
.. _{{ _("`User 'backup'`") }}: mailto:backup@mail.i2p

.. _{{ _('`open tracker`') }}: http://{{ i2pconv('tracker.welterde.i2p') }}/stats?mode=peer

.. _{{ _('`Android app`') }}: https://play.google.com/store/apps/details?id=net.i2p.android

.. _{{ _('`watch them online`') }}: https://media.ccc.de/browse/congress/2014/
