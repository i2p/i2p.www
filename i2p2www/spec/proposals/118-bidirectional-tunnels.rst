=====================
Bidirectional Tunnels
=====================
.. meta::
    :author: orignal
    :created: 2016-01-07
    :thread: http://zzz.i2p/topics/2041
    :lastupdated: 2016-01-07
    :status: Draft

.. contents::


Introduction
============

i2pd is going to introduce bi-directional tunnels build through other i2pd
routers only for now. For the network their will appear as regular inbound and
outbound tunnels.

Goals
=====

1. Reduce network and CPU usage by reducing number of TunnelBuild messages
2. Ability to know instantly if a participant has gone away.
3. More accurate profiling and stats
4. Use other darknets as intermediate peers

Tunnel modifications
====================

TunnelBuild
-----------

Tunnels are built the same way as inbound tunnels. No reply message is required.
There is special type of participant called "entrance" marked by flag, serving
as IBGW and OBEP at the same time. Message has the same format as
VaribaleTunnelBuild but ClearText contains different fields::

    in_tunnel_id
    out_tunnel_id
    in_next_tunnel_id
    out_next_tunnel_id
    in_next_ident
    out_next_ident
    layer_key, iv_key

It will also contain field mentioning what darknet next peer belong to and some
additional information if it's not I2P.

TunnelTermination
-----------------

If peer want to go away it creates TunnelTermination messages encrypts with
layer key and send in "in" direction. If a participant receive such message it
encrypts it over with it's layer key and send to next peer. Once a messsage
reaches tunnel owner it's start decrypting peer-by-peer until gets unencrypted
message. It finds out which peer has gone away and terminate tunnel.
