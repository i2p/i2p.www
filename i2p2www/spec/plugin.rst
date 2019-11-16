====================
Plugin Specification
====================
.. meta::
    :lastupdated: November 2019
    :accuratefor: 0.9.43

.. contents::


Overview
========

This document specifies a .xpi2p file format (like the Firefox .xpi), but with
a simple plugin.config description file instead of an XML install.rdf file.
This file format is used for both initial plugin installs and plugin updates.

In addition, this document provides a brief overview of how the router installs
plugins, and policies and guidelines for plugin developers.

The basic .xpi2p file format is the same as a i2pupdate.sud file (the format
used for router updates), but the installer will let the user install the addon
even if it doesn't know the signer's key yet.

As of release 0.9.15, the SU3 file format [UPDATES]_ is supported and is
preferred. This format enables stronger signing keys.

We do not recommend distributing plugins in the xpi2p format any more.
Use the su3 format.

The standard directory structure will let users install the following types of
addons:

* console webapps

* new eepsite with cgi-bin, webapps

* console themes

* console translations

* Java programs

* Java programs in a separate JVM

* Any shell script or program

A plugin installs all its files in ~/.i2p/plugins/name/
(%APPDIR%\I2P\plugins\name\ on Windows). The installer will prevent
installation anywhere else, although the plugin can access libraries elsewhere
when running.

This should be viewed only as a way to make installation, uninstallation, and
upgrading easier, and to lessen basic inter-plugin conflicts.

There is essentially no security model once the plugin is running, however. The
plugin runs in the same JVM and with the same permissions as the router, and
has full access to the file system, the router, executing external programs,
etc.

Details
=======

foo.xpi2p is a signed update (sud) file [UPDATES]_ containing the following:

Standard .sud header prepended to the zip file, containing the following::

    40-byte DSA signature [CRYPTO-DSA]_
    16-byte plugin version in UTF-8, padded with trailing zeroes if necessary

Zip file containing the following:

plugin.config file
``````````````````
This file is required. It is a standard I2P configuration file [CONFIG]_,
containing the following properties:

The following four are required properties.  The first three must be identical
to those in the installed plugin for an update plugin.

    name
        Will be installed in this directory name

        For native plugins, you may want separate names in different packages -
        foo-windows and foo-linux, for example

    key
        DSA public key [CRYPTO-DSA]_ as 172 B64 chars ending with '='

        Omit for SU3 format.

    signer
        yourname@mail.i2p recommended)

    version
        Must be in a format VersionComparator can parse, e.g. 1.2.3-4

        16 bytes max (must match sud version)

        Valid number separators are '.', '-', and '_'

        This must be greater than the one in the installed plugin for an update plugin.

Values for the following properties are displayed on /configplugins in the
router console if present:

    date
        Java time - long int

    author
        yourname@mail.i2p recommended

    websiteURL
        http://foo.i2p/

    updateURL
        http://foo.i2p/foo.xpi2p

        The update checker will check bytes 41-56 at this URL
        to determine whether a newer version is available

        Not recommended. Do not use unless you previously distributed
        plugins in the xpi2p format, and even then, routers know how
        to update with the su3 URL, as of 0.9.15.

        (Should the checker fetch with ?currentVersion=1.2.3?...
        No. If the dev wants to have the URL contain the current version, just
        set it in the config file, and remember to change it every release)

    updateURL.su3
        http://foo.i2p/foo.su3

        The location of the su3-format update file, as of 0.9.15

    description
        in English

    description_xx
        for language xx

    license
        The plugin license

    disableStop=true
        Default false.
        If true, the stop button will not be shown. Use this if there are no
        webapps and no clients with stopargs.

The following properties are used to add a link on the console summary bar:

    consoleLinkName
        will be added to summary bar

    consoleLinkName_xx
        for language xx

    consoleLinkURL
        /appname/index.jsp

    consoleLinkTooltip
        supported as of 0.7.12-6

    consoleLinkTooltip_xx
        lang xx as of 0.7.12-6

