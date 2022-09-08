====================================================================
{% trans -%}Windows Easy-Install Bundle 1.9.5 Release{%- endtrans %}
====================================================================

.. meta::
   :author: idk
   :date: 2022-09-07
   :category: release
   :excerpt: {% trans %}Windows Easy-Install Bundle 1.9.5{% endtrans %}

{% trans -%}
Bug Fixing release for Windows 11 users
{%- endtrans %}
=======================================

{% trans -%}
This point release includes a bug fix in the included I2P router, which resolves
a highly obscure bug where the context clock is out of sync with the clock in
use by the File System, resulting in a router which is unable to read the current
state of it's own NetDB. Although this bug has only been observed on Windows 11
so far, it is highly recommended that all users update to the new build.
{%- endtrans %}

{% trans -%}
This release also features faster startup and times improved stability in the profile
manager.
{%- endtrans %}
