==================================
{% trans -%}How to Enable SSU2 on I2P and i2pd{%- endtrans %}
==================================

.. meta::
   :author: idk
   :date: 2022-08-03
   :category: ssu2
   :excerpt: {% trans %}How to enable SSU2 on I2P and i2pd{% endtrans %}

{% trans -%}
Help out with SSU2 development and testing
{%- endtrans %}
============================================

{% trans -%}
I2P and i2pd developers are rapidly implementing the successor to the
venerable SSU transport protocol, SSU2. SSU2 featues many improvements on
SSU for censorship resistance, resistance to identification and blocking,
performance, and in many other areas. Users who are comfortable testing
the new protocol can enable it by following these procedures for I2P and
i2pd respectively.
{%- endtrans %}

*{% trans %}Warning: After enabling SSU2, you will publish a routerInfo which
informs other routers that you can speak SSU2. This is still a small
fraction of the network and identifies you as an early-adopter of
SSU2.*{% endtrans %}*

**{% trans %}Enabling SSU2 on I2P{% endtrans %}**

{% trans -%}
In order to enable SSU2 on Java I2P, you will need to locate your `router.config`
file. If you have enabled "Advanced Mode" in your I2P installation already, then
you can edit the `router.config` file from http://127.0.0.1:7657/configadvanced.
{%- endtrans %}

{% trans -%}
If you have not enabled advanced configuration, you'll need to edit the `router.config`
file in a text editor. That file is usually in `/var/lib/i2p/i2p-config/router.config`
on Debian, `$HOME/i2p/router.config` on other Linux,
`$HOME/Library/Application Support/i2p/router.config` on OSX,` and in
`%LOCALAPPDATA%\I2P\router.config` on Windows. Open that file in a text editor(like
`notepad.exe`` on Windows) and add the following line to the end of the file:
{%- endtrans %}

`i2np.ssu2.enable=true`

**{% trans %}Enabling SSU2 on i2pd{% endtrans %}**

{% trans -%}
In order to enable SSU2 on i2pd, you will need to locate your `i2pd.conf` file
and edit that. The `i2pd.conf` file is usually in `/etc/i2pd/i2pd.conf` on Debian,
`$HOME/i2pd/i2pd.conf` on other Linux, on Windows is: `%APPDATA%\i2pd\i2pd.conf`,
and on OSX it is: `$HOME/Library/Application Support/i2pd/i2pd.conf`. Open that,
and add the following lines to the end of the file:
{%- endtrans %}

`[SSU2]`

`enabled = true`

**{% trans %}Thanks to all Testers{% endtrans %}**

{% trans -%}
We'd like to take this moment to thank all of the testers who have helped us so
far and who will continue to help us in the future as we test SSU2 and continue
to develop the I2P network.
{%- endtrans %}