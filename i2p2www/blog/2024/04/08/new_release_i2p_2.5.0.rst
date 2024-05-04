{% trans -%}
=====================
New Release I2P 2.5.0
=====================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2024-04-08
    :category: release
    :excerpt: {% trans %}I2P 2.5.0 release{% endtrans %}

{% trans -%}
This release, I2P 2.5.0, provides more user-facing improvements than the 2.4.0 release, which was focused on implementing the NetDB isolation strategy.
{%- endtrans %}

{% trans -%}
New features have been added to I2PSnark like the ability to search through torrents.
Bugs have been fixed to improve compatibility with other I2P torrent clients like BiglyBT and qBittorrent.
We would like to thank all of the developers who have worked with libtorrent and qBittorrent to enable and improve their I2P support.
New features have also been added to SusiMail including support for Markdown formatting in emails and the ability to drag-and-drop attachments into emails.
Tunnels created with the Hidden Services manager now support "Keepalive" which improves performance and compatibility with web technologies, enabling more sophisticated I2P sites.
{%- endtrans %}

{% trans -%}
During this release we also made several tweaks to the NetDB to improve its resilience to spam and to improve the router's ability to reject suspicious messages.
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

**{% trans %}RELEASE DETAILS{% endtrans %}**

**{% trans %}Changes{% endtrans %}**

- {% trans %}I2PTunnel: Implement support for Keepalive/Server-side Persistence{% endtrans %}
- {% trans %}Susimail: Add markdown support for formatted plain-text content{% endtrans %}
- {% trans %}Susimail: Add HTML Email support{% endtrans %}
- {% trans %}I2PSnark: Add search capability{% endtrans %}
- {% trans %}I2PSnark: Preserve private=0 in torrent files{% endtrans %}
- {% trans %}Data: Store compressed RI and LS{% endtrans %}

**{% trans %}Bug Fixes{% endtrans %}**

- {% trans %}Susimail: Fix handling of forwarded mail with attachments{% endtrans %}
- {% trans %}Susimail: Fix handling of forwarded mail with unspecified encoding{% endtrans %}
- {% trans %}Susimail: Fix forwarding of HTML-only email{% endtrans %}
- {% trans %}Susimail: Bugfixes in presentation of encoded attachmments, mail body{% endtrans %}
- {% trans %}I2PSnark: Handle data directory changes{% endtrans %}
- {% trans %}SSU2: Cancel peer test if Charlie does not have B cap{% endtrans %}
- {% trans %}SSU2: Treat peer test result as unknown if Charlie is unreachable{% endtrans %}
- {% trans %}Router: Filter additional garlic-wrapped messages{% endtrans %}
- {% trans %}I2CP: Prevent loopback messages to same session{% endtrans %}
- {% trans %}NetDB: Resolve Exploratory/Router isolation-piercing event{% endtrans %}

**{% trans %}Other{% endtrans %}**

- API 0.9.62
- {% trans %}Translation updates{% endtrans %}

`{% trans %}Full list of fixed bugs{% endtrans %}`__

__ http://{{ i2pconv('git.idk.i2p') }}/i2p-hackers/i2p.i2p/-/issues?scope=all&state=closed&milestone_title=2.5.0


**{% trans %}SHA256 Checksums:{% endtrans %}**

::
      
    i2pinstall_2.5.0-0.jar - 61d3720accc6935f255611680b08ba1a414d32daa00d052017630c2424c30069
    i2pinstall_2.5.0-0_windows.exe - a0d84c519f3c35874a9f661b9f40220e5a1d29716166c682e2bd1ee15ff83f33
    i2pinstall_2.5.0.jar - 61d3720accc6935f255611680b08ba1a414d32daa00d052017630c2424c30069
    i2pinstall_2.5.0.jar.sig - c8a6d79909d06ac6bca23d8e890765c6e6ed21a535f7529e0708797fdaf9fc1b
    i2pinstall_2.5.0_windows.exe - 762b9d672dfff0baccd46f970deb5a2621358d1e2dfc0dd85a78aecda3623ac6
    i2pinstall_2.5.0_windows.exe.sig - 103a1bd155110514fe9ae075243cc66e2fef866353165b2c806248e15925e957
    i2psource_2.5.0.tar.bz2 - 6bda9aff7daa468cbf6ddf141c670140de4d1db145329645a90c22c1e5c7bc01
    i2psource_2.5.0.tar.bz2.sig - a1d0ea6f2051ed0643bc2c0207a2cf594f2b2bc4303ac49cd6a43baaf0558f62
    i2pupdate-2.5.0.su3 - 7bcfc3df3a14a0b9313b9a0fe20e56db75267d5afcfd8a3203fbfcfac46deae4
    i2pupdate-2.5.0.su3.torrent - a7dd76348bf404d84a67bda8b009d54cc08748c036988dbe78bff6ca6928950c
    i2pupdate.su3 - 7bcfc3df3a14a0b9313b9a0fe20e56db75267d5afcfd8a3203fbfcfac46deae4
    i2pupdate.zip - d0a4cfe6cb587e0ffabcfb6012682f400a38ee87f23fa90f8a18f25e77b742d8
    i2pupdate_2.5.0.zip - d0a4cfe6cb587e0ffabcfb6012682f400a38ee87f23fa90f8a18f25e77b742d8
    i2pupdate_2.5.0.zip.sig - 411eb4ca31e2984dae4c943136411e8ee85435f59749391edefec07509cfd5af 

