=============================================================
{% trans -%}Bitcoin Core adds support for I2P!{%- endtrans %}
=============================================================

.. meta::
   :author: idk
   :date: 2021-09-18
   :category: general
   :excerpt: {% trans %}A new use case and a signal of growing acceptance{% endtrans %}

{% trans -%}
An event months in the making, Bitcoin Core has added official support for I2P!
Bitcoin-over-I2P nodes can interact fully with the rest of the Bitcoin nodes,
using the help of nodes that operate within both I2P and the clearnet, making
them first-class participants in the Bitcoin network. It's exciting to see
large communities like Bitcoin taking notice of the advantages I2P can bring
to them providing privacy and reachability to people all over the world.
{%- endtrans %}

{% trans -%}
How it Works
{%- endtrans %}
------------

{% trans -%}
I2P support is automatic, via the SAM API. This is also exciting news, because
it highlights some of the things I2P is singularly good at, like empowering 
application developers to build I2P connections programmatically and
conveniently. Bitcoin-over-I2P users can use I2P with no manual configuration by
enabling the SAM API and running Bitcoin with I2P enabled.
{%- endtrans %}

{% trans -%}
Configuring your I2P Router
{%- endtrans %}
---------------------------

{% trans -%}
In order to set up an I2P Router to provide anonymous connectivity to bitcoin,
the SAM API needs to be enabled. In Java I2P, you should go to `http://127.0.0.1:7657/configclients
<http://127.0.0.1:7657/configclients>`_. and start the SAM Application Bridge
with the "Start" button. You may also want to enable the SAM Application Bridge
by default by checking the "Run at Startup" box and clicking "Save Client
Configuration."
{%- endtrans %}

{% trans -%}
On i2pd, the SAM API is normally enabled by default, but if it isn't, you should
set::

  sam.enabled=true

in your i2pd.conf file.
{%- endtrans %}

{% trans -%}
Configuring your Bitcoin Node for Anonymity and Connectivity
{%- endtrans %}
------------------------------------------------------------

{% trans -%}
Getting Bitcoin itself launched in an anonymous mode still requires editing some
configuration files in the Bitcoin Data Directory, which is %APPDATA%\Bitcoin on
Windows, ~/.bitcoin on Linux, and ~/Library/Application Support/Bitcoin/ on Mac
OSX. It also requires at least version 22.0.0 for I2P support to be present. 
{%- endtrans %}

{% trans -%}
After following these instructions, you should have a private Bitcoin
node which uses I2P for I2P connections, and Tor for .onion and clearnet
connections, so that all your connections are anonymous. For convenience,
Windows users should open their Bitcoin Data Directory by opening the start menu
and searching for "Run." Inside the run prompt, type "%APPDATA%\Bitcoin" and
press enter.
{%- endtrans %}

{% trans -%}
In that directory create a file called "i2p.conf." On Windows, you should make
sure that you've add quotes around the file when you save it, in order to
prevent Windows from adding a default file extension to the file. The file
should contain the following I2P-Related Bitcoin configuration options::

  i2psam=127.0.0.1:7656
  i2pacceptincoming=true
  onlynet=i2p

Next, you should create another file called "tor.conf." The file should contain
the following Tor related configuration options::

  proxy=127.0.0.1:9050
  onion=127.0.0.1:9050
  onlynet=tor

Finally, you'll need to "include" these configuration options in your Bitcoin
configuration file, called "bitcoin.conf" in the Data Directory. Add these two
lines to your bitcoin.conf file::

  includeconf=i2p.conf
  includeconf=tor.conf

Now your Bitcoin node is configured to only use anonymous connections. In order
to enable direct connections to remote nodes, remove the lines beginning in::

  onlynet=

You can do this if you do not require your Bitcoin node to be anonymous, and
it helps anonymous users connect to the rest of the Bitcoin network.
{%- endtrans %}