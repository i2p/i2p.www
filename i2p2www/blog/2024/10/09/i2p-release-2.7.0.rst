{% trans -%}
==================
I2P 2.7.0 Released
==================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2024-10-09
    :category: release
    :excerpt: {% trans %}I2P 2.7.0 Released{% endtrans %}

{% trans -%}
This release, I2P 2.7.0, continues our work by fixing bugs, improving performance, and adding features.
{%- endtrans %}

{% trans -%}
Access to information from the console and applications has been improved.
Issues have been fixed in I2PSnark and SusiMail search.
The netDB search embedded into the router console now operates in a more intuitive and useful way.
Minor improvements have been made to diagnostic displays in advanced mode.
{%- endtrans %}

{% trans -%}
Bugs have also been fixed to improve compatibility within the network.
An issue with publishing leaseSets was solved which improves reliability major hidden services.
I2PSnark no longer changes the infohash when a user changes only the trackers on an existing torrent.
This prevents torrents from being unnecessarily disrupted by these changes.
We welcomed this contribution from a new contributor.
A conflict in the handling of a streaming library option was resolved to improve compatibility with other I2P implementations.
{%- endtrans %}

{% trans -%}
As usual, we recommend that you update to this release.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}

`{% trans %}Full list of fixed bugs{% endtrans %}`__

__ http://{{ i2pconv('git.idk.i2p') }}/i2p-hackers/i2p.i2p/-/issues?scope=all&state=closed&milestone_title=2.7.0

**{% trans %}SHA256 Checksums:{% endtrans %}**

::
      
     d70ee549b05e58ded4b75540bbc264a65bdfaea848ba72631f7d8abce3e3d67a  i2pinstall_2.7.0_windows.exe
     ea3872af06f7a147c1ca84f8e8218541963da6ad97e30e1d8f7a71504e4b0cee  i2pinstall_2.7.0.jar
     54eebdb1cfdbe6aeb1f60e897c68c6b2921c36ce921350d45d21773256c99874  i2psource_2.7.0.tar.bz2
     b7fae5181cbd8b60be0d5a05e391f4c9d114748a8240eb64b91ee84da5c659f8  i2pupdate_2.7.0.zip
     59d3d61eccf3622985b71e06d454f61f32f39baa1eb9064536d295b4a7e7ae4e  i2pupdate.su3
