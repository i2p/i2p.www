{% trans -%}
=======================================
Easy-Install for Windows 2.3.0 Released
=======================================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2023-07-10
    :category: release
    :excerpt: {% trans %}Easy-Install for Windows 2.3.0 Released{% endtrans %}


{% trans -%}
The I2P Easy-Install bundle for Windows version 2.3.0 has now been released.
As usual, this release includes an updated version of the I2P router.
This extends to security issues which affect people hosting services on the network.
{%- endtrans %}

{% trans -%}
This will be the last release of the Easy-Install bundle which will be incompatible with the I2P Desktop GUI.
It has been updated to include new versions of all included webextensions.
A longstanding bug in I2P in Private Browsing which makes it incompatible with custom themes has been fixed.
Users are still advised to *not* install custom themes.
Snark tabs are not automatically pinned to the top of the tab order in Firefox.
Except for using alternate cookieStores, Snark tabs now behave as normal browser tabs.
{%- endtrans %}

{% trans -%}
**Unfortunately, this release is still an unsigned `.exe` installer.**
Please verify the checksum of the installer before using it.
**The updates, on the other hand** are signed by my I2P signing keys and therefore safe.
{%- endtrans %}

{% trans -%}
This release was compiled with OpenJDK 20.
It uses i2p.plugins.firefox version 1.1.0 as a library for launching the browser.
It uses i2p.i2p version 2.3.0 as an I2P router, and to provide applications.
As always it is recommended that you update to the latest version of the I2P router at your earliest convenient opportunity.
{%- endtrans %}

- `Easy-Install Bundle Source <http://git.idk.i2p/i2p-hackers/i2p.firefox/-/tree/i2p-firefox-2.3.0>`_
- `Router Source <http://git.idk.i2p/i2p-hackers/i2p.i2p/-/tree/i2p-2.3.0>`_
- `Profile Manager Source <http://git.idk.i2p/i2p-hackers/i2p.plugins.firefox/-/tree/1.1.0>`_


