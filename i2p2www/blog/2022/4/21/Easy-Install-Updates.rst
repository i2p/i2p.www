===========================================
{% trans -%}Jpackage Update for Java CVE-2022-21449{%- endtrans %}
===========================================

.. meta::
   :author: idk
   :date: 2022-04-21
   :category: release
   :excerpt: {% trans %}Jpackage bundles released with fixes for Java CVE-2022-21449{% endtrans %}

{% trans -%}
Update details
{%- endtrans %}
============================================

{% trans -%}
New I2P Easy-Install bundles have been generated using the latest release of the
Java Virtual Machine which contains a fix for CVE-2022-21449
"Psychic Signatures." It is recommended that users of the easy-install bundles
update as soon as possible. Current OSX users will recieve updates automatically,
Windows users should download the installer from our downloads page and run the
installer normally.
{%- endtrans %}

{% trans -%}
The I2P router on Linux uses the Java Virtual Machine configured by the host
system. Users on those platforms should downgrade to a stable Java version below
Java 14 in order to mitigate the vulnerability until updates are released by
the package maintainers. Other users using an external JVM should update the JVM
to a fixed version as soon as possible.
{%- endtrans %}
