===========================================
{% trans -%}SSU2 Transport{%- endtrans %}
===========================================

.. meta::
   :author: zzz
   :date: 2022-10-11
   :category: development
   :excerpt: {% trans %}SSU2 Transport{% endtrans %}

{% trans %}Overview{% endtrans %}
------------------------------------

{% trans -%}
I2P has used a censorship-resistant UDP transport protocol "SSU" since 2005.
We've had few, if any, reports of SSU being blocked in 17 years.
However, by today's standards of security, blocking resistance,
and performance, we can do better. Much better.
{%- endtrans %}

{% trans link1="https://i2pd.xyz/" -%}
That's why, together with the `i2pd project <{{ link1 }}>`_, we have created and implemented "SSU2",
a modern UDP protocol designed to the highest standards of security and blocking resistance.
This protocol will replace SSU.
{%- endtrans %}

{% trans -%}
We have combined industry-standard encryption with the best
features of UDP protocols WireGuard and QUIC, together with the
censorship resistance features of our TCP protocol "NTCP2".
SSU2 may be one of the most secure transport protocols ever designed.
{%- endtrans %}


{% trans link1="/spec/proposals/159", link2="/en/docs/transport/ssu", link3="https://en.wikipedia.org/wiki/ElGamal_encryption" -%}
The Java I2P and i2pd teams are finishing the `SSU2 transport <{{ link1 }}>`_ and we will enable it for all routers in the next release.
This completes our decade-long plan to upgrade all the cryptography from the original
Java I2P implementation dating back to 2003.
SSU2 will replace `SSU <{{ link2 }}>`_, our sole remaining use of `ElGamal <{{ link3 }}>`_ cryptography.
{%- endtrans %}

- Signature types and ECDSA signatures (0.9.8, 2013)
- Ed25519 signatures and leasesets (0.9.15, 2014)
- Ed25519 routers (0.9.22, 2015)
- Destination encryption types and X25519 leasesets (0.9.46, 2020)
- Router encryption types and X25519 routers (0.9.49, 2021)

{% trans link1="https://noiseprotocol.org/" -%}
After the transition to SSU2,
we will have migrated all our authenticated and encrypted protocols to standard `Noise Protocol <{{ link1 }}>`_ handshakes:
{%- endtrans %}

- `NTCP2 <{{ spec_url("ntcp2") }}>`_ (0.9.36, 2018)
- `{% trans %}ECIES-X25519-Ratchet end-to-end protocol{% endtrans %} <{{ spec_url("ecies") }}>`_ (0.9.46, 2020)
- `{% trans %}ECIES-X25519 tunnel build messages{% endtrans %} <{{ spec_url("tunnel-creation-ecies") }}>`_ (1.5.0, 2021)
- `SSU2 <{{ proposal_url("159") }}>`_ (2.0.0, 2022)

{% trans -%}
All I2P Noise protocols use the following standard cryptographic algorithms:
{%- endtrans %}

- `X25519 <https://en.wikipedia.org/wiki/Curve25519>`_
- `ChaCha20/Poly1305 AEAD <https://www.rfc-editor.org/rfc/rfc8439.html>`_
- `SHA-256 <https://en.wikipedia.org/wiki/SHA-2>`_


{% trans %}Goals{% endtrans %}
------------------------------------

- {% trans %}Upgrade the asymmetric cryptography to the much faster X25519{% endtrans %}
- {% trans %}Use standard symmetric authenticated encryption ChaCha20/Poly1305{% endtrans %}
- {% trans %}Improve the obfuscation and blocking resistance features of SSU{% endtrans %}
- {% trans %}Improve the resistance to spoofed addresses by adapting strategies from QUIC{% endtrans %}
- {% trans %}Improved handshake CPU efficiency{% endtrans %}
- {% trans %}Improved bandwidth efficiency via smaller handshakes and acknowledgements{% endtrans %}
- {% trans %}Improve the security of the peer test and relay features of SSU{% endtrans %}
- {% trans %}Improve the handling of peer IP and port changes by adapting the "connection migration" feature of QUIC{% endtrans %}
- {% trans %}Move away from heuristic code for packet handling to documented, algorithmic processing{% endtrans %}
- {% trans %}Support a gradual network transition from SSU to SSU2{% endtrans %}
- {% trans %}Easy extensibility using the block concept from NTCP2{% endtrans %}


