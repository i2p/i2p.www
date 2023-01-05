=================================================
{% trans -%}How to Switch to the StormyCloud Outproxy Service{%- endtrans %}
=================================================

.. meta::
   :author: idk
   :date: 2022-08-04
   :category: general
   :excerpt: {% trans %}How to Switch to the StormyCloud Outproxy Service{% endtrans %}

{% trans -%}
How to Switch to the StormyCloud Outproxy Service
{%- endtrans %}
=================================================

**{% trans %}A New, Professional Outproxy{% endtrans %}**

{% trans -%}
For years, I2P has been served by a single default outproxy, `false.i2p`
whose reliability has been degrading. Although several competitors
have emerged to take up some of the slack, they are mostly unable to
volunteer to serve the clients of an entire I2P implementation by
default. However, StormyCloud, a professional, non-profit organization
which runs Tor exit nodes, has started a new, professional outproxy
service which has been tested by members of the I2P community and which
will become the new default outproxy in the upcoming release.
{%- endtrans %}

**{% trans %}Who are StormyCloud{% endtrans %}**

In their own words, StormyCloud is:

{% trans -%}
  Mission of StormyCloud Inc
  To defend Internet access as a universal human right. By doing so, the group protects users’ electronic privacy and builds community by fostering unrestricted access to information and thus the free exchange of ideas across borders. This is essential because the Internet is the most powerful tool available for making a positive difference in the world.
{%- endtrans %}

{% trans -%}
  Hardware
  We own all of our hardware and currently colocate at a Tier 4 data center. As of now have a 10GBps uplink with the option to upgrade to 40GBps without the need for much change. We have our own ASN and IP space (IPv4 & IPv6).
{%- endtrans %}

{% trans -%}
To learn more about StormyCloud visit their `web site
<https://www.stormycloud.org/>`_.
{%- endtrans %}

{% trans -%}
Or, visit them on `I2P
<http://stormycloud.i2p/>`_.
{%- endtrans %}

**{% trans %}Switching to the StormyCloud Outproxy on I2P{% endtrans %}**

{% trans -%}
To switch to the StormyCloud outproxy *today* you can visit `the Hidden Services Manager
<http://127.0.0.1:7657/i2ptunnel/edit?tunnel=0>`_. Once you're there, you should change
the value of **Outproxies** and **SSL Outproxies** to `exit.stormycloud.i2p`. Once you
have done this, scroll down to the bottom of the page and click on the "Save" button.
{%- endtrans %}

.. class:: screenshot
.. image:: /_static/images/stormycloudscreenshot.png

**{% trans %}Thanks to StormyCloud{% endtrans %}**

{% trans -%}
We would like to thank StormyCloud for volunteering to provide high-quality outproxy
services to the I2P network.
{%- endtrans %}
