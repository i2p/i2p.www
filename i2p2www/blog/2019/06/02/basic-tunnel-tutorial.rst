.. meta::
    :author: idk
    :date: 2019-06-02
    :excerpt: {% trans %}Basic i2ptunnel Setup{% endtrans %}

========================================
Basic i2p Tunnels Tutorial with Pictures
========================================

Although the Java i2p router comes pre-configured with a static web server,
jetty, to provide the user's first eepSite, many require more sophisticated
functionality from their web server and would rather create an eepSite with a
different server. This is of course possible, and actually is really easy once
you've done it one time.

Although it is easy to do, there are a few things you should consider before
doing it. You will want to remove identifying characteristics from your web
server, like potentially identifying headers and default error pages that
report the server/distro type. More information about threats to anonymity
posed by improperly configured applications see:
`Riseup here: <https://riseup.net/en/security/network-security/tor/onionservices-best-practices>`__,
`Whonix Here: <https://www.whonix.org/wiki/Onion_Services>`__,
`This blog article for some opsec fails: <https://blog.0day.rocks/securing-a-web-hidden-service-89d935ba1c1d>`__,
`and the i2p applications page here <https://geti2p.net/en/docs/applications/supported>`__.
Although much of this information is expressed for Tor Onion Services, the same
procedures and principles apply to hosting applications over i2p.

Step One: Open the Tunnel Wizard
--------------------------------

Go to the i2p web interface at 127.0.0.1:7657 and open the
`Hidden Services Manager <http://127.0.0.1:7657/i2ptunnelmgr>`__\ (links to
localhost). Click the button that says "Tunnel Wizard" to begin.

|Step One: Open the Tunnel Wizard|

Step Two: Select a Server Tunnel
--------------------------------

The tunnel wizard is very simple. Since we're setting up an http *server*, all
we need to do is select a *server* tunnel.

|Step Two: Select a Server Tunnel|

Step Three: Select an HTTP Tunnel
---------------------------------

An HTTP tunnel is the tunnel type that is optimized for hosting HTTP services.
It has filtering and rate-limiting features enabled that are tailored
specifically to that purpose. A standard tunnel may work as well, but if you
select a atandard tunnel you'll need to take care of those security features
yourself. A more in-depth dive into the HTTP Tunnel configuration is available
in the next tutorial.

|Step Three: Select an HTTP Tunnel|

Step Four: Give it a name and a description
-------------------------------------------

For your own benefit and ability to remeber and distinguish the what you are
using the tunnel for, give it a good nickname and description. If you need to
come back and do more management later, then this is how you will identify the
tunnel in the hidden services manager.

|Step Four: Give it a name and a description|

Step Five: Configure the Host and Port
--------------------------------------

In this step, you point the web server at the TCP port where your web server is
listening. Since most web servers listen on port 80 or port 8080, the example
shows that. If you use alternate ports or virtual machines or containers to
isolate your web services, you may need to adjust the host, port, or both.

|Step Five: Configure the Host and Port|

Step Six: Decide whether to start it automatically
--------------------------------------------------

I cannot think of a way to elaborate on this step.

|Step Six: Decide whether to start it automatically|

Step Seven: Review your settings
--------------------------------

Finally, take a look at the settings you have selected. If you approve, save
them. If you did not choose to start the tunnel automatically, go to the hidden
services manager and start it manually when you wish to make your service
available.

|Step Six: Review your settings|

Appendix: HTTP Server Customization Options
-------------------------------------------

i2p provides a detailed panel for configuring the http server tunnel in custom
ways. I'll finish this tutorial by walking through all of them. Eventually.

|Options page|
|Options page|
|Options page|
|Options page|

.. |Step One: Open the Tunnel Wizard| image:: /_static/images/00-wizard.png
.. |Step Two: Select a Server Tunnel| image:: /_static/images/01-select.png
.. |Step Three: Select an HTTP Tunnel| image:: /_static/images/02-http.png
.. |Step Four: Give it a name and a description| image:: /_static/images/03-name.png
.. |Step Five: Configure the Host and Port| image:: /_static/images/04-port.png
.. |Step Six: Decide whether to start it automatically| image:: /_static/images/05-auto.png
.. |Step Six: Review your settings| image:: /_static/images/06-finish.png
.. |Options page| image:: /_static/images/07-finished.png
.. |Options page| image:: /_static/images/08-finished.png
.. |Options page| image:: /_static/images/09-finished.png
.. |Options page| image:: /_static/images/10-finished.png

