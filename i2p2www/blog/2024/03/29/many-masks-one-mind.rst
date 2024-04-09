{% trans -%}
========================================
Many Masks, One Mind: Securing the NetDB
========================================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2024-03-29
    :category: development
    :excerpt: {% trans %}Many Masks, One Mind: Securing the NetDB{% endtrans %}

{% trans -%}
Author's note: the attacks referred to in this article are not possible against current versions of I2P.
{%- endtrans %}

{% trans -%}
As a self-organizing peer-to-peer network, I2P relies on the routers participating in the network to have a way to share information about what is on the network and how to reach it.
I2P routers achieve this information sharing using the NetDB, a DHT based on Kademlia but modified to work for I2P.
The NetDB needs to share two main kinds of entries, "RouterInfos" which peers will use to communicate with other routers directly, and "LeaseSets" which other peers will use to communicate with I2P clients through anonymous tunnels.
Routers are frequently commmunicating NetDB entries with eachother, either by sending the information to a router or client, or requesting information from a router or client.
This means that the entries can arrive directly or indirectly, anonymously or non-anonymously, depending on the needs of the network and the capabilities of the client.
However, as an anonymizing network, it is also important that it remain impossible for information sent anonymously to be requested back non-anonymously.
It is also important and for information sent non-anonymously to be impossible to request back anonymously.
If it becomes possible for either of those situations to occur, then a linking attack may be carried out which allows an attacker to determine if a clients and routers are sharing a common view of the NetDB.
If it can be reliably determined that the 2 targets share a common view of the NetDB, then there's a very good chance they are on the same router, weakening the target's anonymity drastically.
Because there are so few anonymizing networks, and I2P is the only one where the routing table is shared via the operation of a DHT, this class of attack is all but unique to I2P and its resolution is important to I2P's success.
{%- endtrans %}

{% trans -%}
Consider the following scenario: There is an I2P router hosting an I2P client.
The router publishes a RouterInfo, and the I2P client publishes its LeaseSet.
Because they are both published in the NetDB, other I2P routers can query the NetDB to discover how to communicate with them.
This is normal and essential to the operation of an overlay network of the type implemented by I2P.
An attacker runs an I2P router and queries the NetDB for the target RouterInfo and the target LeaseSet.
It then crafts a new LeaseSet which is unique and and potentially even fake, and sends it down a tunnel to the LeaseSet for the client it is targeting for attack.
The client processes the crafted LeaseSet and adds it to its own NetDB.
The attacker then requests the crafted LeaseSet back directly, from the router, using the RouterInfo it got from the NetDB.
If the crafted LeaseSet is received back as a reply, then the attacker can conclude that the target client and the target router share a common view of the NetDB.
{%- endtrans %}

{% trans -%}
That is a simple example of a NetDB deanonymization attack class which relies on adding an entry into another person's NetDB with one identity, and then requesting it back out with another identity.
In this case, the identities in question are the "router" and the "client" identity.
However, client-to-client linking, which is less damaging, is also possible in some designs.
Designing a defense against this class of attack requires giving the router a way of determining whether or not it is safe to communicate a piece of information with a potential identity.
{%- endtrans %}

{% trans -%}
So how should we think about this problem?
What we're dealing with here, really, has to do with the linkability of different "identities" on the network.
The possibility of linking is created because all these identities share a common datastructure which "remembers" who it has communicated with, and who has communicated with it.
It also "remembers" how that communication occurred.
{%- endtrans %}

{% trans -%}
For a moment, we should imagine ourselves as an attacker.
Imagine if you were trying to discover the identity of a master of disguise.
You know for sure you have seen his real face, and you know for sure that you regularly communicate with one of his disguises.
How would you go about establishing that the disguise identity and the real identity belong to the same person?
I might tell the disguised person a secret.
If the non-disguised person responds by using the secret information, then I can determine that the non-disguised person knows the secret.
Under the assumption that the disguised person did not communicate the secret to anyone else, then I can assume that the non-disguised person and the disguised person are in fact, the same person.
No matter how many masks the master of disguise wears, he has but one mind.
{%- endtrans %}

{% trans -%}
In order to successfully protect the identities of I2P clients, I2P needs to be able to perform as a better master of disguise than the one described above.
It needs to be able to "remember" several important pieces of information about how it has participated in the NetDB and respond appropriately based on those details.
It must be able to recall:
{%- endtrans %}

* {% trans -%}Whether a NetDB Entry was received directly, or received down a client tunnel{%- endtrans %}
* {% trans -%}Whether a NetDB Entry was sent by a peer in response to our lookup, or sent unsolicited{%- endtrans %}
* {% trans -%}Which NetDB Entry was received down Which client Tunnel{%- endtrans %}
* {% trans -%}Multiple versions of the same entry for different client tunnels{%- endtrans %}

{% trans -%}
Structurally, the most understandable and reliable way to handle this pattern is to use "Sub-DBs."
Sub-DB's are miniature NetDB's which serve to help the NetDB organize entries without losing track.
Every client gets a Sub-DB for its own use, and the router itself gets a fully-fledged NetDB.
Using Sub-DB's, we give our master of disguise a rolodex of secrets organized by who shared those secrets with him.
When a request is sent to a client, it only looks for entries which have been communicated to the client, and when a request is sent to a router, only the router-wide NetDB is used.
By doing things this way, we resolve not only the simplest form of the attack, but also undermine the potency of the entire attack class.
{%- endtrans %}