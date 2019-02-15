{% trans -%}
=========================================================
Developing privacy-aware applications with Python and I2P
=========================================================
{%- endtrans %}

.. meta::
    :author: villain
    :date: 2018-10-23
    :category: development
    :excerpt: {% trans %}Basic concepts of I2P application development with Python{% endtrans %}

.. image:: {{ url_for('static', filename='images/blog/i2plib.jpeg') }}
   :align: center
   :width: 700px
   :alt: {% trans %}i2plib{% endtrans %}

{% trans -%}
`Invisible Internet Project`_ (I2P) provides a framework for
developing privacy-aware applications. It is a virtual network working on top of
the regular Internet, in which hosts can exchange data without disclosing their
"real" IP addresses. Connections inside I2P network are established between 
virtual addresses called *I2P destinations*. It's possible to have as many
of destinations as one needs, even use a new destination for each connection,
they don't disclose any information about the real IP address to the other
side. 
{%- endtrans %}

.. _`Invisible Internet Project`: https://geti2p.net/

{% trans -%}
This article describes basic concepts one needs to know when developing I2P
applications. Code samples are written in Python with the use of built-in
asynchronous framework asyncio.
{%- endtrans %}

{% trans -%}
Enabling SAM API and i2plib installation
========================================
{%- endtrans %}

{% trans -%}
I2P provides many different APIs to the client applications. Regular
client-server apps can use I2PTunnel, HTTP and Socks proxies, Java applications 
usually use I2CP. For developing with other languages, like Python, the best 
option is `SAM`_. SAM is disabled by 
default in the original Java client implementation, so we need to enable it. 
Go to Router Console, page "I2P internals" -> "Clients". Check "Run at Startup" 
and press "Start", then "Save Client Configuration".
{%- endtrans %}

.. _`SAM`: https://geti2p.net/en/docs/api/samv3

.. image:: {{ url_for('static', filename='images/enable-sam.jpeg') }}
   :align: center
   :width: 700px
   :alt: {% trans %}Enable SAM API{% endtrans %}

{% trans -%}
`C++ implementation i2pd`_ has SAM enabled by default.
{%- endtrans %}

.. _`C++ implementation i2pd`: https://i2pd.website

{% trans -%}
I've developed a handy Python library for SAM API called
`i2plib`_. You can install it with pip or
manually download the source code from GitHub. 
{%- endtrans %}

.. _`i2plib`: https://github.com/l-n-s/i2plib


::

    pip install i2plib


{% trans -%}
This library works with the Python's built-in `asynchronous framework asyncio`_,
so please note that code samples are taken from async functions (coroutines)
which are running inside the event loop. Additional examples of i2plib usage can
be found in the `source code repository`_.
{%- endtrans %}

.. _`asynchronous framework asyncio`: https://docs.python.org/3/library/asyncio.html
.. _`source code repository`: https://github.com/l-n-s/i2plib/tree/master/docs/examples
    
{% trans -%}
I2P Destination and session creation
====================================
{%- endtrans %}

{% trans -%}
I2P destination is literally a set of encryption and cryptographic signature
keys. Public keys from this set are published to the I2P network and are used to
make connections instead of IP addresses.
{%- endtrans %}

{% trans -%}
This is how you create `i2plib.Destination`_:
{%- endtrans %}

.. _`i2plib.Destination`: https://i2plib.readthedocs.io/en/latest/api.html#i2plib.Destination

.. sourcecode:: python

    dest = await i2plib.new_destination()
    print(dest.base32 + ".b32.i2p") # print base32 address


{% trans -%}
base32 address is a hash which is used by other peers to discover your full
Destination in the network. If you plan to use this destination as a permanent
address in your program, save the binary data from *dest.private\_key.data* 
to a local file.
{%- endtrans %}

{% trans -%}
Now you can create a SAM session, which literally means to make the Destination
online in I2P:
{%- endtrans %}

.. sourcecode:: python

        session_nickname = "test-i2p" # each session must have unique nickname
        _, session_writer = await i2plib.create_session(session_nickname, destination=dest)


{% trans -%}
Important note here: Destination will remain online while *session\_writer* socket
is kept open. If you wish to switch it off, you can call *session\_writer.close()*.
{%- endtrans %}

{% trans -%}
Making outgoing connections
===========================
{%- endtrans %}

{% trans -%}
Now when the Destination is online, you can use it to connect to other peers.
For example, this is how you connect to
"udhdrtrcetjm5sxzskjyr5ztpeszydbh4dpl3pl4utgqqw2v4jna.b32.i2p", send HTTP GET
request and read the response (it is "i2p-projekt.i2p" web server):
{%- endtrans %}

.. sourcecode:: python

    remote_host = "udhdrtrcetjm5sxzskjyr5ztpeszydbh4dpl3pl4utgqqw2v4jna.b32.i2p"
    reader, writer = await i2plib.stream_connect(session_nickname, remote_host)

    writer.write("GET /en/ HTTP/1.0\nHost: {}\r\n\r\n".format(remote_host).encode())

    buflen, resp = 4096, b""
    while 1:
        data = await reader.read(buflen)
        if len(data) > 0:
            resp += data
        else:
            break

    writer.close()
    print(resp.decode())


{% trans -%}
Accepting incoming connections
==============================
{%- endtrans %}

{% trans -%}
While making outgoing connections is trivial, when you accept connections there
is one important detail. After a new client is connected, SAM API sends an ASCII
string with base64-encoded client's Destination to the socket. Since Destination 
and data can come in one chunk, you should be aware of it.
{%- endtrans %}

{% trans -%}
This is how a simple PING-PONG server looks like. It accepts incoming
connection, saves client's Destination to a *remote\_destination* variable and
sends back "PONG" string:
{%- endtrans %}

.. sourcecode:: python

    async def handle_client(incoming, reader, writer):
        """Client connection handler"""
        dest, data = incoming.split(b"\n", 1)
        remote_destination = i2plib.Destination(dest.decode())
        if not data:
            data = await reader.read(BUFFER_SIZE)
        if data == b"PING":
            writer.write(b"PONG")
        writer.close()

    # An endless loop which accepts connetions and runs a client handler
    while True:
        reader, writer = await i2plib.stream_accept(session_nickname)
        incoming = await reader.read(BUFFER_SIZE)
        asyncio.ensure_future(handle_client(incoming, reader, writer))


{% trans -%}
More info
=========
{%- endtrans %}

{% trans -%}
This article describes the usage of a TCP-like Streaming protocol. SAM API also
provides a UDP-like protocol to send and receive datagrams. This feature will
be added to i2plib later. 
{%- endtrans %}

{% trans -%}
This is just a basic information, but it's enough to start your own project with
the use of I2P. Invisible Internet is a great tool to develop all kinds of
privacy-aware applications. There are no design constraints by the network,
those applications can be client-server as well as P2P. 
{%- endtrans %}

- `Examples of i2plib usage`_
- `i2plib documentation`_
- `i2plib at GitHub`_
- `SAM API documentation`_ 
- `asyncio documentation`_ 
- `I2P network technical overview`_

.. _`Examples of i2plib usage`: https://github.com/l-n-s/i2plib/tree/master/docs/examples
.. _`i2plib documentation`: https://i2plib.readthedocs.io/en/latest/
.. _`i2plib at GitHub`: https://github.com/l-n-s/i2plib
.. _`SAM API documentation`: https://geti2p.net/en/docs/api/samv3
.. _`asyncio documentation`: https://docs.python.org/3/library/asyncio.html
.. _`I2P network technical overview`: https://geti2p.net/en/docs/how/tech-intro
