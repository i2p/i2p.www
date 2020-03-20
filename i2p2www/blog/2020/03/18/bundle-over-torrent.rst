{% trans -%}Using a git bundle to fetch the I2P source code{%- endtrans %}
==========================================================================

.. meta::
    :author: idk
    :date: 2020-03-18
    :excerpt: {% trans -%}Download the I2P Source code via Bittorrent.{%- endtrans %}

{% trans -%}Cloning large software repositories over I2P can be difficult, and using
git can sometimes make this harder. Fortunately, it can also sometimes
make it easier. Git has a ``git bundle`` command which can be used to
turn a git repository into a file which git can then clone, fetch, or
import from a location on your local disk. By combining this capability
with bittorrent downloads, we can solve our remaining problems with
``git clone``.{%- endtrans %}

{% trans -%}Before you Start{%- endtrans %}
-------------------------------------------

{% trans -%}If you intend to generate a git bundle, you **must** already possess a
full copy of the **git** repository, not the mtn repository. You can get
it from github or from git.idk.i2p, but a shallow clone(a clone done to
–depth=1) *will not* *work*. It will fail silently, creating what looks
like a bundle, but when you try to clone it it will fail. If you are
just retrieving a pre-generated git bundle, then this section does not
apply to you.{%- endtrans %}

{% trans -%}Fetching I2P Source via Bittorrent{%- endtrans %}
-------------------------------------------------------------

{% trans -%}Someone will need to supply you with a torrent file or a magnet link
corresponding to an existing ``git bundle`` that they have already
generated for you. A recent, correctly-generated bundle of the mainline
i2p.i2p source code as-of Wednesday, March 18, 2020, can be found inside
of I2P at my pastebin
`paste.idk.i2p/f/4hq37i <http://paste.idk.i2p/f/4hq37i>`__. You can also use a
`magnet link <magnet:?xt=urn:btih:72be6b12fdb38529acc3a22ad7e927842fdaa04f&tr=http://zviyq72xcmjupynn5y2f5qa3u7bxyu34jnqmwt6czte2l7idxm7q.b32.i2p/announce>`__,
and if you're a BiglyBT user who wants to bridge the torrent, use 
`this magnet link instead <magnet:?xt=urn:btih:OK7GWEX5WOCSTLGDUIVNP2JHQQX5VICP&dn=i2p.i2p.bundle&net=Public&net=I2P&net=Tor&tr=http%3A%2F%2Fzviyq72xcmjupynn5y2f5qa3u7bxyu34jnqmwt6czte2l7idxm7q.b32.i2p%2Fannounce&tr=http%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=http%3A%2F%2Ftracker1.itzmx.com%3A8080%2Fannounce&tr=http%3A%2F%2Ftracker2.postman.i2p%2Fannounce.php&tr=http%3A%2F%2Fs5ikrdyjwbcgxmqetxb3nyheizftms7euacuub2hic7defkh3xhq.b32.i2p%2Fa&tr=http%3A%2F%2Fuajd4nctepxpac4c4bdyrdw7qvja2a5u3x25otfhkptcjgd53ioq.b32.i2p%2Fannounce&tr=http%3A%2F%2Fw7tpbzncbcocrqtwwm3nezhnnsw4ozadvi2hmvzdhrqzfxfum7wa.b32.i2p%2Fa&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Fretracker.lanta-net.ru%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.sbsub.com%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Ftracker.moeking.me%3A6969%2Fannounce&tr=http%3A%2F%2Ftracker.nyap2p.com%3A8080%2Fannounce&tr=udp%3A%2F%2Fbt1.archive.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker3.itzmx.com%3A6961%2Fannounce&tr=udp%3A%2F%2Fbt2.archive.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2940%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2790%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce>`__
to announce to clearnet trackers as well.
{%- endtrans %}

{% trans -%}Once you have a bundle, you will need to use git to create a working
repository from it. If you’re using GNU/Linux and i2psnark, the git
bundle should be located in $HOME/.i2p/i2psnark or, as a service on
Debian, /var/lib/i2p/i2p-config/i2psnark. If you are using BiglyBT on
GNU/Linux, it is probably at “$HOME/BiglyBT Downloads/” instead. The
examples here assume I2PSnark on GNU/Linux, if you use something else,
replace the path to the bundle with the download directory preferred by
your client and platform.{%- endtrans %}

{% trans -%}Using ``git clone``{%- endtrans %}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{% trans -%}Cloning from a git bundle is easy, just:{%- endtrans %}

::

       git clone $HOME/.i2p/i2psnark/i2p.i2p.bundle

{% trans -%}If you get the following error, try using git init and git fetch
manually instead.{%- endtrans %}

::

       fatal: multiple updates for ref 'refs/remotes/origin/master' not allowed

{% trans -%}Using ``git init`` and ``git fetch``{%- endtrans %}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{% trans -%}First, create an i2p.i2p directory to turn into a git repository.{%- endtrans %}

::

       mkdir i2p.i2p && cd i2p.i2p

{% trans -%}Next, initialize an empty git repository to fetch changes back into.{%- endtrans %}


::

       git init

{% trans -%}Finally, fetch the repository from the bundle.{%- endtrans %}


::

       git fetch $HOME/.i2p/i2psnark/i2p.i2p.bundle

{% trans -%}Replace the bundle remote with the upstream remote{%- endtrans %}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{% trans -%}Now that you have a bundle, you can keep up with changes by setting the
remote to the upstream repository source.{%- endtrans %}

::

       git remote set-url origin git@127.0.0.1:i2p-hackers/i2p.i2p

{% trans -%}Generating a Bundle{%- endtrans %}
----------------------------------------------

{% trans -%}First, follow the `Git guide for Users <GIT.md>`__ until you have a
successfully ``--unshallow``\ ed clone of clone of the i2p.i2p
repository. If you already have a clone, make sure you run
``git fetch --unshallow`` before you generate a torrent bundle.{%- endtrans %}

{% trans -%}Once you have that, simply run the corresponding ant target:{%- endtrans %}

::

       ant bundle

{% trans -%}and copy the resulting bundle into your I2PSnark downloads directory.
For instance:{%- endtrans %}

::

       cp i2p.i2p.bundle* $HOME/.i2p/i2psnark/

{% trans -%}In a minute or two, I2PSnark will pick up on the torrent. Click on the
“Start” button to begin seeding the torrent.{%- endtrans %}
