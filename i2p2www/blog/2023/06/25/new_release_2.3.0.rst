{% trans -%}
=================
I2P Release 2.3.0
=================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2023-06-25
    :category: release
    :excerpt: {% trans %}I2P 2.3.0: Security Fixes, Tweakable Blocklists{% endtrans %}

{% trans -%}
This release contains fixes for CVE-2023-36325.
CVE-2023-36325 is a context-confusion bug which occurred in the bloom filter.
An attacker crafts an I2NP message containing a unique messageID, and sends that messageID to a client.
The message, after passing through the bloom filter, is not allowed to be re-used in a second message.
The attacker then sends the same message directly to the router.
The router passes the message to the bloom filter, and is dropped.
This leaks the information that the messageID has been seen before, giving the attacker a strong reason to believe that the router is hosting the client.
This has been fixed by separting the bloom filter's functionality into different contexts based on whether a message came down a client tunnel, an exploratory tunnel, was sent to the router directly.
Under normal circumstances, this attack takes several days to perform successfully and may be confounded by several factors such as routers restarting during the attack phase and sensitivity to false-positives.
Users of Java I2P are recommended to update immediately to avoid the attack.
{%- endtrans %}

{% trans -%}
In the course of fixing this context confusion bug, we have revised some of our strategies to code defensively, against these types of leaks.
This includes tweaks to the netDb, the rate-limiting mechanisms, and the behavior of floodfill routers.
{%- endtrans %}

{% trans -%}
This release adds not_bob as a second default hosts provider, and adds `notbob.i2p <http://notbob.i2p>`_ and `ramble.i2p <http://ramble.i2p>`_ to the console homepage.
{%- endtrans %}

{% trans -%}
This release also contains a tweakable blocklist.
Blocklisting is semi-permanent, each blocked IP address is normally blocked until the router is restarted.
Users who observe explosive blocklist growth during sybil attacks may opt-in to shorter timeouts by configuring the blocklist to expire entries at an interval.
This feature is off-by-default and is only recommended for advanced users at this time.
{%- endtrans %}

{% trans -%}
This release also includes an API for plugins to modify with the Desktop GUI(DTG).
It is now possible to add menu items to the system tray, enabling more intuitive launching of plugins which use native application interfaces.
{%- endtrans %}

{% trans -%}
As usual, we recommend that you update to this release.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}

**DETAILS**

*Changes*

- {% trans %}netDb: Throttle bursts of netDB lookups{% endtrans %}
- {% trans %}Sybil/Blocklist: Allow users to override blocklist expiration with an interval{% endtrans %}
- {% trans %}DTG: Provide an API for extending DTG with a plugin{% endtrans %}
- {% trans %}Addressbook: add notbob's main addressbook to the default subscriptions.{% endtrans %}
- {% trans %}Console: Add Ramble and notbob to console homepage{% endtrans %}

*Bug Fixes*

- {% trans %}Fix replay attack: CVE-2023-36325{% endtrans %}
- {% trans %}Implement handling of multihomed routers in the netDb{% endtrans %}
- {% trans %}Fully copy new leaseSets when a leaseSet recievedAsPublished overwrites a leaseSet recievedAsReply{% endtrans %}

Full list of fixed bugs: http://git.idk.i2p/i2p-hackers/i2p.i2p/-/issues?scope=all&state=closed&milestone_title=2.3.0
