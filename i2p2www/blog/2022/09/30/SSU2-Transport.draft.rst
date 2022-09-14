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
That's why, together with i2pd, we have designed and implemented "SSU2",
A modern UDP protocol designed to the highest standards of security and blocking resistance.
{%- endtrans %}

{% trans -%}
We have combined industry-standard encryption with the best
features of UDP protocols Wireguard and QUIC, together with the
censorship resistance features of our TCP protocol "NTCP2".
SSU2 may be one of the most secure transport protocols ever designed.
{%- endtrans %}


{% trans link1="{{proposal_url('159')}}", link2="{{ site_url('docs/transport/ssu') }}", link3="https://en.wikipedia.org/wiki/ElGamal_encryption" -%}
The Java I2P and i2pd teams are finishing the `SSU2 transport <{{ link1 }}>`_ and we will enable it for all in the next release.
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

{% trans -%}
With the completion of SSU2,
we will have migrated all our authenticated and encrypted protocols to Noise handshakes:
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


{% trans -%}
Designing a UDP transport presents unique and complex challenges not present in TCP protocols.
A UDP protocol must handle security issues caused by address spoofing,
and must implement its own congestion control.
{%- endtrans %}

{% trans -%}
We first relied heavily on our previous experience with our NTCP2, SSU, and streaming protocols.
Then, we carefully reviewed and borrowed heavily from two recently-developed UDP protocols:
{%- endtrans %}

- QUIC (`RFC 9000 <https://www.rfc-editor.org/rfc/rfc9000.html>`_, `RFC 9001 <https://www.rfc-editor.org/rfc/rfc9001.html>`_, `RFC 9002 <https://www.rfc-editor.org/rfc/rfc9002.html>`_)
- `Wireguard <https://www.wireguard.com/protocol/>`_




{% trans %}Header Encryption{% endtrans %}
`````````````````````````````````````````````````




{% trans %}Packet Numbering, ACKS, and Retransmission{% endtrans %}
```````````````````````````````````````````````````````````````````````




{% trans %}Connection Migration{% endtrans %}
`````````````````````````````````````````````````





{% trans %}Peer Test and Relay{% endtrans %}
`````````````````````````````````````````````````

