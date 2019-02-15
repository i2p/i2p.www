{% trans -%}
====================
Android app releases
====================
{%- endtrans %}

.. meta::
   :author: str4d
   :date: 2014-12-01
   :category: android
   :excerpt: {% trans %}I2P Android 0.9.17 and Bote 0.3 have been released on the website, Google Play and F-Droid.{% endtrans %}

{% trans -%}
It has been some time since I last posted updates about our Android development,
and several I2P releases have gone by without any matching Android releases.
At last, the wait is over!
{%- endtrans %}

{% trans -%}
New app versions
----------------
{%- endtrans %}

{% trans -%}
New versions of I2P Android and Bote have been released! They can be downloaded
from these URLs:
{%- endtrans %}

* `I2P Android 0.9.17`__
* `Bote 0.3`__

__ {{ get_url('downloads_list') }}#android
__ https://download.i2p.io/android/bote/releases/0.3/Bote.apk

{% trans -%}
The main change in these releases is the transition to Android's new Material
design system. Material has made it much easier for app developers with, shall
we say, "minimalist" design skills (like myself) to create apps that are nicer
to use. I2P Android also updates its underlying I2P router to the just-released
version 0.9.17. Bote brings in several new features along with many smaller
improvements; for example, you can now add new email destinations via QR codes.
{%- endtrans %}

{% trans -%}
As I mentioned in `my last update`__, the release key that signs the apps has
changed. The reason for this was because we needed to change the package name
of I2P Android. The old package name (``net.i2p.android.router``) had already
been taken on Google Play (we still don't know who was using it), and we wanted
to use the same package name and signing key for all distributions of I2P
Android. Doing so means that a user could initially install the app from the I2P
website, and then later if the website was blocked they could upgrade it using
Google Play. Android OS considers an application to be completely different when
its package name changes, so we took the opportunity to increase the strength of
the signing key.
{%- endtrans %}

__ {{ url_for('blog_post', slug='2014/08/23/Android-test-release-on-Google-Play-in-Norway') }}

{% trans -%}
The fingerprint (SHA-256) of the new signing key is:
{%- endtrans %}

::

    AD 1E 11 C2 58 46 3E 68 15 A9 86 09 FF 24 A4 8B C0 25 86 C2 36 00 84 9C 16 66 53 97 2F 39 7A 90


{% trans -%}
Google Play
-----------
{%- endtrans %}

{% trans -%}
A few months ago we `released`__ both I2P Android and Bote on Google Play in
Norway, to test the release process there. We are pleased to announce that both
apps are now being released globally by `Privacy Solutions`__. The apps can be
found at these URLs:
{%- endtrans %}

__ {{ url_for('blog_post', slug='2014/08/23/Android-test-release-on-Google-Play-in-Norway') }}
__ https://privacysolutions.no/

* `I2P on Google Play`__
* `Bote on Google Play`__

__ https://play.google.com/store/apps/details?id=net.i2p.android
__ https://play.google.com/store/apps/details?id=i2p.bote.android

{% trans -%}
The global release is being done in several stages, starting with the countries
for which we have translations. The notable exception to this is France; due to
import regulations on cryptographic code, we are unable yet to distribute these
apps on Google Play France. This is the same issue that has affected other apps
like TextSecure and Orbot.
{%- endtrans %}


{% trans -%}
F-Droid
-------
{%- endtrans %}

{% trans -%}
Don't think we have forgotten about you, F-Droid users! In addition to the two
locations above, we have set up our own F-Droid repository. If you are reading
this post on your phone, `click here`__ to add it to F-Droid (this only works in
some Android browsers). Or, you can manually add the URL below to your F-Droid
repository list:
{%- endtrans %}

__ https://f-droid.i2p.io/repo?fingerprint=68E76561AAF3F53DD53BA7C03D795213D0CA1772C3FAC0159B50A5AA85C45DC6

https://f-droid.i2p.io/repo

{% trans -%}
If you would like to manually verify the fingerprint (SHA-256) of the repository
signing key, or type it in when adding the repository, here it is:
{%- endtrans %}

::

    68 E7 65 61 AA F3 F5 3D D5 3B A7 C0 3D 79 52 13 D0 CA 17 72 C3 FA C0 15 9B 50 A5 AA 85 C4 5D C6

{% trans -%}
Unfortunately the I2P app in the main F-Droid repository has not been updated
because our F-Droid maintainer has disappeared. We hope that by maintaining this
binary repository, we can better support our F-Droid users and keep them
up-to-date. If you have already installed I2P from the main F-Droid repository,
you will need to uninstall it if you want to upgrade, because the signing key
will be different. The apps in our F-Droid repository are the same APKs that are
provided on our website and on Google Play, so in future you will be able to
upgrade using any of these sources.
{%- endtrans %}

