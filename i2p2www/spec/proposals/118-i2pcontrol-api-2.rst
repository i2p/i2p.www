================
I2PControl API 2
================
.. meta::
    :author: hottuna
    :created: 2016-01-23
    :thread: http://zzz.i2p/topics/2030
    :lastupdated: 2016-02-01
    :status: Open

.. contents::


Overview
========

This proposal outlines API2 for I2PControl.


Developer headsup!
------------------

All RPC paramters will now be lower case. This *will* break backwards
compatibility with API1 implementations. The reasons for this is to provide
users of >=API2 with simplest most coherent possible API.


API 2 Specification
===================

.. raw:: html

  {% highlight lang='json' -%}
{
    "id": "id",
    "method": "method_name",
    "params": {
      "token": "auth_token",
      "method_param": "method_parameter_value",
    },
    "jsonrpc": "2.0"
  }

  {
    "id": "id",
    "result": "result_value",
    "jsonrpc": "2.0"
  }
{% endhighlight %}

Parameters
----------

"id"
  The id number or the request.

  Used to identify which reply was spawn by which request.

"method_name"
  The name of the RPC that is being invoked.

"auth_token"
  The session authentication token.

  Needs to be supplied with every RPC except for the 'authenticate' call.

"method_parameter_value"
  The method parameter.

  Used to offer a different flavors of a method.  Like 'get', 'set' and flavors
  like that.

"result_value"
  The value that the RPC returns. Its type and contents depends on the method
  and which method.


Prefixes
--------

The RPC naming scheme is similar to how it's done in CSS, with vendor prefixes
for the different API implementations (i2p, kovri, i2pd)::

    XXX.YYY.ZZZ
    i2p.XXX.YYY.ZZZ
    i2pd.XXX.YYY.ZZZ
    kovri.XXX.YYY.ZZZ

The overall idea with vendor-specific prefixes is to allow for some wiggle room
and let implementations innovate without having to wait for every other
implementation to catch up. If a RPC is implemented by all implementations its
multiple prefixes can be removed and it can be included as a core RPC in the
next API version.


Method reading guide
--------------------

 * **rpc.method**

   * *parameter* [type of parameter]:  [null], [number], [string], [boolean],
     [array] or [object]. [object] being a {key:value} map.

::

  "return_value" [string] // This is the value returned by the RPC call


Methods
-------

* **authenticate** - Given that a correct password is provided, this method provides you with a token for further access and a list of supported API levels.

  * *password* [string]:  The password for this i2pcontrol implementation

  ::

    [object]
    {
      "token" : [string], // The token to be used be supplied with all other RPC methods
      "api" : [[int],[int], ...]  // A list of supported API levels.
    }


* **control.** - Control i2p

  * **control.reseed** - Start reseeding

    * [nil]: No parameter needed

    ::

      [nil]

  * **control.restart** - Restart i2p instance

    * [nil]: No parameter needed

    ::

      [nil]

  * **control.restart.graceful** - Restart i2p instance gracefully

    * [nil]: No parameter needed

    ::

      [nil]

  * **control.shutdown** - Shut down i2p instance

    * [nil]: No parameter needed

    ::

      [nil]

  * **control.shutdown.graceful** - Shut down i2p instance gracefully

    * [nil]: No parameter needed

    ::

      [nil]

  * **control.update.find** - **BLOCKING** Search for signed updates

    * [nil]: No parameter needed

    ::

      true [boolean] // True iff signed update is available

  * **control.update.start** - Start update process

    * [nil]: No parameter needed

    ::

      [nil]


* **i2pcontrol.** - Configure i2pcontrol

  * **i2pcontrol.address** - Get/Set the ip address that i2pcontrol listens to.

    * *get* [null]: This parameter does not need to be set.

    ::

      "0.0.0.0" [string]

    * *set* [string]: This will be an ip address like "0.0.0.0" or "192.168.0.1"

    ::

      [nil]

  * **i2pcontrol.password** - Change the i2pcontrol password.

    * *set* [string]: Set the new password to this string

    ::

      [nil]

  * **i2pcontrol.port** - Get/Set the port that i2pcontrol listens to.

    * *get* [null]: This parameter does not need to be set.

    ::

      7650 [number]

    * *set* [number]: Change the port that i2pcontrol listens to to this port

    ::

      [nil]


