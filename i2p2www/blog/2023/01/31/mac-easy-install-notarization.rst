{% trans -%}
=======================================
Update on Mac Easy Install Notarization
=======================================
{%- endtrans %}
.. meta::
    :author: idk
    :date: 2023-01-31
    :category: release
    :excerpt: {% trans %}{% endtrans %}

{% trans -%}
The I2P Easy-Install Bundle for Mac has been experiencing stalled updates for the past 2 releases due to the departure of its maintainer.
For the time being, it is temporarily recommended that existing Easy-Install users delay updating and remain on 1.9.0 until the development team can successfully notarize the application and resume automatic updates.
The updates will happen immediately once this has happened.
For now, 1.9.0 is stable and has no known critical security issues.
{%- endtrans %}

{% trans -%}The Notarization Process For MacOS{%- endtrans %}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{% trans -%}
There are many steps in the process of distributing an application to Apple users.
In order to distribute an application as a .dmg securely, the application must pass a notarization process.
In order to submit an application for notarization, a developer must sign the application using a set of certificates that includes one for code signing, and one for signing the application itself.
This signing must take place at specific points during the build process, before the final .dmg bundle which is distributed to the end users can be created.
{%- endtrans %}

{% trans -%}
I2P Java is a complex application, and because of this it is a process of trial and error to match the types of code used in the application to Apple's certificates, and where the signing takes place to produce a valid timestamp.
It is due to this complexity that existing documentation for developers is falling short of helping the team understand the correct combination of factors that will result in successful notarization.
{%- endtrans %}

{% trans -%}
These difficulties leave the timeline for completing this process difficult to predict.
We won't know we're done until we are able to clean up the build environment and follow the process end-to-end.
The good news is that we are down to only 4 errors during the notarization process from more than 50 during the first attempt and can reasonably predict that it will be competed before or in time for the next release in April.
{%- endtrans %}

{% trans -%}Options for New macOS I2P Installs and Updates{%- endtrans %}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{% trans -%}
New I2P participants can still download the Easy Installer for the macOS 1.9.0 software.
It will receive updates no later than the next scheduled release in April.
Updates to the latest version will become available as soon as notarization is successful.
{%- endtrans %}

{% trans -%}
The classic install options is also available.
This will require downloading Java and the I2P software via the .jar based installer.
{%- endtrans %}

`{% trans -%}Jar Install Instructions are available here.{%- endtrans %} <https://geti2p.net/en/download/macos>`_

{% trans -%}
Easy-Install users can update to that latest version using a locally-produced development build.
{%- endtrans %}

`{% trans -%}Easy-Install Build Instructions are available here.{%- endtrans %} <https://i2pgit.org/i2p-hackers/i2p-jpackage-mac/-/blob/master/BUILD.md>`_

{% trans -%}
There is also the option to uninstall the software, remove the I2P configuration directory and reinstall I2P using the .jar installer.
{%- endtrans %}
