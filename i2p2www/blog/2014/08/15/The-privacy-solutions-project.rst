{% trans -%}
==============================
The birth of Privacy solutions
==============================
{%- endtrans %}
.. meta::
   :author: Meeh
   :date: 2014-08-15
   :category: news
   :excerpt: {% trans %}Organization launch{% endtrans %}



{% trans -%}
Hello all!

You might have heard about the Abscond browser bundle or i2pd, I will talk a bit about both. First the Abscond browser bundle. This was first a one-man project by me but later on friends started sending patches, I was/is trying to create the same easy access to I2P as Tor has with their browser bundle. Our first release isn't far away, it's just some gitian script tasks left, including setup of the Apple toolchain. But again I will add monitoring with PROCESS_INFORMATION (A C struct keeping vital proces information about an process) from the Java instance to check on I2P before I declare it stable. I2pd will also switch with the Java version once it's ready, and there is no point in shipping a JRE in the bundle anymore. You can read more about the Abscond browser bundle at https://hideme.today/dev

If it's a bit unclear, The privacy solution project is an organization that develops, maintain and keep track of some I2P related software and services.
{%- endtrans %}

{% trans -%}
I would also like to inform of the current status of i2pd. I2pd supports bi-directional streaming now, that allows to use not only HTTP but long-lived communication channels. Instant IRC support has been added. I2pd users are able to use it same way as Java I2P for access to I2P IRC network. I2PTunnel is one of key features of I2P network, allowing non-I2P applications communicate transparently. That's why it's vital feature for i2pd and one of key milestones.
{%- endtrans %}

{% trans -%}
At last, if you are familiar with I2P you probably know about Bigbrother.i2p, which is a metrics system I made over a year back. This has until now runned on my home PC without much maintaince since the graphs created themself based on trusted people with routers reporting anonymous statistics from their view on I2P, and a router is limited to how many it can "see". Recently I noticed that I actually have 100Gb of non-duplicated data from nodes reporting in. This will also be moved to Privacy Solutions and be rewritten. This time the storage would be on a no-single-point-of-failure database system (Carbon backend over Cassandra) and multiple reciever nodes. With this we will aslo start using the Graphite ( http://graphite.wikidot.com/screen-shots ). This will give us a great overview over the network without privacy issues. The clients filter all data except country, router hash and success rate on tunnel buildings.
{%- endtrans %}


{% trans -%}
I've shorted down a bit the news here, if you're interested in more information please visit https://blog.privacysolutions.no/
We're still under construction and more content will come!



Best regards,

Mikal "Meeh" Villa
{%- endtrans %}

