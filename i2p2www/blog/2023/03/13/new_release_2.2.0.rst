{% trans -%}
=================
I2P Release 2.2.0
=================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2023-03-13
    :category: release
    :excerpt: {% trans %}DDoS Mitigations, New Release Maintainer{% endtrans %}

{% trans -%}
We have elected to move forward the 2.2.0 release date, which will be occurring today, March 13, 2023.
This release includes a changes across the NetDB, Floodfill, and Peer-Selection components which improve the ability of the router to survive DDOS attacks.
The attacks are likely to continue, but the improvements to these systems will help to mitigate the risk of DDOS attacks by helping the router identify and de-prioritize routers that appear malicious.
{%- endtrans %}

{% trans -%}
This release also adds replay protection to the Streaming subsystem, which prevents an attacker who can capture an encrypted packet from being able to re-use it by sending it to unintended recipients.
This is a backward-compatible change, so older routers will still be able to use the streaming capabilities of newer routers.
This issue was discovered and fixed internally, by the I2P development team, and is not related to the DDOS attacks.
We have never encountered a replayed streaming packet in the wild and do not believe a streaming replay attack has ever taken place against the I2P network at this time.
{%- endtrans %}

{% trans -%}
As you may have noticed, these release notes and the release itself have been signed by idk, and not zzz.
zzz has chosen to step away from the project and his responsibilities are being taken on by other team members.
As such, the project is working on replacing the network statistics infrastructure and moving the development forum to i2pforum.i2p.
We thank zzz for providing these services for such a long time.
{%- endtrans %}

{% trans -%}
As usual, we recommend that you update to this release.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}



**DETAILS**

*Changes*

- {% trans %}i2psnark: New search feature{% endtrans %}
- {% trans %}i2psnark: New max files per torrent config{% endtrans %}
- {% trans %}NetDB: Expiration improvements{% endtrans %}
- {% trans %}NetDB: More restrictions on lookups and exploration{% endtrans %}
- {% trans %}NetDB: Store handling improvements{% endtrans %}
- {% trans %}NTCP2: Banning improvements{% endtrans %}
- {% trans %}Profiles: Adjust capacity estimates{% endtrans %}
- {% trans %}Profiles: Expiration improvements{% endtrans %}
- {% trans %}Router: Initial support for congestion caps (proposal 162){% endtrans %}
- {% trans %}Transports: Add inbound connection limiting{% endtrans %}
- {% trans %}Tunnels: Refactor and improve peer selection{% endtrans %}
- {% trans %}Tunnels: Improve handling of "probabalistic" rejections{% endtrans %}
- {% trans %}Tunnels: Reduce usage of unreachable and floodfill routers{% endtrans %}


*Bug Fixes*

- {% trans %}Docker: Fix graphs not displaying{% endtrans %}
- {% trans %}i2psnark: Fix torrents with '#' in the name{% endtrans %}
- {% trans %}i2psnark standalone: Fix running from outside directory{% endtrans %}
- {% trans %}i2psnark standalone: Remove "Start I2P" menu item from systray{% endtrans %}
- {% trans %}i2ptunnel: Fix typo in HTTPS outproxy hostname{% endtrans %}
- {% trans %}i2ptunnel: Interrupt tunnel build if stop button clicked{% endtrans %}
- {% trans %}i2ptunnel: Return error message to IRC, HTTP, and SOCKS clients on failure to build tunnels{% endtrans %}
- {% trans %}NTCP2: Ensure an IPv6 address is published when firewalled and IPv4 is not{% endtrans %}
- {% trans %}Ratchet: Don't bundle wrong leaseset with ack{% endtrans %}
- {% trans %}Router: Fixes for symmetric NAT errors on 'full cone' NAT{% endtrans %}
- {% trans %}SAM: Interrupt tunnel build if client times out{% endtrans %}
- {% trans %}SSU2: Fix rare peer test NPE{% endtrans %}
- {% trans %}Sybil: Don't blame i2pd publishing ::1{% endtrans %}
- {% trans %}Sybil: Memory usage and priority reduction{% endtrans %}
- {% trans %}Transports: More IP checks{% endtrans %}


*Other*

- {% trans %}Blocklist efficiency improvements{% endtrans %}
- {% trans %}Bundles: Identify Win and Mac bundles in version info{% endtrans %}
- {% trans %}Console: Identify service installs, revision, and build time in version info{% endtrans %}
- {% trans %}Console: NetDB search form and tunnels page improvements (advanced only){% endtrans %}
- {% trans %}Router: Reduce stats memory usage{% endtrans %}
- {% trans %}Tunnels: Reduce "grace period"{% endtrans %}
- {% trans %}Translation updates{% endtrans %}



Full list of fixed bugs: http://git.idk.i2p/i2p-hackers/i2p.i2p/-/issues?scope=all&state=closed&milestone_title=2.2.0
