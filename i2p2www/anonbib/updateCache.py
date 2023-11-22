#!/usr/bin/python
# Copyright 2003-2008, Nick Mathewson.  See LICENSE for licensing info.

"""Download files in bibliography into a local cache.
"""

import os
import sys
import signal
import time
import gzip

from . import BibTeX
from . import config
import urllib.request, urllib.error, urllib.parse
import getopt
import socket
import errno
import http.client

FILE_TYPES = [ "txt", "html", "pdf", "ps", "ps.gz", "abstract" ]
BIN_FILE_TYPES = [ 'pdf', 'ps.gz' ]

class UIError(Exception):
    pass

def tryUnlink(fn):
    try:
        os.unlink(fn)
    except OSError:
        pass

def getCacheFname(key, ftype, section):
    return BibTeX.smartJoin(config.OUTPUT_DIR,config.CACHE_DIR,
                            section,
                            "%s.%s"%(key,ftype))

def downloadFile(key, ftype, section, url,timeout=None):
    if timeout is None:
        timeout = config.DOWNLOAD_CONNECT_TIMEOUT
    fname = getCacheFname(key, ftype, section)
    parent = os.path.split(fname)[0]
    if not os.path.exists(parent):
        os.makedirs(parent)

    fnameTmp = fname+".tmp"
    fnameURL = fname+".url"
    tryUnlink(fnameTmp)

    def sigalrmHandler(sig,_):
        pass
    signal.signal(signal.SIGALRM, sigalrmHandler)
    signal.alarm(timeout)
    try:
        try:
            infile = urllib.request.urlopen(url)
        except http.client.InvalidURL as e:
            raise UIError("Invalid URL %s: %s"%(url,e))
        except IOError as e:
            raise UIError("Cannot connect to url %s: %s"%(url,e))
        except socket.error as e:
            if getattr(e,"errno",-1) == errno.EINTR:
                raise UIError("Connection timed out to url %s"%url)
            else:
                raise UIError("Error connecting to %s: %s"%(url, e))
    finally:
        signal.alarm(0)

    mode = 'w'
    if ftype in BIN_FILE_TYPES:
        mode = 'wb'
    outfile = open(fnameTmp, mode)
    try:
        while 1:
            s = infile.read(1<<16)
            if not s: break
            outfile.write(s)
    finally:
        infile.close()
        outfile.close()

    urlfile = open(fnameURL, 'w')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), file=urlfile)
    if "\n" in url: url = url.replace("\n", " ")
    print(url, file=urlfile)
    urlfile.close()

    os.rename(fnameTmp, fname)

def getURLs(entry):
    r = {}
    for ftype in FILE_TYPES:
        ftype2 = ftype.replace(".", "_")
        url = entry.get("www_%s_url"%ftype2)
        if url:
            r[ftype] = url.strip().replace("\n", " ")
    return r

def getCachedURL(key, ftype, section):
    fname = getCacheFname(key, ftype, section)
    urlFname = fname+".url"
    if not os.path.exists(fname) or not os.path.exists(urlFname):
        return None
    f = open(urlFname, 'r')
    lines = f.readlines()
    f.close()
    if len(lines) != 2:
        print("ERROR: unexpected number of lines in", urlFname, file=sys.stderr)
    return lines[1].strip()

def downloadAll(bibtex, missingOnly=0):
    """returns list of tuples of key, ftype, url, error"""
    errors = []
    for e in bibtex.entries:
        urls = getURLs(e)
        key = e.key
        section = e.get("www_cache_section", ".")
        for ftype, url in list(urls.items()):
            if missingOnly:
                cachedURL = getCachedURL(key, ftype, section)
                if cachedURL == url:
                    print("Skipping",url, file=sys.stderr)
                    continue
                elif cachedURL is not None:
                    print("URL for %s.%s has changed"%(key,ftype), file=sys.stderr)
                else:
                    print("I have no copy of %s.%s"%(key,ftype), file=sys.stderr)
            try:
                downloadFile(key, ftype, section, url)
                print("Downloaded",url)
            except UIError as e:
                print(str(e), file=sys.stderr)
                errors.append((key,ftype,url,str(e)))
            except (IOError, socket.error) as e:
                msg = "Error downloading %s: %s"%(url,str(e))
                print(msg, file=sys.stderr)
                errors.append((key,ftype,url,msg))
        if "ps" in urls and "ps.gz" not in urls:
            # Say, this is something we'd like to have gzipped locally.
            psFname = getCacheFname(key, "ps", section)
            psGzFname = getCacheFname(key, "ps.gz", section)
            if os.path.exists(psFname) and not os.path.exists(psGzFname):
                # This is something we haven't gzipped yet.
                print("Compressing a copy of",psFname)
                outf = gzip.GzipFile(psGzFname, "wb")
                inf = open(psFname, "rb")
                while 1:
                    s = inf.read(4096)
                    if not s:
                        break
                    outf.write(s)
                outf.close()
                inf.close()

    return errors

if __name__ == '__main__':
    if len(sys.argv) == 2:
        print("Loading from %s"%sys.argv[1])
    else:
        print("Expected a single configuration file as an argument", file=sys.stderr)
        sys.exit(1)
    config.load(sys.argv[1])

    if config.CACHE_UMASK != None:
        os.umask(config.CACHE_UMASK)

    bib = BibTeX.parseFile(config.MASTER_BIB)
    downloadAll(bib,missingOnly=1)
