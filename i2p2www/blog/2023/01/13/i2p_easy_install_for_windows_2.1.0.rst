=============================================================
{% trans -%}Windows Easy-Install 2.1.0 Release{%- endtrans %}
=============================================================

.. meta::
   :author: idk
   :date: 2023-01-13
   :category: release
   :excerpt: {% trans %}Windows Easy-Install Bundle 2.1.0 released to improve stability, performance.{% endtrans %}

{% trans -%}
Update details
{%- endtrans %}
============================================

{% trans -%}
The I2P Easy-Install bundle for Windows version 2.1.0 has been released.
As usual, this release includes an updated version of the I2P Router.
This release of I2P provides improved strategies for dealing with network congestion.
These should improve performance, connectivity, and secure the long-term health of the I2P network.
{%- endtrans %}

{% trans -%}
This release features mostly under-the-hood improvements to the browser profile launcher.
Compatibility with Tor Browser Bundle has been improved by enabling TBB configuration through environment variables.
The Firefox profile has been updated, an the base versions of the extensions have been updated.
Improvements have been made throughout the codebase and the deployment process.
{%- endtrans %}

{% trans -%}
Unfortunately, this release is still an unsigned .exe installer.
Please verify the checksum of the installer before using it.
The updates, on the other hand are signed by my I2P signing keys and therefore safe.
{%- endtrans %}

{% trans -%}
This release was compiled with OpenJDK 19.
It uses i2p.plugins.firefox version 1.0.7 as a library for launching the browser.
It uses i2p.i2p version 2.1.0 as an I2P router, and to provide applications.
As always it is recommended that you update to the latest version of the I2P router at your earliest convenient opportunity.
{%- endtrans %}