* **settings.** - Get/Set i2p instance settings

  * **settings.advanced** - Advanced settings

    * *get*  [string]: Get the value of this setting

    ::

      "setting-value" [string]

    * *getAll* [null]:

    ::

      [object]
      {
        "setting-name" : "setting-value", [string]
        ".." : ".." 
      }

    * *set* [string]: Set the value of this setting
    * *setAll* [object] {"setting-name" : "setting-value", ".." : ".." }

    ::

      [nil]

  * **settings.bandwidth.in** - Inbound bandwidth settings
  * **settings.bandwidth.out** - Outbound bandwidth settings

    * *get* [nil]: This parameter does not need to be set.

    ::

      0 [number]

    * *set* [number]: Set the bandwidth limit

    ::

     [nil]

  * **settings.ntcp.autoip** - Get IP auto detection setting for NTCP

    * *get* [null]: This parameter does not need to be set.

    ::

      true [boolean]

  * **settings.ntcp.hostname** - Get NTCP hostname

    * *get* [null]: This parameter does not need to be set.

    ::

      "0.0.0.0" [string]

    * *set* [string]: Set new hostname

    ::

      [nil]

  * **settings.ntcp.port** - NTCP port

    * *get* [null]: This parameter does not need to be set.

    ::

      0 [number]

    * *set* [number]: Set new NTCP port.

    ::

      [nil]

    * *set* [boolean]: Set NTCP IP auto detection

    ::

      [nil]

  * **settings.ssu.autoip** - Configure IP auto detection setting for SSU

    * *get* [nil]: This parameter does not need to be set.

    ::

      true [boolean]

  * **settings.ssu.hostname** - Configure SSU hostname

    * *get* [null]: This parameter does not need to be set.

    ::

      "0.0.0.0" [string]

    * *set* [string]: Set new SSU hostname

    ::

      [nil]

  * **settings.ssu.port** - SSU port

    * *get* [null]: This parameter does not need to be set.

    ::

      0 [number]

    * *set* [number]: Set new SSU port.

    ::

      [nil]

    * *set* [boolean]: Set SSU IP auto detection

    ::

      [nil]

  * **settings.share** - Get bandwidth share percentage

    * *get* [null]: This parameter does not need to be set.

    ::

      0 [number] // Bandwidth share percentage (0-100)

    * *set* [number]: Set bandwidth share percentage (0-100)

  * **settings.upnp** - Enable or disable UPNP

    * *get* [nil]: This parameter does not need to be set.

    ::

      true [boolean]

    * *set* [boolean]: Set SSU IP auto detection

    ::

      [nil]



* **stats.** - Get stats from the i2p instance

  * **stats.advanced** - This method provides access to all stats kept within the instance.

    * *get* [string]:  Name of the advanced stat to be provided
    * *Optional:* *period* [number]:  The period for the requested stat

  * **stats.knownpeers** - Returns the number of known peers
  * **stats.uptime** - Returns the time in ms since the router started
  * **stats.bandwidth.in** - Returns the inbound bandwidth (ideally for the last second)
  * **stats.bandwidth.in.total** - Returns the number of bytes received since last restart
  * **stats.bandwidth.out** - Returns the outbound bandwidth (ideally for the last second)'
  * **stats.bandwidth.out.total** - Returns the number of bytes sent since last restart'
  * **stats.tunnels.participating** - Returns the number of tunnels participated in currently
  * **stats.netdb.peers.active** - Returns the number of peers we've recently communicated with
  * **stats.netdb.peers.fast** - Returns the number of 'fast' peers
  * **stats.netdb.peers.highcapacity** - Returns the number of 'high capacity' peers
  * **stats.netdb.peers.known** - Returns the number of known peers

    * *get* [null]: This parameter does not need to be set.

    ::

      0.0 [number]


* **status.** - Get i2p instance status

  * **status.router** - Get router status

    * *get* [null]: This parameter does not need to be set.

    ::

      "status" [string]

  * **status.net** - Get router network status

    * *get* [null]: This parameter does not need to be set.

    ::

      0 [number]
      /**
       *    0 – OK
       *    1 – TESTING
       *    2 – FIREWALLED
       *    3 – HIDDEN
       *    4 – WARN_FIREWALLED_AND_FAST
       *    5 – WARN_FIREWALLED_AND_FLOODFILL
       *    6 – WARN_FIREWALLED_WITH_INBOUND_TCP
       *    7 – WARN_FIREWALLED_WITH_UDP_DISABLED
       *    8 – ERROR_I2CP
       *    9 – ERROR_CLOCK_SKEW
       *   10 – ERROR_PRIVATE_TCP_ADDRESS
       *   11 – ERROR_SYMMETRIC_NAT
       *   12 – ERROR_UDP_PORT_IN_USE
       *   13 – ERROR_NO_ACTIVE_PEERS_CHECK_CONNECTION_AND_FIREWALL
       *   14 – ERROR_UDP_DISABLED_AND_TCP_UNSET
       */

  * **status.isfloodfill** - Is the i2p instance currently a floodfill

    * *get* [null]: This parameter does not need to be set.

    ::

      true [boolean]

  * **status.isreseeding** - Is the i2p instance currently reseeding

    * *get* [null]: This parameter does not need to be set.

    ::

      true [boolean]

  * **status.ip** - Public IP detected of this i2p instance

    * *get* [null]: This parameter does not need to be set.

    ::

      "0.0.0.0" [string]
