.. meta::
     :author: mhatta
     :editor: idk
     :date: 2019-07-27
     :excerpt: {% trans %}Speeding up your I2P network{% endtrans %}

=====================================================
{% trans %}Speeding up your I2P network{% endtrans %}
=====================================================

{% trans %}*This post is adapted directly from material originally created for mhatta's*
`medium blog <https://medium.com/@mhatta/speeding-up-your-i2p-network-c08ec9de225d>`__\ *.*
*He deserves the credit for the OP. It has been updated in certain places where*
*it refers to old versions of I2P as current and has undergone some light*
*editing. -idk*{% endtrans %}

{% trans %}Right after it starts up, I2P is often seen as a little bit slow. It's true, and
we all know why, by nature, `garlic routing <https://en.wikipedia.org/wiki/Garlic_routing>`__
adds overhead to the familiar experience of using the internet so that you can
have privacy, but this means that for many or most I2P services, your data will
need to go through 12 hops by default.{% endtrans %}

|Diagram of I2P Connection|
`Analysis of tools for online anonymity <https://www.researchgate.net/publication/289531182_An_analysis_of_tools_for_online_anonymity>`__

{% trans %}Also, unlike Tor, I2P was primarily designed as a closed network. You can
easily access `eepsites <https://medium.com/@mhatta/how-to-set-up-untraceable-websites-eepsites-on-i2p-1fe26069271d>`__ or other resources inside I2P, but you are not supposed
to access `clearnet <https://en.wikipedia.org/wiki/Clearnet_(networking)>`__
websites through I2P. There exist a few I2P “outproxies” similar to
`Tor <https://en.wikipedia.org/wiki/Tor_(anonymity_network)>`__\ ’s exit nodes to
access clearnet, but most of them are very slow to use as going to the clearnet
is effectively *another* hop in the already 6 hops in, six hops out connection.{% endtrans %}

{% trans %}Until a few versions ago, this problem was even harder to deal with because many
I2P router users were having difficulties configuring the bandwidth settings for
their routers. If everyone who can takes the time to adjust their bandwidth
settings properly, they will improve not only your connection but also the I2P
network as a whole.{% endtrans %}

{% trans %}Adjusting bandwidth limits{% endtrans %}
===================================================

{% trans %}Since I2P is a peer-to-peer network, you have to share some of your network
bandwidth with other peers. You see choose how much in “I2P Bandwidth
Configuration” (“Configure Bandwidth” button in the “Applications and
Configuration” section of I2P Router Console, or
http://localhost:7657/config).{% endtrans %}

|I2P Bandwidth Configuration|

{% trans %}If you see a shared bandwidth limit of 48 KBps, which is very low, then you
may not have adjusted your shared bandwidth from the default. As the original
author of the material this blog post is adapted from noted, I2P has a default
shared bandwidth limit that is very low until the user adjusts it to avoid
causing issues with the user's connection.{% endtrans %}

{% trans %}However, since many users may not know exactly which bandwidth settings to
adjust, the `I2P 0.9.38 release <https://geti2p.net/en/download>`__ introduced a
New Install Wizard. It contains a Bandwidth Test, which automatically detects
(thanks to M-Lab’s `NDT <https://www.measurementlab.net/tests/ndt/>`__) and adjusts
I2P’s bandwidth settings accordingly.{% endtrans %}

{% trans %}If you want to re-run the wizard, for instance following a change in your
service provider or bcause you installed I2P before version 0.9.38, you can
re-launch it from the 'Setup' link on the 'Help & FAQ' page, or simply access
the wizard directly at http://localhost:7657/welcome{% endtrans %}

|Can you find “Setup”?|

{% trans %}Using the Wizard is straightforward, simply keep clicking “Next”. Sometimes
M-Lab’s chosen measurement servers are down and the test fails. In such case,
click “Previous” (do not use your web browser’s “back” button), then
try it again.{% endtrans %}

|Bandwidth Test Results|

{% trans %}Running I2P continuously{% endtrans %}
=================================================

{% trans %}Even after adjusted the bandwidth, your connection might still be slow As I
said, I2P is a P2P network. It will take some time for your I2P router to be
discovered by other peers and integrated into the I2P network. If your router
not up long enough to become well integrated, or if you shut down un-gracefully
too often, the network will remain fairly slow. On the other hand, the longer
you run your I2P router continuously, the faster and more stable your connection
becomes, and more of your bandwidth share will be used in the network.{% endtrans %}

{% trans %}However, many people might not be able to stay your I2P router up. In such
case, you can still run the I2P router on a remote server such as VPS, then use
SSH port forwarding.{% endtrans %}

.. |Diagram of I2P Connection| image:: /_static/images/fullhops.png
.. |I2P Bandwidth Configuration| image:: /_static/images/bandwidthmenu.png
.. |Can you find “Setup”?| image:: /_static/images/sidemenu.png
.. |Bandwidth Test Results| image:: /_static/images/bwresults.png

