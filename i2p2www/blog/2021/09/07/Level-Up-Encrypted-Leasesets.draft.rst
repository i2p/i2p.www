=============================================================
{% trans -%}Level up your I2P Skills with Encrypted LeaseSets{%- endtrans %}
=============================================================

.. meta::
   :author: idk
   :date: 2021-09-07
   :category: general
   :excerpt: {% trans %}It has been said that I2P emphasizes Hidden Services, we examine one interpretation of this{% endtrans %}

{% trans -%}
Level up your I2P Skills with Encrypted LeaseSets
{%- endtrans %}
=================================================

{% trans -%}
It has been said in the past that I2P emphasizes support for Hidden Services,
which is true in many ways. However, what this means to users, developers, and
hidden service administrators isn't always the same. Encrypted LeaseSets and
their use-cases provide a unique, practical window into how I2P makes hidden
services more versatile, easier to administer, and how I2P extends on the
Hidden Service concept to provide security benefits for potentially interesting
use-cases.
{%- endtrans %}

{% trans -%}
What is a LeaseSet?
-------------------
{%- endtrans %}

{% trans -%}
When you create a hidden service, you publish something called a "LeaseSet" to
the I2P NetDB. The "LeaseSet" is, in the simplest terms, what other I2P users
need to discover "where" your hidden service is on the I2P Network. It contains
"Leases" which identify tunnels that can be used to reach your hidden service,
and the public key of your destination, which clients will encrypt messages to.
This type of hidden service is reachable by anyone who has the address, which
is probably the most common use case for now.
{%- endtrans %}

{% trans -%}
Sometimes, you might not want to allow your hidden services to be accessible by
anyone, though. Some people use hidden services as a way of accessing an SSH
server on a home PC, or to stitch together a network of IOT Devices. In these
cases it's not necessary, and may be counter-productive, to make your hidden
service accessible to everyone one the I2P Network. This is where "Encrypted
LeaseSets" come into play.
{%- endtrans %}

{% trans -%}
Encrypted LeaseSets: VERY Hidden Services
------------------------------------------
{%- endtrans %}

{% trans -%}
Encrypted LeaseSets are LeaseSets which are published to the NetDB in an
encrypted form, where none of the Leases or public keys are visible unless
the client has the keys required to decrypt the LeaseSet inside of it. Only
clients you share keys with(For PSK Encrypted LeaseSets), or who share their
keys with you(For DH Encrypted LeaseSets), will be able to see the destination
and no one else.
{%- endtrans %}

{% trans -%}
I2P Supports several strategies for Encrypted LeaseSets. The key characteristics
of each strategy are important to understand when deciding which one to use. If
an Encrypted LeaseSet uses a "Pre-Shared Key(PSK)" strategy, then the server
will generate a key(or keys) which the server operator then shares with each
client. Of course, this exchange must happen out-of-band, possibly via an
exchange on IRC for example. This version of Encrypted LeaseSets is sort of
like logging into Wi-Fi with a password. Except, what you're logging into is
a Hidden Service.
{%- endtrans %}

{% trans -%}
If an Encrypted LeaseSet uses a "Diffie-Hellman(DH)
strategy, then they keys are generated on the client instead. When a
Diffie-Hellman client connects to a destination with an Encrypted LeaseSet, they
must first share their keys with the server operator. The server operator then
decides whether to authorize the DH client. This version of Encrypted LeaseSets
is sort of like SSH with an `authorized_keys` file. Except, what you're logging
into is a Hidden Service.
{%- endtrans %}

{% trans -%}
By Encrypting your LeaseSet, you not only make it impossible for unauthorized
users to connect to your destination, you make it impossible for unauthorized
visitors to even discover the real destination of the I2P Hidden Service. Some
readers have probably already considered a use-case for their own Encrypted
LeaseSet.
{%- endtrans %}

{% trans -%}
Using Encrypted LeaseSets to Safely Access a Router Console
-----------------------------------------------------------
{%- endtrans %}

{% trans -%}
As a general rule, the more complex information a service has access to about
your device, the more dangerous it is to expose that service to the Internet or
indeed, to a Hidden Service network like I2P. If you want to expose such a
service, you need to protect it with something like a password, or, in the case
of I2P, a much more thorough and secure option could be an Encrypted LeaseSet.
{%- endtrans %}

{% trans -%}
**Before continuing, please read and understand that if you do the following**
**procedure without an Encrypted LeaseSet, you will be defeating the security of**
**your I2P router. Do not configure access to your router console over I2P without**
**an Encrypted LeaseSet. Additionally, do not share your Encrypted LeaseSet PSK's**
**with any devices you do not control.**
{%- endtrans %}

{% trans -%}
One such service which is useful to share over I2P, but ONLY with an Encrypted
LeaseSet, is the I2P router console itself. Exposing the I2P router console on
one machine to I2P with an Encrypted LeaseSet allows another machine with a
browser to administer the remote I2P instance. I find this useful for remotely
monitoring my regular I2P Services. It could also be used to monitor a server
which is used to seed a torrent long-term as a way to access I2PSnark.
{%- endtrans %}

{% trans -%}
For as long as it takes to explain them, setting up an Encrypted LeaseSet is
straightforward to configure via the Hidden Services Manager UI. 
{%- endtrans %}

{% trans -%}
On the "Server"
---------------
{%- endtrans %}

.. compound::
  .. image:: /_static/images/encryptls/newhs.png
     :width: 100%

{% trans -%}
Start by opening the Hidden Services Manager at http://127.0.0.1:7657/i2ptunnelmgr
and scroll to the bottom of the section that says "I2P Hidden Services." Create
a new hidden service with the host "127.0.0.1" and the port "7657" with these
"Tunnel Cryptography Options" and save the hidden service. 
{%- endtrans %}

.. compound::
  .. image:: /_static/images/encryptls/demosettings.png
     :width: 100%

{% trans -%}
Then, select your new tunnel from the Hidden Services Manager main page. The
Tunnel Cryptography Options should now include your first Pre-Shared Key. Copy
this down for the next step, along with the Encrypted Base32 Address of your
tunnel.
{%- endtrans %}

.. compound::
  .. image:: /_static/images/encryptls/demoresult.png
     :width: 100%

{% trans -%}
On the "Client"
---------------
{%- endtrans %}

{% trans -%}
Now switch computers to the client which will connect to the hidden service,
and visit the Keyring Configuration at http://127.0.0.1:7657/configkeyring to
add the keys from earlier. Start by pasting the Base32 from the Server into
the field labeled: "Full destination, name, Base32, or hash." Next, paste the
Pre-Shared Key from the server into the "Encryption Key" field. Click save,
and you're ready to securely visit the Hidden Service using an Encrypted
LeaseSet.
{%- endtrans %}

.. compound::
  .. image:: /_static/images/encryptls/client.png
     :width: 100%

{% trans -%}
Now You're Ready to Remotely Administer I2P
-------------------------------------------
{%- endtrans %}

{% trans -%}
As you can see, I2P offers unique capabilities to Hidden Service Administrators
which empower them to securely manage their I2P connections from anywhere in the
world. Other Encrypted LeaseSets I keep on the same device for the same reason
point to the SSH server, the Portainer instance I user to manage my service
containers, and my personal NextCloud instance. With I2P, truly private, always
reachable Self-Hosting is an achievable goal, in fact I think it's one of the
things we're uniquely suited to, because of Encrypted LeaseSets. With them, I2P
could become the key to securing self-hosted home automation or simply become
the backbone of a new more private peer-to-peer web.
{%- endtrans %}
