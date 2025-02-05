{% trans -%}
==================
I2P 2.8.0 Released
==================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2025-02-04
    :category: release
    :excerpt: {% trans %}I2P 2.8.0 Released{% endtrans %}

{% trans -%}
This release improves I2P by fixing bugs, removing unused code, and improving network stability.
{%- endtrans %}

{% trans -%}
We have improved handling of congested routers in the network.
Issues in UPnP and NAT traversal were addressed to improve connectivity and error reporting.
We now have a more aggressive strategy for leaseset removal from the NetDb to improve router performance and mitigate overload.
Other changes were implemented to reduce the observability of events like a router rebooting or shutting down.
{%- endtrans %}

{% trans -%}
As usual, we recommend that you update to this release.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}

`{% trans %}Full list of fixed bugs{% endtrans %}`__

__ http://{{ i2pconv('git.idk.i2p') }}/i2p-hackers/i2p.i2p/-/issues?scope=all&state=closed&milestone_title=2.8.0

**{% trans %}SHA256 Checksums:{% endtrans %}**

::
    
     f2699359fd7c5a2fddb5730666e61c0dce2184f95507d4f33dcfaca16569b580  i2pinstall_2.8.0_windows.exe
     32255865c5f89bceab4902ba401c971c5aa238ebe8bc1bfb2153acb6478ce656  i2pinstall_2.8.0.jar
     06b305c24ed163bb09b1afaa3a8d44b2477eb3eb0e1c84236d210606986bd820  i2psource_2.8.0.tar.bz2
     3ff1e0c52757a39e20ac864aa610c92f1a1168979b42a61cd1e9284becc0fe22  i2pupdate_2.8.0.zip
     bfc6fc3c6e2cb486448450d3f08cef6afe2966b57113b17df65cbb53ed6d4a82  i2pupdate.su3