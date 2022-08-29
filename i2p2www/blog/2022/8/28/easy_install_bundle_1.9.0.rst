====================================================================
{% trans -%}Windows Easy-Install Bundle 1.9.0 Release{%- endtrans %}
====================================================================

.. meta::
   :author: idk
   :date: 2022-08-28
   :category: release
   :excerpt: {% trans %}Windows Easy-Install Bundle 1.9.0 - Major Stability/Compatibility Improvements{% endtrans %}

{% trans -%}
This update includes the new 1.9.0 router and major quality-of-life improvements for bundle users
{%- endtrans %}
=================================================================================================

{% trans -%}
This release includes the new I2P 1.9.0 router and is based on Java 18.02.1.
{%- endtrans %}

{% trans -%}
The old batch scripts have been phased out in favor of a more flexible and stable solution in the jpackage itself.
This should fix all bugs related to path-finding and path-quoting which were present in the batch scripts. After
you upgrade, the batch scripts can be safely deleted. They will be removed by the installer in the next update.
{%- endtrans %}

{% trans -%}
A sub-project for managing browsing tools has been started: i2p.plugins.firefox which has extensive capabilities
for configuring I2P browsers automatically and stably on many platforms. This was used to replace the batch
scripts but also functions as a cross-platform I2P Browser management tool. Contributions are welcome
here: http://git.idk.i2p/idk/i2p.plugins.firefox at the source repository.
{%- endtrans %}

{% trans -%}
This release improves compatibility with externally-running I2P routers such as those provided by the IzPack
installer and by third-party router implementations such as i2pd. By improving external router discovery it
requires less of a system's resources, improves start-up time, and prevents resource conflicts from occurring.
{%- endtrans %}

{% trans -%}
Besides that, the profile has been updated to the latest version of the Arkenfox profile. I2P in Private
Browsing and NoScript have both been updated. The profile has been restructured in order to allow for
evaluating different configurations for different threat models.
{%- endtrans %}
