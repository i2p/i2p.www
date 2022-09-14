===========================================
{% trans -%}SSU2 Transport{%- endtrans %}
===========================================

.. meta::
   :author: zzz
   :date: 2022-09-30
   :category: development
   :excerpt: {% trans %}SSU2 Transport{% endtrans %}

{% trans link1="{{proposal_url("159")}}" link2="{{ site_url('docs/transport/ssu') }}" link3="https://en.wikipedia.org/wiki/ElGamal_encryption" -%}
The Java I2P and i2pd teams are finishing the `SSU2 <{{ link1 }}>`_ transport and we will enable it for all in the next release.
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
We have now migrated all our authenticated and encrypted protocols to Noise handshakes:
{%- endtrans %}

- `NTCP2 <{{spec_url("ntcp2")}}>`_ (0.9.36, 2018)
- `{% trans %}Ratchet end-to-end protocol{% endtrans %} <{{spec_url("ecies")}}>`_ (0.9.46, 2020)
- `{% trans %}ECIES tunnel build messages{% endtrans %} <{{spec_url("tunnel-creation-ecies")}}>`_ (1.5.0, 2021)
- `SSU2 <{{proposal_url("159")}}>`_ (2.0.0, 2022)

{% trans -%}
All Noise protocols use the following standard cryptographic algorithms:
{%- endtrans %}

- `X25519 <https://en.wikipedia.org/wiki/Curve25519>`_
- `ChaCha20/Poly1305 AEAD <https://www.rfc-editor.org/rfc/rfc8439.html>`_
- `SHA-256 <https://en.wikipedia.org/wiki/SHA-2>`_

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