The following optional properties may be used to add a custom icon on the
console:

    console-icon
        supported as of 0.9.20

        Only for webapps.

        A path within the webapp to a 32x32 image, e.g. /icon.png
        Applies to all webapps in the plugin.

    icon-code
        supported as of 0.9.25

        Provides a console icon for plugins without web resources.

        A B64 string produced by calling `net.i2p.data.Base64 encode FILE` on a
        32x32 png image file.

The following properties are used by the plugin installer:

    type
        app/theme/locale/webapp/...

        (unimplemented, probably not necessary)

    min-i2p-version
        The minimum version of I2P this plugin requires

    max-i2p-version
        The maximum version of I2P this plugin will run on

    min-java-version
        The minimum version of Java this plugin requires

    min-jetty-version
        supported as of 0.8.13, use 6 for Jetty 6 webapps

    max-jetty-version
        supported as of 0.8.13, use 5.99999 for Jetty 5 webapps

    required-platform-OS
        unimplemented - perhaps will be displayed only, not verified

    other-requirements
        unimplemented

        e.g. python x.y - not verified by the installer, just displayed to the
        user

    dont-start-at-install=true
        Default false.

        Won't start the plugin when it is installed or updated. On initial
        installation, configures the plugin so the user must manually start it.
        An update will not change the user's preference to start it if they
        choose to do so.

    router-restart-required=true
        Default false.

        This does not restart the router or the plugin on an update, it just
        informs the user that a restart is required. It has no effect on initial
        plugin installation.

    update-only=true
        Default false.

        If true, will fail if an installation does not exist.

    install-only=true
        Default false.
        If true, will fail if an installation exists.

    min-installed-version
        to update over, if an installation exists

    max-installed-version
        to update over, if an installation exists

    depends=plugin1,plugin2,plugin3
        unimplemented - is this too hard? proposed by sponge

    depends-version=0.3.4,,5.6.7
        unimplemented

The following property is used for translation plugins:

    langs=xx,yy,Klingon,...
        (unimplemented)
        (yy is the country flag)

Application Directories and Files
`````````````````````````````````
Each of the following directories or files is optional, but something must be
there or it won't do anything:

console/
    locale/
        Only jars containing new resource bundles (translations) for apps in the
        base I2P installation. Bundles for this plugin should go inside
        console/webapp/foo.war or lib/foo.jar

    themes/
        New themes for the router console
        Place each theme in a subdirectory.

    webapps/
        (See important notes below about webapps)

        .wars
            These will be run at install time unless disabled in webapps.config
            The war name does not have to be the same as the plugin name.
            Do not duplicate war names in the base I2P installation.

    webapps.config 
        Same format as router's webapps.config. Also used to specify additional
        jars in $PLUGIN/lib/ or $I2P/lib for the webapp classpath, with
        ``webapps.warname.classpath=$PLUGIN/lib/foo.jar,$I2P/lib/bar.jar``

        NOTE: Currently, the classpath line is only loaded if the warname is the
        same as the plugin name.

        NOTE: Prior to router version 0.7.12-9, the router looked for
        ``plugin.warname.startOnLoad`` instead of
        ``webapps.warname.startOnLoad``. For compatibility with older router
        versions, a plugin wishing to disable a war should include both lines.

eepsite/
    (See important notes below about eepsites)

    cgi-bin/

    docroot/

    logs/

    webapps/

    jetty.xml
        The installer will have to do variable substitution in here to set the
        path. The location and name of this file doesn't really matter, as long
        as it is set in clients.config - it may be more convenient to be up one
        level from here (that's what the zzzot plugin does)

lib/
    Put any jars here, and specify them in a classpath line in
    console/webapps.config and/or clients.config

clients.config file
```````````````````
This file is optional, and specifies clients that will be run when a plugin is
started.  It uses the same format as the router's clients.config file.  See the
clients.config configuration file specification [CONFIG]_ for more information
about the format and important details about how clients are started and
stopped.

    property clientApp.0.stopargs=foo bar stop baz
        If present, the class will be called with these args to stop the client
        All stop tasks are called with zero delay
        Note: The router can't tell if your unmanaged clients are running or not.
        Each should handle stopping an app that isn't running without complaint.
        That probably goes for starting a client that is already started too.

    property clientApp.0.uninstallargs=foo bar uninstall baz
        If present, the class will be called with these args just before
        deleting $PLUGIN. All uninstall tasks are called with zero delay

    property clientApp.0.classpath=$I2P/lib/foo.bar,$PLUGIN/lib/bar.jar
        The plugin runner will do variable substitution in the args and stopargs
        lines as follows:

        $I2P
            I2P base installation dir

        $CONFIG
            I2P config dir (typically ~/.i2p)

        $PLUGIN
            this plugin's installation dir (typically ~/.i2p/plugins/appname)

        (See important notes below about running shell scripts or external
        programs)


