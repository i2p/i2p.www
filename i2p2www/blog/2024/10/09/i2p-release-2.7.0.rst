{% trans -%}
==================
I2P 2.7.0 Released
==================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2024-10-09
    :category: release
    :excerpt: {% trans %}I2P 2.7.0 Released{% endtrans %}

{% trans -%}
This release, I2P 2.7.0, continues our work by fixing bugs, improving performance, and adding features.
{%- endtrans %}
{% trans -%}
Access to information from the console and applications has been improved.
Issues have been fixed in I2PSnark and SusiMail search.
The netDB search embedded into the router console now operates in a more intuitive and useful way.
Minor improvements have been made to diagnostic displays in advanced mode.
{%- endtrans %}
{% trans -%}
Bugs have also been fixed to improve compatibility within the network.
An issue with publishing leaseSets was solved which improves reliability major hidden services.
I2PSnark no longer changes the infohash when a user changes only the trackers on an existing torrent.
This prevents torrents from being unnecessarily disrupted by these changes.
We welcomed this contribution from a new contributor.
A conflict in the handling of a streaming library option was resolved to improve compatibility with other I2P implementations.
{%- endtrans %}
{% trans -%}
As usual, we recommend that you update to this release.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}