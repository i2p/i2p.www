{% trans -%}
=====================
Syndie 1.105b Release
=====================
{%- endtrans %}

.. meta::
   :date: 2014-01-21
   :category: release
   :excerpt: {% trans %}Update to HSQLDB 2.3.1{% endtrans %}

{% trans -%}
This is the first stable release since February 2013.
It is essentially the same as 1.104b-7-rc, with some translation updates.
{%- endtrans %}

{% trans -%}
All binaries and source packages are at `syndie.de`_ and `syndie.i2p`_.
Plugins are available at `plugins.i2p`_ and `stats.i2p`_.
{%- endtrans %}

{% trans -%}
For those of you upgrading from 1.103b, you will find syndie startup and shutdown much faster due to the new version of HSQLDB.
{%- endtrans %}

{% trans -%}
If you have a large database or an identity you wish to preserve,
you may wish to back up your entire ~/.syndie directory before you start.
The upgrade process does make its own backup, however you may find it easier to use your own backup if the upgrade fails.
{%- endtrans %}

{% trans -%}
Upgrades from 1.103b may fail for some people due to database corruption due to bugs in the old HSQLDB.
Unfortunately, we don't know how to fix it.
Your alternatives are to start over with a clean database, or stay with 1.103b forever.
Sorry about that.
{%- endtrans %}

.. _`stats.i2p`: http://stats.i2p/i2p/plugins/
.. _`plugins.i2p`: http://plugins.i2p/plugins/syndie/
.. _`syndie.i2p`: http://www.syndie.i2p/download.html
.. _`syndie.de`: https://syndie.de/download

{% trans -%}
As usual, we recommend that you update to this release.
The best way to maintain security and help the network is to run the latest release.
{%- endtrans %}

**{% trans %}RELEASE DETAILS{% endtrans %}**


**{% trans %}Bug Fixes{% endtrans %}**

- Fix NPE in SyndieTreeListener
- Fix, or maybe just move, NPE in addURI/getURI

**{% trans %}GUI Improvements and Fixes{% endtrans %}**

- Don't open message view tab for unreadable messages or stub messages
- Don't fail on duplicate cancel requests
- Fix BrowseForumTab text on forum with blank name
- For consistency, always put cancel button to the left of OK/Save
- Move message date to date column in syndicator tab
- Better formatting of file sizes in Syndicator tab
- Clean up internal error popup
- Catch dispose errors when changing translation or theme
- Add menu item to delete PBE messages and forums
- Add keyboard shortcuts in message view tab
- Fix dup archive in Syndicator Tab after rename
- Don't display PBE messages after deletion
- Update to SWT 3.8.2 20130131

**{% trans %}Syndication{% endtrans %}**

- Improve import failure propagation and display
- More cleanup of Importer and enhanced ImportResults by passing missing key and PBE indications in result code
- Simplification of SyncArchive.IncomingAction using Results
- Handle and display "stub" cancel messages correctly
- Early check for banned target in ImportPost
- Reduce default pull policy to 14 days
- Only pull indexes needed for pulled messages
- Fetch messages newest-first

**{% trans %}Database{% endtrans %}**

- Update to DB version 25
- Add LOBs for attachments and pages
- Increase length limits on cancelledURI, headerValue, and others
- Implement offline database backup
- Backup database before upgrading to hsqldb 2.x
- Add code to migrate large things to LOBs
- Enable migration of large attachments and pages to LOBs
- Implement retrieval of pages and attachments from LOBs
- Implement getAttachmentAsStream for real (unused yet)
- Implement storage to LOBs in ImportPost
- Sleep a while before shutdown compact
- Shutdown compact immediately after upgrade, then reconnect, as recommended by hsqldb
- Use attachment size from messageAttachment table, not actual size from messageAttachmentData table

**{% trans %}Other{% endtrans %}**

- Use DataHelper.loadProps() to deserialize properties UTF-8-safely
- Add script for the hsqldb database manager tool
- More code refactoring
- {% trans %}New translations{% endtrans %}: Polish, Portuguese, Romanian
- {% trans %}Translation updates{% endtrans %}

