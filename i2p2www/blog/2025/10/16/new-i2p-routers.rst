{% trans -%}
===============
New I2P Routers
===============
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2025-10-16
    :category: development
    :excerpt: {% trans %}An overview of new I2P router implementations and how to get involved.{% endtrans %}

{% trans -%}
It's an exciting time for I2P development, our community is growing and there are now multiple new, fully-functioning I2P router prototypes emerging on the scene!
We're very excited about this development and about sharing the news with you.
{%- endtrans %}

{% trans -%}
How does this help the network?
{%- endtrans %}
===============================

{% trans -%}
Writing I2P routers helps us prove that our specification documents can be used to produce new I2P routers, opens up the code to new analysis tools, and generally improves the security and interoperability of the network.
Multiple I2P routers means that potential bugs are not uniform, an attack on one router may not work on a different router, avoiding a monoculture problem.
Perhaps the most exciting prospect in the long-term, however, is ``embedding``.
{%- endtrans %}

{% trans -%}
What is ``embedding``?
{%- endtrans %}
======================

{% trans -%}
In the context of I2P, ``embedding`` is a way of including an I2P router in another app directly, without requiring a freestanding router running in the background.
This is a way we can make I2P easier to use, which makes the network easier to grow by making the software more accessible.
Both Java and C++ suffer from being difficult to use outside of their own ecosystems, with C++ requiring brittle handwritten C bindings and in the case of Java, the pain of communicating with a JVM application from a non-JVM application.
{%- endtrans %}

{% trans -%}
While in many ways this situation is quite normal, I believe it can be improved to make I2P more accessible.
Other languages have more elegant solutions to these problems.
Of course, we should always consider and use the existing guidelines for the Java and C++ routers.
{%- endtrans %}

{% trans -%}
``emissary`` appears from the darkness
{%- endtrans %}
======================================

{% trans -%}
Completely independent from our team, a developer called ``altonen`` has developed a Rust implementation of I2P called ``emissary``.
While it's quite new still, and Rust is unfamiliar to us, this intriguing project has great promise.
Congratulations to altonen for creating ``emissary``, we are quite impressed.
{%- endtrans %}

{% trans -%}
Why Rust?
{%- endtrans %}
---------

{% trans -%}
The main reason to use Rust is basically the same as the reason to use Java or Go.
Rust is a compiled programming language with memory management and a huge, highly enthusiastic community.
Rust also offers advanced features for producing bindings to the C programming language which may be easier to maintain than in other languages while still inheriting Rust's strong memory-safety features.
{%- endtrans %}

{% trans -%}
Do you want to get involved with ``emissary``?
{%- endtrans %}
-----------------------------------------------

{% trans -%}
``emissary`` is developed on Github by ``altonen``.
You can find the repository at: `altonen/emissary <https://github.com/altonen/emissary>`_.
Rust also suffers from a lack of comprehensive SAMv3 client libraries that are compatible with popular Rust networking stuff, writing a SAMv3 library is a great place to start.
{%- endtrans %}

{% trans -%}
``go-i2p`` is getting closer to completion
{%- endtrans %}
==========================================

{% trans -%}
For about 3 years I've been working on ``go-i2p``, trying to turn a fledgeling library into a fully-fledged I2P router in pure-Go, another memory-safe language.
In the past 6 months or so, it has been drastically restructured to improve performance, reliability, and maintainability.
{%- endtrans %}

{% trans -%}
Why Go?
{%- endtrans %}
-------

{% trans -%}
While Rust and Go have many of the same advantages, in many ways Go is much simpler to learn.
For years, there have been excellent libraries and applications for using I2P in the Go programming language, including the most complete implementations of the SAMv3.3 libraries.
The point of go-i2p is bridge that gap, and to remove all the rough edges for I2P application developers who are working in Go.
{%- endtrans %}

{% trans -%}
Do you want to get involved with ``go-i2p``?
{%- endtrans %}
---------------------------------------------

