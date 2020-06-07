================================================================
{% trans -%}Help your Friends Join I2P by Sharing Reseed Bundles{%- endtrans %}
================================================================

.. meta::
   :author: idk
   :date: 2020-06-07
   :category: reseed
   :excerpt: {% trans %}Create, exchange, and use reseed bundles{% endtrans %}

{% trans -%}
Most new I2P routers join the network by bootstrapping with the help of
a reseed service. However, reseed services are centralized and
comparatively easy to block, considering the emphasis on de-centralized
and un-blockable connections in the rest of the I2P network. If a new
I2P router finds itself unable to bootstrap, it may be a possible to use
an existing I2P router to generate a working “Reseed bundle” and
bootstrap without the need of a reseed service.
{%- endtrans %}

{% trans -%}
It is possible for a user with a working I2P connection to help a
blocked router join the network by generating a reseed file and passing
it to them via a secret or non-blocked channel. In fact, in many
circumstances, an I2P router that is already connected will not be
affected by reseed blocking at all, so **having working I2P routers
around means that existing I2P routers can help new I2P routers by
providing them with a hidden way of bootstrapping**.
{%- endtrans %}

{% trans -%}Generating a Reseed Bundle{%- endtrans %}
--------------------------------------

-  {% trans -%} To create a reseed bundle for others to use, go to the `Reseed
   configuration page <http://127.0.0.1:7657/configreseed>`__. You will
   see a section that looks like this. Click the button indicated by the
   red circle. |Create a Reseed Zip| {%- endtrans %}
-  {% trans -%} Now that you’ve clicked the button, a zip will be generated
   containing enough information to bootstrap a new I2P router. Download
   it and transfer it to the computer with the new, un-bootstrapped I2P
   router. |Downloads a Reseed Zip| {%- endtrans %}

{% trans -%}Performing a Reseed from File{%- endtrans %}
------------------------------------------

-  {% trans -%} Obtain an i2preseed.zip file from a friend with an I2P router that is
   already running, or from a trusted source somewhere on the internet,
   and visit the `Reseed Configuration
   page <http://127.0.0.1:7657/configreseed>`__. Click the button that
   says “Select zip or su3 file” and navigate to that file. |Select a
   Reseed Zip| {%- endtrans %}
-  {% trans -%} When you’ve selected your reseed file, click the “Reseed from File”
   button. |Reseed from a Zip File|. You’re done! Your router will now
   bootstrap using the zip file, and you will be ready to join the I2P
   network. {%- endtrans %}

.. |Create a Reseed Zip| image:: /_static/images/reseed/createreseed.png
.. |Downloads a Reseed Zip| image:: /_static/images/reseed/dlreseed.png
.. |Select a Reseed Zip| image:: /_static/images/reseed/ulreseed.png
.. |Reseed from a Zip File| image:: /_static/images/reseed/filereseed.png

