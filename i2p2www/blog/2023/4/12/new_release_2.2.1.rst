{% trans -%}
=================
I2P Release 2.2.1
=================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2023-04-12
    :category: release
    :excerpt: {% trans %}Packaging Fixes{% endtrans %}

{% trans -%}
After the I2P 2.2.0 release, which was moved forward to accelerate mitigations for the DDOS attacks, we learned about a few developing issues which made it necessary to build and release new packages.
This release fixes an issue within Ubuntu Lunar and Debian Sid where the router console was inaccessible using an updated version of the jakarta package.
Docker packages were not reading arguments correctly, resulting in inaccessible configuration files.
This issue has also been resolved.
The docker container is now also compatible with Podman.
{%- endtrans %}

{% trans -%}
This release syncs translations with transifex and updates the GeoIP database.
{%- endtrans %}

{% trans -%}
As usual, we recommend that you update to this release.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}

**DETAILS**

*Changes*

- {% trans %}Fix missing Java options in docker/rootfs/startapp.sh{% endtrans %}
- {% trans %}Detect when running in Podman instead of regular Docker{% endtrans %}
- {% trans %}Update Tor Browser User-Agent String{% endtrans %}
- {% trans %}Update local GeoIP database{% endtrans %}
- {% trans %}Remove invalid signing keys from old installs{% endtrans %}
- {% trans %}Update Tomcat version in Ubuntu Lunar and Debian Sid{% endtrans %}

Full list of fixed bugs: http://git.idk.i2p/i2p-hackers/i2p.i2p/-/issues?scope=all&state=closed&milestone_title=2.2.1
