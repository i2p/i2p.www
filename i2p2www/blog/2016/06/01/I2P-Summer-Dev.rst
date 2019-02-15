{% trans -%}
==============
I2P Summer Dev
==============
{%- endtrans %}

.. meta::
    :author: str4d
    :date: 2016-06-01
    :category: summer-dev
    :excerpt: {% trans %}We are pleased to announce that this summer, I2P will be embarking on a development program aimed at improving the privacy software ecosystem for both developers and users.{% endtrans %}

{% trans -%}
Over the last few years, the need for users to be in control of their own data
has become increasingly apparent. Some excellent progress had been made in this
regard with the rise of messaging apps like Signal_, and file storage systems
like Tahoe-LAFS_. The ongoing work of `Let's Encrypt`_ to bring HTTPS to the
whole world is steadily gaining traction.
{%- endtrans %}

{% trans -%}
But building privacy and anonymity into applications is not trivial. Much of the
software people use every day was not designed to be privacy-preserving, and the
tools developers have available are generally not easy to work with. The
recently-published OnionScan_ survey gives some insight into just how easy it is
for even technical users to mis-configure their services, completely undermining
their intentions.
{%- endtrans %}

.. _Signal: https://whispersystems.org/
.. _Tahoe-LAFS: https://tahoe-lafs.org/trac/tahoe-lafs
.. _`Let's Encrypt`: https://letsencrypt.org/
.. _OnionScan: https://onionscan.org/


{% trans -%}
Helping developers help their users
===================================
{%- endtrans %}

{% trans -%}
We are pleased to announce that this summer, I2P will be embarking on a
development program aimed at improving the privacy software ecosystem. Our goal
is to make life easier both for developers wanting to leverage I2P in their
applications, and for users trying to configure and run their apps through I2P.
{%- endtrans %}

{% trans -%}
We will be focusing our time this summer into three complementary areas:
{%- endtrans %}

{% trans -%}
June: APIs
----------
{%- endtrans %}

{% trans -%}
In June, we will be updating the various libraries that exist for interfacing
with I2P. We have made significant progress this year on extending our SAM_ API
with additional features, such as support for datagrams and ports. We plan to
make these features easily accessible in our C++ and Python libraries.
{%- endtrans %}

{% trans -%}
We will also soon be making it much easier for Java and Android developers to
add I2P support to their applications. Stay tuned!
{%- endtrans %}

.. _SAM: {{ site_url('docs/api/samv3') }}

{% trans -%}
July: Apps
----------
{%- endtrans %}

{% trans -%}
In July we will be working with applications that have expressed interest in
adding support for I2P. There are some really neat ideas being developed in the
privacy space right now, and we want to help their communities leverage over a
decade of research and development on peer-to-peer anonymity. Extending these
applications to work natively over I2P is a good step forward for usability, and
in the process will improve how these applications think about and handle user
information.
{%- endtrans %}

{% trans -%}
August: Plugins
---------------
{%- endtrans %}

{% trans -%}
Finally, in August we will turn out attention to the apps we bundle inside I2P,
and the wider array of plugins. Some of these are due for some love, to make
them more user-friendly - as well as fix any outstanding bugs! We hope that
longtime I2P supporters will enjoy the outcome of this work.
{%- endtrans %}


{% trans -%}
Take part in Summer Dev!
========================
{%- endtrans %}

{% trans -%}
We have many more ideas for things we'd like to get done in these areas. If
you're interested in hacking on privacy and anonymity software, designing usable
websites or interfaces, or writing guides for users: come and chat with us on
IRC or Twitter! We are always happy to "see" new "faces" in our community, both
inside and outside I2P. We'll be sending I2P stickers out to all new
contributors taking part (or possibly other pending I2P goodies)!
{%- endtrans %}

{% trans -%}
Likewise, if you are an application developer who wants a hand with integrating
I2P, or even just to chat about the concepts or details: get in touch! If you
want to get involved in our July Apps month, contact `@GetI2P`_, `@i2p`_ or
`@str4d`_ on Twitter. You can also find us in #i2p-dev on OFTC or FreeNode.
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