Plugin installer tasks
======================

This lists what happens when a plugin is installed by I2P.

* The .xpi2p file is downloaded.

* The .sud signature is verified against stored keys. As of release 0.9.14.1,
  if there is no matching key, the installation fails, unless an advanced
  router property is set to allow all keys.

* Verify the integrity of the zip file.

* Extract the plugin.config file.

* Verify the I2P version, to make sure the plugin will work.

* Check that webapps don't duplicate the existing $I2P applications.

* Stop the existing plugin (if present).

* Verify that the install directory does not exist yet if update=false, or ask
  to overwrite.

* Verify that the install directory does exist if update=true, or ask to
  create.

* Unzip the plugin in to appDir/plugins/name/

* Add the plugin to plugins.config


Plugin starter tasks
====================

This lists what happens when plugins are started.
First, plugins.config is checked to see which plugins need to be started.
For each plugin:

* Check clients.config, and load and start each item (add the configured jars
  to the classpath).

* Check console/webapp and console/webapp.config. Load and start required items
  (add the configured jars to the classpath).

* Add console/locale/foo.jar to the translation classpath if present.

* Add console/theme to the theme search path if present.

* Add the summary bar link.


Console webapp notes
====================

Console webapps with background tasks should implement a ServletContextListener
(see seedless or i2pbote for examples), or override destroy() in the servlet,
so that they can be stopped.  As of router version 0.7.12-3, console webapps
will always be stopped before they are restarted, so you do not need to worry
about multiple instances, as long as you do this.  Also as of router version
0.7.12-3, console webapps will be stopped at router shutdown.

Don't bundle library jars in the webapp; put them in lib/ and put a classpath
in webapps.config.  Then you can make separate install and update plugins,
where the update plugin does not contain the library jars.

Never bundle Jetty, Tomcat, or servlet jars in your plugin, as they may
conflict with the version in the I2P installation.
Take care not to bundle any conflicting libraries.

Don't include .java or .jsp files; otherwise Jetty will recompile them at
installation, which will increase the startup time.
While most I2P installations will have a working Java and JSP
compiler in the classpath, this is not guaranteed, and may not work in all cases.

For now, a webapp needing to add classpath files in $PLUGIN must be the same
name as the plugin.  For example, a webapp in plugin foo must be named foo.war.

While I2P has supported Servlet 3.0 since I2P release 0.9.30,
it does NOT support annotation scanning for @WebContent (no web.xml file).
Several additional runtime jars would be required, and we do not provide
those in a standard installation.
Contact the I2P developers if you need support for @WebContent.


Eepsite notes
=============

It isn't clear how to have a plugin install to an existing eepsite.  The router
has no hook to the eepsite, and it may or may not be running, and there may be
more than one.  Better is to start your own Jetty instance and I2PTunnel
instance, for a brand new eepsite.

It can instantiate a new I2PTunnel (somewhat like the i2ptunnel CLI does), but
it won't appear in the i2ptunnel gui of course, that's a different instance.
But that's ok. Then you can start and stop i2ptunnel and jetty together.

