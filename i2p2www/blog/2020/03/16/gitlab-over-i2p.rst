{% trans -%}Gitlab over I2P Setup{%- endtrans %}
================================================

.. meta::
    :author: idk
    :date: 2020-03-16
    :excerpt: {% trans -%}Mirror I2P Git repositories and Bridge Clearnet repositories for others.{%- endtrans %}

{% trans -%}
This is the setup process I use for configuring Gitlab and I2P, with
Docker in place to manage the service itself. Gitlab is very easy to
host on I2P in this fashion, it can be administered by one person
without much difficulty. In my configuration, I use a Debian VM to host
docker containers and an I2P router, on a Debian Host system, however,
this may be more than necessary for some people. These instructions
should work on any Debian-based system, regardless of whether it is in a
VM or not, and should easily translate to any system where Docker and an
I2P router are available. This guide starts at Docker and does not
assume any VM underneath.
{%- endtrans %}

{% trans -%}Dependencies and Docker{%- endtrans %}
---------------------------------------------------

{% trans -%}
Because Gitlab runs in a container, we only need to install the
dependencies required for the container on our main system.
Conveniently, you can install everything you need with:
{%- endtrans %}

::

       sudo apt install docker.io

{% trans -%}
on an otherwise unmodified Debian system, or if you have added Docker’s
own “Community” Debian repository, you may use:
{%- endtrans %}

::

       sudo apt install docker-ce

{% trans -%}
instead.
{%- endtrans %}

------------------------------------------------------
{% trans -%}Fetch the Docker Containers{%- endtrans %}
------------------------------------------------------

{% trans -%}
Once you have docker installed, you can fetch the docker containers
required for gitlab. *Don’t run them yet.*
{%- endtrans %}

::

       docker pull gitlab/gitlab-ce

{% trans -%}
For those who are concerned, the gitlab-ce Docker image is built using
only Ubuntu Docker images as a parent, which are built from scratch
images. Since there are no third-party images involved here, updates
should come as soon as they are available in the host images. To review
the Dockerfile for yourself, visit the `Gitlab source
code <https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/master/docker/Dockerfile>`__.
{%- endtrans %}

{% trans -%}Set up an I2P HTTP Proxy for Gitlab to use(Important information, optional steps){%- endtrans %}
------------------------------------------------------------------------------------------------------------

{% trans -%}
Gitlab servers inside of I2P can be run with or without the ability to
interact with servers on the internet outside of I2P. In the case where
the Gitlab server is *not allowed* to interact with servers outside of
I2P, they cannot be de-anonymized by cloning a git repository from a git
server on the internet outside of I2P. They can, however, export and
mirror repositories from other git services inside of I2P.
{%- endtrans %}

{% trans -%}
In the case where the Gitlab server is *allowed* to interact with
servers outside of I2P, it can act as a “Bridge” for the users, who can
use it to mirror content outside I2P to an I2P-accessible source,
however it *is not anonymous* in this case. Git services on the
non-anonymous internet will be connected to directly.
{%- endtrans %}

{% trans -%}
**If you want to have a bridged, non-anonymous Gitlab instance with
access to** **web repositories,** no further modification is necessary.
{%- endtrans %}

{% trans -%}
**If you want to have an I2P-Only Gitlab instance with no access to
Web-Only** **Repositories**, you will need to configure Gitlab to use an
I2P HTTP Proxy. Since the default I2P HTTP proxy only listens on
``127.0.0.1``, you will need to set up a new one for Docker that listens
on the Host/Gateway address of the Docker network, which is usually
``172.17.0.1``. I configure mine on port ``4446``.
{%- endtrans %}

{% trans -%}Start the Container Locally{%- endtrans %}
------------------------------------------------------

{% trans -%}
Once you have that set up, you can start the container and publish your
Gitlab instance locally.
{%- endtrans %}

::

       docker run --detach \
         --env HTTP_PROXY=http://172.17.0.1:4446 \
         --publish 127.0.0.1:8443:443 --publish 127.0.0.1:8080:80 --publish 127.0.0.1:8022:22 \
         --name gitlab \
         --restart always \
         --volume /srv/gitlab/config:/etc/gitlab:Z \
         --volume /srv/gitlab/logs:/var/log/gitlab:Z \
         --volume /srv/gitlab/data:/var/opt/gitlab:Z \
         gitlab/gitlab-ce:latest

{% trans -%}
Visit your Local Gitlab instance and set up your admin account. Choose a
strong password, and configure user account limits to match your
resources.
{%- endtrans %}

{% trans -%}Modify gitlab.rb(Optional, but a good idea for “Bridged non-anonymous” hosts){%- endtrans %}
--------------------------------------------------------------------------------------------------------

{% trans -%}
It’s also possible to apply your HTTP Proxy settings in a more granular
way, so that you can only allow users to mirror repositories from the
domains that you choose. Since the domain is presumably operated by an
organization, you can use this to ensure that repositories that are
mirrorable follow a reasonable set of policies. After all, there is far
more abusive content on the non-anonymous internet than there is on I2P,
we wouldn’t want to make it too easy to introduce abusive content from
such a nefarious place.
{%- endtrans %}

