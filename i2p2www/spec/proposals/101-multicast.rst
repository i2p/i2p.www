=========
Multicast
=========
.. meta::
    :author: zzz
    :created: 2008-12-08
    :thread: http://zzz.i2p/topics/172
    :lastupdated: 2009-03-25
    :status: Draft

.. contents::


Introduction
============

Basic idea: Send one copy through your outbound tunnel, outbound endpoint
distributes to all the inbound gateways. End-end encryption precluded.


Thoughts
========

- New multicast tunnel message type (delivery type = 0x03)
- Outbound endpoint multicast distribute
- New I2NP Multicast Message type ?
- New I2CP Multicast SendMessageMessage Message type
- Don't encrypt router-router in OutNetMessageOneShotJob (garlic?)

App:

- RTSP Proxy?

Streamr:

- Tune MTU? Or just do it at the app?
- On-demand receive & transmit
