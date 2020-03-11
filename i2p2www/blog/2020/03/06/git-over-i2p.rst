======================
{% trans -%}Git over I2P for Users{%- endtrans %}
======================

.. meta::
    :author: idk
    :date: 2020-03-06
    :excerpt: {% trans %}Help Bootstrap I2P-Bote!{% endtrans %}

{% trans -%}
Tutorial for setting up git access through an I2P Tunnel. This tunnel
will act as your access point to a single git service on I2P. It is part of the
overall effort to transition I2P from monotone to Git.
{%- endtrans %}

{% trans -%}Before anything else: Know the capabilities the service offers to the public{%- endtrans %}
-------------------------------------------------------------------------------------------------------

{% trans -%}
Depending on how the git service is configured, it may or may not offer
all services on the same address. In the case of git.idk.i2p, there is a
public HTTP URL, but this URL is read-only and cannot be used to make
changes. To do that, you must also know the SSH base32, which isn’t
public at this time. Unless I’ve told you the SSH base32 to git.idk.i2p,
head over to the `Server <GITLAB.md>`__ tutorial to set up your own.
{%- endtrans %}

{% trans -%}First: Set up an account at a Git service{%- endtrans %}
--------------------------------------------------------------------

{% trans -%}
To create your repositories on a remote git service, sign up for a user
account at that service. Of course it’s also possible to create
repositories locally and push them to a remote git service, but most
will require an account and for you to create a space for the repository
on the server. Gitlab has a very simple sign-up form:
{%- endtrans %}

.. class:: screenshot
.. figure:: /_static/images/git/register.png
   :alt: Registration is easy!

   Registration is easy!

{% trans -%}Second: Create a project to test with{%- endtrans %}
----------------------------------------------------------------

{% trans -%}
To make sure the setup process works, it helps to make a repository to
test with from the server, and for the sake of this tutorial, we’re
going to use a fork of the I2P router. First, browse to the
i2p-hackers/i2p.i2p repository:
{%- endtrans %}

.. class:: screenshot
.. figure:: /_static/images/git/explore.png
   :alt: Browse to i2p.i2p

.. class:: screenshot
.. figure:: /_static/images/git/i2p.png
   :alt: I2P Hackers i2p.i2p

{% trans -%}
Then, fork it to your account.
{%- endtrans %}

.. class:: screenshot
.. figure:: /_static/images/git/fork.png
   :alt: Roger is forking

.. class:: screenshot
.. figure:: /_static/images/git/forked.png
   :alt: Roger is finished

{% trans -%}Third: Set up your git client tunnel{%- endtrans %}
---------------------------------------------------------------

{% trans -%}
To have read-write access to my server, you’ll need to set up a tunnel
for your SSH client. As an example, we’re going to use the HTTP tunnel
instead, but if all you need is read-only, HTTP/S cloning, then you can
skip all this and just use the http_proxy environment variable to
configure git to use the pre-configured I2P HTTP Proxy. For example:
{%- endtrans %}

::

       http_proxy=http://localhost:4444 git clone http://git.idk.i2p/welshlyluvah1967/i2p.i2p

.. class:: screenshot
.. figure:: /_static/images/git/wizard1.png
   :alt: Client tunnel

.. class:: screenshot
.. figure:: /_static/images/git/wizard2.png
   :alt: Git over I2P

{% trans -%}
Then, add the address you will be pushing and pulling from. Note that
this example address is for Read-Only HTTP-over-I2P clones, if your
admin does not allow the git HTTP(Smart HTTP) protocol, then you will
need to get the SSH clone base32 from them. If you have an SSH clone
base32, substitute it for the base32 in this step, which will fail.
{%- endtrans %}

.. class:: screenshot
.. figure:: /_static/images/git/wizard3.png
   :alt: git.idk.i2p

{% trans -%}
Pick a port to forward the I2P service to locally.
{%- endtrans %}

.. class:: screenshot
.. figure:: /_static/images/git/wizard4.png
   :alt: localhost:localport

{% trans -%}
I use it alot, so I start my client tunnel automatically, but it’s up to
you.
{%- endtrans %}

