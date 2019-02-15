{% trans -%}
==============================
The birth of Privacy Solutions
==============================
{%- endtrans %}

.. meta::
   :author: Meeh
   :date: 2014-08-15
   :category: news
   :excerpt: {% trans %}Organization launch{% endtrans %}

{% trans -%}
Hello all!

Today we announce the Privacy Solutions project, a new organization that develops and maintains I2P software. Privacy Solutions includes several new development efforts designed to enhance the privacy, security, and anonymity for users, based on I2P protocols and technology.

These efforts include

1) The Abscond browser bundle.
2) The i2pd C++ router project.
3) The "BigBrother" I2P network monitoring project.
4) The Anoncoin crypto-coin project.
5) The Monero crypto-coin project.

Privacy Solutions' initial funding was provided by the supporters of the Anoncoin and Monero projects. Privacy Solutions is a Norway-based non-profit type of organization registered within the Norwegian government registers. ( Kind of like US 501(c)3. )

Privacy Solutions plans to apply for funding from the Norwegian goverment for network research, because of BigBrother (We'll get back to what that is) and the coins that are planned to use low-latency networks as primary transport layer. Our research will support advances in software technology for anonymity, security, and privacy.


First a little bit about the Abscond Browser Bundle. This was first a one-man project by Meeh, but later on friends started sending patches, the project is now trying to create the same easy access to I2P as Tor has with their browser bundle. Our first release isn't far away, it's just some gitian script tasks left, including setup of the Apple toolchain. But again we will add monitoring with PROCESS_INFORMATION (A C struct keeping vital proces information about an process) from the Java instance to check on I2P before we declare it stable. I2pd will also switch with the Java version once it's ready, and there is no point in shipping a JRE in the bundle anymore. You can read more about the Abscond Browser Bundle at https://hideme.today/dev

{%- endtrans %}

{% trans -%}
We would also like to inform of the current status of i2pd. I2pd supports bi-directional streaming now, that allows to use not only HTTP but long-lived communication channels. Instant IRC support has been added. I2pd users are able to use it same way as Java I2P for access to I2P IRC network. I2PTunnel is one of key features of I2P network, allowing non-I2P applications communicate transparently. That's why it's vital feature for i2pd and one of key milestones.
{%- endtrans %}

{% trans -%}
At last, if you are familiar with I2P you probably know about Bigbrother.i2p, which is a metrics system Meeh made over a year back. Recently we noticed that Meeh actually have 100Gb of non-duplicated data from nodes reporting in since initial launch. This will also be moved to Privacy Solutions and be rewritten with a NSPOF backend. With this we will aslo start using the Graphite ( http://graphite.wikidot.com/screen-shots ). This will give us a great overview over the network without privacy issues for our end users. The clients filter all data except country, router hash and success rate on tunnel buildings. The name of this service is as always a little joke from Meeh.


{%- endtrans %}


{% trans -%}
We have shorted down a bit of the news here, if you're interested in more information please visit https://blog.privacysolutions.no/
We're still under construction and more content will come!



For further information contact: press@privacysolutions.no




Best regards,

Mikal "Meeh" Villa
{%- endtrans %}