{% trans -%}
``go-i2p`` is developed on Github, primarily by ``eyedeekay`` at this time and open to contributions from the community at `go-i2p <https://github.com/go-i2p/>`_.
Within this namespace exist many projects, such as:
{%- endtrans %}

{% trans -%}
Router Libraries
{%- endtrans %}
~~~~~~~~~~~~~~~~

{% trans -%}
We built these libraries to produce our I2P router libraries.
They're spread out into multiple, focused repositories to ease review and make them useful to other people who want to build experimental, custom I2P routers.
{%- endtrans %}

- `go-i2p the router itself, most active right now <https://github.com/go-i2p/go-i2p>`_
- `common our core library for I2P datastructures <https://github.com/go-i2p/common>`_
- `crypto our library for cryptographic operations <https://github.com/go-i2p/crypto>`_
- `go-noise a library for implementing noise-based connections <https://github.com/go-i2p/go-noise>`_
- `noise a low-level library for using the Noise framework <https://github.com/go-i2p/noise>`_
- `su3 a library for manipulating su3 files <https://github.com/go-i2p/su3>`_

{% trans -%}
Client libraries
{%- endtrans %}
~~~~~~~~~~~~~~~~

- `onramp a very convenient library for using(or combining) I2P and Tor <https://github.com/go-i2p/onramp>`_
- `go-sam-go an advanced, efficient, and very complete SAMv3 library <https://github.com/go-i2p/go-sam-go>`_

{% trans -%}
If you don't like Go or Rust and are thinking of writing an I2P Router, what should you do?
{%- endtrans %}
============================================================================================

{% trans -%}
Well there's a dormant project to write an `I2P router in C# <https://github.com/PeterZander/i2p-cs>`_ if you want to run I2P on an XBox.
Sounds pretty neat actually.
If that's not your preference either, you could do like ``altonen`` did and develop a whole new one.
{%- endtrans %}

{% trans -%}
Decide why you're writing it, who you're writing it for
{%- endtrans %}
-------------------------------------------------------

{% trans -%}
You can write an I2P router for any reason, it's a free network, but it will help you to know why.
Is there a community you want to empower, a tool you think is a good fit for I2P, or a strategy you want to try out?
Figure out what your goal is to figure out where you need to start, and what a "finished" state will look like.
{%- endtrans %}

{% trans -%}
Decide what language you want to do it in and why
{%- endtrans %}
--------------------------------------------------

{% trans -%}
Here are some reasons you might choose a language:
{%- endtrans %}

- C: No need for binding-generation, supported everywhere, can be called from any language, lingua franca of modern computing
- Typescript: Massive community, lots of applications, services, and libraries, works with ``node`` and ``deno``, seems like it's everywhere right now
- D: It's memory safe and not Rust or Go
- Vala: It emits C code for the target platform, combining some of the advantages of memory-safe languages with the flexibility of C
- Python: Everybody uses Python

{% trans -%}
But here are some reasons why you might not choose those languages:
{%- endtrans %}

- C: Memory management can be challenging, leading to impactful bugs
- Typescript: TypeScript is transpiled to JavaScript, which is interpreted and may impact performance
- D: Relatively small community
- Vala: Not a lot of underlying infrastructure in Vala, you end up using C versions of most libraries
- Python: It's an interpreted language which may impact performance

{% trans -%}
There are hundreds of programming languages and we welcome maintained I2P libraries and routers in all of them. Choose your trade-offs wisely and begin.
{%- endtrans %}

{% trans -%}
Get in touch and start coding
{%- endtrans %}
=============================

{% trans -%}
Whether you want to work in Rust, Go, Java, C++ or some other language, get in touch with us at #i2p-dev on Irc2P.
Start there, and we'll onboard you to router-specific channels.
We are also present on ramble.i2p at f/i2p, on reddit at r/i2p, and on GitHub and git.idk.i2p.
We look forward to hearing from you soon.
{%- endtrans %}
