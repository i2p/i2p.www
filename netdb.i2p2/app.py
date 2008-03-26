from werkzeug import BaseRequest, BaseResponse, ETagResponseMixin, escape, run_simple, SharedDataMiddleware
from werkzeug.exceptions import HTTPException
import os
import sha
from time import time
from random import choice

class Request(BaseRequest):
    """Useful subclass of the default request that knows how to build urls."""

    def __init__(self, environ):
        BaseRequest.__init__(self, environ)


class Response(BaseResponse, ETagResponseMixin):
    """Subclass of base response that has a default mimetype of text/html."""
    default_mimetype = 'text/html'


def app(environ, start_response):
    """The WSGI application that connects all together."""
    req = Request(environ)
    path = req.path[1:].lower()
    if path == '':
        # page
        page = u'<html><head><title>NetDB</title></head><body><ul>%s</ul></body></html>'
        
        # generate links
        entries = os.listdir('netdb')
        if len(entries) > 150:
            # select some randomly
            new = []
            for i in range(100):
                while True:
                    sel = choice(entries)
                    if sel not in new:
                        new.append(sel)
                        break
            entries = new
        res = ''
        for entry in entries:
            res += '<li><a href="%s">%s</a></li>' % (entry, entry)
        resp = Response(page % res, mimetype='text/html')
    elif path == 'robots.txt':
        dat = u"User-agent: *\nDisallow: /routerInfo-*.dat$\n"
        resp = Response(dat, mimetype='text/plain')
    else:
        # load file
        f = open(path, 'rb')
        resp = Response(f.read(), mimetype='application/octet-stream')
        f.close()
    resp.add_etag()
    return resp(environ, start_response)

if __name__ == '__main__':
    run_simple('localhost', 5007, app)
