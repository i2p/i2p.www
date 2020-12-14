======================================================
{% trans -%}Hello Git, Goodbye Monotone{%- endtrans %}
======================================================

.. meta::
   :author: idk
   :date: 2020-12-10
   :category: git
   :excerpt: {% trans %}Hello git, goodbye mtn{% endtrans %}

{% trans -%}
Hello Git, Goodbye Monotone
{%- endtrans %}
===========================

{% trans -%}
The I2P Git Migration is nearly concluded
{%- endtrans %}
-----------------------------------------

{% trans -%}
For over a decade, I2P has relied on the venerable Monotone service to support
its version control needs, but during the past few years, most of the world has
moved on to the now-universal Git version control system. In that same
time, the I2P Network has become faster and more reliable, and accessible
workarounds to Git's non-resumability have been developed.
{%- endtrans %}

{% trans -%}
Today marks a significant occasion for I2P, as we switched off the old mtn
i2p.i2p branch, and moved the development of the core Java I2P libraries from
Monotone to Git officially.
{%- endtrans %}

{% trans -%}
While our use of mtn has been questioned in the past, and it's not always been a
popular choice, I'd like to take this moment, as perhaps the very last project to use
Monotone to thank the Monotone developers, current and former, wherever they are,
for the software they created.
{%- endtrans %}

.. image:: /_static/images/GoodbyeMTN.png

{% trans -%}
GPG Signing
{%- endtrans %}
-----------

{% trans -%}
Checkins to the I2P Project repositories require you to configure GPG signing for
your git commits, including Merge Requests and Pull Requests. Please configure
your git client for GPG signing before you fork i2p.i2p and check anything in.
{%- endtrans %}

{% trans -%}
Official Repositories and Gitlab/Github Syncing
{%- endtrans %}
-----------------------------------------------

{% trans -%}
The official repository is the one hosted at https://i2pgit.org/i2p-hackers/i2p.i2p
and at https://git.idk.i2p/i2p-hackers/i2p.i2p, but there is a "Mirror" available
at Github at https://github.com/i2p/i2p.i2p.
{%- endtrans %}

{% trans -%}
Now that we're on git, we can synchronize repositories from our own self-hosted Gitlab
instance, to Github, and back again. This means that it is possible to create and submit
a merge request on Gitlab and when it is merged, the result will be synced with Github,
and a Pull Request on Github, when merged, will appear on Gitlab.
{%- endtrans %}

{% trans -%}
This means that it's possible to submit code to us through our Gitlab instance or through
Github depending on what you prefer, however, more of the I2P developers are regularly
monitoring Gitlab than Github. MR's to Gitlab are more likely to be merged sooner
than PR's to Github.
{%- endtrans %}

{% trans -%}
Thanks
{%- endtrans %}
------

{% trans -%}
Congratulations and thanks to everyone who helped in the git migration, especially
zzz, eche|on, nextloop, and our site mirror operators! While some of us will miss
Monotone, it has become a barrier for new and existing participants in I2P development
and we're excited to join the world of developers using Git to manage their distributed
projects.
{%- endtrans %}