{% trans %}Design{% endtrans %}
------------------------------------

{% trans -%}
I2P uses multiple layers of encryption to protect traffic from attackers.
The lowest layer is the transport protocol layer, used for point-to-point links between two routers.
We currently have two transport protocols:
NTCP2, a modern TCP protocol introduced in 2018,
and SSU, a UDP protocol developed in 2005.
{%- endtrans %}


{% trans link1="/spec/i2np" -%}
SSU2, like previous I2P transport protocols, is not a general-purpose pipe for data.
Its primary task is to securely deliver I2P's low-level `I2NP messages <{{ link1 }}>`_
from one router to the next.
Each of these point-to-point connections comprises one hop in an I2P tunnel.
Higher-layer I2P protocols run over these point-to-point connections
to deliver garlic messages end-to-end between I2P's destinations.
{%- endtrans %}

{% trans -%}
Designing a UDP transport presents unique and complex challenges not present in TCP protocols.
A UDP protocol must handle security issues caused by address spoofing,
and must implement its own congestion control.
Additionally, all messages must be fragmented to fit within the maximum packet size (MTU)
of the network path, and reassembled by the receiver.
{%- endtrans %}

{% trans -%}
We first relied heavily on our previous experience with our NTCP2, SSU, and streaming protocols.
Then, we carefully reviewed and borrowed heavily from two recently-developed UDP protocols:
{%- endtrans %}

- QUIC (`RFC 9000 <https://www.rfc-editor.org/rfc/rfc9000.html>`_, `RFC 9001 <https://www.rfc-editor.org/rfc/rfc9001.html>`_, `RFC 9002 <https://www.rfc-editor.org/rfc/rfc9002.html>`_)
- `WireGuard <https://www.wireguard.com/protocol/>`_

{% trans -%}
Protocol classification and blocking by adversarial on-path attackers such
as nation-state firewalls is not an explicit part of the threat model for those protocols.
However, it is an important part of I2P's threat model, as our mission is to
provide an anonymous and censorship-resistant communications system to at-risk users around the world.
Therefore, much of our design work involved combining the lessons learned from
NTCP2 and SSU with the features and security supported by QUIC and WireGuard.
{%- endtrans %}


{% trans -%}
Unlike QUIC, I2P transport protocols are peer-to-peer, with no defined server/client relationship.
Identities and public keys are published in I2P's network database,
and the handshake must authenticate participants to those identities.
{%- endtrans %}


{% trans -%}
A complete summary of the SSU2 design is beyond the scope of this article.
However, we highlight several features of the protocol below,
emphasizing the challenges of UDP protocol design and threat models.
{%- endtrans %}





{% trans %}DoS Resistance{% endtrans %}
`````````````````````````````````````````````````

{% trans -%}
UDP protocols are especially vulnerable to Denial of Service (DoS) attacks.
By sending a large amount of packets with spoofed source addresses to a victim,
an attacker can induce the victim to consume large amounts of CPU and bandwidth to respond.
In SSU2, we adapt the token concept from QUIC and WireGuard.
When a router receives a connection request without a valid token,
it does not perform an expensive cryptographic DH operation.
It simply responds with small message containing a valid token using inexpensive cryptographic operations.
If the initiator was not spoofing his address, he will receive the token and the handshake may proceed normally.
This prevents any traffic amplification attacks using spoofed addresses.
{%- endtrans %}



{% trans %}Header Encryption{% endtrans %}
`````````````````````````````````````````````````

{% trans -%}
SSU2's packet headers are similar to WireGuard, and are encrypted in a manner similar to that in QUIC.
{%- endtrans %}

{% trans -%}
Header encryption is vitally important to prevent traffic classification, protocol identification, and censorship.
Headers also contain information that would make it easier for attackers to interfere with
or even decrypt packet contents.
While nation-state firewalls are mostly focused on classification and possible disruption of TCP traffic,
we anticipate that their UDP capabilities will increase to meet the challenges of
new UDP protocols such as QUIC and WireGuard.
Ensuring that SSU2 headers are adequately obfuscated and/or encrypted was the first task we addressed.
{%- endtrans %}

