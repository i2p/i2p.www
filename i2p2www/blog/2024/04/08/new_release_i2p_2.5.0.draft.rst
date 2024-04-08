{% trans -%}
=====================
New Release I2P 2.5.0
=====================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2024-04-08
    :category: release
    :excerpt: {% trans %}{% endtrans %}

{% trans -%}
This release, I2P 2.5.0, provides more user-facing improvements than the 2.4.0 release, which was focused on implementing the NetDB isolation strategy.
{%- endtrans %}

{% trans -%}
New features have been added to I2PSnark like the ability to search through torrents.
Bugs have been fixed to improve compatibility with other I2P torrent clients like BiglyBT and qBittorrent.
We would like to thank all of the developers who have worked with libtorrent and qBittorrent to enable and improve their I2P support.
New features have also been added to SusiMail including support for Markdown formatting in emails and the ability to drag-and-drop attachments into emails.
Tunnels created with the Hidden Services manager now support "Keepalive" which improves performance and compatibility with web technologies, enabling more sophisticated I2P sites.{%- endtrans %}
{%- endtrans %}

{% trans -%}
During this release we also made several tweaks to the NetDB to improve it's resilience to spam and to improve the router's ability to reject suspicious messages.
This was part of an effort to "audit" the implementation of "Sub-DB isolation" defenses from the 2.4.0 release.
This investigation uncovered one minor isolation-piercing event which we repaired.
This issue was discovered and fixed internally by the I2P team.
{%- endtrans %}

{% trans -%}
  During this release several improvements were made to the process of releasing our downstream distributions for Android and Windows.
This should result in improved delivery and availability for these downstream products.
{%- endtrans %}

{% trans -%}
As usual, we recommend that you update to this release.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}