So don't count on the router to automatically merge this with some existing
eepsite. It probably won't happen.  Start a new I2PTunnel and Jetty from
clients.config.  The best examples of this are the zzzot and pebble plugins,
available at zzz's plugins page [STATS-PLUGINS]_.

How to get path substitution into jetty.xml?  See zzzot and pebble plugins for
examples.


Client start/stop notes
=======================

As of release 0.9.4, the router supports "managed" plugin clients.  Managed
plugin clients are instantiated and started by the ``ClientAppManager``.  The
ClientAppManager maintains a reference to the client and receives updates on
the client's state.  Managed plugin client are preferred, as it is much easier
to implement state tracking and to start and stop a client. It also is much
easier to avoid static references in the client code which could lead to
excessive memory usage after a client is stopped.  See the clients.config
configuration file specification [CONFIG]_ for more information on writing a
managed client.

For "unmanaged" plugin clients, The router has no way to monitor the state of
clients started via clients.config.  The plugin author should handle multiple
start or stop calls gracefully, if at all possible, by keeping a static state
table, or using PID files, etc.  Avoid logging or exceptions on multiple starts
or stops.  This also goes for a stop call without a previous start.  As of
router version 0.7.12-3, plugins will be stopped at router shutdown, which
means that all clients with stopargs in clients.config will be called, whether
or not they were previously started.


Shell script and external program notes
=======================================

To run shell scripts or other external programs, see [ZZZ-141]_.

To work on both Windows and Linux, write a small Java class that checks the OS
type, then runs ShellCommand on either the .bat or a .sh file you provide.

External programs won't be stopped when the router stops, and a second copy
will fire up when the router starts. To work around this, you could write a
wrapper class or shell script that does the usual storage of the PID in a PID
file, and check for it on start.


Other plugin guidelines
=======================

* See i2p.scripts monotone branch or any of the sample plugins on zzz's page for
  the makeplugin.sh shell script. This automates most of the tasks for
  key generation, plugin su3 file creation, and verification.
  You should incorporate this script into your plugin build process.

* Pack200 of jars and wars is strongly recommended for plugins, it generally
  shrinks plugins by 60-65&#37;. See any of the sample plugins on zzz's page for
  an example. Pack200 unpacking is supported on routers 0.7.11-5 or higher,
  which is essentially all routers that support plugins at all.

* Plugins must not attempt to write anywhere in $I2P as it may be readonly,
  and that isn't good policy anyway.

* Plugins may write to $CONFIG but keeping files in $PLUGIN only is recommended.
  All files in $PLUGIN will be deleted at uninstall. Files elsewhere will not be
  deleted at uninstall unless the plugin does it explicitly with a client in
  clients.config run with uninstallargs. If the user may want to save data after
  uninstallation, the uninstallargs hook could ask.

* $CWD may be anywhere; do not assume it is in a particular place, do not
  attempt to read or write files relative to $CWD.

* Java programs should find out where they are with the directory getters in
  I2PAppContext.

* Plugin directory is
  ``I2PAppContext.getGlobalContext().getAppDir().getAbsolutePath() + "/plugins/" + appname``,
  or put a $PLUGIN argument in the args line in clients.config. There is no
  reliable way to find the i2p install or config or plugin directory without
  using the context API in i2p.jar.

* See [ZZZ-16]_ for info on generating signing keys and generating/verifying
  keys and sud files.

* See [ZZZ-1473]_ for info on generating signing keys and generating/verifying
  keys for su3 files.

* All config files must be UTF-8.

* To run in a separate JVM, use ShellCommand with
  ``java -cp foo:bar:baz my.main.class arg1 arg2 arg3``. Of course, it will be a
  lot harder to stop the plugin then... But with some trickery with PID files it
  should be possible.