{% trans link1="https://eprint.iacr.org/2019/624.pdf" -%}
Headers are encrypted using a header protection scheme by XORing with data calculated from known keys,
using ChaCha20, similar to QUIC RFC-9001_ and `Nonces are Noticed <{{ link1 }}>`_.
This ensures that the encrypted headers will appear to be random, without any distinguishable pattern.
{%- endtrans %}

{% trans link1="https://eprint.iacr.org/2019/624.pdf" -%}
Unlike the QUIC RFC-9001_ header protection scheme, all parts of all headers, including destination and source connection IDs, are encrypted.
QUIC RFC-9001_ and `Nonces are Noticed <{{ link1 }}>`_ are primarily focused on encrypting the "critical" part of the header, i.e. the packet number (ChaCha20 nonce).
While encrypting the session ID makes incoming packet classification a little more complex, it makes some attacks more difficult.
{%- endtrans %}

{% trans -%}
Our threat model assumes that censorship firewalls do not have real-time access to I2P's network database.
Headers are encrypted with known keys published in the network database or calculated later.
In the handshake phase, header encryption is for traffic classification resistance only,
as the decryption key is public and the key and nonces are reused.
Header encryption in this phase is effectively just obfuscation.
Note that the header encryption is also used to obfuscate the X25519 ephemeral keys in the handshake,
for additional protection.
{%- endtrans %}

{% trans -%}
In the data phase, only the session ID field is encrypted with a key from the network database.
The critical nonce field is encrypted with a key derived from the handshake,
so it may not be decrypted even by a party with access to the network database.
{%- endtrans %}




{% trans %}Packet Numbering, ACKS, and Retransmission{% endtrans %}
```````````````````````````````````````````````````````````````````````

{% trans link1="/en/docs/api/streaming" -%}
SSU2 contains several improvements over SSU for security and efficiency.
The packet number is the AEAD nonce, and each packet number is only used once.
Acknowledgements (ACKs) are for packet numbers, not I2NP message numbers or fragments.
ACKs are sent in a very efficient, compact format adapted from QUIC.
An immediate-ack request mechanism is supported, similar to SSU.
Congestion control, windowing, timers, and retransmission strategies are not fully specified,
to allow for implementation flexibility and improvements,
but general guidance is taken from the RFCs for TCP.
Additional algorithms for timers are adapted from I2P's `streaming protocol <{{ link1 }}>`_ and SSU implementations.
{%- endtrans %}





{% trans %}Connection Migration{% endtrans %}
`````````````````````````````````````````````````

{% trans -%}
UDP protocols are susceptible to breakage from peer port and IP changes
caused by NAT rebinding, IPv6 temporary address changes, and mobile device address changes.
Previous SSU implementations attempted to handle some of these cases with complex and brittle heuristics.
SSU2 provides a formal, documented process to detect and validate peer
address changes and migrate connections to the peer's new address without data loss.
It prevents migration caused by packet injection or modification by attackers.
The protocol to implement connection migration is adapted and simplified from QUIC.
{%- endtrans %}





