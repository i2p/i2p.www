========================
GeoIP File Specification
========================
.. meta::
    :lastupdated: December 2013
    :accuratefor: 0.9.9

.. contents::


Overview
========

This page specifies the format of the various GeoIP files,
used by the router to look up a country for an IP.


Country Name (countries.txt) Format
===================================

This format is easily generated from data files available from many public sources.
For example:

.. raw:: html

  {% highlight lang='bash' %}$ wget http://geolite.maxmind.com/download/geoip/database/GeoIPCountryCSV.zip
  $ unzip GeoIPCountryCSV.zip
  $ cut -d, -f5,6 < GeoIPCountryWhois.csv | sed 's/"//g' | sort | uniq > countries.txt
{% endhighlight %}

* Encoding is UTF-8
* '#' in column 1 specifies a comment line
* Entry lines are CountryCode,CountryName
* CountryCode is the ISO two-letter code, upper case
* CountryName is in English


IPv4 (geoip.txt) Format
=======================

This format is borrowed from Tor and is easily generated from data files available from many public sources.
For example:

.. raw:: html

  {% highlight lang='bash' %}$ wget http://geolite.maxmind.com/download/geoip/database/GeoIPCountryCSV.zip
  $ unzip GeoIPCountryCSV.zip
  $ cut -d, -f3-5 < GeoIPCountryWhois.csv | sed 's/"//g' > geoip.txt
  $ cut -d, -f5,6 < GeoIPCountryWhois.csv | sed 's/"//g' | sort | uniq > countries.txt
{% endhighlight %}

* Encoding is ASCII
* '#' in column 1 specifies a comment line
* Entry lines are FromIP,ToIP,CountryCode
* FromIP and ToIP are unsigned integer representations of the 4-byte IP
* CountryCode is the ISO two-letter code, upper case
* Entry lines must be sorted by numeric FromIP


IPv6 (geoipv6.dat.gz) Format
============================

This is a compressed binary format designed for I2P.
The file is gzipped. Ungzipped format:

.. raw:: html

  {% highlight %}  Bytes 0-9: Magic number "I2PGeoIPv6"
    Bytes 10-11: Version (0x0001)
    Bytes 12-15 Options (0x00000000) (future use)
    Bytes 16-23: Creation date (ms since 1970-01-01)
    Bytes 24-xx: Optional comment (UTF-8) terminated by zero byte
    Bytes xx-255: null padding
    Bytes 256-: 18 byte records:
        8 byte from (/64)
        8 byte to (/64)
        2 byte ISO country code LOWER case (ASCII)
{% endhighlight %}

NOTES:

* Data must be sorted (SIGNED long twos complement), no overlap.
  So the order is 80000000 ... FFFFFFFF 00000000 ... 7FFFFFFF.
* The GeoIPv6.java class contains a program to generate this format from
  public sources such as the Maxmind GeoLite data.
* IPv6 GeoIP lookup is supported as of release 0.9.8.