* As an alternative to stopargs in clients.config, a Java client may register a
  shutdown hook with I2PAppContext.addShutdownTask(). But this wouldn't shut
  down a plugin when upgrading, so stopargs is recommended. Also, set all
  created threads to daemon mode.

* Do not include classes duplicating those in the standard installation. Extend
  the classes if necessary.

* Beware of the different classpath definitions in wrapper.config between old
  and new installations - see classpath section below.

* Clients will reject duplicate keys with different keynames, and duplicate
  keynames with different keys, and different keys or keynames in upgrade
  packages. Safeguard your keys. Only generate them once.

* Do not modify the plugin.config file at runtime as it will be overwritten on
  upgrade. Use a different config file in the directory for storing runtime
  configuration.

* In general, plugins should not require access to $I2P/lib/router.jar. Do not
  access router classes, unless you are doing something special. The router may
  in the future implement a restricted classpath for plugins that prevents
  access to router classes.

* Since each version must be higher than the one before, you could enhance your
  build script to add a build number to the end of the version. This helps for
  testing. Most of zzz's plugins have that feature, check build.xml for an example.

* Plugins must never call ``System.exit()``.

* Please respect licenses by meeting license requirements for any software you
  bundle.

* The router sets the JVM time zone to UTC. If a plugin needs to know the user's
  actual time zone, it is stored by the router in the I2PAppContext property
  ``i2p.systemTimeZone``.


Classpaths
==========

The following jars in $I2P/lib can be assumed to be in the standard classpath
for all I2P installations, no matter how old or how new the original
installation.

All recent public APIs in i2p jars have the since-release number specified in the Javadocs.
For bundled jars, see the API guidelines below.
If your plugin requires certain features only available in recent versions, be sure to set the
properties min-i2p-version, min-jetty-version, or both, in the plugin.config file.
This will give your users a clear error message on installation if
the requirements are not met.


=====================  ============================  ==============================================
         Jar                     Contains                         Usage
=====================  ============================  ==============================================
addressbook.jar        Subscription and blockfile    No plugin should need; use the NamingService
                       support                       interface
commons-logging.jar    Apache Logging                Empty since release 0.9.30.

                                                     * Prior to Jetty 6 (release 0.9), this
                                                       contained Apache Commons Logging only.
                                                     * From release 0.9 to release 0.9.23, this
                                                       contained both Commons Logging and Tomcat
                                                       JULI.
                                                     * As of release 0.9.24, this contained
                                                       Apache Tomcat JULI logging only.
                                                     * As of release 0.9.30 (Jetty 9),
                                                       this is empty.
commons-el.jar         JSP Expressions Language      For plugins with JSPs that use EL

                                                     * Prior to release 0.9.30, this contained
                                                       the EL 2.1 API.
                                                     * As of release 0.9.30 (Jetty 9), this contains
                                                       the EL 3.0 API.
i2p.jar                Core API                      All plugins will need
i2ptunnel.jar          I2PTunnel                     For plugins with HTTP or other servers
jasper-compiler.jar    nothing                       Empty since Jetty 6 (release 0.9)
jasper-runtime.jar     Jasper Compiler and Runtime,  Needed for plugins with JSPs
                       and some Tomcat utils
javax.servlet.jar      Servlet API                   Needed for plugins with JSPs

                                                     * Prior to release 0.9.30, this contained
                                                       the Servlet 2.5 and JSP 2.1 APIs.
                                                     * As of release 0.9.30 (Jetty 9), this contains
                                                       the Servlet 3.1 and JSP 2.3 APIs.
jbigi.jar              Binaries                      No plugin should need
jetty-i2p.jar          Support utilities             Some plugins will need. As of release 0.9.
mstreaming.jar         Streaming API                 Most plugins will need
org.mortbay.jetty.jar  Jetty Base                    Only plugins starting their own Jetty instance
                                                     will need. Recommended way of starting Jetty
                                                     is with `net.i2p.jetty.JettyStart` in
                                                     jetty-i2p.jar. This will insulate your code
                                                     from Jetty API changes.