{% trans %}Peer Test and Relay{% endtrans %}
`````````````````````````````````````````````````


{% trans -%}
SSU provides two important services in addition to the transport of I2NP messages.
First, it supports Peer Test, which is a cooperative scheme to determine local IP
and detect the presence of network address translation (NAT) and firewall devices.
This detection is used to update router state, share that state with other transports,
and publish current address and state in I2P's network database.
Second, it supports Relaying, in which routers cooperate to traverse firewalls
so that all routers may accept incoming connections.
These two services are essentially sub-protocols within the SSU transport.
{%- endtrans %}

{% trans -%}
SSU2 updates the security and reliability of these services by
enhancing them to add more response codes, encryption, authentication,
and restrictions to the design and implementation.
{%- endtrans %}





{% trans %}Performance{% endtrans %}
--------------------------------------------

{% trans -%}
The I2P network is a complex mix of diverse routers.
There are two primary implementations running all over the world on
hardware ranging from high-performance data center computers to
Raspberry Pis and Android phones.
Routers use both TCP and UDP transports.
While the SSU2 improvements are significant, we do not expect them
to be apparent to the user, either locally or in end-to-end transfer speeds.
End-to-end transfers depend on the performance of 13 other routers
and 14 point-to-point transport links, each of which could be
SSU2, NTCP2, or SSU.
{%- endtrans %}

{% trans -%}
In the live network, latency and packet loss vary widely.
Even in a test setup, performance depends on configured latency and packet loss.
The i2pd project reports that maximum transfer rates for SSU2 were over 3 times
faster than SSU in some tests. However, they completely redesigned their
SSU code for SSU2 as their previous implementation was rather poor.
The Java I2P project does not expect that their SSU2 implementation will be any faster than SSU.
{%- endtrans %}

{% trans -%}
Very low-end platforms such as Raspberry Pis and OpenWRT may see substantial improvements
from the elimination of SSU.
ElGamal is extremely slow and limits performance on those platforms.
{%- endtrans %}

{% trans -%}
SSU2 data phase encryption uses ChaCha20/Poly1305, compared to AES with a MD5 HMAC for SSU.
Both are very fast and the change is not expected to measurably affect performance.
{%- endtrans %}

{% trans -%}
Here are some highlights of the estimated improvements for SSU2 vs. SSU:
{%- endtrans %}

- {% trans %}40% reduction in total handshake packet size{% endtrans %}
- {% trans %}50% or more reduction in handshake CPU{% endtrans %}
- {% trans %}90% or more reduction in ACK overhead{% endtrans %}
- {% trans %}50% reduction in packet fragmentation{% endtrans %}
- {% trans %}10% reduction in data phase overhead{% endtrans %}



{% trans %}Transition Plan{% endtrans %}
--------------------------------------------

{% trans -%}
I2P strives to maintain backward compatibility, both to ensure network stability,
and to allow older routers to continue to be useful and secure.
However, there are limits, because compatibility increases code complexity
and maintenance requirements.
{%- endtrans %}


{% trans -%}
The Java I2P and i2pd projects will both enable SSU2 by default in their next releases (2.0.0 and 2.44.0) in late November 2022.
However, they have different plans for disabling SSU.
I2pd will disable SSU immediately, because SSU2 is a vast improvement over their SSU implementation.
Java I2P plans to disable SSU in mid-2023, to support a gradual transition
and give older routers time to upgrade.
Because Java I2P release 0.9.36 and i2pd release 2.20.0 (2018) were the first to support NTCP2,
routers older than that will not be able to connect to i2pd routers 2.44.0 or higher,
as they have no compatible transports.
{%- endtrans %}





{% trans %}Summary{% endtrans %}
------------------------------------

{% trans -%}
The founders of I2P had to make several choices for cryptographic algorithms and protocols.
Some of those choices were better than others, but twenty years later, most are showing their age.
Of course, we knew this was coming, and we've spent the last decade planning and implementing cryptographic upgrades.
As the old saying goes, upgrading things while maintaining backward compatibility
and avoiding a "flag day" is quite challenging, like changing the tires on the bus while it's rolling down the road.
{%- endtrans %}

{% trans -%}
SSU2 was the last and most complex protocol to develop in our long upgrade path.
UDP has a very challenging set of assumptions and threat model.
We first designed and rolled out three other flavors of Noise protocols,
and gained experience and deeper understanding of the security and protocol design issues.
Finally, we had to research and fully understand other modern UDP protocols - WireGuard and QUIC.
While the authors of those protocols didn't solve all of our problems for us,
their documentation of the UDP threat models and their designed countermeasures gave us the
confidence that we too would be able to complete our task.
We thank them as well as the creators of all the cryptography we rely on to keep our users safe.
{%- endtrans %}


{% trans -%}
Expect SSU2 to be enabled in the i2pd and Java I2P releases scheduled for late November 2022.
If the update goes well, nobody will notice anything different at all.
The performance benefits, while significant, will probably not be measurable for most people.
{%- endtrans %}


{% trans -%}
As usual, we recommend that you update to the new release when it's available.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}


.. _RFC-9000: https://www.rfc-editor.org/rfc/rfc9000.html
.. _RFC-9001: https://www.rfc-editor.org/rfc/rfc9001.html
.. _RFC-9002: https://www.rfc-editor.org/rfc/rfc9002.html
