{% trans -%}
=================================================================
I2P 2.4.0 Release with Congestion and NetDB Security improvements
=================================================================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2023-12-18
    :category: release
    :excerpt: {% trans %}{% endtrans %}

{% trans -%}
Update details
{%- endtrans %}
============================================

{% trans -%}
This release, I2P 2.4.0, continues our effort to improve the security and stability of the I2P network.
It contains significant improvements to the Network Database, an essential structure within the I2P network used for disovering your peers.
{%- endtrans %}

{% trans -%}
The congestion handling changes will improve network stability by giving routers the ability to relieve congested peers by avoiding them.
This will help the network limit the effect of tunnel spam.
It will also help the network heal during and after DDoS attacks.
{%- endtrans %}

{% trans -%}
The NetDb changes also help secure individual routers and the applications that use them. 
Routers can now defend against attackers by separating the NetDB into multiple "Sub-DB's" which we use to prevent information leaks between applications and the router.
This also improves the information available to Java routers about their NetDB activity and simplifies our support for multihoming applications.
{%- endtrans %}

{% trans -%}
Also included are a number of bug fixes and enhancements across the I2PSnark and SusiMail applications.
{%- endtrans %}

{% trans -%}
As usual, we recommend that you update to this release.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}


**{% trans %}RELEASE DETAILS{% endtrans %}**

**{% trans %}Changes{% endtrans %}**

- {% trans %}i2psnark: Uncomment and fix local torrent file picker{% endtrans %}
- {% trans %}NetDB: Lookup handler/throttler fixes{% endtrans %}
- {% trans %}Router: Restructure netDb to isolate data recieved as a client from data recieved as a router{% endtrans %}
- {% trans %}Router: Implement handling and penalties for congestion caps{% endtrans %}
- {% trans %}Router: Temporarily ban routers publishing in the future{% endtrans %}
- {% trans %}Transports: Disable SSU 1{% endtrans %}

**{% trans %}Bug Fixes{% endtrans %}**

- {% trans %}Addressbook: Workaround for i2p-projekt.i2p etag bug (Gitlab #454){% endtrans %}
- {% trans %}Console: Clear out "proxy must be running" status after success{% endtrans %}
- {% trans %}Console: Don't lose tabs in log messages{% endtrans %}
- {% trans %}Console: Fix sidebar not immediately showing results of manual update check{% endtrans %}
- {% trans %}Console: Fix visibility of radio/checkboxes (light theme){% endtrans %}
- {% trans %}Console: Prevent overflow of sidebar status{% endtrans %}
- {% trans %}Debian: Change JRE dependency order (Gitlab #443, Debian #1024461){% endtrans %}
- {% trans %}i2psnark: Increase comment bucket size to reduce duplicates{% endtrans %}
- {% trans %}i2psnark: Prevent start-all from within search results erroring (Gitlab #445){% endtrans %}
- {% trans %}i2ptunnel: Exempt tunnel name from XSS filter (Gitlab #467){% endtrans %}
- {% trans %}i2ptunnel: Fix gzip footer check in GunzipOutputStream (Gitlab #458){% endtrans %}
- {% trans %}i2ptunnel: Remove nonstandard Proxy-Connection headers (Gitlab #452){% endtrans %}
- {% trans %}NTCP2: Fix updating address on transition to firewalled (Gitlab #435){% endtrans %}
- {% trans %}SAM: Fix accept after soft restart (Gitlab #399){% endtrans %}
- {% trans %}SAM: Reset incoming socket if no subsession is matched (Gitlab #456){% endtrans %}
- {% trans %}SSU2: Fix uncaught IAE caused by itags with zero values (Gitlab #415){% endtrans %}
- {% trans %}SSU2: Prevent rare IAE in peer test timer (Gitlab #433){% endtrans %}
- {% trans %}Susimail: Dark theme fixes{% endtrans %}
- {% trans %}Susimail: Fix binary content-encoding{% endtrans %}
- {% trans %}Susimail: Fix incorrect "previous" icons{% endtrans %}
- {% trans %}Susimail: Fix setting encoding for attachments{% endtrans %}
- {% trans %}Susimail: Flush output to fix truncated mails{% endtrans %}
- {% trans %}Sybil: Don't ban NAT64 addresses{% endtrans %}
- {% trans %}Transport: Fix NPE during soft restart (Gitlab #437){% endtrans %}
- {% trans %}UPnP: Fix handing of multiple IGDs{% endtrans %}
- {% trans %}UPnP: Fix missing port in Host header causing failures on libupnp-based devices{% endtrans %}

**{% trans %}Other{% endtrans %}**

- API 0.9.61
- {% trans %}Translation updates{% endtrans %}

`{% trans %}Full list of fixed bugs{% endtrans %}`__

__ http://{{ i2pconv('git.idk.i2p') }}/i2p-hackers/i2p.i2p/-/issues?scope=all&state=closed&milestone_title=2.4.0


**{% trans %}SHA256 Checksums:{% endtrans %}**

::

      d08db62457d4106ca0e36df3487bdf6731cbb81045b824a003cde38c7e1dfa27  i2pinstall_2.4.0_windows.exe
      ef5f3d0629fec292aae15d027f1ecb3cc7f2432a99a5f7738803b453eaad9cad  i2pinstall_2.4.0.jar
      30ef8afcad0fffafd94d30ac307f86b5a6b318e2c1f44a023005841a1fcd077c  i2psource_2.4.0.tar.bz2
      97be217bf07319a50b6496f932700c3f3c0cceeaf1e0643260d38c9e6e139b53  i2pupdate_2.4.0.zip
      8f4a17a8cbadb2eabeb527a36389fd266a4bbcfd9d634fa4f20281f48c486e11  i2pupdate.su3