router.jar             Router                        Only plugins using router context will need;
                                                     most will not
routerconsole.jar      Console libraries             No plugin should need, not a public API
sam.jar                SAM API                       No plugin should need
streaming.jar          Streaming Implementation      Most plugins will need
systray.jar            URL Launcher                  Most plugins should not need
systray4j.jar          Systray                       No plugin should need. As of 0.9.26,
                                                     no longer present.
wrapper.jar            Router                        No plugin should need
=====================  ============================  ==============================================

The following jars in $I2P/lib can be assumed to be present for all I2P
installations, no matter how old or how new the original installation, but are
not necessarily in the classpath:

============  ===============  =====
    Jar          Contains      Usage
============  ===============  =====
jstl.jar      Standard Taglib  For plugins using JSP tags
standard.jar  Standard Taglib  For plugins using JSP tags
============  ===============  =====

Anything not listed above may not be present in everybody's classpath, even if
you have it in the classpath in YOUR version of i2p.  If you need any jar not
listed above, add $I2P/lib/foo.jar to the classpath specified in clients.config
or webapps.config in your plugin.

Previously, a classpath entry specified in clients.config was added to the
classpath for the entire JVM.  However, as of 0.7.13-3, this was fixed using
class loaders, and now, as originally intended, the specified classpath in
clients.config is only for the particular thread.  See the section on JVM
crashes below, and [ZZZ-633]_ for background.  Therefore, specify the full
required classpath for each client.


Java Version Notes
==================

I2P has required Java 7 since release 0.9.24 (January 2016).
I2P has required Java 6 since release 0.9.12 (April 2014).
Any I2P users on the latest release should be running a 1.7 (7.0) JVM.
In early 2016, unless you require 1.7 language or library features, you should
create your plugin so it works on 1.6. Later in the year, most of the network
will be on 0.9.24 or higher with Java 7.

If your plugin **does not require 1.7**:

* Ensure that all java and jsp files are compiled with source="1.6"
  target="1.6".

* Ensure that all bundled library jars are also for 1.6 or lower.

If your plugin **requires 1.7**:

* Note that on your download page.

* Add min-java-version=1.7 to your plugin.config

In any case, you **must** set a bootclasspath when compiling with Java 8 to
prevent runtime crashes.


JVM Crashes When Updating
=========================

Note - this should all be fixed now.

The JVM has a tendency to crash when updating jars in a plugin if that plugin
was running since I2P was started (even if the plugin was later stopped).  This
may have been fixed with the class loader implementation in 0.7.13-3, but it
may not.  For further testing.

The safest is to design your plugin with the jar inside the war (for a webapp),
or to require a restart after update, or don't update the jars in your plugin.

Due to the way class loaders work inside a webapp, it _may_ be safe to have
external jars if you specify the classpath in webapps.config.  More testing is
required to verify this.  Don't specify the classpath with a 'fake' client in
clients.config if it's only needed for a webapp - use webapps.config instead.

The least safe, and apparently the source of most crashes, is clients with
plugin jars specified in the classpath in clients.config.

None of this should be a problem on initial install - you should not ever have
to require a restart for an initial install of a plugin.


References
==========

.. [CONFIG]
    {{ spec_url('configuration') }}

.. [CRYPTO-DSA]
    {{ site_url('docs/how/cryptography', True) }}#DSA

.. [STATS-PLUGINS]
    http://{{ i2pconv('stats.i2p') }}/i2p/plugins/

.. [UPDATES]
    {{ spec_url('updates') }}

.. [ZZZ-16]
    http://{{ i2pconv('zzz.i2p') }}/topics/16

.. [ZZZ-141]
    http://{{ i2pconv('zzz.i2p') }}/topics/141

.. [ZZZ-633]
    http://{{ i2pconv('zzz.i2p') }}/topics/633

.. [ZZZ-1473]
    http://{{ i2pconv('zzz.i2p') }}/topics/1473
