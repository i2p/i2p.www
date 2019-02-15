{% trans -%}
========================
Summer Dev roundup: APIs
========================
{%- endtrans %}

.. meta::
    :author: str4d
    :date: 2016-07-02
    :category: summer-dev
    :excerpt: {% trans %}In the first month of Summer Dev, we have improved the usability of our APIs for Java, Android, and Python developers.{% endtrans %}

{% trans -%}
Summer Dev is in full swing: we've been busy greasing wheels, sanding edges, and
tidying the place up. Now it's time for our first roundup, where we bring you up
to speed on the progress we are making!
{%- endtrans %}

{% trans %}
But first, a big thank you to `Elio Qoshi`_ and `ura`_ for designing us the
fantastic logo you see above. It adds a cheerful personality to our development
program (and is going to look great on t-shirts).
{%- endtrans %}

.. _`Elio Qoshi`: http://elioqoshi.me
.. _`ura`: http://ura.al

{% trans -%}
APIs month
==========
{%- endtrans %}

{% trans -%}
Our goal for this month was to "blend in" - to make our APIs and libraries work
within the existing infrastructure of various communities, so that application
developers can work with I2P more efficiently, and users don't need to worry
about the details.
{%- endtrans %}

Java / Android
--------------

{% trans -%}
The I2P client libraries are now available on `Maven Central`_! See our
`previous blog post`_ for full details.
{% endtrans %}

{% trans -%}
This should make it much simpler for Java developers to use I2P in their
applications. Instead of needing to obtain the libraries from a current install,
they can simply add I2P to their dependencies. Upgrading to new versions will
similarly be much easier.
{%- endtrans %}

{% trans -%}
The `I2P Android client library`_ has also been updated to use the new I2P
libraries. This means that cross-platform applications can work natively with
either I2P Android or desktop I2P.
{%- endtrans %}

.. _`Maven Central`: http://search.maven.org/#search%7Cga%7C1%7Cg%3A"net.i2p"%20OR%20g%3A"net.i2p.client"
.. _{% trans %}`previous blog post`{% endtrans %}: {{ url_for('blog_post', slug='2016/06/13/I2P-on-Maven-Central') }}
.. _{% trans %}`I2P Android client library`{% endtrans %}: http://search.maven.org/#artifactdetails%7Cnet.i2p.android%7Cclient%7C0.8%7Caar

Python
------

txi2p
`````
{% trans -%}
The `Twisted`_ plugin ``txi2p`` now supports in-I2P ports, and will work
seamlessly over local, remote, and port-forwarded `SAM APIs`_. See its
`documentation`_ for usage instructions, and report any issues on `GitHub`_.
{%- endtrans %}

i2psocket
`````````
{% trans -%}
The first (beta) version of ``i2psocket`` has been released! This is a direct
replacement for the standard Python ``socket`` library that extends it with I2P
support over the `SAM API`_. See its `GitHub page`_ for usage instructions, and
to report any issues.
{%- endtrans %}

.. _`Twisted`: https://twistedmatrix.com
.. _`SAM APIs`:
.. _`SAM API`: {{ site_url('docs/api/samv3') }}
.. _{% trans %}`documentation`{% endtrans %}: https://txi2p.readthedocs.io
.. _`GitHub`: https://github.com/str4d/txi2p
.. _{% trans %}`GitHub page`{% endtrans %}: https://github.com/majestrate/i2p.socket

{% trans -%}
Other progress
--------------
{%- endtrans %}

- {% trans %}zzz has been hard at work on Syndie, getting a headstart on Plugins month. You can follow his progress on `the development forum thread`_.{% endtrans %}

- {% trans %}psi has been creating an I2P test network using i2pd, and in the process has found and fixed several i2pd bugs that will improve its compatibility with Java I2P.{% endtrans %}

.. _{% trans %}`the development forum thread`{% endtrans %}: http://zzz.i2p/topics/2064-syndie-release-july-2016

{% trans -%}
Coming up: Apps month!
======================
{%- endtrans %}

{% trans -%}
We are excited to be working with `Tahoe-LAFS`_ in July! I2P has for a long time
been home to one of the `largest public grids`_, using a patched version of
Tahoe-LAFS. During Apps month we will be helping them with their ongoing work to
add native support for I2P and Tor, so that I2P users can benefit from all of
the improvements upstream.
{%- endtrans %}

{% trans -%}
There are several other projects that we will be talking with about their plans
for I2P integration, and helping with design. Stay tuned!
{%- endtrans %}

.. _`Tahoe-LAFS`: https://tahoe-lafs.org
.. _{% trans %}`largest public grids`{% endtrans %}: https://tahoe-lafs.org/pipermail/tahoe-lafs-weekly-news/2015-December/000056.html


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
