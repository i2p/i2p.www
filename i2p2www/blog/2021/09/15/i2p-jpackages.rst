==========================================================================
{% trans -%}Improving I2P Adoption and Onboarding using Jpackage, I2P-Zero{%- endtrans %}
==========================================================================

.. meta::
   :author: idk
   :date: 2021-09-15
   :category: general
   :excerpt: {% trans %}Versatile and emerging ways of installing and embedding I2P in your application{% endtrans %}

{% trans -%}
For the majority of I2P's existence, it's been an application that runs with the
help of a Java Virtual Machine that is already installed on the platform. This
has always been the normal way to distribute Java applications, but it leads to
a complicated installation procedure for many people. To make things even more
complicated, the "right answer" to making I2P easy to install on any given
platform might not be the same as any other platform. For example, I2P is quite
simple to install with standard tools on Debian and Ubuntu based operating
systems, because we can simply list the required Java components as "Required"
by our package, however on Windows or OSX, there is no such system allowing us to make
sure that a compatible Java is installed.
{%- endtrans %}

{% trans -%}
The obvious solution would be to manage the Java installation ourselves, but
this used to a problem in-and-of-itself, outside of the scope of I2P. However,
in recent Java versions, a new set of options has emerged which has the
potential to solve this problem for many Java software. This exciting tool is
called **"Jpackage."**
{%- endtrans %}

{% trans -%}
I2P-Zero and Dependency-Free I2P Installation
{%- endtrans %}
---------------------------------------------

{% trans -%}
The first very successful effort at building a dependency-free I2P Package was
I2P-Zero, which was created by the Monero project originally for use with the
Monero cryptocurrency. This project got us very excited because of it's success
in creating a general-purpose I2P router which could easily packaged with an
I2P application. Especially on Reddit, many people express their preference for
the simplicity of setting up an I2P-Zero router.
{%- endtrans %}

{% trans -%}
This really proved to us that a dependency-free I2P Package which was easy to
install was possible using modern Java tools, but I2P-Zero's use case was a
little bit different than ours. It is best for embedded apps that need an I2P
router that they can easily control using it's convenient control port on port
"8051". Our next step would be to adapt the technology to the general-purpose
I2P Application.
{%- endtrans %}

{% trans -%}
OSX Application Security Changes affect I2P IzPack Installer
{%- endtrans %}
------------------------------------------------------------

{% trans -%}
The issue became more pressing in recent versions of Mac OSX, where it is no
longer straightforward to use the "Classic" installer which comes in the .jar
format. This is because the application is not "Notarized" by Apple authorities
and it is deemed a security risk. **However**, Jpackage can produce a .dmg file,
which can be notarized by Apple authorities, conveniently solving our problem.
{%- endtrans %}

{% trans -%}
The new I2P .dmg installer, created by Zlatinb, makes I2P easier to install on
OSX than ever, no longer requiring users to install Java themselves and using
standard OSX installation tools in their prescribed ways. The new .dmg installer
makes setting up I2P on Mac OSX easier than it's ever been.
{%- endtrans %}

Get the dmg_.

.. _dmg: /mac

{% trans -%}
The I2P of the future is Easy to Install
{%- endtrans %}
----------------------------------------

{% trans -%}
One of the things I hear from users the most is that if I2P wants adoption, it
needs to be easy to use for people. Many of them want a "Tor Browser Like" user
experience, to quote or paraphrase many familiar Redditors. Installation should
not require complicated and error-prone "post-installation" steps. Many new
users are not prepared to deal with their browser configuration in a thorough
and complete way. To address this problem, we created the I2P Profile Bundle
which configured Firefox so that it would automatically "Just Work" for I2P.
As it's developed, it's added security features and improved integration with
I2P itself. In it's latest version, it **also** bundles a complete, Jpackage
powered I2P Router. The I2P Firefox Profile is now a fully-fledged distribution
of I2P for Windows, with the only remaining dependency being Firefox itself.
This should provide an unprecedented level of convenience for I2P users on
Windows.
{%- endtrans %}

Get the installer_.

.. _installer: /nsis