{% trans -%}
Add the following lines to your gitlab.rb file inside the
/src/gitlab/config container. These settings will take effect when you
restart in a moment.
{%- endtrans %}

::

       gitlab_rails['env'] = {
           "http_proxy" => "http://172.17.0.1:4446",
           "https_proxy" => "http://172.17.0.1:4446",
           "no_proxy" => ".github.com,.gitlab.com"
       }
       gitaly['env'] = {
           "http_proxy" => "http://172.17.0.1:4446",
           "https_proxy" => "http://172.17.0.1:4446",
           "no_proxy" => "unix,.github.com,.gitlab.com"
       }
       gitlab_workhorse['env'] = {
           "http_proxy" => "http
           "https_proxy" => "http://172.17.0.1:4446",
           "no_proxy" => "unix,.github.com,.gitlab.com"
       }

---------------------------------------------------------------------------------
{% trans -%}Set up your Service tunnels and sign up for a Hostname{%- endtrans %}
---------------------------------------------------------------------------------

{% trans -%}
Once you have Gitlab set up locally, go to the I2P Router console. You
will need to set up two server tunnels, one leading to the Gitlab
web(HTTP) interface on TCP port 8080, and one to the Gitlab SSH
interface on TCP Port 8022.
{%- endtrans %}

{% trans -%}Gitlab Web(HTTP) Interface{%- endtrans %}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{% trans -%}
For the Web interface, use an “HTTP” server tunnel. From
http://127.0.0.1:7657/i2ptunnelmgr launch the “New Tunnel Wizard” and
enter the following values at each step:
{%- endtrans %}

1. {% trans -%}Select “Server Tunnel”{%- endtrans %}
2. {% trans -%}Select “HTTP Server”{%- endtrans %}
3. {% trans -%}Fill in “Gitlab Web Service” or otherwise describe the tunnel{%- endtrans %}
4. {% trans -%}Fill in ``127.0.0.1`` for the host and ``8080`` for the port.{%- endtrans %}
5. {% trans -%}Select “Automatically start tunnel when Router Starts”{%- endtrans %}
6. {% trans -%}Confirm your selections.{%- endtrans %}

{% trans -%}Register a Hostname(Optional){%- endtrans %}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

{% trans -%}
Web services on I2P can register hostnames for themselves by providing
an authentication string to a jump service provider like
`stats.i2p <http://stats.i2p>`__. To do this, open the
http://127.0.0.1:7657/i2ptunnelmgr again and click on the “Gitlab Web
Service” item you just set up. Scroll to the bottom of the “Edit Server
Settings” section and click Registration Authentication. Copy the field
that says “Authentication for adding Hostname” and visit
`stats.i2p <http://stats.i2p/i2p/addkey.html>`__ to add your hostname.
Note that if you want to use a subdomain(Like git.idk.i2p) then you will
have to use the correct authentication string for your subdomain, which
is a little bit more complicated and merits it’s own instructions.
{%- endtrans %}

{% trans -%}Gitlab SSH Interface{%- endtrans %}
~~~~~~~~~~~~~~`~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{% trans -%}
For the SSH interface, use a “Standard” server tunnel. From
http://127.0.0.1:7657/i2ptunnelmgr launch the “New Tunnel Wizard” and
enter the following values at each step:
{%- endtrans %}

1. {% trans -%}Select “Server Tunnel”{%- endtrans %}
2. {% trans -%}Select “Standard Server”{%- endtrans %}
3. {% trans -%}Fill in “Gitlab SSH Service” or otherwise describe the tunnel{%- endtrans %}
4. {% trans -%}Fill in ``127.0.0.1`` for the host and ``8022`` for the port.{%- endtrans %}
5. {% trans -%}Select “Automatically start tunnel when Router Starts”{%- endtrans %}
6. {% trans -%}Confirm your selections.{%- endtrans %}

{% trans -%}Re-start the Gitlab Service with the new Hostname{%- endtrans %}
----------------------------------------------------------------------------

{% trans -%}
Finally, if you either modified ``gitlab.rb`` or you registered a
hostname, you will need to re-start the gitlab service for the settings
to take effect.
{%- endtrans %}

::

       docker stop gitlab
       docker rm gitlab
       docker run --detach \
         --hostname your.hostname.i2p \
         --hostname thisisreallylongbase32hostnamewithfiftytwocharacters.b32.i2p \
         --env HTTP_PROXY=http://172.17.0.1:4446 \
         --publish 127.0.0.1:8443:443 --publish 127.0.0.1:8080:80 --publish 127.0.0.1:8022:22 \
         --name gitlab \
         --restart always \
         --volume /srv/gitlab/config:/etc/gitlab:Z \
         --volume /srv/gitlab/logs:/var/log/gitlab:Z \
         --volume /srv/gitlab/data:/var/opt/gitlab:Z \
         gitlab/gitlab-ce:latest
