===========================================
{% trans -%}SSU2 Transport{%- endtrans %}
===========================================

.. meta::
   :author: zzz
   :date: 2022-09-30
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

{% trans -%}
That's why, together with the i2pd project, we have created and implemented "SSU2",
a modern UDP protocol designed to the highest standards of security and blocking resistance.
{%- endtrans %}

{% trans -%}
We have combined industry-standard encryption with the best
features of UDP protocols WireGuard and QUIC, together with the
censorship resistance features of our TCP protocol "NTCP2".
SSU2 may be one of the most secure transport protocols ever designed.
{%- endtrans %}


{% trans link1="{{ proposal_url('159') }}", link2="{{ site_url('docs/transport/ssu') }}", link3="https://en.wikipedia.org/wiki/ElGamal_encryption" -%}
The Java I2P and i2pd teams are finishing the `SSU2 transport <{{ link1 }}>`_ and we will enable it for all routers in the next release.
This completes our decade-long plan to upgrade all the cryptography from the original
Java I2P implementation dating back to 2003.
SSU2 will replace `SSU <{{ link2 }}>`_, our last remaining use of `ElGamal <{{ link3 }}>`_ cryptography.
{%- endtrans %}

- Signature types and ECDSA signatures (0.9.12, 2014)
- ECDSA routers (??)
- Ed25519 signatures and leasesets (0.9.15, 2014)
- Ed25519 routers (0.9.22, 2015)
- Destination encryption types and X25519 leasesets (0.9.46, 2020)
- Router encryption types and X25519 routers (0.9.49, 2021)

{% trans link1="https://noiseprotocol.org/" -%}
With the completion of SSU2,
we will have migrated all our authenticated and encrypted protocols to standard `Noise Protocol <{{ link1 }}>`_ handshakes:
{%- endtrans %}

- `NTCP2 <{{ spec_url("ntcp2") }}>`_ (0.9.36, 2018)
- `{% trans %}Ratchet end-to-end protocol{% endtrans %} <{{ spec_url("ecies") }}>`_ (0.9.46, 2020)
- `{% trans %}ECIES tunnel build messages{% endtrans %} <{{ spec_url("tunnel-creation-ecies") }}>`_ (1.5.0, 2021)
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

{% trans link1="{{ spec_url('i2np') }}" -%}
SSU2, like previous I2P transport protocols, is not a general-purpose pipe for data.
Its primary job is to securely deliver I2P's low-level `I2NP messages <{{ link1 }}>`_
from one router to the next router.
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
SSU2's packet headers are similar to WireGuard, with encryption similar to that in QUIC.
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

{% trans -%}
Headers are encrypted with known keys published in the network database or calculated later.
In the handshake phase, this is for DPI resistance only, as the key is public and the key and nonces are reused,
so it is effectively just obfuscation.
Note that the header encryption is also used to obfuscate the X25519 ephemeral keys in the handshake,
to inhibit protocol identification.
{%- endtrans %}

{% trans link1="https://eprint.iacr.org/2019/624.pdf" -%}
Headers are encrypted using a header protection scheme by XORing with data calculated from known keys,
using ChaCha20, similar to QUIC [RFC-9001] and `Nonces are Noticed <{{ link1 }}>`_.
This ensures that the encrypted short header and the first part of the long header will appear to be random.
{%- endtrans %}

{% trans -%}
Unlike the QUIC [RFC-9001] header protection scheme, all parts of all headers, including destination and source connection IDs, are encrypted.
QUIC [RFC-9001] and [Nonces] are primarily focused on encrypting the "critical" part of the header, i.e. the packet number (ChaCha20 nonce).
While encrypting the session ID makes incoming packet classification a little more complex, it makes some attacks more difficult.
{%- endtrans %}







{% trans %}Packet Numbering, ACKS, and Retransmission{% endtrans %}
```````````````````````````````````````````````````````````````````````

{% trans link1="{{ spec_url('streaming') }}" -%}
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
enhancing the sub-protocols to add more response codes, encryption, authentication,
and restrictions to the design and implementation.
{%- endtrans %}





{% trans %}Summary{% endtrans %}
------------------------------------

{% trans -%}
The founders of I2P had to make plenty of choices for cryptographic algorithms and protocols.
Some of those choices were better than others, but twenty years later, most are showing their age.
Of course, we knew this was coming, and we've spent the last decade planning and making changes.
As the old saying goes, upgrading protocols while maintaining backward compatibility
and avoiding a "flag day" is like changing the tires on the bus while it's rolling down the road.
{%- endtrans %}

{% trans -%}
The final and most complex protocol to develop in our long upgrade path has been SSU2.
UDP has a very challenging set of assumptions and threat model.
We first needed to design and roll out three other flavors of Noise protocols,
and gain experience and deeper understanding of security and protocol design issues.
Finally, we had to discover, research, and fully understand two modern UDP protocols - WireGuard and QUIC.
While the authors of those protocols didn't solve all of our problems for us,
the documentation of the UDP threat models and their designed countermeasures gave us the
confidence that we too would be able to complete our task.
We thank them as well as the creators of all the cryptography we rely on to keep our users safe.
{%- endtrans %}


{% trans -%}
Expect SSU2 to be enabled in the i2pd and Java I2P releases scheduled for November 2022.
If the update goes well, nobody will notice anything different at all.
It's just additional protection for whatever is coming at us next.
{%- endtrans %}