.. class:: screenshot
.. figure:: /_static/images/git/wizard5.png
   :alt: Auto Start

{% trans -%}
When you’re all done, it should look alot like this.
{%- endtrans %}

.. class:: screenshot
.. figure:: /_static/images/git/wizard6.png
   :alt: Review settings

{% trans -%}Fourth: Attempt a clone{%- endtrans %}
--------------------------------------------------

{% trans -%}
Now your tunnel is all set up, you can attempt a clone over SSH.
{%- endtrans %}

::

       GIT_SSH_COMMAND="ssh -p 7442" \
           git clone git@127.0.0.1:welshlyluvah1967/i2p.i2p

{% trans -%}
You might get an error where the remote end hangs up unexpectedly.
Unfortunately git still doesn’t support resumable cloning. Until it
does, there are a couple fairly easy ways to handle this. The first and
easiest is to try and clone to a shallow depth:
{%- endtrans %}

::

       GIT_SSH_COMMAND="ssh -p 7442" \
           git clone --depth 1 git@127.0.0.1:welshlyluvah1967/i2p.i2p

{% trans -%}
Once you’ve performed a shallow clone, you can fetch the rest resumably
by changing to the repo directory and running:
{%- endtrans %}

::

       git fetch --unshallow

{% trans -%}
At this point, you still don’t have all your branches yet. You can get
them by running the following commands:
{%- endtrans %}

::

       git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
       git fetch origin

{% trans -%}
Which tells git to alter the repository configuration so that fetching
from origin fetches all branches.
{%- endtrans %}

{% trans -%}
If that doesn’t work, you can try opening the tunnel configuration menu
and adding some backup tunnels.
{%- endtrans %}

.. class:: screenshot
.. figure:: /_static/images/git/tweak2.png
   :alt: Backup Tunnels

   Backup Tunnels

{% trans -%}
If that doesn’t work, then the next easy thing to try is to decrease the
tunnel length. Don’t do this if you believe you are at risk of your
code-contribution activity being de-anonymized by a well-resourced
attacker seeking to run many malicious nodes and control your whole
path. If that sounds unlikely to you then you can probably do it safely.
{%- endtrans %}

.. class:: screenshot
.. figure:: /_static/images/git/tweak1.png
   :alt: One-Hop Tunnels

   One-Hop Tunnels

{% trans -%}Suggested Workflow for Developers!{%- endtrans %}
-------------------------------------------------------------

{% trans -%}
Revision control can make your life easier, but it works best if you use
it well! In light of this, we strongly suggest a fork-first,
feature-branch workflow as many are familiar with from Github. In such a
workflow, the master branch is used as a sort of “Trunk” for updates and
is never touched by the programmmer, instead, all changes to the master
are merged from branches. In order to do set up your workspace for this,
take the following steps:
{%- endtrans %}

-  {% trans -%}**Never make changes to the Master Branch**. You will be using the
   master branch to periodially obtain updates to the official source
   code. All changes should be made in feature branches.{%- endtrans %}

1. {% trans -%}Set up a second remote in your local repository using the upstream
   source code.{%- endtrans %}

   ::

       git remote add upstream git@127.0.0.1:i2p-hackers/i2p.i2p

2. {% trans -%}Pull in any upstream changes on your current master:{%- endtrans %}

   ::

       git pull upstream master

3. {% trans -%}Before making any changes to the source code, check out a new feature
   branch to develop on:{%- endtrans %}

   ::

       git checkout -b feature-branch-name

4. {% trans -%}When you’re done with your changes, commit them and push them to your
   branch{%- endtrans %}

   ::

       git commit -am "I added an awesome feature!"
       git push origin feature-branch-name

5. {% trans -%}Submit a merge request. When the merge request is approved and
   brought into the upstream master, check out the master locally and
   pull in the changes:{%- endtrans %}

   ::

       git checkout master
       git pull upstream master

6. {% trans -%}Whenever a change to the upstream master(i2p-hackers/i2p.i2p) is
   made, you can update your master code using this procedure as well.{%- endtrans %}

   ::

       git checkout master
       git pull upstream master
