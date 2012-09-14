#
# Required software:
# sqlite3 3.6.23.1 or newer
#    http://www.sqlite.org/
# unixodbc
#    http://www.unixodbc.org/
# pyodbc-3.0.6 or newer
#    http://www.ch-werner.de/sqliteodbc/
# werkzeug
#    http://werkzeug.pocoo.org/
# python 2.6 or 2.7
#    http://python.org/
#


# Modify as needed, or use a symlink.
netdbdir = 'netdb'
database = 'Driver=SQLite;DATABASE=I2PnetDb'


from werkzeug import BaseRequest, BaseResponse, ETagResponseMixin, escape, SharedDataMiddleware
from werkzeug.exceptions import HTTPException
import os
from time import time, gmtime
import calendar
#import time
from random import choice
import pyodbc


#
# Not needed?
#
#import sha


# db format
#
#  table client ipaddress, time of access
#
#  table html index, time of creation


#
# Init database if it does not exist.
#

def checkdatabase():
    cnxn = pyodbc.connect(database)
    cur = cnxn.cursor()

    try:
        cur.execute("select * from client")
    except pyodbc.Error:
        #print ("Creating new table 'client'")
        cur.execute("create table client (ip string, whn float)")
        cnxn.commit()
    try:
        cur.execute("select * from entry")
    except pyodbc.Error:
        #print ("Creating new table 'entry'")
        cur.execute("create table entry (whn float, wht string)")
        cnxn.commit()
    cnxn.close()




#    try:
#        cur.execute("select * from html")
#    except pyodbc.Error:
#        cur.execute("create table client (index, time, html)")


#    cur.execute("insert into foo values(1, 'Me')")
#    cnxn.commit()
#    cur.execute("select * from foo")
#    cnxn.close()

class Request(BaseRequest):
    """Useful subclass of the default request that knows how to build urls."""

    def __init__(self, environ):
        BaseRequest.__init__(self, environ)


class Response(BaseResponse, ETagResponseMixin):
    """Subclass of base response that has a default mimetype of text/html."""
    default_mimetype = 'text/html'

def application(environ, start_response):
    """The WSGI application that connects all together."""
    checkdatabase()
    req = Request(environ)
    remote = req.remote_addr
    now = time()
    old = now - 3600
    oldest = now - 7200
    t = gmtime(now)
    nowtag = calendar.timegm((t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, 0, 0, t.tm_wday, t.tm_yday, t.tm_isdst))

    cnxn = pyodbc.connect(database)
    cur = cnxn.cursor()
    #
    # Prune database from peers that are over 1 hour old
    #
    cur.execute("delete from client where whn < ?", old)
    cnxn.commit()
    #
    # Prune database from entries that are over 2 hours old
    #
    cur.execute("delete from entry where whn < ?", oldest)
    cnxn.commit()

    #
    # Get peer info
    #
    cur.execute("select * from client where ip = ?", remote)
    info = cur.fetchall()
    # page
    path = req.path[1:]


    if path == '':
        page = u'<html><head><title>NetDB</title></head><body><ul>%s</ul></body></html>'

        if len(info) == 0:
            # tag the ip as new
            cur.execute("insert into client values (?, ?)", (remote, now))
            # see if we have a list already, and use that
            cur.execute("select * from entry where whn = ?", nowtag)
            stuff = cur.fetchall()
            if (len(stuff) == 0):
                # generate links
                entries = os.listdir(netdbdir)
                new = []
                if len(entries) > 150:
                    # select some randomly
                    for i in xrange(100):
                        while True:
                            sel = choice(entries)
                            if not sel.startswith('routerInfo-'):
                                continue
                            if sel not in new:
                                new.append(sel)
                                cur.execute("insert into entry values (?, ?)", (nowtag, sel))
                                break
                else:
                    for sel in entries:
                        if not sel.startswith('routerInfo-'):
                            continue
                        if sel not in new:
                            new.append(sel)
                            cur.execute("insert into entry values (?, ?)", (nowtag, sel))
                entries = new
            else:
                # Use what we already generated
                entries = []
                for junk,sel in stuff:
                    entries.append(sel)
        else:
            # use old list based on date in database, i.e. sends the same as before.
            junk, last = info[0]
            t = gmtime(last)
            oldtag = calendar.timegm((t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, 0, 0, t.tm_wday, t.tm_yday, t.tm_isdst))
            cur.execute("select * from entry where whn = ?", oldtag)
            stuff = cur.fetchall()
            entries = []
            for junk,sel in stuff:
                entries.append(sel)

        res = ''
        for entry in entries:
            # Already sanitized above.
            #if not entry.startswith('routerInfo-'):
            #    continue
            res += '<li><a href="%s">%s</a></li>' % (entry, entry)
        resp = Response(page % res, mimetype='text/html')
        resp.add_etag()

    elif path == 'robots.txt':
        dat = u"User-agent: *\nDisallow: /routerInfo-*.dat$\n"
        resp = Response(dat, mimetype='text/plain')
        resp.add_etag()

    else:
        if len(info) == 0:
            # 404 This is to prevent cross seed site scrapes
            resp = Response("Hi! Having fun?", status=403, mimetype='text/plain')
        else:
            #
            # zap badness from path
            #
            #print "path given is " + repr(path)

            chkpath = path.replace("'","").replace("/","")
            # check to see if we have this entry in the database at all.
            cur.execute("select * from entry where wht = ?",  chkpath)
            chk = cur.fetchall()
            if len(chk) == 0:
                resp = Response("Do you not have anything better to do?", status=400, mimetype='text/plain')
            else:
                try:
                    # load file
                    f = open(os.path.join(netdbdir, path), 'rb')
                    resp = Response(f.read(), mimetype='application/octet-stream')
                    f.close()
                    resp.add_etag()
                except IOError:
                    # 404
                    resp = Response("Owch! Could not find file! It got deleted before you could get a copy, sorry.", status=404, mimetype='text/plain')
    cnxn.commit()
    cnxn.close()
    return resp(environ, start_response)

if __name__ == '__main__':
    from werkzeug import run_simple
    run_simple('localhost', 5007, application)
