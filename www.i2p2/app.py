from werkzeug import BaseRequest, BaseResponse, ETagResponseMixin, escape, run_simple, SharedDataMiddleware
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from jinja import Environment, FileSystemLoader
from jinja.exceptions import TemplateNotFound
import os
import sha
from time import time
from random import randint

class Request(BaseRequest):
    """Useful subclass of the default request that knows how to build urls."""

    def __init__(self, environ):
        BaseRequest.__init__(self, environ)


class Response(BaseResponse, ETagResponseMixin):
    """Subclass of base response that has a default mimetype of text/html."""
    default_mimetype = 'text/html'


# setup jinja
env = Environment(loader=FileSystemLoader('pages', use_memcache=True))

def read_mirrors():
    file = open('mirrors', 'r')
    dat = file.read()
    file.close()
    return dat.split('\n')

def app(environ, start_response):
    """The WSGI application that connects all together."""
    req = Request(environ)
    path = req.path[1:].lower()
    if path == '':
        path = 'index'
    mime_type='text/html'
    try:
        try:
            path.index('.')
            tmpl = env.get_template(path)
            if path[-3:] == 'txt':
                mime_type='text/plain'
            if path[-3:] == 'xml':
                mime_type='text/xml'
        except ValueError:
            tmpl = env.get_template(path + '.html')
    except TemplateNotFound:
        tmpl = env.get_template('not_found.html')
    resp = Response(tmpl.render(), mimetype=mime_type)
    resp.add_etag()
    return resp(environ, start_response)

app = SharedDataMiddleware(app, {
    '/_static': os.path.join(os.path.dirname(__file__), 'static'),
    '/.bzr': os.path.join(os.path.dirname(__file__), '../.bzr')
})
if __name__ == '__main__':
    run_simple('localhost', 5009, app)
