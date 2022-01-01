===============================================
{% trans -%}Year in Review: 2021{%- endtrans %}
===============================================

.. meta::
   :author: Sadie
   :date: 2021-12-29
   :category: general
   :excerpt: {% trans %}I2P Turns 20, Faster Crypto and A Growing Network{% endtrans %}

{% trans -%}
Update details
{%- endtrans %}
============================================

{% trans -%}Development Highlights{%- endtrans %}
#################################################

{% trans -%}
The 0.9.49 release began the migration to the new, faster ECIES-X25519
encryption for routers. It took many years of work on the specifications and
protocols for new encryption, and this release, new installs and a very small
percentage of existing installs (randomly selected at restart) began using the
new encryption. This is the first time that the default encryption type has
ever been changed, so the full migration would take place over several
releases in order to minimize any issues.
{%- endtrans %}

{% trans -%}Full release notes{%- endtrans %}: https://geti2p.net/en/blog/post/2021/02/17/0.9.49-Release

{% trans -%}
0.9.50 enabled DNS over HTTPS for reseeding to protect users from passive DNS
snooping. Additionally, work was done to protect the network from possible
malicious and buggy routers, and numerous fixes and improvements for IPv6
addresses, including new UPnP support were completed.
{%- endtrans %}

{% trans -%}Full release notes{%- endtrans %}: https://geti2p.net/en/blog/post/2021/05/17/0.9.50-Release

{% trans -%}
In recognition of almost 20 years of work to provide anonymity and security,
the team decided to go straight from 0.9.50 to 1.5.0. The 1.5.0 release
finished support for new build messages (proposal 157), and finished
implementation of smaller tunnel build messages to reduce bandwidth. The
transition of the network’s routers to X25519 encryption continued.
{%- endtrans %}


{% trans -%}Full release notes{%- endtrans %}: https://geti2p.net/en/blog/post/2021/08/23/1.5.0-Release

{% trans -%}
The rollout of two major protocol updates reached completed in 1.6.1. Almost
all routers will be rekeyed by the end of the year. Also, short tunnel build
messages were enabled for a significant bandwidth reduction. Progress on the
design of the new UDP transport SSU2 began, and is expected to start
implementation early next year.
{%- endtrans %}


{% trans -%}Full release notes{%- endtrans %}: https://geti2p.net/en/blog/post/2021/11/29/1.6.0-Release

{% trans -%}Easier Installs: JPackage{%- endtrans %}
****************************************************

{% trans -%}
With upwards of 30 steps required to install both the I2P software and Java,
the process for new user onboarding has not been historically easy. Unfamiliar
and unintuitive, it was a process that has created issues for usability for
many years.
{%- endtrans %}

{% trans -%}
However, in recent Java versions, a new option emerged that had the potential
to solve this issue for the Java software. The tool is called “Jpackage” and
would allow for the creation of a Jpackage powered I2P Router.
{%- endtrans %}

{% trans -%}
We removed dozens of steps from the installation process by switching from an
external JVM to a Jpackage, built standard packages for target operating systems,
and signed them in a way the operating system would recognize to keep the user
secure. Since then, the jpackage routers have reached a new milestone, they have
recieved their first incremental updates. These updates will replace the JDK 16
jpackage with an updated JDK 17 jpackage and provide fixes for some small bugs
which we caught after the release.
{%- endtrans %}

{% trans -%}Improving I2P Adoption and Onboarding using Jpackage, I2P-Zero{%- endtrans %}: https://geti2p.net/en/blog/post/2021/09/15/i2p-jpackages
{% trans -%}JPackages Get their First Update{%- endtrans %}: https://geti2p.net/en/blog/post/2021/11/2/i2p-jpackage-1.5.1

{% trans -%}Bitcoin Core added Support for I2P{%- endtrans %}
*************************************************************

{% trans -%}
Bitcoin-over-I2P nodes can now fully interact with the rest of the Bitcoin nodes,
using the help of nodes that operate within both I2P and the clearnet.
{%- endtrans %}

{% trans -%}Read the full blog post{%- endtrans %}: https://geti2p.net/en/blog/post/2021/09/18/i2p-bitcoin

{% trans -%}I2P Usability Lab{%- endtrans %}
********************************************

{% trans -%}
This year, the I2P Usability Lab was created. The focus will be on user research,
product development and tooling to support adoption. Additionally, better focus on
localization efforts, protocol bridge building within the privacy community and
sustainability considerations will be part of the ongoing effort to bring I2P to
more people.
{%- endtrans %}

{% trans -%}New User Onboarding Research{%- endtrans %}
*******************************************************

{% trans -%}
In 2020 the I2P UX team worked with Simply Secure on a usability sprint to assess
user interaction with the I2P website. Many changes were applied, however, feedback
has indicated that there are still issues with some aspects of new user onboarding.
{%- endtrans %}

{% trans -%}
We have expanded our team thanks to the BASICS project (Building Analytical and
Support Infrastructure for Critical Security tools), and not only revisiting the
new user onboarding, but we are also expanding the scope to include onboarding for
developers and researchers. The goal will be to present an improved information
architecture.
{%- endtrans %}

{% trans -%}
This year we focused on the massive overhaul of the new user onboarding for the
download and browser configuration workflow and language. New wireframes for the
I2P website have been created, and new information architecture put in place. This
has been done in order to better support new users, maintainers, application 
developers, I2P core contributors, and researchers. This work will continue into
2022 as documentation is refined and the site changes are implemented.
{%- endtrans %}

{% trans -%}Read the full UX review here:{%- endtrans %} https://i2p.medium.com/i2p-ux-research-d2567aefd275

{% trans -%}Forum on internet Freedom in Africa 2021{%- endtrans %}
*******************************************************************

{% trans -%}
Working with our partners in Africa, the Invisible Internet Project was invited
to participate in both a panel discussion, as well as work with a group of 
journalists to explore what privacy and security mean to them. The goal for the
outcome from this opportunity was to understand what establishes trust, the
concept of privacy and what it means, and egin to evaluate I2P and its tooling
through this lens.
{%- endtrans %}

{% trans -%}
We saw that adoption results from efficiency, ease of use, and empowerment. All
of these things result in a person not just wanting to use a privacy option, but to
feel like they are actually taking control of their privacy. This is one of the
most important aspects we have encountered during the past year when talking with
new users: the emotional aspect of interacting with technology. Telling a person
that something can technically provide a solution is one part of adoption. Providing
a person with something that they can use with confidence is the other. 
Meeting people where they are and asking about who they are ensures that we are
creating for real needs and for the most people possible.
{%- endtrans %}

{% trans -%}Read the entire blog post here{%- endtrans %}: https://i2p.medium.com/i2p-usability-lab-b2098bf27d4d

{% trans -%}
Thank you to everyone who contributes to building the Invisible Internet!
{%- endtrans %}

{% trans -%}
This post originally appeared on Sadie's blog. https://i2p.medium.com/4b926a488919
Copied with permission.
{%- endtrans %}